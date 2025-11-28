# -*- coding: utf-8 -*-
"""
Settings management routes

This module handles application settings configuration
"""
import logging
import os
import json
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from models.response import ApiResponse
from models.settings import ApplicationSettings, YouTubeAPIKeyUpdate
from services.settings_service import get_settings_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_settings():
    """
    Get current application settings

    Returns:
        ApiResponse with current settings
    """
    try:
        settings_service = get_settings_service()
        settings = settings_service.load_settings()

        # Mask API keys for security (show only last 6 characters)
        masked_settings = settings.model_dump()
        if masked_settings.get('youtube', {}).get('api_keys'):
            masked_keys = []
            for key in masked_settings['youtube']['api_keys']:
                if len(key) > 6:
                    masked_keys.append('***' + key[-6:])
                else:
                    masked_keys.append('***')
            masked_settings['youtube']['api_keys'] = masked_keys

        return ApiResponse.success(
            data=masked_settings,
            message="Settings retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting settings: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to get settings: {str(e)}",
            code=500
        )


@router.put("/youtube-keys")
async def update_youtube_keys(update: YouTubeAPIKeyUpdate):
    """
    Update YouTube API keys

    Args:
        update: YouTube API keys update data

    Returns:
        ApiResponse with updated settings
    """
    try:
        settings_service = get_settings_service()

        # Validate keys (basic format check)
        invalid_keys = []
        for i, key in enumerate(update.api_keys):
            if not key or len(key) < 30:  # YouTube keys are typically 39 chars
                invalid_keys.append(f"Key #{i+1}")

        if invalid_keys:
            return ApiResponse.error(
                message=f"Invalid API key format: {', '.join(invalid_keys)}",
                code=400
            )

        # Update keys
        settings = settings_service.update_youtube_keys(
            api_keys=update.api_keys,
            per_key_budget=update.per_key_budget
        )

        logger.info(f"Updated {len(update.api_keys)} YouTube API keys")

        return ApiResponse.success(
            data={
                "api_keys_count": len(update.api_keys),
                "per_key_budget": settings.youtube.per_key_budget
            },
            message=f"Successfully updated {len(update.api_keys)} YouTube API key(s)"
        )
    except Exception as e:
        logger.error(f"Error updating YouTube keys: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to update YouTube keys: {str(e)}",
            code=500
        )


@router.delete("/youtube-keys")
async def clear_youtube_keys():
    """
    Clear all YouTube API keys

    Returns:
        ApiResponse confirming deletion
    """
    try:
        settings_service = get_settings_service()
        settings = settings_service.update_youtube_keys(api_keys=[])

        logger.info("Cleared all YouTube API keys")

        return ApiResponse.success(
            message="All YouTube API keys have been cleared"
        )
    except Exception as e:
        logger.error(f"Error clearing YouTube keys: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to clear YouTube keys: {str(e)}",
            code=500
        )


@router.get("/youtube-keys/status")
async def get_youtube_keys_status():
    """
    Get YouTube API keys configuration status

    Returns:
        ApiResponse with keys status (count, masked keys)
    """
    try:
        settings_service = get_settings_service()
        keys = settings_service.get_youtube_keys()

        # Mask keys
        masked_keys = []
        for key in keys:
            if len(key) > 6:
                masked_keys.append('***' + key[-6:])
            else:
                masked_keys.append('***')

        return ApiResponse.success(
            data={
                "configured": len(keys) > 0,
                "keys_count": len(keys),
                "keys": masked_keys
            },
            message=f"{len(keys)} YouTube API key(s) configured"
        )
    except Exception as e:
        logger.error(f"Error getting YouTube keys status: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to get YouTube keys status: {str(e)}",
            code=500
        )


class BatchAddKeysRequest(BaseModel):
    """批量添加密钥请求"""
    api_keys: List[str] = Field(..., min_items=1, max_items=50, description="API密钥列表")


@router.get("/youtube/keys/detailed")
async def get_detailed_keys_info():
    """
    获取所有API密钥的详细使用情况（用于Settings页面）

    Returns:
        详细的密钥使用信息
    """
    try:
        from services.youtube_service import YouTubeService
        from services.youtube_quota_service import YouTubeQuotaService

        # 获取API密钥数量和实际密钥
        try:
            yt_service = YouTubeService()
            num_keys = len(yt_service.api_keys)
            api_keys = yt_service.api_keys
        except ValueError:
            # No API keys configured
            return ApiResponse.success(
                data={
                    'summary': {
                        'total_keys': 0,
                        'total_used': 0,
                        'total_remaining': 0,
                        'total_quota': 0,
                        'usage_percent': 0
                    },
                    'keys': []
                },
                message="No API keys configured"
            )

        # 获取详细信息
        quota_service = YouTubeQuotaService()
        detailed_info = quota_service.get_detailed_keys_info(num_keys)

        # 添加前端需要的字段
        for i, key_info in enumerate(detailed_info['keys']):
            # 获取实际的API密钥并创建masked版本
            actual_key = api_keys[i] if i < len(api_keys) else ''
            if len(actual_key) > 10:
                masked_key = actual_key[:4] + '...' + actual_key[-6:]
            else:
                masked_key = '****...****'

            # 添加前端期望的字段
            key_info['id'] = str(i)  # 使用索引作为ID
            key_info['masked_key'] = masked_key
            key_info['quota_used'] = key_info['used']  # 添加别名
            key_info['quota_remaining'] = key_info['remaining']  # 添加别名
            key_info['daily_budget'] = quota_service.DAILY_QUOTA_LIMIT

        return ApiResponse.success(
            data=detailed_info,
            message=f"Retrieved detailed info for {num_keys} API keys"
        )

    except Exception as e:
        logger.error(f"Error getting detailed keys info: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to get detailed keys info: {str(e)}",
            code=500
        )


@router.delete("/youtube/keys/{key_id}")
async def delete_youtube_key(key_id: str):
    """
    删除单个YouTube API密钥

    Args:
        key_id: 密钥ID（索引）

    Returns:
        ApiResponse confirming deletion
    """
    try:
        # 验证key_id是有效的数字
        try:
            key_index = int(key_id)
        except ValueError:
            return ApiResponse.error(
                message="Invalid key ID format",
                code=400
            )

        # 获取当前所有密钥
        settings_service = get_settings_service()
        current_keys = settings_service.get_youtube_keys()

        # 验证索引是否有效
        if key_index < 0 or key_index >= len(current_keys):
            return ApiResponse.error(
                message=f"Key ID {key_id} not found",
                code=404
            )

        # 删除指定索引的密钥
        deleted_key = current_keys.pop(key_index)
        masked_deleted = deleted_key[:4] + '...' + deleted_key[-6:] if len(deleted_key) > 10 else '****'

        # 更新设置
        settings_service.update_youtube_keys(api_keys=current_keys)

        logger.info(f"Deleted YouTube API key at index {key_index}: {masked_deleted}")

        return ApiResponse.success(
            data={
                "deleted_index": key_index,
                "remaining_keys": len(current_keys)
            },
            message=f"Successfully deleted API key {masked_deleted}"
        )

    except Exception as e:
        logger.error(f"Error deleting YouTube key: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to delete YouTube key: {str(e)}",
            code=500
        )


@router.post("/youtube/keys/batch")
async def batch_add_keys(request: BatchAddKeysRequest):
    """
    批量添加API密钥到配置

    Args:
        request: 包含API密钥列表的请求

    Returns:
        添加结果
    """
    try:
        # 验证密钥格式（YouTube API密钥通常以AIza开头，长度39字符）
        invalid_keys = []
        for key in request.api_keys:
            if not key.startswith('AIza') or len(key) != 39:
                invalid_keys.append(key[:10] + '...')

        if invalid_keys:
            return ApiResponse.error(
                message=f"Invalid API key format: {', '.join(invalid_keys)}",
                code=400
            )

        # 使用settings service添加密钥
        settings_service = get_settings_service()
        existing_keys = settings_service.get_youtube_keys()

        # 去重并添加新密钥
        existing_keys_set = set(existing_keys)
        new_keys = [key for key in request.api_keys if key not in existing_keys_set]

        all_keys = existing_keys + new_keys

        # 更新设置
        settings_service.update_youtube_keys(api_keys=all_keys)

        logger.info(f"Batch added {len(new_keys)} new API keys")

        return ApiResponse.success(
            data={
                "added_count": len(new_keys),
                "total_keys": len(all_keys),
                "duplicates_skipped": len(request.api_keys) - len(new_keys)
            },
            message=f"Successfully added {len(new_keys)} new API keys"
        )

    except Exception as e:
        logger.error(f"Error batch adding keys: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to batch add keys: {str(e)}",
            code=500
        )
