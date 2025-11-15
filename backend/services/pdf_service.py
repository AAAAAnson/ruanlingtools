# -*- coding: utf-8 -*-
"""
PDF processing service

This module provides PDF processing functionality:
- PDF to images conversion
- PDF merging and splitting
- Text extraction from PDF
- PDF metadata extraction
"""
import os
import io
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import uuid

from PyPDF2 import PdfReader, PdfWriter, PdfMerger

logger = logging.getLogger(__name__)


class PDFService:
    """Service for PDF processing operations"""

    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize PDF service

        Args:
            output_dir: Directory for saving processed PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PDFService initialized with output_dir: {output_dir}")

    def extract_text(self, pdf_data: bytes) -> str:
        """
        Extract text content from PDF

        Args:
            pdf_data: PDF file content as bytes

        Returns:
            Extracted text content
        """
        try:
            pdf_file = io.BytesIO(pdf_data)
            reader = PdfReader(pdf_file)

            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num} ---\n{text}\n")

            full_text = "\n".join(text_content)
            logger.info(f"Extracted text from {len(reader.pages)} pages")
            return full_text

        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            raise Exception(f"Failed to extract text: {str(e)}")

    def get_pdf_info(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Get PDF metadata and information

        Args:
            pdf_data: PDF file content as bytes

        Returns:
            Dictionary containing PDF metadata
        """
        try:
            pdf_file = io.BytesIO(pdf_data)
            reader = PdfReader(pdf_file)

            info = {
                "num_pages": len(reader.pages),
                "is_encrypted": reader.is_encrypted,
                "metadata": {}
            }

            if reader.metadata:
                metadata = reader.metadata
                info["metadata"] = {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "creation_date": metadata.get("/CreationDate", ""),
                    "modification_date": metadata.get("/ModDate", "")
                }

            # Get page sizes
            if len(reader.pages) > 0:
                first_page = reader.pages[0]
                box = first_page.mediabox
                info["page_size"] = {
                    "width": float(box.width),
                    "height": float(box.height),
                    "unit": "points"
                }

            logger.info(f"Retrieved info for PDF with {info['num_pages']} pages")
            return info

        except Exception as e:
            logger.error(f"PDF info extraction error: {str(e)}")
            raise Exception(f"Failed to get PDF info: {str(e)}")

    def merge_pdfs(self, pdf_files: List[bytes]) -> bytes:
        """
        Merge multiple PDF files into one

        Args:
            pdf_files: List of PDF file contents as bytes

        Returns:
            Merged PDF content as bytes
        """
        try:
            merger = PdfMerger()

            for idx, pdf_data in enumerate(pdf_files):
                pdf_file = io.BytesIO(pdf_data)
                merger.append(pdf_file)
                logger.info(f"Added PDF {idx + 1}/{len(pdf_files)} to merger")

            output = io.BytesIO()
            merger.write(output)
            merger.close()

            output.seek(0)
            result = output.read()

            logger.info(f"Successfully merged {len(pdf_files)} PDFs")
            return result

        except Exception as e:
            logger.error(f"PDF merge error: {str(e)}")
            raise Exception(f"Failed to merge PDFs: {str(e)}")

    def split_pdf(self, pdf_data: bytes, page_ranges: str) -> List[Tuple[str, bytes]]:
        """
        Split PDF into multiple files based on page ranges

        Args:
            pdf_data: PDF file content as bytes
            page_ranges: Page ranges string (e.g., "1-3,5,7-10")

        Returns:
            List of tuples (range_name, pdf_content)
        """
        try:
            pdf_file = io.BytesIO(pdf_data)
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)

            # Parse page ranges
            ranges = self._parse_page_ranges(page_ranges, total_pages)

            results = []
            for range_name, pages in ranges:
                writer = PdfWriter()

                for page_num in pages:
                    writer.add_page(reader.pages[page_num - 1])

                output = io.BytesIO()
                writer.write(output)
                output.seek(0)

                results.append((range_name, output.read()))
                logger.info(f"Created split PDF: {range_name} with {len(pages)} pages")

            logger.info(f"Successfully split PDF into {len(results)} parts")
            return results

        except Exception as e:
            logger.error(f"PDF split error: {str(e)}")
            raise Exception(f"Failed to split PDF: {str(e)}")

    def _parse_page_ranges(self, ranges_str: str, total_pages: int) -> List[Tuple[str, List[int]]]:
        """
        Parse page range string into list of page numbers

        Args:
            ranges_str: Page ranges string (e.g., "1-3,5,7-10")
            total_pages: Total number of pages in PDF

        Returns:
            List of tuples (range_name, page_numbers)
        """
        results = []
        parts = [p.strip() for p in ranges_str.split(',')]

        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                start_page = int(start.strip())
                end_page = int(end.strip())

                if start_page < 1 or end_page > total_pages or start_page > end_page:
                    raise ValueError(f"Invalid page range: {part}")

                pages = list(range(start_page, end_page + 1))
                range_name = f"pages_{start_page}-{end_page}"
            else:
                page_num = int(part.strip())
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"Invalid page number: {page_num}")

                pages = [page_num]
                range_name = f"page_{page_num}"

            results.append((range_name, pages))

        return results

    def save_pdf(self, pdf_data: bytes, original_filename: str, suffix: str = "") -> str:
        """
        Save PDF file to disk

        Args:
            pdf_data: PDF content as bytes
            original_filename: Original filename
            suffix: Optional suffix to add to filename

        Returns:
            Saved filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        base_name = Path(original_filename).stem

        if suffix:
            filename = f"{base_name}_{suffix}_{timestamp}_{unique_id}.pdf"
        else:
            filename = f"{base_name}_{timestamp}_{unique_id}.pdf"

        filepath = self.output_dir / filename

        with open(filepath, 'wb') as f:
            f.write(pdf_data)

        logger.info(f"Saved PDF to {filepath}")
        return filename


# Global PDF service instance
pdf_service = PDFService()
