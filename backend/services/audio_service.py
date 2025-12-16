# -*- coding: utf-8 -*-
"""
Audio processing service using Whisper

This module handles audio transcription using faster-whisper
Optimized for 4GB RAM systems with CPU-only processing
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import psutil
from datetime import datetime

logger = logging.getLogger(__name__)

# Whisper models information
WHISPER_MODELS_INFO = {
    "tiny": {
        "name": "Tiny",
        "display_name": "极速模式",
        "memory_mb": 400,
        "speed": "最快",
        "quality": "基础",
        "description": "快速转录，适合会议记录、快速预览",
        "max_audio_minutes": 30,
        "icon": "⚡",
        "recommended_for": ["快速预览", "会议记录", "短音频"]
    },
    "base": {
        "name": "Base",
        "display_name": "标准模式（推荐）",
        "memory_mb": 500,
        "speed": "快",
        "quality": "良好",
        "description": "速度和质量的最佳平衡，适合日常使用",
        "max_audio_minutes": 20,
        "icon": "⭐",
        "recommended": True,
        "recommended_for": ["日常使用", "播客转录", "视频字幕"]
    },
    "small": {
        "name": "Small",
        "display_name": "高质量模式",
        "memory_mb": 1000,
        "speed": "中等",
        "quality": "优秀",
        "description": "更高识别准确度，处理速度较慢",
        "max_audio_minutes": 10,
        "icon": "💎",
        "warning": "处理时间较长，可能占用较多内存",
        "recommended_for": ["重要音频", "专业转录", "多语言内容"]
    }
}


class AudioService:
    """Audio transcription service using Whisper"""

    def __init__(self):
        from config import (
            WHISPER_MODELS_DIR,
            WHISPER_SUPPORTED_MODELS,
            WHISPER_DEVICE,
            WHISPER_COMPUTE_TYPE,
            OUTPUT_DIR
        )

        self.models_dir = WHISPER_MODELS_DIR
        self.supported_models = WHISPER_SUPPORTED_MODELS
        self.device = WHISPER_DEVICE
        self.compute_type = WHISPER_COMPUTE_TYPE
        self.output_dir = OUTPUT_DIR

        self.model = None
        self.current_model_size = None

        logger.info(f"AudioService initialized with device: {self.device}")

    def get_available_models(self) -> List[Dict]:
        """
        Get list of available models based on current system memory

        Returns:
            List of model information dictionaries
        """
        models = []

        for model_name in self.supported_models:
            info = WHISPER_MODELS_INFO[model_name].copy()

            # Check if current memory is sufficient
            is_available, message = self.check_memory_available(model_name)
            info["available"] = is_available
            info["unavailable_reason"] = None if is_available else message
            info["model_size"] = model_name

            models.append(info)

        return models

    def check_memory_available(self, model_size: str) -> Tuple[bool, str]:
        """
        Check if there's enough memory to load the model

        Args:
            model_size: Model name (tiny/base/small)

        Returns:
            Tuple of (is_available, message)
        """
        model_info = WHISPER_MODELS_INFO.get(model_size)
        if not model_info:
            return False, f"不支持的模型: {model_size}"

        required_mb = model_info["memory_mb"]
        available_mb = psutil.virtual_memory().available / (1024 * 1024)

        # Reserve 500MB for system
        safety_margin_mb = 500

        if available_mb < (required_mb + safety_margin_mb):
            return False, f"内存不足。需要 {required_mb}MB，当前可用 {int(available_mb)}MB"

        return True, "OK"

    def load_model(self, model_size: str):
        """
        Load Whisper model

        Args:
            model_size: Model size (tiny/base/small)

        Returns:
            Loaded model instance

        Raises:
            ValueError: If model is not supported
            MemoryError: If insufficient memory
        """
        # Check if model is supported
        if model_size not in self.supported_models:
            raise ValueError(
                f"4GB 内存的系统不支持 {model_size} 模型。"
                f"支持的模型: {', '.join(self.supported_models)}"
            )

        # If same model already loaded, return it
        if self.current_model_size == model_size and self.model:
            logger.info(f"Model {model_size} already loaded, reusing")
            return self.model

        # Memory check
        is_available, message = self.check_memory_available(model_size)
        if not is_available:
            raise MemoryError(message)

        # Release old model
        if self.model:
            logger.info(f"Releasing old model: {self.current_model_size}")
            del self.model
            import gc
            gc.collect()

        # Load new model
        logger.info(f"Loading Whisper model: {model_size}")
        try:
            from faster_whisper import WhisperModel

            self.model = WhisperModel(
                model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=self.models_dir
            )

            self.current_model_size = model_size
            logger.info(f"Model loaded successfully: {model_size}")

            return self.model

        except Exception as e:
            logger.error(f"Failed to load model {model_size}: {e}")
            raise

    def transcribe(
        self,
        audio_path: str,
        model_size: str = "base",
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Tuple[any, any]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            model_size: Model size (tiny/base/small)
            language: Language code (zh/en/ja etc), None for auto-detect
            task: 'transcribe' or 'translate' (translate to English)

        Returns:
            Tuple of (segments, info)
        """
        # Load model
        model = self.load_model(model_size)

        # Transcribe
        logger.info(f"Transcribing audio: {audio_path}")
        logger.info(f"Model: {model_size}, Language: {language or 'auto'}, Task: {task}")

        try:
            segments, info = model.transcribe(
                audio_path,
                language=language,
                task=task,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )

            logger.info(f"Transcription completed. Detected language: {info.language}")

            return segments, info

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def format_transcription_text(self, segments) -> str:
        """
        Format segments as plain text

        Args:
            segments: Transcription segments

        Returns:
            Formatted text string
        """
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        return "\n".join(text_parts)

    def format_transcription_srt(self, segments) -> str:
        """
        Format segments as SRT subtitle format

        Args:
            segments: Transcription segments

        Returns:
            SRT formatted string
        """
        srt_parts = []

        for i, segment in enumerate(segments, start=1):
            start_time = self._format_timestamp_srt(segment.start)
            end_time = self._format_timestamp_srt(segment.end)
            text = segment.text.strip()

            srt_parts.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")

        return "\n".join(srt_parts)

    def format_transcription_vtt(self, segments) -> str:
        """
        Format segments as WebVTT subtitle format

        Args:
            segments: Transcription segments

        Returns:
            VTT formatted string
        """
        vtt_parts = ["WEBVTT\n"]

        for segment in segments:
            start_time = self._format_timestamp_vtt(segment.start)
            end_time = self._format_timestamp_vtt(segment.end)
            text = segment.text.strip()

            vtt_parts.append(f"{start_time} --> {end_time}\n{text}\n")

        return "\n".join(vtt_parts)

    def format_transcription_json(self, segments, info) -> Dict:
        """
        Format segments as JSON

        Args:
            segments: Transcription segments
            info: Transcription info

        Returns:
            Dictionary with transcription data
        """
        segments_list = []

        for segment in segments:
            segments_list.append({
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })

        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": segments_list
        }

    def _format_timestamp_srt(self, seconds: float) -> str:
        """
        Format timestamp for SRT format (HH:MM:SS,mmm)

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def _format_timestamp_vtt(self, seconds: float) -> str:
        """
        Format timestamp for VTT format (HH:MM:SS.mmm)

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"

    def save_transcription(
        self,
        content: str,
        original_filename: str,
        output_format: str
    ) -> str:
        """
        Save transcription to file

        Args:
            content: Transcription content
            original_filename: Original audio filename
            output_format: Output format (txt/srt/vtt/json)

        Returns:
            Saved filename
        """
        # Generate output filename
        base_name = Path(original_filename).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_name}_{timestamp}.{output_format}"

        # Save file
        output_path = Path(self.output_dir) / output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Transcription saved: {output_filename}")

        return output_filename

    def get_system_info(self) -> Dict:
        """
        Get system information

        Returns:
            Dictionary with system info
        """
        mem = psutil.virtual_memory()

        return {
            "total_memory_gb": round(mem.total / (1024**3), 1),
            "available_memory_mb": round(mem.available / (1024**2)),
            "device": self.device,
            "compute_type": self.compute_type,
            "supported_models": self.supported_models
        }
