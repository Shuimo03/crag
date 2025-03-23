import logging

import requests
import secrets
from typing import Dict, Any, Optional
from fastapi.responses import RedirectResponse
from app.util import config

# 获取日志记录器
logger = logging.getLogger(__name__)


class GitHubOAuthService:
    """GitHub OAuth服务"""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化 GitHub OAuth 服务
        
        Args:
            config_dict: 可选的配置字典，如果提供则使用，否则从全局配置获取
        """
        # 获取配置
        if config_dict is None:
            config_dict = config.get_config()
        
        # 从配置中获取值
        self.client_id = config_dict.get("GITHUB_CLIENT_ID", "")
        self.client_secret = config_dict.get("GITHUB_CLIENT_SECRET", "")
        self.redirect_uri = config_dict.get("GITHUB_REDIRECT_URI", "http://127.0.0.1:8001/api/auth/github/callback")
        
        # 记录配置获取结果
        # logger.info(f"GitHubOAuthService 已初始化，client_id={bool(self.client_id)}, redirect_uri={self.redirect_uri}")
        
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.api_url = "https://api.github.com"
        # 存储状态值，用于防止CSRF攻击
        self.states = {}

    def generate_state(self) -> str:
        """
        生成随机状态值

        Returns:
            随机状态字符串
        """
        state = secrets.token_urlsafe(16)
        self.states[state] = True
        return state

    def validate_state(self, state: str) -> bool:
        """
        验证状态值

        Args:
            state: 状态值

        Returns:
            是否有效
        """
        if state in self.states:
            # 使用后删除，确保一次性使用
            del self.states[state]
            return True
        return False

    def get_authorization_redirect(self, state: Optional[str] = None) -> RedirectResponse:
        """
        获取重定向到GitHub授权页面的响应

        Args:
            state: 可选的状态参数

        Returns:
            重定向响应
        """
        auth_url = self.get_authorization_url(state)
        logger.info(f"授权 URL: {auth_url}")
        return RedirectResponse(url=auth_url)

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        获取GitHub授权URL

        Args:
            state: 可选的状态参数，用于防止CSRF攻击

        Returns:
            授权URL
        """
        if not state:
            state = self.generate_state()

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": "repo,user"
        }

        # 构建URL参数
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"



    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        用授权码交换访问令牌

        Args:
            code: GitHub返回的授权码

        Returns:
            包含访问令牌的字典
        """
        headers = {
            "Accept": "application/json"
        }

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            if "error" in token_data:
                raise Exception(f"获取访问令牌失败: {token_data['error_description']}")
            return token_data
        else:
            raise Exception(f"获取访问令牌失败: {response.text}")

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        获取GitHub用户信息

        Args:
            access_token: GitHub访问令牌

        Returns:
            用户信息字典
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        response = requests.get(f"{self.api_url}/user", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取用户信息失败: {response.text}")

    def get_user_emails(self, access_token: str) -> list:
        """
        获取GitHub用户邮箱

        Args:
            access_token: GitHub访问令牌

        Returns:
            用户邮箱列表
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        response = requests.get(f"{self.api_url}/user/emails", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取用户邮箱失败: {response.text}")


def create_github_service(config_dict: Optional[Dict[str, Any]] = None) -> GitHubOAuthService:
    """
    创建 GitHubOAuthService 实例的工厂函数
    
    Args:
        config_dict: 可选的配置字典
        
    Returns:
        GitHubOAuthService 实例
    """
    return GitHubOAuthService(config_dict)
