# -*- coding: utf-8 -*-
"""
Image processing service

This module handles image format conversion, resizing, and optimization.
"""
from PIL import Image
from typing import Optional, Tuple
import io
import os
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ImageService:
    """
    Service class for image processing operations
    """

    SUPPORTED_FORMATS = {
        'jpg': 'JPEG',
        'jpeg': 'JPEG',
        'png': 'PNG',
        'webp': 'WEBP',
        'gif': 'GIF',
        'bmp': 'BMP',
    }

    OUTPUT_FORMATS = ['jpg', 'png', 'webp']

    def __init__(self, output_dir: str = 'outputs'):
        """
        Initialize ImageService

        Args:
            output_dir: Directory to save converted images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def convert_image(
        self,
        image_data: bytes,
        output_format: str,
        quality: int = 85,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Tuple[bytes, str]:
        """
        Convert image to specified format

        Args:
            image_data: Input image bytes
            output_format: Target format (jpg, png, webp)
            quality: Output quality (1-100)
            width: Optional target width
            height: Optional target height

        Returns:
            Tuple of (converted image bytes, file extension)
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))

            # Convert RGBA to RGB for JPEG
            if output_format.lower() in ['jpg', 'jpeg'] and image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # Resize if dimensions specified
            if width or height:
                image = self._resize_image(image, width, height)

            # Get PIL format name
            pil_format = self.SUPPORTED_FORMATS.get(output_format.lower(), 'JPEG')

            # Convert to bytes
            output_buffer = io.BytesIO()

            # Save with quality setting for JPEG and WebP
            if pil_format in ['JPEG', 'WEBP']:
                image.save(output_buffer, format=pil_format, quality=quality, optimize=True)
            else:
                image.save(output_buffer, format=pil_format, optimize=True)

            output_buffer.seek(0)
            converted_data = output_buffer.read()

            # Get file extension
            extension = output_format.lower()
            if extension == 'jpeg':
                extension = 'jpg'

            logger.info(f"Converted image to {output_format} (quality: {quality})")

            return converted_data, extension

        except Exception as e:
            logger.error(f"Error converting image: {e}")
            raise

    def _resize_image(
        self,
        image: Image.Image,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> Image.Image:
        """
        Resize image to specified dimensions

        Args:
            image: PIL Image object
            width: Target width
            height: Target height
            maintain_aspect_ratio: Whether to maintain aspect ratio

        Returns:
            Resized PIL Image
        """
        original_width, original_height = image.size

        if maintain_aspect_ratio:
            if width and not height:
                # Calculate height based on width
                aspect_ratio = original_height / original_width
                height = int(width * aspect_ratio)
            elif height and not width:
                # Calculate width based on height
                aspect_ratio = original_width / original_height
                width = int(height * aspect_ratio)
            elif width and height:
                # Use smallest dimension to maintain aspect ratio
                width_ratio = width / original_width
                height_ratio = height / original_height
                ratio = min(width_ratio, height_ratio)
                width = int(original_width * ratio)
                height = int(original_height * ratio)
        else:
            width = width or original_width
            height = height or original_height

        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        logger.info(f"Resized image from {original_width}x{original_height} to {width}x{height}")

        return resized

    def save_converted_image(
        self,
        image_data: bytes,
        original_filename: str,
        extension: str
    ) -> str:
        """
        Save converted image to disk

        Args:
            image_data: Converted image bytes
            original_filename: Original filename (without extension)
            extension: New file extension

        Returns:
            Saved file path
        """
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{original_filename}_{timestamp}_{unique_id}.{extension}"

        filepath = os.path.join(self.output_dir, filename)

        # Save to disk
        with open(filepath, 'wb') as f:
            f.write(image_data)

        logger.info(f"Saved converted image to {filepath}")

        return filename

    def get_image_info(self, image_data: bytes) -> dict:
        """
        Get image information

        Args:
            image_data: Image bytes

        Returns:
            Dictionary with image info (format, size, mode)
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            return {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.size[0],
                'height': image.size[1],
            }
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            raise
