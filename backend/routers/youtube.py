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
        # Check if API key is configured
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            return ApiResponse.error(
                message="YouTube API key not configured. Please contact administrator.",
                code=503
            )

        # Initialize YouTube service
        youtube_service = YouTubeService(api_key=api_key)

        # Search for KOLs
        results = await youtube_service.search_kols(
            keyword=request.keyword,
            max_results=request.max_results,
            min_subscribers=request.min_subscribers
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
        # Check if API key is configured
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            return ApiResponse.error(
                message="YouTube API key not configured. Please contact administrator.",
                code=503
            )

        # Initialize YouTube service
        youtube_service = YouTubeService(api_key=api_key)

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
