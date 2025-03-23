from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.core.session import session_manager

router = APIRouter()

@router.get("/logout")
async def logout(request: Request):
    """
    用户登出
    
    Args:
        request: FastAPI请求对象
    """
    # 获取会话ID
    session_id = session_manager.get_session_id(request)
    
    if session_id:
        # 删除会话
        session_manager.delete_session(session_id)
    
    # 创建响应
    response = RedirectResponse(url="/")
    
    # 清除会话Cookie
    session_manager.clear_session_cookie(response)
    
    return response

@router.get("/me")
async def get_current_user(request: Request):
    """
    获取当前登录用户信息
    
    Args:
        request: FastAPI请求对象
    """
    # 获取会话ID
    session_id = session_manager.get_session_id(request)
    
    if not session_id:
        return {"authenticated": False}
    
    # 获取会话数据
    session_data = session_manager.get_session_data(session_id)
    user = session_data.get("user")
    
    if not user:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user": user
    }
