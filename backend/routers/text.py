# -*- coding: utf-8 -*-
"""
Text processing routes

This module handles text-related operations.
Note: Most text processing will be done on frontend for privacy.
Backend provides minimal text services.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from models.response import ApiResponse

router = APIRouter()


class TextInput(BaseModel):
    """Text input model"""
    text: str


@router.get("/tools")
async def get_text_tools():
    """
    Get list of available text tools

    Returns:
        ApiResponse with list of text tools
    """
    return ApiResponse.success(
        data={
            "tools": [
                {
                    "id": "case-converter",
                    "name": "Case Converter",
                    "description": "Convert text case (upper, lower, title, etc.)",
                    "frontend_only": True
                },
                {
                    "id": "formatter",
                    "name": "Text Formatter",
                    "description": "Format text with various options",
                    "frontend_only": True
                },
                {
                    "id": "encoder",
                    "name": "Text Encoder",
                    "description": "Encode/decode text (Base64, URL, etc.)",
                    "frontend_only": True
                },
                {
                    "id": "sort",
                    "name": "Text Sorter",
                    "description": "Sort lines alphabetically or numerically",
                    "frontend_only": True
                },
                {
                    "id": "stats",
                    "name": "Text Statistics",
                    "description": "Count words, characters, lines, etc.",
                    "frontend_only": True
                }
            ]
        },
        message="Text tools list"
    )


@router.post("/analyze")
async def analyze_text(input: TextInput):
    """
    Analyze text and return statistics

    Args:
        input: Text to analyze

    Returns:
        ApiResponse with text statistics
    """
    text = input.text
    lines = text.split('\n')
    words = text.split()

    return ApiResponse.success(
        data={
            "characters": len(text),
            "characters_no_spaces": len(text.replace(' ', '')),
            "words": len(words),
            "lines": len(lines),
            "sentences": text.count('.') + text.count('!') + text.count('?'),
            "paragraphs": len([line for line in lines if line.strip()])
        },
        message="Text analysis complete"
    )
