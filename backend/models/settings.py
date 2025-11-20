# -*- coding: utf-8 -*-
"""
Settings models for application configuration
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class YouTubeAPISettings(BaseModel):
    """YouTube API configuration"""
    api_keys: List[str] = Field(default_factory=list, description="List of YouTube API keys")
    per_key_budget: int = Field(default=9800, ge=0, le=10000, description="Daily quota per API key")
    current_key_index: int = Field(default=0, ge=0, description="Current active key index")


class ApplicationSettings(BaseModel):
    """Application settings"""
    youtube: YouTubeAPISettings = Field(default_factory=YouTubeAPISettings)

    class Config:
        json_schema_extra = {
            "example": {
                "youtube": {
                    "api_keys": ["AIzaSyXXXXXXXXXXXXXXXXXX", "AIzaSyYYYYYYYYYYYYYYYYYY"],
                    "per_key_budget": 9800,
                    "current_key_index": 0
                }
            }
        }


class YouTubeAPIKeyUpdate(BaseModel):
    """Update YouTube API keys"""
    api_keys: List[str] = Field(..., min_items=1, description="List of YouTube API keys (at least one)")
    per_key_budget: Optional[int] = Field(default=9800, ge=0, le=10000)
