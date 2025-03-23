from fastapi import APIRouter
from app.routers import auth, github

# 创建主路由
router = APIRouter()

# 注册认证路由
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

# 注册GitHub路由
router.include_router(
    github.router,
    prefix="/auth/github",
    tags=["github"]
)
