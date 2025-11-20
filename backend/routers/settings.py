# -*- coding: utf-8 -*-
"""
Settings management routes

This module handles application settings configuration
"""
import logging
from fastapi import APIRouter
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
