import os
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import routes
from app.util.config import load_config, get_value, setup_logging
from app.core.session import session_manager
from app.core.service_provider import service_provider
from app.core.service_context import ServiceContext
from app.services.github_oauth_service import GitHubOAuthService, create_github_service

# 标记服务是否已注册
_services_registered = False

# 预加载配置，确保只加载一次
def preload_config():
    """预加载配置，确保只加载一次"""
    # 使用绝对路径加载配置
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", ".config.dev.yaml")
    
    # 加载配置
    config = load_config(config_path)
    return config

# 预加载配置
cnf = preload_config()

# 创建服务上下文
service_context = ServiceContext(cnf)

def create_app() -> FastAPI:
    """
    创建FastAPI应用

    Returns:
        FastAPI应用实例
    """
    # 首先设置日志系统
    setup_logging()
    
    # 注册服务
    register_services()
    
    # 创建应用
    app = FastAPI(
        title="CRAG API",
        description="代码审查智能助手 API",
        version="0.1.0"
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_value("CORS_ORIGINS", ["*"]),  # 允许的来源列表
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加会话清理中间件
    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        # 处理请求前的操作
        response = await call_next(request)
        
        # 处理请求后的操作
        # 每100个请求清理一次过期会话（可以根据需要调整）
        if hash(request.url.path) % 100 == 0:
            session_manager.cleanup_expired_sessions()
        
        return response

    # 注册API路由
    app.include_router(routes.router, prefix="/api")

    # 添加健康检查路由
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


def register_services():
    """
    注册所有服务，确保只注册一次
    """
    global _services_registered, service_context
    
    if _services_registered:
        logging.debug("服务已注册，跳过")
        return
    
    # 使用服务上下文注册 GitHubOAuthService
    github_service = service_context.register(GitHubOAuthService)
    
    # 同时注册到服务提供者，保持向后兼容
    service_provider.register_instance(GitHubOAuthService, github_service)
    
    _services_registered = True


# 创建应用实例
run = create_app()
# 如果直接运行此文件，则启动服务器
if __name__ == "__main__":
    # 配置 Uvicorn 日志
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.WARNING)
    
    # 配置 Uvicorn 访问日志
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(logging.WARNING)
    
    # 从环境变量获取是否启用热重载
    enable_reload = os.environ.get("ENABLE_RELOAD", "").lower() == "true"
    
    host = get_value("HOST", "127.0.0.1")
    port = int(get_value("PORT", 8001))
    
    print(f"启动服务器: http://{host}:{port} {'(热重载已启用)' if enable_reload else '(热重载已禁用)'}")
    

    uvicorn.run(
    "app.main:run",
        host=host,
        port=port,
        reload=enable_reload,  # 根据环境变量决定是否启用热重载
        reload_excludes=["*.pyc", "*.pyo", "__pycache__"] if enable_reload else None,  # 排除缓存文件
        log_level="warning"  # 降低日志级别
    )
