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


class RedditAPISettings(BaseModel):
    """Reddit API configuration"""
    client_id: str = Field(default="", description="Reddit application client ID")
    client_secret: str = Field(default="", description="Reddit application client secret")
    user_agent: str = Field(default="", description="Reddit API user agent")


class ApplicationSettings(BaseModel):
    """Application settings"""
    youtube: YouTubeAPISettings = Field(default_factory=YouTubeAPISettings)
    reddit: RedditAPISettings = Field(default_factory=RedditAPISettings)

    class Config:
        json_schema_extra = {
            "example": {
                "youtube": {
                    "api_keys": ["AIzaSyXXXXXXXXXXXXXXXXXX", "AIzaSyYYYYYYYYYYYYYYYYYY"],
                    "per_key_budget": 9800,
                    "current_key_index": 0
                },
                "reddit": {
                    "client_id": "your_client_id",
                    "client_secret": "your_client_secret",
                    "user_agent": "platform:app_id:v1.0 (by /u/username)"
                }
            }
        }


class YouTubeAPIKeyUpdate(BaseModel):
    """Update YouTube API keys"""
    api_keys: List[str] = Field(..., min_items=1, description="List of YouTube API keys (at least one)")
    per_key_budget: Optional[int] = Field(default=9800, ge=0, le=10000)


class RedditAPIUpdate(BaseModel):
    """Update Reddit API credentials"""
    client_id: str = Field(..., min_length=1, description="Reddit application client ID")
    client_secret: str = Field(..., min_length=1, description="Reddit application client secret")
    user_agent: str = Field(..., min_length=1, description="Reddit API user agent")
