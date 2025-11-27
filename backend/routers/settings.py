# -*- coding: utf-8 -*-
"""
Settings API Routes - YouTube API Key Management
"""
import logging
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from models.response import ApiResponse
from services.youtube_service import YouTubeService

router = APIRouter()
logger = logging.getLogger(__name__)


class BatchAddKeysRequest(BaseModel):
    """Batch add API keys request"""
    api_keys: List[str] = Field(..., min_items=1, max_items=50)


@router.post("/youtube/keys/batch")
async def batch_add_keys(request: BatchAddKeysRequest):
    """
    Batch add YouTube API keys

    Validates and adds multiple API keys at once
    Automatically deduplicates existing keys
    """
    try:
        # Validate key format (YouTube keys start with AIza, length 39)
        invalid_keys = []
        valid_keys = []

        for key in request.api_keys:
            key = key.strip()
            if not key.startswith('AIza') or len(key) != 39:
                invalid_keys.append(key[:10] + '...')
            else:
                valid_keys.append(key)

        if invalid_keys:
            return ApiResponse.error(
                message=f"Invalid key format: {', '.join(invalid_keys)}",
                code=400
            )

        # Get existing keys
        existing_keys = YouTubeService.get_all_keys()
        existing_set = set(existing_keys)

        # Filter out duplicates
        new_keys = [k for k in valid_keys if k not in existing_set]
        duplicates = len(valid_keys) - len(new_keys)

        # Save all keys
        all_keys = existing_keys + new_keys
        YouTubeService.save_keys(all_keys)

        logger.info(f"Added {len(new_keys)} new key(s), skipped {duplicates} duplicate(s)")

        return ApiResponse.success(
            data={
                'added_count': len(new_keys),
                'duplicate_count': duplicates,
                'total_keys': len(all_keys)
            },
            message=f"Added {len(new_keys)} key(s) successfully"
        )

    except Exception as e:
        logger.error(f"Failed to add keys: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to add keys: {str(e)}",
            code=500
        )


@router.get("/youtube/keys/detailed")
async def get_detailed_keys():
    """
    Get detailed information about all API keys

    Returns masked keys with statistics
    """
    try:
        keys = YouTubeService.get_all_keys()

        # Prepare detailed info
        keys_info = []
        for idx, key in enumerate(keys):
            keys_info.append({
                'id': f"key_{idx + 1}",
                'masked_key': f"***{key[-6:]}" if len(key) > 6 else "***",
                'index': idx + 1
            })

        summary = {
            'total_keys': len(keys),
            'quota_per_key': 10000  # YouTube default daily quota
        }

        return ApiResponse.success(
            data={
                'summary': summary,
                'keys': keys_info
            },
            message=f"Retrieved {len(keys)} key(s)"
        )

    except Exception as e:
        logger.error(f"Failed to get keys info: {e}")
        return ApiResponse.success(
            data={'summary': {'total_keys': 0}, 'keys': []},
            message="No keys configured"
        )


@router.delete("/youtube/keys/{key_id}")
async def delete_key(key_id: str):
    """
    Delete a specific API key by ID

    Args:
        key_id: Key ID in format "key_N" where N is 1-based index
    """
    try:
        # Extract index from key_id (format: key_1, key_2, etc.)
        if not key_id.startswith('key_'):
            return ApiResponse.error(message="Invalid key ID format", code=400)

        try:
            index = int(key_id.split('_')[1]) - 1  # Convert to 0-based index
        except (IndexError, ValueError):
            return ApiResponse.error(message="Invalid key ID", code=400)

        # Get current keys
        keys = YouTubeService.get_all_keys()

        if index < 0 or index >= len(keys):
            return ApiResponse.error(message="Key not found", code=404)

        # Remove key
        deleted_key = keys.pop(index)
        YouTubeService.save_keys(keys)

        logger.info(f"Deleted key #{index + 1}")

        return ApiResponse.success(
            data={'remaining_keys': len(keys)},
            message="Key deleted successfully"
        )

    except Exception as e:
        logger.error(f"Failed to delete key: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to delete key: {str(e)}",
            code=500
        )
