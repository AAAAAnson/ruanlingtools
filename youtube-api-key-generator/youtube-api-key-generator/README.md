# YouTube API Key Generator - Windows Tool

A standalone Windows PowerShell tool for batch generating YouTube Data API v3 keys.

## Features

- 🎨 Modern GUI with high-resolution display (1200x800)
- 🔄 Batch generation of 1-20 API keys
- 📊 Real-time progress tracking
- 📝 Detailed logging with color coding
- 💾 Export to both TXT and JSON formats
- 📋 Easy copy-to-clipboard functionality
- 🌙 Dark theme with teal accents

## Prerequisites

1. **Windows 10/11** with PowerShell 5.1 or later
2. **Google Cloud SDK** installed and configured
   - Download from: https://cloud.google.com/sdk/docs/install
3. **Authenticated Google Cloud Account**
   - Run `gcloud auth login` to authenticate
4. **Billing Account** configured in Google Cloud Console
   - Required for creating new projects

## Quick Start

### Step 1: Initialize Environment

Open PowerShell as Administrator and navigate to this folder:

```powershell
cd path\to\youtube-api-key-generator
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

This will:
- Check prerequisites
- Create necessary directories
- Generate configuration file
- Create a desktop shortcut

### Step 2: Launch GUI

Double-click the generated `YouTube-API-Key-Generator.bat` file or run:

```powershell
.\gui.ps1
```

### Step 3: Generate Keys

1. Select the number of keys to generate (1-20)
2. Click "Start Generation"
3. Monitor progress in real-time
4. Copy or export generated keys

## File Structure

```
youtube-api-key-generator/
├── README.md                    # This file
├── setup.ps1                    # Environment setup script
├── generate-keys.ps1            # Core generation logic
├── gui.ps1                      # High-resolution GUI
├── config.json                  # Configuration (auto-generated)
├── output/                      # Generated key files
│   ├── api-keys-YYYYMMDD-HHMMSS.txt
│   └── api-keys-YYYYMMDD-HHMMSS.json
├── logs/                        # Execution logs
│   └── generation-YYYYMMDD-HHMMSS.log
└── temp/                        # Temporary files (auto-cleanup)
```

## Configuration

Edit `config.json` to customize:

```json
{
  "projectPrefix": "yt-api",
  "billingAccount": "your-billing-account-id",
  "organization": "",
  "outputFormats": ["txt", "json"],
  "enableLogging": true,
  "cleanupTempFiles": true
}
```

## Troubleshooting

### PowerShell Execution Policy Error

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Google Cloud SDK Not Found

Install from: https://cloud.google.com/sdk/docs/install

### Authentication Error

```powershell
gcloud auth login
gcloud auth application-default login
```

### Billing Account Required

1. Go to https://console.cloud.google.com/billing
2. Create or link a billing account
3. Copy the billing account ID
4. Update `config.json` with the ID

## Security Best Practices

⚠️ **Important Security Notes:**

1. **API Key Management**
   - Store generated keys securely
   - Never commit keys to version control
   - Rotate keys regularly (every 90 days)

2. **API Key Restrictions**
   - Add application restrictions in GCP Console
   - Restrict by HTTP referrer or IP address
   - Limit to YouTube Data API v3 only

## License

This tool is provided as-is for personal use. Use responsibly and in accordance with Google Cloud Platform Terms of Service.
