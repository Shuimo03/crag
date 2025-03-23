import logging
from typing import List, Dict, Any, Optional
import httpx
from app.util import config

logger = logging.getLogger(__name__)


class GitHubApiError(Exception):
    """GitHub API 相关错误的基类"""
    pass


class RateLimitExceededError(GitHubApiError):
    """API 速率限制异常"""

    def __init__(self, reset_time):
        self.reset_time = reset_time
        super().__init__(f"GitHub API 速率限制已达到，将在 {reset_time} 重置")


class GithubReposService:
    """GitHub 仓库服务，用于获取仓库信息"""

    def __init__(self, access_token=None, config_dict=None):
        """
        初始化 GitHub 仓库服务

        Args:
            access_token: GitHub 访问令牌，如果提供则使用此令牌
            config_dict: 可选的配置字典
        """
        # 获取配置
        if config_dict is None:
            config_dict = config.get_config()

        self.access_token = access_token
        self.api_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

        logger.info("GithubReposService 已初始化")

    def set_access_token(self, access_token: str):
        """
        设置 GitHub 访问令牌

        Args:
            access_token: GitHub 访问令牌
        """
        self.access_token = access_token
        self.headers["Authorization"] = f"Bearer {access_token}"

    async def get_authenticated_user_repos(
            self,
            sort: str = "updated",
            direction: str = "desc",
            per_page: int = 30,
            page: int = 1,
            visibility: str = "all"  # all, public, private
    ) -> List[Dict[str, Any]]:
        """
        获取已认证用户的仓库列表

        Args:
            sort: 排序字段，可选值：created, updated, pushed, full_name
            direction: 排序方向，可选值：asc, desc
            per_page: 每页结果数量
            page: 页码
            visibility: 可见性过滤，可选值：all, public, private

        Returns:
            仓库列表

        Raises:
            GitHubApiError: 当 API 调用失败时
        """
        if not self.access_token:
            raise GitHubApiError("需要访问令牌才能获取仓库列表")

        url = f"{self.api_url}/user/repos"

        params = {
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page,
            "visibility": visibility
        }

        logger.info(f"获取已认证用户的仓库列表, 排序={sort}, 页码={page}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                repos = response.json()

                logger.info(f"成功获取 {len(repos)} 个仓库")
                return repos

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403 and "rate limit" in e.response.text.lower():
                reset_time = e.response.headers.get("X-RateLimit-Reset", "unknown time")
                logger.error(f"GitHub API 速率限制错误: {reset_time}")
                raise RateLimitExceededError(reset_time)

            logger.error(f"获取仓库列表失败: {str(e)}")
            raise GitHubApiError(f"获取仓库列表失败: {str(e)}")

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"请求 GitHub API 时发生错误: {str(e)}")
            raise GitHubApiError(f"网络错误: {str(e)}")

    async def get_user_repos(
            self,
            username: str,
            sort: str = "updated",
            direction: str = "desc",
            per_page: int = 30,
            page: int = 1,
            type: str = "owner"  # owner, member
    ) -> List[Dict[str, Any]]:
        """
        获取指定用户的仓库列表

        Args:
            username: GitHub 用户名
            sort: 排序字段，可选值：created, updated, pushed, full_name
            direction: 排序方向，可选值：asc, desc
            per_page: 每页结果数量
            page: 页码
            type: 仓库类型，可选值：all, owner, member

        Returns:
            仓库列表

        Raises:
            GitHubApiError: 当 API 调用失败时
        """
        url = f"{self.api_url}/users/{username}/repos"

        params = {
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page,
            "type": type
        }

        logger.info(f"获取用户 {username} 的仓库列表, 排序={sort}, 页码={page}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                repos = response.json()

                logger.info(f"成功获取 {len(repos)} 个仓库")
                return repos

        except httpx.HTTPStatusError as e:
            logger.error(f"获取用户仓库列表失败: {str(e)}")
            raise GitHubApiError(f"获取用户仓库列表失败: {str(e)}")

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"请求 GitHub API 时发生错误: {str(e)}")
            raise GitHubApiError(f"网络错误: {str(e)}")

    async def get_org_repos(
            self,
            org: str,
            sort: str = "updated",
            direction: str = "desc",
            per_page: int = 30,
            page: int = 1,
            type: str = "all"  # all, public, private, forks, sources, member
    ) -> List[Dict[str, Any]]:
        """
        获取指定组织的仓库列表

        Args:
            org: GitHub 组织名称
            sort: 排序字段，可选值：created, updated, pushed, full_name
            direction: 排序方向，可选值：asc, desc
            per_page: 每页结果数量
            page: 页码
            type: 仓库类型

        Returns:
            仓库列表

        Raises:
            GitHubApiError: 当 API 调用失败时
        """
        url = f"{self.api_url}/orgs/{org}/repos"

        params = {
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page,
            "type": type
        }

        logger.info(f"获取组织 {org} 的仓库列表, 排序={sort}, 页码={page}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                repos = response.json()

                logger.info(f"成功获取 {len(repos)} 个仓库")
                return repos

        except httpx.HTTPStatusError as e:
            logger.error(f"获取组织仓库列表失败: {str(e)}")
            raise GitHubApiError(f"获取组织仓库列表失败: {str(e)}")

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"请求 GitHub API 时发生错误: {str(e)}")
            raise GitHubApiError(f"网络错误: {str(e)}")

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        获取单个仓库的详细信息

        Args:
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            仓库详细信息

        Raises:
            GitHubApiError: 当 API 调用失败时
        """
        url = f"{self.api_url}/repos/{owner}/{repo}"

        logger.info(f"获取仓库信息: {owner}/{repo}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"仓库不存在: {owner}/{repo}")
                raise GitHubApiError(f"仓库 {owner}/{repo} 不存在")

            logger.error(f"获取仓库信息失败: {str(e)}")
            raise GitHubApiError(f"获取仓库信息失败: {str(e)}")

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"请求 GitHub API 时发生错误: {str(e)}")
            raise GitHubApiError(f"网络错误: {str(e)}")


# 工厂函数
def create_repos_service(access_token=None, config_dict=None) -> GithubReposService:
    """
    创建 GitHub 仓库服务实例

    Args:
        access_token: GitHub 访问令牌
        config_dict: 可选的配置字典

    Returns:
        GithubReposService 实例
    """
    return GithubReposService(access_token, config_dict)