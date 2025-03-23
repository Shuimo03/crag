from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from app.services.github_oauth_service import GitHubOAuthService
from app.services.github_repos_service import GithubReposService, create_repos_service, GitHubApiError, RateLimitExceededError
from app.core.session import session_manager
from app.core.service_provider import service_provider
from app.core.service_context import service_context
import logging

# 设置日志
logger = logging.getLogger(__name__)
router = APIRouter()

# 依赖函数，用于获取 GitHubOAuthService 实例
def get_github_service() -> GitHubOAuthService:
    """
    获取 GitHubOAuthService 实例
    
    Returns:
        GitHubOAuthService 实例
    """
    # 优先从服务上下文获取
    if service_context:
        return service_context.get(GitHubOAuthService)
    
    # 如果服务上下文不可用，则从服务提供者获取
    return service_provider.get(GitHubOAuthService)


# 添加依赖项函数
def get_repos_service(request: Request):
    """
    获取 GitHub 仓库服务实例

    Args:
        request: FastAPI 请求对象

    Returns:
        GithubReposService 实例
    """
    session_id = session_manager.get_session_id(request)
    if not session_id:
        return create_repos_service()

    session_data = session_manager.get_session_data(session_id)
    github_data = session_data.get("github", {})
    access_token = github_data.get("access_token")

    return create_repos_service(access_token)

@router.get("/login")
async def github_login(request: Request, github_service: GitHubOAuthService = Depends(get_github_service)):
    """
    重定向到GitHub授权页面
    """

    # 生成状态并存储重定向URL
    state = github_service.generate_state()
    
    # 创建或获取会话
    session_id = session_manager.get_session_id(request)
    if not session_id:
        session_id = session_manager.create_session()

    # 存储状态和重定向URL到会话
    session_manager.set_session_data(session_id, {
        "oauth_state": state,
        "redirect_after_login": "http://localhost:5173/repos"
    })

    # 获取授权重定向
    response = github_service.get_authorization_redirect(state)
    
    # 设置会话Cookie
    session_manager.set_session_cookie(response, session_id)
    
    return response


@router.get("/callback")
async def github_callback(
        request: Request,
        code: str,
        state: str = None,
        github_service: GitHubOAuthService = Depends(get_github_service)
):
    """
    处理GitHub回调

    Args:
        request: FastAPI请求对象
        code: GitHub返回的授权码
        state: 状态参数
        github_service: GitHubOAuthService 实例
    """
    try:
        # 获取会话ID
        session_id = session_manager.get_session_id(request)
        if not session_id:
            raise HTTPException(status_code=400, detail="无效的会话")

        # 获取会话数据
        session_data = session_manager.get_session_data(session_id)

        # 验证状态
        stored_state = session_data.get("oauth_state")
        if not state or state != stored_state:
            raise HTTPException(status_code=400, detail="无效的状态参数")

        # 获取登录后重定向URL
        redirect_after_login = session_data.get("redirect_after_login", "/")

        # 交换授权码获取访问令牌
        token_data = github_service.exchange_code_for_token(code)

        # 获取访问令牌
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="获取访问令牌失败")

        # 获取用户信息
        user_info = github_service.get_user_info(access_token)

        # 获取用户邮箱
        user_emails = github_service.get_user_emails(access_token)

        # 获取主邮箱
        primary_email = next((email.get("email") for email in user_emails if email.get("primary")), None)

        # 存储用户信息到会话
        session_manager.set_session_data(session_id, {
            "user": {
                "id": user_info.get("id"),
                "login": user_info.get("login"),
                "name": user_info.get("name"),
                "email": primary_email,
                "avatar_url": user_info.get("avatar_url")
            },
            "github": {
                "access_token": access_token
            }
        })

        # 创建响应
        response = RedirectResponse(url=redirect_after_login)

        # 设置会话Cookie
        session_manager.set_session_cookie(response, session_id)

        return response

    except HTTPException as e:
        logger.error(f"GitHub OAuth错误: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.detail}
        )
    except Exception as e:
        logger.error(f"GitHub OAuth未知错误: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"认证过程中发生错误: {str(e)}"}
        )



@router.get("/repos")
async def github_repos(
        request: Request,
        sort: str = "updated",
        direction: str = "desc",
        per_page: int = 30,
        page: int = 1,
        visibility: str = "all",
        repos_service=Depends(get_repos_service)
):
    """
    获取已登录用户的仓库列表

    Args:
        request: FastAPI 请求对象
        sort: 排序字段
        direction: 排序方向
        per_page: 每页结果数量
        page: 页码
        visibility: 可见性过滤
        repos_service: GitHub 仓库服务实例
    """
    # 获取会话ID
    session_id = session_manager.get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=401, detail="未登录，请先登录")

    # 获取会话数据
    session_data = session_manager.get_session_data(session_id)
    github_data = session_data.get("github", {})
    access_token = github_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="未找到有效的GitHub令牌，请重新登录")

    # 确保服务有正确的访问令牌
    repos_service.set_access_token(access_token)

    try:
        # 获取仓库列表
        repos = await repos_service.get_authenticated_user_repos(
            sort=sort,
            direction=direction,
            per_page=per_page,
            page=page,
            visibility=visibility
        )

        # 处理响应数据，只返回需要的字段
        simplified_repos = []
        for repo in repos:
            simplified_repos.append({
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "html_url": repo.get("html_url"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count"),
                "forks_count": repo.get("forks_count"),
                "visibility": repo.get("visibility"),
                "default_branch": repo.get("default_branch"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "owner": {
                    "login": repo.get("owner", {}).get("login"),
                    "avatar_url": repo.get("owner", {}).get("avatar_url")
                }
            })

        return {
            "repos": simplified_repos,
            "page": page,
            "per_page": per_page,
            "total": len(simplified_repos)  # 注意：这不是总数，只是当前页的数量
        }

    except RateLimitExceededError as e:
        logger.error(f"GitHub API 速率限制: {str(e)}")
        raise HTTPException(
            status_code=429,
            detail=f"GitHub API 速率限制已达到，请稍后再试: {str(e)}"
        )

    except GitHubApiError as e:
        logger.error(f"获取仓库列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仓库列表失败: {str(e)}")

    except Exception as e:
        logger.exception(f"未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/pullrequest")
async  def github_pull_request(request):
    pass
