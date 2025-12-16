# -*- coding: utf-8 -*-
"""
Application configuration
"""
import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 encoding
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

# Basic configuration
APP_NAME = "Soft Collar Toolbox 2.0"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "True") == "True"

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# File configuration
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Whisper (Audio) configuration
WHISPER_MODELS_DIR = os.path.join(os.path.dirname(__file__), "models", "whisper")
WHISPER_SUPPORTED_MODELS = ["tiny", "base", "small"]
WHISPER_DEFAULT_MODEL = "base"
WHISPER_MAX_FILE_SIZE_MB = 25
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(WHISPER_MODELS_DIR, exist_ok=True)
