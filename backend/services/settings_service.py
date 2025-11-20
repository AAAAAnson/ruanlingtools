# -*- coding: utf-8 -*-
"""
Settings management service

Handles reading and writing application settings to JSON file
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional
from models.settings import ApplicationSettings, YouTubeAPISettings

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing application settings"""

    def __init__(self, settings_file: str = "data/settings.json"):
        """
        Initialize settings service

        Args:
            settings_file: Path to settings JSON file
        """
        self.settings_file = settings_file
        self._ensure_settings_directory()

    def _ensure_settings_directory(self):
        """Ensure the settings directory exists"""
        settings_dir = os.path.dirname(self.settings_file)
        if settings_dir and not os.path.exists(settings_dir):
            os.makedirs(settings_dir, exist_ok=True)
            logger.info(f"Created settings directory: {settings_dir}")

    def load_settings(self) -> ApplicationSettings:
        """
        Load settings from file

        Returns:
            ApplicationSettings object
        """
        # First, try to load from file
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    settings = ApplicationSettings(**data)
                    logger.info("Settings loaded from file")
                    return settings
            except Exception as e:
                logger.error(f"Error loading settings from file: {e}")

        # If no file or error, load from environment variables
        env_keys = os.getenv('YOUTUBE_API_KEY', '').strip()
        if env_keys:
            # Support both single key and comma-separated keys
            api_keys = [k.strip() for k in env_keys.split(',') if k.strip()]
            if api_keys:
                settings = ApplicationSettings(
                    youtube=YouTubeAPISettings(
                        api_keys=api_keys,
                        per_key_budget=int(os.getenv('PER_KEY_BUDGET', '9800'))
                    )
                )
                logger.info(f"Settings loaded from environment ({len(api_keys)} API keys)")
                return settings

        # Return default settings
        logger.info("Using default settings")
        return ApplicationSettings()

    def save_settings(self, settings: ApplicationSettings) -> bool:
        """
        Save settings to file

        Args:
            settings: ApplicationSettings object

        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_settings_directory()

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings.model_dump(), f, indent=2, ensure_ascii=False)

            logger.info(f"Settings saved to {self.settings_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def update_youtube_keys(self, api_keys: list, per_key_budget: Optional[int] = None) -> ApplicationSettings:
        """
        Update YouTube API keys

        Args:
            api_keys: List of API keys
            per_key_budget: Optional budget per key

        Returns:
            Updated ApplicationSettings
        """
        settings = self.load_settings()

        # Update YouTube settings
        settings.youtube.api_keys = api_keys
        if per_key_budget is not None:
            settings.youtube.per_key_budget = per_key_budget

        # Reset key index
        settings.youtube.current_key_index = 0

        # Save and return
        self.save_settings(settings)
        return settings

    def get_youtube_keys(self) -> list:
        """
        Get list of YouTube API keys

        Returns:
            List of API keys
        """
        settings = self.load_settings()
        return settings.youtube.api_keys

    def has_youtube_keys(self) -> bool:
        """
        Check if YouTube API keys are configured

        Returns:
            True if at least one key is configured
        """
        keys = self.get_youtube_keys()
        return len(keys) > 0


# Global instance
_settings_service = None


def get_settings_service() -> SettingsService:
    """Get global settings service instance"""
    global _settings_service
    if _settings_service is None:
        _settings_service = SettingsService()
    return _settings_service
