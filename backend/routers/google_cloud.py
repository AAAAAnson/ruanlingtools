"""
Google Cloud API路由
处理OAuth授权和批量生成API密钥
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, Field

from services.google_cloud_service import GoogleCloudService
from utils.response import ApiResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# 临时存储OAuth凭据（生产环境建议使用Redis或数据库）
# Key: state, Value: credentials
oauth_credentials_store = {}
oauth_state_store = {}


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    count: int = Field(..., ge=1, le=20, description="生成数量（1-20）")


@router.get("/oauth/authorize")
async def get_oauth_url(request: Request):
    """
    获取Google Cloud OAuth授权URL

    Returns:
        授权URL和state
    """
    try:
        # 构建回调地址
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/api/google-cloud/oauth/callback"

        logger.info(f"Generating OAuth URL with redirect_uri: {redirect_uri}")

        gcp_service = GoogleCloudService()
        auth_url, state = gcp_service.get_oauth_url(redirect_uri)

        # 保存state用于验证
        oauth_state_store[state] = True

        return ApiResponse.success(
            data={
                "auth_url": auth_url,
                "state": state
            },
            message="OAuth authorization URL generated"
        )

    except Exception as e:
        logger.error(f"Error generating OAuth URL: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to generate OAuth URL: {str(e)}",
            code=500
        )


@router.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter"),
    request: Request = None
):
    """
    OAuth回调处理

    Args:
        code: OAuth授权码
        state: OAuth state参数
    """
    try:
        # 验证state
        if state not in oauth_state_store:
            logger.error(f"Invalid OAuth state: {state}")
            return HTMLResponse(
                content="""
                <html>
                    <body>
                        <h1>授权失败</h1>
                        <p>无效的state参数</p>
                        <a href="/settings">返回设置页面</a>
                    </body>
                </html>
                """,
                status_code=400
            )

        # 构建回调地址（必须与授权时一致）
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/api/google-cloud/oauth/callback"

        logger.info(f"Processing OAuth callback with redirect_uri: {redirect_uri}")

        # 交换授权码获取凭据
        gcp_service = GoogleCloudService()
        credentials = gcp_service.exchange_code_for_credentials(code, redirect_uri, state)

        # 保存凭据
        oauth_credentials_store[state] = credentials

        logger.info(f"OAuth authorization successful, state: {state}")

        # 重定向到前端settings页面
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <meta http-equiv="refresh" content="3;url=/settings?oauth=success&state={state}" />
                </head>
                <body>
                    <h1>授权成功！</h1>
                    <p>正在跳转回设置页面...</p>
                    <p>如果没有自动跳转，请点击 <a href="/settings?oauth=success&state={state}">这里</a></p>
                </body>
            </html>
            """
        )

    except Exception as e:
        logger.error(f"OAuth callback error: {e}", exc_info=True)
        return HTMLResponse(
            content=f"""
            <html>
                <body>
                    <h1>授权失败</h1>
                    <p>错误信息: {str(e)}</p>
                    <a href="/settings">返回设置页面</a>
                </body>
            </html>
            """,
            status_code=500
        )


@router.get("/oauth/status")
async def get_oauth_status(state: str = Query(..., description="OAuth state")):
    """
    检查OAuth授权状态

    Args:
        state: OAuth state参数

    Returns:
        授权状态
    """
    try:
        is_authorized = state in oauth_credentials_store

        return ApiResponse.success(
            data={
                "authorized": is_authorized,
                "state": state
            },
            message="Authorized" if is_authorized else "Not authorized"
        )

    except Exception as e:
        logger.error(f"Error checking OAuth status: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to check OAuth status: {str(e)}",
            code=500
        )


@router.post("/keys/batch-generate")
async def batch_generate_keys(
    request: BatchGenerateRequest,
    state: str = Query(..., description="OAuth state from authorization")
):
    """
    批量生成API密钥

    Args:
        request: 生成请求（包含数量）
        state: OAuth state参数

    Returns:
        生成结果
    """
    try:
        # 检查是否已授权
        if state not in oauth_credentials_store:
            return ApiResponse.error(
                message="Not authorized. Please authorize with Google Cloud first.",
                code=401
            )

        credentials = oauth_credentials_store[state]
        gcp_service = GoogleCloudService(credentials=credentials)

        # 进度消息列表
        progress_messages = []

        async def progress_callback(message: str):
            progress_messages.append(message)
            logger.info(f"Generation progress: {message}")

        # 批量生成
        logger.info(f"Starting batch generation of {request.count} API keys")
        results = await gcp_service.batch_generate_keys(
            count=request.count,
            progress_callback=progress_callback
        )

        # 统计成功/失败
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']

        logger.info(f"Batch generation completed: {len(successful)} success, {len(failed)} failed")

        return ApiResponse.success(
            data={
                "total": request.count,
                "successful": len(successful),
                "failed": len(failed),
                "keys": [r['api_key'] for r in successful],
                "details": results,
                "progress": progress_messages
            },
            message=f"Generated {len(successful)}/{request.count} API keys successfully"
        )

    except Exception as e:
        logger.error(f"Error generating API keys: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to generate API keys: {str(e)}",
            code=500
        )
