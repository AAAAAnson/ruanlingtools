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

        # 获取API密钥
        settings_service = get_settings_service()
        api_keys = settings_service.get_youtube_keys()
        num_keys = len(api_keys)

        if num_keys == 0:
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

        # 转换数据格式以匹配前端期望
        transformed_keys = []
        for key_info in detailed_info['keys']:
            index = key_info['index']
            # 获取masked key
            masked_key = '***' + api_keys[index][-6:] if len(api_keys[index]) > 6 else '***'

            transformed_keys.append({
                'id': str(index),  # 前端使用id而不是index
                'masked_key': masked_key,
                'status': key_info['status'],
                'quota_used': key_info['used'],  # 前端使用quota_used而不是used
                'quota_remaining': key_info['remaining'],  # 前端使用quota_remaining而不是remaining
                'daily_budget': 10000,  # YouTube API每日配额限制
                'last_used': key_info['last_used']
            })

        response_data = {
            'summary': detailed_info['summary'],
            'keys': transformed_keys
        }

        return ApiResponse.success(
            data=response_data,
            message=f"Retrieved detailed info for {num_keys} API keys"
        )

    except Exception as e:
        logger.error(f"Error getting detailed keys info: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to get detailed keys info: {str(e)}",
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


@router.delete("/youtube/keys/{key_index}")
async def delete_youtube_key(key_index: int):
    """
    删除指定的YouTube API密钥

    Args:
        key_index: 密钥索引（0-based）

    Returns:
        删除结果
    """
    try:
        settings_service = get_settings_service()
        existing_keys = settings_service.get_youtube_keys()

        # 验证索引
        if key_index < 0 or key_index >= len(existing_keys):
            return ApiResponse.error(
                message=f"Invalid key index: {key_index}",
                code=400
            )

        # 删除密钥
        deleted_key = existing_keys.pop(key_index)
        settings_service.update_youtube_keys(api_keys=existing_keys)

        logger.info(f"Deleted API key at index {key_index}")

        return ApiResponse.success(
            data={
                "deleted_index": key_index,
                "remaining_keys": len(existing_keys)
            },
            message=f"Successfully deleted API key"
        )

    except Exception as e:
        logger.error(f"Error deleting key: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to delete key: {str(e)}",
            code=500
        )
