# Soft Collar Toolbox 2.0

A pixel art themed web application for image, PDF, text processing, audio transcription, and YouTube KOL search.

## Features

### Image Tools
- **Format Conversion**: Convert images between JPG, PNG, WebP, and AVIF formats
- **Image Watermark**: Add text or image watermarks to your photos

### PDF Tools
- **PDF Merge**: Combine multiple PDF files into one
- **PDF Split**: Split PDF files into separate pages
- **Extract Text**: Extract text content from PDF documents
- **PDF Info**: View detailed PDF metadata and information

### Text Tools
- **Case Converter**: Convert text between different cases (uppercase, lowercase, title case, etc.)
- **Text Formatter**: Format and clean up text content
- **Text Encoder**: Encode/decode text (Base64, URL encoding, etc.)
- **Text Sorter**: Sort lines of text alphabetically or by custom rules
- **Text Statistics**: Analyze text for word count, character count, and more

### Audio Tools
- **Speech to Text**: Convert audio files to text using OpenAI's Whisper model
  - Support for 99+ languages with auto-detection
  - Multiple model sizes (Tiny/Base/Small) optimized for 4GB RAM systems
  - Output formats: Plain text, SRT subtitles, WebVTT, JSON
  - Translate audio to English
  - Batch processing support
  - Supported formats: MP3, WAV, M4A, FLAC, OGG, AAC

### YouTube Tools
- **KOL Search**: Search for influential YouTube channels by keyword
- **Channel Analysis**: Analyze channel statistics and engagement rates
- **Video Performance**: View top-performing videos from KOLs

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **UI Theme**: Pixel Art (8-bit game aesthetic)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Image Processing**: Pillow, pillow-avif
- **PDF Processing**: PyPDF2, pdf2image
- **Audio Processing**: faster-whisper, ffmpeg
- **YouTube API**: Google API Python Client

### Deployment
- **Platform**: Docker + Docker Compose
- **Web Server**: Nginx
- **Target**: Synology NAS (or any Docker-compatible platform)
- **Port**: 8888 (configurable)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- (For YouTube features) YouTube Data API v3 key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and update the values, especially:
# - YOUTUBE_API_KEY (if using YouTube features)
# - NGINX_PORT (default: 8888)
# - NEXT_PUBLIC_API_URL (for your deployment URL)
```

3. Build and start the application:
```bash
docker-compose up -d --build
```

4. Access the application:
- Open your browser and navigate to `http://localhost:8888`
- API documentation: `http://localhost:8888/docs`

### YouTube API Setup

To use the YouTube KOL Search feature:

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create an API key:
   - Navigate to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - (Recommended) Restrict the key to YouTube Data API v3
5. Add the API key to your `.env` file:
```env
YOUTUBE_API_KEY=your_api_key_here
```
6. Restart the application:
```bash
docker-compose restart
```

## Development

### Local Development (without Docker)

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Backend runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Project Structure

```
ruanlingtools/
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities
│   │   └── styles/         # Global styles
│   └── public/             # Static assets
├── backend/                 # FastAPI backend
│   ├── main.py             # Entry point
│   ├── routers/            # API routes
│   ├── services/           # Business logic
│   ├── models/             # Data models
│   └── utils/              # Utilities
├── nginx/                   # Nginx configuration
├── docker-compose.yml       # Docker orchestration
├── .env.example             # Environment template
└── README.md               # This file
```

## Usage

### YouTube KOL Search

1. Navigate to the YouTube page in the app
2. Enter a search keyword (e.g., "AI technology", "Gaming", "Cooking")
3. Adjust search parameters:
   - **Min Subscribers**: Minimum subscriber count filter (default: 10,000)
   - **Max Results**: Maximum number of results (1-50, default: 20)
4. Click "Search KOLs"
5. View results:
   - Channel statistics (subscribers, total videos, avg views, engagement rate)
   - Click on a channel to see latest videos
   - Click external link icon to visit the YouTube channel

### Image Conversion

1. Navigate to Image → Convert
2. Upload one or more images
3. Select output format (PNG, JPG, WebP, AVIF)
4. Adjust quality settings
5. Click "Convert"
6. Download converted images

### PDF Operations

1. Navigate to the PDF tool you need
2. Upload PDF file(s)
3. Configure options
4. Process and download results

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `NGINX_PORT`: External port for the application (default: 8888)
- `YOUTUBE_API_KEY`: YouTube Data API v3 key for KOL search
- `NEXT_PUBLIC_API_URL`: API URL for frontend (update for production)
- `CORS_ORIGINS`: Allowed CORS origins
- `DEBUG`: Enable debug mode (True/False)

### Deployment on Synology NAS

1. Install Docker package from Package Center
2. Clone the repository to your NAS
3. Configure `.env` file with your NAS IP
4. Run `docker-compose up -d --build`
5. Access via `http://your-nas-ip:8888`

For reverse proxy setup, see `DEPLOYMENT.md`.

## API Documentation

When the backend is running, visit:
- Swagger UI: `http://localhost:8888/docs`
- ReDoc: `http://localhost:8888/redoc`

### API Endpoints

#### YouTube
- `POST /api/youtube/kol-search` - Search for KOLs by keyword
- `GET /api/youtube/channel/{channel_id}` - Get channel information
- `GET /api/youtube/config` - Check YouTube API configuration

#### Image
- `POST /api/image/convert` - Convert image formats
- `POST /api/image/watermark` - Add watermark to images

#### PDF
- `POST /api/pdf/merge` - Merge PDF files
- `POST /api/pdf/split` - Split PDF file
- `POST /api/pdf/extract-text` - Extract text from PDF
- `GET /api/pdf/info` - Get PDF metadata

#### Audio
- `POST /api/audio/transcribe` - Convert audio to text (speech-to-text)
- `GET /api/audio/models` - Get available Whisper models
- `GET /api/audio/languages` - Get supported languages
- `GET /api/audio/formats` - Get supported audio formats
- `GET /api/audio/download/{filename}` - Download transcription file
- `GET /api/audio/health` - Audio service health check

## License

This project is for educational and personal use. Please respect YouTube's Terms of Service and API usage policies.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
1. Check the documentation
2. Review existing issues on GitHub
3. Create a new issue with detailed information

---

**Built with Next.js, FastAPI, and Docker**
**Styled with Pixel Art Aesthetic**
