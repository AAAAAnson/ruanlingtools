# -*- coding: utf-8 -*-
"""
YouTube search routes (placeholder)

This module will handle YouTube-related operations:
- KOL (Key Opinion Leader) search
- Channel information retrieval
- Video statistics

Note: These features require YouTube API integration
and will be implemented in future phases.
"""
from fastapi import APIRouter
from models.response import ApiResponse

router = APIRouter()


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
                    "description": "Search for influential YouTube channels",
                    "status": "planned"
                },
                {
                    "id": "channel-info",
                    "name": "Channel Information",
                    "description": "Get detailed channel statistics",
                    "status": "planned"
                },
                {
                    "id": "video-stats",
                    "name": "Video Statistics",
                    "description": "Analyze video performance",
                    "status": "planned"
                }
            ],
            "note": "YouTube features require API integration and will be available in future updates"
        },
        message="YouTube tools information"
    )


@router.get("/search")
async def search_channels():
    """Search YouTube channels (not implemented)"""
    return ApiResponse.not_implemented(
        message="YouTube search is not available yet. Coming in future updates."
    )


@router.get("/channel/{channel_id}")
async def get_channel_info(channel_id: str):
    """Get channel information (not implemented)"""
    return ApiResponse.not_implemented(
        message=f"Channel information retrieval is not available yet. Coming in future updates."
    )
