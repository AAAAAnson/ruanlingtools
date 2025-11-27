# -*- coding: utf-8 -*-
"""
YouTube KOL Search API Routes
"""
import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field
from models.response import ApiResponse
from services.youtube_service import YouTubeService

router = APIRouter()
logger = logging.getLogger(__name__)


class KOLSearchRequest(BaseModel):
    """KOL search request"""
    keyword: str = Field(..., min_length=1, max_length=100)
    max_results: int = Field(20, ge=1, le=50)
    min_subscribers: int = Field(10000, ge=0)


@router.post("/kol-search")
async def search_kols(request: KOLSearchRequest):
    """
    Search for YouTube KOLs by keyword

    Returns channels with statistics sorted by subscriber count
    """
    try:
        youtube_service = YouTubeService()
        results = await youtube_service.search_kols(
            keyword=request.keyword,
            max_results=request.max_results,
            min_subscribers=request.min_subscribers
        )

        return ApiResponse.success(
            data=results,
            message=f"Found {results['total_channels']} KOL(s)"
        )

    except ValueError as e:
        # No API keys configured
        return ApiResponse.error(
            message="Please configure YouTube API keys in Settings",
            code=503
        )

    except Exception as e:
        logger.error(f"KOL search failed: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Search failed: {str(e)}",
            code=500
        )


@router.get("/keys/status")
async def get_keys_status():
    """
    Get API keys status

    Returns number of configured keys (masked for security)
    """
    try:
        keys = YouTubeService.get_all_keys()

        # Mask keys for security
        masked_keys = [f"***{key[-6:]}" if len(key) > 6 else "***" for key in keys]

        return ApiResponse.success(
            data={
                'total': len(keys),
                'keys': masked_keys
            },
            message=f"{len(keys)} key(s) configured"
        )

    except Exception as e:
        logger.error(f"Failed to get keys status: {e}")
        return ApiResponse.success(
            data={'total': 0, 'keys': []},
            message="No keys configured"
        )
