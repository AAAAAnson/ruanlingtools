# -*- coding: utf-8 -*-
"""
YouTube KOL search routes

This module handles YouTube-related operations:
- KOL (Key Opinion Leader) search
- Channel information retrieval
"""
import os
import logging
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from models.response import ApiResponse
from services.youtube_service import YouTubeService

router = APIRouter()
logger = logging.getLogger(__name__)


class KOLSearchRequest(BaseModel):
    """KOL search request model"""
    keyword: str = Field(..., min_length=1, max_length=100, description="Search keyword")
    max_results: int = Field(50, ge=1, le=50, description="Maximum results to return")
    min_subscribers: int = Field(10000, ge=0, description="Minimum subscriber count filter")
    # New fields for enhanced search
    published_after: Optional[str] = Field(None, description="Start date (ISO 8601: 2023-01-01T00:00:00Z)")
    published_before: Optional[str] = Field(None, description="End date (ISO 8601: 2024-12-31T23:59:59Z)")
    order_by: str = Field("relevance", description="Sort order: relevance, date, viewCount, rating")
    get_latest_videos: bool = Field(True, description="Get latest videos for each channel")
    save_to_database: bool = Field(True, description="Save search results to database")


@router.get("/")
async def youtube_tools_index():
    """
    Get YouTube tools information

    Returns:
        ApiResponse with YouTube tools information
    """
    return ApiResponse.success(
        data={
            "tools": [
                {
                    "id": "kol-search",
                    "name": "KOL Search",
                    "description": "Search for influential YouTube channels by keyword",
                    "status": "available"
                },
                {
                    "id": "channel-info",
                    "name": "Channel Information",
                    "description": "Get detailed channel statistics",
                    "status": "available"
                }
            ],
            "note": "YouTube features require a valid API key configured in environment variables"
        },
        message="YouTube tools available"
    )


@router.post("/kol-search")
async def search_kols(request: KOLSearchRequest):
    """
    Search for KOLs (Key Opinion Leaders) by keyword

    This endpoint searches for influential YouTube channels related to a keyword.
    It analyzes video engagement, subscriber counts, and channel statistics.

    Args:
        request: KOL search parameters

    Returns:
        ApiResponse containing:
        - keyword: Search keyword used
        - channels: List of KOL channels with statistics
        - total_channels: Total number of channels found
        - total_videos: Total number of videos analyzed
        - timestamp: Search timestamp

    Raises:
        HTTPException: If API key is not configured or API error occurs
    """
    try:
        # Initialize YouTube service (will load keys from settings)
        try:
            youtube_service = YouTubeService()
        except ValueError as e:
            return ApiResponse.error(
                message="YouTube API key not configured. Please configure in Settings.",
                code=503
            )

        # Search for KOLs
        results = await youtube_service.search_kols(
            keyword=request.keyword,
            max_results=request.max_results,
            min_subscribers=request.min_subscribers,
            published_after=request.published_after,
            published_before=request.published_before,
            order_by=request.order_by,
            get_latest_videos=request.get_latest_videos,
            save_to_database=request.save_to_database
        )

        if results['total_channels'] == 0:
            return ApiResponse.success(
                data=results,
                message=f"No KOLs found for keyword: {request.keyword}"
            )

        return ApiResponse.success(
            data=results,
            message=f"Found {results['total_channels']} KOLs for keyword: {request.keyword}"
        )

    except Exception as e:
        logger.error(f"KOL search error: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to search KOLs: {str(e)}",
            code=500
        )


@router.get("/channel/{channel_id}")
async def get_channel_info(channel_id: str):
    """
    Get detailed channel information

    Args:
        channel_id: YouTube channel ID

    Returns:
        ApiResponse containing channel information

    Raises:
        HTTPException: If API key is not configured or channel not found
    """
    try:
        # Initialize YouTube service (will load keys from settings)
        try:
            youtube_service = YouTubeService()
        except ValueError as e:
            return ApiResponse.error(
                message="YouTube API key not configured. Please configure in Settings.",
                code=503
            )

        # Get channel information
        channel_info = await youtube_service.get_channel_info(channel_id)

        return ApiResponse.success(
            data=channel_info,
            message=f"Channel information retrieved: {channel_info['title']}"
        )

    except Exception as e:
        logger.error(f"Channel info error: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to get channel information: {str(e)}",
            code=500
        )


@router.get("/config")
async def get_youtube_config():
    """
    Get YouTube API configuration status

    Returns:
        ApiResponse with configuration status
    """
    api_key = os.getenv('YOUTUBE_API_KEY')

    return ApiResponse.success(
        data={
            "api_configured": api_key is not None and len(api_key) > 0,
            "features_available": api_key is not None
        },
        message="YouTube configuration status"
    )


@router.get("/history")
async def get_search_history(
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    start_date: Optional[str] = Query(None, description="Start date filter"),
    end_date: Optional[str] = Query(None, description="End date filter"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get search history

    Returns list of previous KOL searches with basic statistics
    """
    try:
        from repositories.youtube_repository import YouTubeRepository

        repo = YouTubeRepository()
        history = repo.get_search_history(
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        return ApiResponse.success(
            data={
                "searches": history,
                "total": len(history),
                "limit": limit,
                "offset": offset
            },
            message=f"Retrieved {len(history)} search records"
        )

    except Exception as e:
        logger.error(f"Error getting search history: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to get search history: {str(e)}",
            code=500
        )


@router.get("/history/{search_id}")
async def get_search_detail(search_id: int):
    """
    Get detailed search results

    Returns complete search results including all channels and videos
    """
    try:
        from repositories.youtube_repository import YouTubeRepository

        repo = YouTubeRepository()
        detail = repo.get_search_detail(search_id)

        if not detail:
            return ApiResponse.error(
                message=f"Search record not found: {search_id}",
                code=404
            )

        return ApiResponse.success(
            data=detail,
            message=f"Search detail for '{detail['keyword']}'"
        )

    except Exception as e:
        logger.error(f"Error getting search detail: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"Failed to get search detail: {str(e)}",
            code=500
        )
