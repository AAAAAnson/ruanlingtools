# -*- coding: utf-8 -*-
"""
Unified API response models
"""
from pydantic import BaseModel
from typing import Any, Optional
import time


class ApiResponse(BaseModel):
    """
    Unified API response format

    Attributes:
        code: HTTP status code
        message: Response message
        data: Response data (optional)
        timestamp: Unix timestamp of response
    """
    code: int
    message: str
    data: Optional[Any] = None
    timestamp: int = int(time.time())

    @staticmethod
    def success(data: Any = None, message: str = "success"):
        """
        Create a success response

        Args:
            data: Response data
            message: Success message

        Returns:
            ApiResponse with code 200
        """
        return ApiResponse(
            code=200,
            message=message,
            data=data
        )

    @staticmethod
    def error(message: str, code: int = 400, data: Any = None):
        """
        Create an error response

        Args:
            message: Error message
            code: HTTP error code
            data: Additional error data

        Returns:
            ApiResponse with error code
        """
        return ApiResponse(
            code=code,
            message=message,
            data=data
        )

    @staticmethod
    def not_found(message: str = "Resource not found"):
        """Create a 404 not found response"""
        return ApiResponse.error(message=message, code=404)

    @staticmethod
    def server_error(message: str = "Internal server error"):
        """Create a 500 server error response"""
        return ApiResponse.error(message=message, code=500)

    @staticmethod
    def not_implemented(message: str = "Feature not implemented yet"):
        """Create a 501 not implemented response"""
        return ApiResponse.error(message=message, code=501)
