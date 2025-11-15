# -*- coding: utf-8 -*-
"""
PDF processing routes

This module handles PDF-related operations:
- PDF to images conversion
- PDF merging and splitting
- PDF compression
- PDF to Word conversion
- Text extraction
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, Response
from typing import List, Optional
from pathlib import Path
import traceback

from models.response import ApiResponse
from services.pdf_service import pdf_service

router = APIRouter()


@router.post("/to-images")
async def pdf_to_images(
    file: UploadFile = File(...),
    format: str = Form("png"),
    dpi: int = Form(200)
):
    """
    Convert PDF pages to images

    Args:
        file: PDF file to convert
        format: Output image format (png, jpg)
        dpi: Image resolution

    Returns:
        ApiResponse with image files
    """
    return ApiResponse.not_implemented(
        message="PDF to images conversion will be implemented in P3 phase"
    )


@router.post("/merge")
async def merge_pdfs(
    files: List[UploadFile] = File(...)
):
    """
    Merge multiple PDF files into one

    Args:
        files: List of PDF files to merge

    Returns:
        ApiResponse with merged PDF
    """
    try:
        if len(files) < 2:
            return ApiResponse.error(
                message="At least 2 PDF files are required for merging",
                code=400
            )

        # Validate all files
        pdf_files = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                return ApiResponse.error(
                    message=f"Invalid file: {file.filename}. Only PDF files are supported.",
                    code=400
                )
            pdf_data = await file.read()
            pdf_files.append(pdf_data)

        # Merge PDFs
        merged_pdf = pdf_service.merge_pdfs(pdf_files)

        # Save merged PDF
        filename = pdf_service.save_pdf(merged_pdf, "merged", suffix="merged")

        return ApiResponse.success(
            data={
                "filename": filename,
                "num_files_merged": len(files),
                "download_url": f"/api/pdf/download/{filename}"
            },
            message=f"Successfully merged {len(files)} PDF files"
        )

    except Exception as e:
        return ApiResponse.error(
            message=f"PDF merge error: {str(e)}",
            code=500
        )


@router.post("/split")
async def split_pdf(
    file: UploadFile = File(...),
    pages: str = Form(...)
):
    """
    Split PDF into multiple files

    Args:
        file: PDF file to split
        pages: Page ranges (e.g., "1-3,5,7-10")

    Returns:
        ApiResponse with split PDF files
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return ApiResponse.error(
                message="Invalid file type. Only PDF files are supported.",
                code=400
            )

        # Read PDF file
        pdf_data = await file.read()

        # Split PDF based on page ranges
        split_results = pdf_service.split_pdf(pdf_data, pages)

        # Save split PDFs
        saved_files = []
        for range_name, pdf_content in split_results:
            filename = pdf_service.save_pdf(
                pdf_content,
                file.filename,
                suffix=range_name
            )
            saved_files.append({
                "range": range_name,
                "filename": filename,
                "download_url": f"/api/pdf/download/{filename}"
            })

        return ApiResponse.success(
            data={
                "original_filename": file.filename,
                "split_files": saved_files,
                "num_files": len(saved_files)
            },
            message=f"Successfully split PDF into {len(saved_files)} file(s)"
        )

    except ValueError as e:
        return ApiResponse.error(
            message=f"Invalid page range: {str(e)}",
            code=400
        )
    except Exception as e:
        return ApiResponse.error(
            message=f"PDF split error: {str(e)}",
            code=500
        )


@router.post("/compress")
async def compress_pdf(
    file: UploadFile = File(...),
    quality: str = Form("medium")
):
    """
    Compress PDF to reduce file size

    Args:
        file: PDF file to compress
        quality: Compression quality (low, medium, high)

    Returns:
        ApiResponse with compressed PDF
    """
    return ApiResponse.not_implemented(
        message="PDF compression will be implemented in P3 phase"
    )


@router.post("/to-word")
async def pdf_to_word(
    file: UploadFile = File(...)
):
    """
    Convert PDF to Word document

    Args:
        file: PDF file to convert

    Returns:
        ApiResponse with Word document
    """
    return ApiResponse.not_implemented(
        message="PDF to Word conversion will be implemented in P3 phase"
    )


@router.post("/extract-text")
async def extract_text_from_pdf(
    file: UploadFile = File(...)
):
    """
    Extract text content from PDF

    Args:
        file: PDF file

    Returns:
        ApiResponse with extracted text
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return ApiResponse.error(
                message="Invalid file type. Only PDF files are supported.",
                code=400
            )

        # Read PDF file
        pdf_data = await file.read()

        # Extract text
        text_content = pdf_service.extract_text(pdf_data)

        return ApiResponse.success(
            data={
                "filename": file.filename,
                "text": text_content,
                "length": len(text_content)
            },
            message="Text extracted successfully"
        )

    except Exception as e:
        return ApiResponse.error(
            message=f"Text extraction error: {str(e)}",
            code=500
        )


@router.post("/info")
async def get_pdf_info(
    file: UploadFile = File(...)
):
    """
    Get PDF file information

    Args:
        file: PDF file

    Returns:
        ApiResponse with PDF metadata
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return ApiResponse.error(
                message="Invalid file type. Only PDF files are supported.",
                code=400
            )

        # Read PDF file
        pdf_data = await file.read()

        # Get PDF information
        pdf_info = pdf_service.get_pdf_info(pdf_data)

        return ApiResponse.success(
            data={
                "filename": file.filename,
                "info": pdf_info
            },
            message="PDF information retrieved successfully"
        )

    except Exception as e:
        return ApiResponse.error(
            message=f"PDF info extraction error: {str(e)}",
            code=500
        )


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Download a processed PDF file

    Args:
        filename: Name of the file to download

    Returns:
        FileResponse with the PDF file
    """
    try:
        # Construct file path
        file_path = pdf_service.output_dir / filename

        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Validate it's a PDF file
        if not filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Return file
        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
