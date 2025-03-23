import secrets
import time
from typing import Dict, Any, Optional
from fastapi import Request, Response
from app.util.config import get_value

class SessionManager:
    """会话管理器，用于处理用户会话"""
    
    def __init__(self):
        self.secret_key = get_value("SESSION_SECRET_KEY", "default_secret_key")
        self.cookie_name = "crag_session"
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lifetime = int(get_value("SESSION_LIFETIME", 3600))  # 默认1小时
    
    def create_session(self) -> str:
        """创建新会话并返回会话ID"""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        return session_id
    
    def get_session_id(self, request: Request) -> Optional[str]:
        """从请求中获取会话ID"""
        session_id = request.cookies.get(self.cookie_name)
        
        # 如果会话ID存在，检查是否有效
        if session_id and session_id in self.sessions:
            # 更新最后访问时间
            self.sessions[session_id]["last_accessed"] = time.time()
            return session_id
        
        return None
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """获取会话数据"""
        if session_id not in self.sessions:
            return {}
        
        # 检查会话是否过期
        if self._is_session_expired(session_id):
            self.delete_session(session_id)
            return {}
        
        # 更新最后访问时间
        self.sessions[session_id]["last_accessed"] = time.time()
        
        # 返回会话数据（排除内部字段）
        return {k: v for k, v in self.sessions[session_id].items() 
                if k not in ["created_at", "last_accessed"]}
    
    def set_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        """设置会话数据"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": time.time(),
                "last_accessed": time.time()
            }
        
        # 更新会话数据，保留内部字段
        self.sessions[session_id].update(data)
        self.sessions[session_id]["last_accessed"] = time.time()
    
    def delete_session(self, session_id: str) -> None:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def set_session_cookie(self, response: Response, session_id: str) -> None:
        """设置会话Cookie"""
        secure = get_value("COOKIE_SECURE", False)
        response.set_cookie(
            key=self.cookie_name,
            value=session_id,
            httponly=True,
            secure=secure,  # 在生产环境中应设为True
            max_age=self.session_lifetime,
            samesite="lax"
        )
    
    def clear_session_cookie(self, response: Response) -> None:
        """清除会话Cookie"""
        response.delete_cookie(key=self.cookie_name)
    
    def _is_session_expired(self, session_id: str) -> bool:
        """检查会话是否过期"""
        if session_id not in self.sessions:
            return True
        
        last_accessed = self.sessions[session_id].get("last_accessed", 0)
        return (time.time() - last_accessed) > self.session_lifetime
    
    def cleanup_expired_sessions(self) -> None:
        """清理过期会话"""
        expired_sessions = [
            session_id for session_id in self.sessions
            if self._is_session_expired(session_id)
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)

# 创建全局会话管理器实例
session_manager = SessionManager()
