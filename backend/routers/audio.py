# -*- coding: utf-8 -*-
"""
Audio processing routes

This module handles all audio-related operations:
- Audio transcription (speech-to-text)
- Translation to English
- Subtitle generation (SRT, VTT)
- Multiple output formats support
"""
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from config import WHISPER_MAX_FILE_SIZE_MB, WHISPER_DEFAULT_MODEL, UPLOAD_DIR
from models.response import ApiResponse
from services.audio_service import AudioService
from utils.file_handler import file_handler

router = APIRouter()
audio_service = AudioService()
logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.opus']


@router.get("/models")
async def get_available_models():
    """
    Get list of available Whisper models

    Returns:
        ApiResponse with available models and system info
    """
    try:
        models = audio_service.get_available_models()
        system_info = audio_service.get_system_info()

        return ApiResponse.success(
            data={
                "models": models,
                "default_model": WHISPER_DEFAULT_MODEL,
                "system_info": system_info
            },
            message="获取可用模型列表成功"
        )

    except Exception as e:
        logger.error(f"Failed to get models: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"获取模型列表失败: {str(e)}",
            code=500
        )


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages

    Returns:
        ApiResponse with supported languages
    """
    # Common languages supported by Whisper
    languages = [
        {"code": "zh", "name": "中文", "native_name": "中文"},
        {"code": "en", "name": "English", "native_name": "English"},
        {"code": "ja", "name": "Japanese", "native_name": "日本語"},
        {"code": "ko", "name": "Korean", "native_name": "한국어"},
        {"code": "es", "name": "Spanish", "native_name": "Español"},
        {"code": "fr", "name": "French", "native_name": "Français"},
        {"code": "de", "name": "German", "native_name": "Deutsch"},
        {"code": "it", "name": "Italian", "native_name": "Italiano"},
        {"code": "pt", "name": "Portuguese", "native_name": "Português"},
        {"code": "ru", "name": "Russian", "native_name": "Русский"},
        {"code": "ar", "name": "Arabic", "native_name": "العربية"},
        {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
        {"code": "th", "name": "Thai", "native_name": "ไทย"},
        {"code": "vi", "name": "Vietnamese", "native_name": "Tiếng Việt"},
    ]

    return ApiResponse.success(
        data={
            "languages": languages,
            "note": "留空将自动检测语言"
        },
        message="支持 99+ 种语言"
    )


@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported input/output formats

    Returns:
        ApiResponse with supported formats
    """
    return ApiResponse.success(
        data={
            "input_formats": SUPPORTED_AUDIO_FORMATS,
            "output_formats": [
                {
                    "format": "txt",
                    "name": "纯文本",
                    "description": "纯文本格式，无时间戳"
                },
                {
                    "format": "srt",
                    "name": "SRT 字幕",
                    "description": "标准字幕格式，包含时间戳"
                },
                {
                    "format": "vtt",
                    "name": "WebVTT 字幕",
                    "description": "Web 视频字幕格式"
                },
                {
                    "format": "json",
                    "name": "JSON",
                    "description": "结构化数据，包含详细信息"
                }
            ]
        },
        message="支持的格式列表"
    )


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    model_size: str = Form(WHISPER_DEFAULT_MODEL),
    language: Optional[str] = Form(None),
    output_format: str = Form("txt"),
    task: str = Form("transcribe")
):
    """
    Transcribe audio to text

    Args:
        file: Audio file (mp3, wav, m4a, flac, ogg, aac, etc.)
        model_size: Model size (tiny/base/small)
        language: Language code (zh/en/ja etc.), leave empty for auto-detect
        output_format: Output format (txt/srt/vtt/json)
        task: 'transcribe' (transcribe) or 'translate' (translate to English)

    Returns:
        ApiResponse with transcription result
    """
    temp_audio_path = None

    try:
        # Validate file format
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_AUDIO_FORMATS:
            return ApiResponse.error(
                message=f"不支持的文件格式。支持的格式: {', '.join(SUPPORTED_AUDIO_FORMATS)}",
                code=400
            )

        # Read and validate file size
        file_data = await file.read()
        file_size_mb = len(file_data) / (1024 * 1024)

        if file_size_mb > WHISPER_MAX_FILE_SIZE_MB:
            return ApiResponse.error(
                message=f"文件过大。最大支持 {WHISPER_MAX_FILE_SIZE_MB}MB，当前文件 {file_size_mb:.1f}MB",
                code=400
            )

        # Validate output format
        if output_format not in ['txt', 'srt', 'vtt', 'json']:
            return ApiResponse.error(
                message="不支持的输出格式。支持: txt, srt, vtt, json",
                code=400
            )

        # Validate task
        if task not in ['transcribe', 'translate']:
            return ApiResponse.error(
                message="不支持的任务类型。支持: transcribe, translate",
                code=400
            )

        # Save temporary audio file
        temp_audio_path = Path(UPLOAD_DIR) / file.filename
        with open(temp_audio_path, 'wb') as f:
            f.write(file_data)

        logger.info(f"Processing audio: {file.filename} ({file_size_mb:.1f}MB)")
        logger.info(f"Model: {model_size}, Language: {language or 'auto'}, Format: {output_format}")

        # Transcribe audio
        segments, info = audio_service.transcribe(
            audio_path=str(temp_audio_path),
            model_size=model_size,
            language=language,
            task=task
        )

        # Format output based on requested format
        if output_format == 'txt':
            content = audio_service.format_transcription_text(segments)
            content_type = "text/plain"

        elif output_format == 'srt':
            content = audio_service.format_transcription_srt(segments)
            content_type = "text/plain"

        elif output_format == 'vtt':
            content = audio_service.format_transcription_vtt(segments)
            content_type = "text/plain"

        elif output_format == 'json':
            content_dict = audio_service.format_transcription_json(segments, info)
            content = json.dumps(content_dict, ensure_ascii=False, indent=2)
            content_type = "application/json"

        # Save transcription file
        saved_filename = audio_service.save_transcription(
            content=content,
            original_filename=file.filename,
            output_format=output_format
        )

        # Prepare response data
        response_data = {
            "original_filename": file.filename,
            "file_size_mb": round(file_size_mb, 2),
            "model_used": model_size,
            "detected_language": info.language,
            "language_probability": round(info.language_probability, 2),
            "duration_seconds": round(info.duration, 1),
            "output_format": output_format,
            "output_filename": saved_filename,
            "download_url": f"/api/audio/download/{saved_filename}",
            "content": content if output_format != 'json' else content_dict
        }

        # Clean up temp file
        if temp_audio_path and temp_audio_path.exists():
            temp_audio_path.unlink()

        return ApiResponse.success(
            data=response_data,
            message=f"转录成功！检测到语言: {info.language}"
        )

    except MemoryError as e:
        logger.error(f"Memory error: {e}")
        return ApiResponse.error(
            message=f"内存不足: {str(e)}",
            code=507
        )

    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        return ApiResponse.error(
            message=f"转录失败: {str(e)}",
            code=500
        )

    finally:
        # Clean up temp file
        if temp_audio_path and temp_audio_path.exists():
            try:
                temp_audio_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")


@router.get("/download/{filename}")
async def download_transcription(filename: str):
    """
    Download transcription file

    Args:
        filename: Name of the transcription file

    Returns:
        FileResponse with the transcription file
    """
    try:
        file_path = Path(audio_service.output_dir) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        # Security check: ensure file is within output directory
        if not str(file_path.resolve()).startswith(str(Path(audio_service.output_dir).resolve())):
            raise HTTPException(status_code=403, detail="访问被拒绝")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check for audio service

    Returns:
        ApiResponse with service status
    """
    try:
        system_info = audio_service.get_system_info()

        return ApiResponse.success(
            data={
                "status": "healthy",
                "current_model": audio_service.current_model_size,
                "system_info": system_info
            },
            message="Audio service is running"
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ApiResponse.error(
            message=f"服务异常: {str(e)}",
            code=500
        )
