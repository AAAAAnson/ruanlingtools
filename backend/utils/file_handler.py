# -*- coding: utf-8 -*-
"""
File handling utilities

This module provides utilities for:
- Temporary file management
- File path operations
- ZIP archive creation
- File validation
"""
import os
import uuid
import zipfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime, timedelta


class FileHandler:
    """Handle file operations for uploaded and processed files"""

    def __init__(self, upload_dir: str = "uploads", temp_dir: str = "temp"):
        """
        Initialize file handler

        Args:
            upload_dir: Directory for uploaded files
            temp_dir: Directory for temporary files
        """
        self.upload_dir = Path(upload_dir)
        self.temp_dir = Path(temp_dir)

        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def generate_unique_filename(self, original_filename: str, extension: str = None) -> str:
        """
        Generate unique filename with timestamp and UUID

        Args:
            original_filename: Original file name
            extension: File extension (with or without dot)

        Returns:
            Unique filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        if extension:
            ext = extension if extension.startswith('.') else f'.{extension}'
        else:
            ext = Path(original_filename).suffix

        base_name = Path(original_filename).stem
        safe_name = "".join(c for c in base_name if c.isalnum() or c in ('-', '_'))

        return f"{safe_name}_{timestamp}_{unique_id}{ext}"

    def save_upload_file(self, file_data: bytes, filename: str,
                        subdir: str = None) -> Tuple[str, Path]:
        """
        Save uploaded file to disk

        Args:
            file_data: File content as bytes
            filename: Original filename
            subdir: Optional subdirectory within upload_dir

        Returns:
            Tuple of (unique_filename, full_path)
        """
        unique_filename = self.generate_unique_filename(filename)

        if subdir:
            save_dir = self.upload_dir / subdir
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.upload_dir

        file_path = save_dir / unique_filename

        with open(file_path, 'wb') as f:
            f.write(file_data)

        return unique_filename, file_path

    def create_zip_archive(self, files: List[Tuple[str, Path]],
                          archive_name: str = None) -> Path:
        """
        Create ZIP archive from multiple files

        Args:
            files: List of tuples (filename_in_zip, file_path)
            archive_name: Name for the ZIP file

        Returns:
            Path to created ZIP file
        """
        if archive_name:
            zip_filename = self.generate_unique_filename(archive_name, '.zip')
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"converted_images_{timestamp}.zip"

        zip_path = self.temp_dir / zip_filename

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename_in_zip, file_path in files:
                zipf.write(file_path, arcname=filename_in_zip)

        return zip_path

    def validate_file_size(self, file_size: int, max_size_mb: int = 10) -> bool:
        """
        Validate file size

        Args:
            file_size: File size in bytes
            max_size_mb: Maximum allowed size in MB

        Returns:
            True if valid, False otherwise
        """
        max_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_bytes

    def validate_file_extension(self, filename: str,
                               allowed_extensions: List[str]) -> bool:
        """
        Validate file extension

        Args:
            filename: Filename to check
            allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])

        Returns:
            True if valid, False otherwise
        """
        ext = Path(filename).suffix.lower()
        allowed_lower = [e.lower() if e.startswith('.') else f'.{e.lower()}'
                        for e in allowed_extensions]
        return ext in allowed_lower

    def cleanup_old_files(self, directory: Path = None,
                         max_age_hours: int = 24) -> int:
        """
        Clean up files older than specified age

        Args:
            directory: Directory to clean (defaults to temp_dir)
            max_age_hours: Maximum age in hours

        Returns:
            Number of files deleted
        """
        target_dir = directory if directory else self.temp_dir

        if not target_dir.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        deleted_count = 0

        for file_path in target_dir.iterdir():
            if file_path.is_file():
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception:
                        # Skip files that can't be deleted
                        pass

        return deleted_count

    def cleanup_file(self, file_path: Path) -> bool:
        """
        Delete a specific file

        Args:
            file_path: Path to file to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_info(self, file_path: Path) -> dict:
        """
        Get file information

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information
        """
        if not file_path.exists():
            return None

        stat = file_path.stat()

        return {
            "filename": file_path.name,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_path.suffix
        }


# Global file handler instance
file_handler = FileHandler()
