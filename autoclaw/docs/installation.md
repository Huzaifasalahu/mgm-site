# AutoClaw Installation Guide

## System Requirements

### Windows
- Windows 10 or later (64-bit)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Python 3.8+ (if building from source)

### macOS
- macOS 10.15 (Catalina) or later
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Python 3.8+ (if building from source)

### Linux
- Ubuntu 20.04+ or equivalent
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Python 3.8+ (if building from source)

## Quick Start (Pre-built Installer)

### Windows
1. Download `AutoClaw_Setup.exe` from releases
2. Run the installer
3. Follow the installation wizard
4. Launch AutoClaw from Start Menu or Desktop

### macOS
1. Download `AutoClaw.dmg` from releases
2. Open the DMG file
3. Drag AutoClaw to Applications folder
4. Launch from Applications

## Building from Source

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/autoclaw.git
cd autoclaw
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Browser Automation
```bash
# For Playwright
playwright install chromium

# Or for Pyppeteer
pyppeteer-install
```

### Step 4: Run AutoClaw
```bash
# GUI mode (default)
python main.py

# CLI mode
python main.py --cli
```

## Building Installers

### Windows Installer
```bash
cd installer
build_windows.bat
```

Requirements:
- NSIS (Nullsoft Scriptable Install System)
- PyInstaller

### macOS Installer
```bash
cd installer
./build_macos.sh
```

Requirements:
- PyInstaller
- create-dmg (optional, for polished DMG)

## Configuration

After first launch, configure your LLM provider:

1. Go to Settings tab
2. Select your LLM provider (OpenAI, Anthropic, Google, etc.)
3. Enter your API key
4. Click "Save Configuration"

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for common issues.
