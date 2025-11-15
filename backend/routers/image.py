# -*- coding: utf-8 -*-
"""
Image processing routes

This module handles all image-related operations:
- Format conversion (JPG, PNG, WebP, AVIF)
- Image resizing and optimization
- Watermark application
- Batch processing
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path
import traceback

from models.response import ApiResponse
from services.image_service import ImageService
from utils.file_handler import file_handler

router = APIRouter()
image_service = ImageService()


@router.post("/convert")
async def convert_images(
    files: List[UploadFile] = File(...),
    output_format: str = Form(...),
    quality: Optional[int] = Form(85),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None)
):
    """
    Convert images to specified format

    Args:
        files: List of image files to convert
        output_format: Target format (jpg, png, webp, avif)
        quality: Output quality (1-100)
        width: Optional target width
        height: Optional target height

    Returns:
        ApiResponse with conversion results and file paths
    """
    try:
        # Validate output format
        supported_formats = ['jpg', 'jpeg', 'png', 'webp']
        if output_format.lower() not in supported_formats:
            return ApiResponse.error(
                message=f"Unsupported output format. Supported: {', '.join(supported_formats)}",
                code=400
            )

        # Validate quality
        if quality < 1 or quality > 100:
            return ApiResponse.error(
                message="Quality must be between 1 and 100",
                code=400
            )

        # Validate file extensions
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
        results = []
        errors = []

        for file in files:
            try:
                # Validate file extension
                if not file_handler.validate_file_extension(file.filename, allowed_extensions):
                    errors.append({
                        "filename": file.filename,
                        "error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
                    })
                    continue

                # Read file data
                file_data = await file.read()

                # Validate file size (10MB limit)
                if not file_handler.validate_file_size(len(file_data), max_size_mb=10):
                    errors.append({
                        "filename": file.filename,
                        "error": "File size exceeds 10MB limit"
                    })
                    continue

                # Convert image
                converted_data, mime_type = image_service.convert_image(
                    image_data=file_data,
                    output_format=output_format,
                    quality=quality,
                    width=width,
                    height=height
                )

                # Save converted image
                saved_filename = image_service.save_converted_image(
                    image_data=converted_data,
                    original_filename=file.filename,
                    extension=output_format
                )

                # Get file info
                file_path = Path(image_service.output_dir) / saved_filename
                file_info = file_handler.get_file_info(file_path)

                results.append({
                    "original_filename": file.filename,
                    "converted_filename": saved_filename,
                    "output_format": output_format,
                    "size": file_info["size"],
                    "size_mb": file_info["size_mb"],
                    "download_url": f"/api/image/download/{saved_filename}"
                })

            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })

        # Return results
        response_data = {
            "total": len(files),
            "successful": len(results),
            "failed": len(errors),
            "results": results
        }

        if errors:
            response_data["errors"] = errors

        if len(results) == 0:
            return ApiResponse.error(
                message="All image conversions failed",
                code=400,
                data=response_data
            )

        return ApiResponse.success(
            data=response_data,
            message=f"Successfully converted {len(results)} out of {len(files)} images"
        )

    except Exception as e:
        return ApiResponse.error(
            message=f"Image conversion error: {str(e)}",
            code=500
        )


@router.post("/resize")
async def resize_images(
    files: List[UploadFile] = File(...),
    width: int = Form(...),
    height: Optional[int] = Form(None),
    maintain_aspect_ratio: bool = Form(True)
):
    """
    Resize images to specified dimensions

    Args:
        files: List of image files to resize
        width: Target width in pixels
        height: Target height in pixels (optional)
        maintain_aspect_ratio: Whether to maintain aspect ratio

    Returns:
        ApiResponse with resized images
    """
    return ApiResponse.not_implemented(
        message="Image resizing will be implemented in future phases"
    )


@router.post("/watermark")
async def add_watermark(
    files: List[UploadFile] = File(...),
    watermark_text: Optional[str] = Form(None),
    watermark_image: Optional[UploadFile] = File(None),
    position: str = Form("bottom-right"),
    opacity: float = Form(0.5)
):
    """
    Add watermark to images

    Args:
        files: List of image files
        watermark_text: Text watermark
        watermark_image: Image watermark file
        position: Watermark position
        opacity: Watermark opacity (0-1)

    Returns:
        ApiResponse with watermarked images
    """
    return ApiResponse.not_implemented(
        message="Watermark feature will be implemented in future phases"
    )


@router.post("/compress")
async def compress_images(
    files: List[UploadFile] = File(...),
    quality: int = Form(85),
    max_width: Optional[int] = Form(None),
    max_height: Optional[int] = Form(None)
):
    """
    Compress images to reduce file size

    Args:
        files: List of image files to compress
        quality: Compression quality (1-100)
        max_width: Maximum width
        max_height: Maximum height

    Returns:
        ApiResponse with compressed images
    """
    return ApiResponse.not_implemented(
        message="Image compression will be implemented in future phases"
    )


@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported image formats

    Returns:
        ApiResponse with supported formats
    """
    return ApiResponse.success(
        data={
            "input_formats": ["jpg", "jpeg", "png", "webp", "gif", "bmp"],
            "output_formats": ["jpg", "png", "webp"],
            "planned_formats": ["avif", "heic"]
        },
        message="Supported image formats"
    )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a converted image file

    Args:
        filename: Name of the file to download

    Returns:
        FileResponse with the image file
    """
    try:
        file_path = Path(image_service.output_dir) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Validate file is within output directory (security check)
        if not str(file_path.resolve()).startswith(str(Path(image_service.output_dir).resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")


@router.post("/download-zip")
async def download_zip(filenames: List[str]):
    """
    Download multiple files as a ZIP archive

    Args:
        filenames: List of filenames to include in ZIP

    Returns:
        FileResponse with ZIP archive
    """
    try:
        if not filenames:
            raise HTTPException(status_code=400, detail="No files specified")

        # Collect valid files
        files_to_zip = []
        output_dir = Path(image_service.output_dir)

        for filename in filenames:
            file_path = output_dir / filename

            # Validate file exists and is within output directory
            if not file_path.exists():
                continue

            if not str(file_path.resolve()).startswith(str(output_dir.resolve())):
                continue

            files_to_zip.append((filename, file_path))

        if not files_to_zip:
            raise HTTPException(status_code=404, detail="No valid files found")

        # Create ZIP archive
        zip_path = file_handler.create_zip_archive(files_to_zip)

        return FileResponse(
            path=zip_path,
            filename=zip_path.name,
            media_type="application/zip",
            background=None  # File will be deleted by cleanup task
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ZIP creation error: {str(e)}")
