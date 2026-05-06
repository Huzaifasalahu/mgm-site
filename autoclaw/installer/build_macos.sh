#!/bin/bash
# AutoClaw macOS Installer Build Script
# Builds the macOS .dmg installer using PyInstaller and create-dmg

set -e

echo "============================================"
echo "  AutoClaw macOS Installer Builder"
echo "============================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found"
    exit 1
fi

# Install dependencies
echo "[1/6] Installing Python dependencies..."
pip3 install -r requirements.txt

# Build with PyInstaller
echo "[2/6] Building executable with PyInstaller..."
pyinstaller main.spec --clean

if [ ! -f "dist/main" ]; then
    echo "ERROR: PyInstaller build failed"
    exit 1
fi

# Prepare app bundle structure
echo "[3/6] Creating application bundle..."
mkdir -p dist/AutoClaw.app/Contents/MacOS
mkdir -p dist/AutoClaw.app/Contents/Resources

# Create Info.plist
cat > dist/AutoClaw.app/Contents/Info.plist << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AutoClaw</string>
    <key>CFBundleIdentifier</key>
    <string>com.autoclaw.agent</string>
    <key>CFBundleName</key>
    <string>AutoClaw</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# Copy executable
cp dist/main dist/AutoClaw.app/Contents/MacOS/AutoClaw

# Copy resources
cp -r skills dist/AutoClaw.app/Contents/Resources/
cp -r ui dist/AutoClaw.app/Contents/Resources/
cp main.py dist/AutoClaw.app/Contents/Resources/
cp agent.py dist/AutoClaw.app/Contents/Resources/
cp tools.py dist/AutoClaw.app/Contents/Resources/

# Create launcher script
cat > dist/AutoClaw.app/Contents/MacOS/launch.sh << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")/../Resources"
export PYTHONPATH="$(dirname "$0")/../Resources"
exec "$(dirname "$0")/AutoClaw"
LAUNCHER
chmod +x dist/AutoClaw.app/Contents/MacOS/launch.sh

# Create DMG
echo "[4/6] Creating disk image..."

# Create temporary directory for DMG contents
mkdir -p dist/dmg_temp
cp -r dist/AutoClaw.app dist/dmg_temp/
ln -s /Applications dist/dmg_temp/Applications

# Check if create-dmg is available
if command -v create-dmg &> /dev/null; then
    echo "[5/6] Using create-dmg..."
    create-dmg \
        --volname "AutoClaw Installer" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --app-drop-link 450 200 \
        dist/AutoClaw.dmg \
        dist/dmg_temp/
else
    echo "[5/6] create-dmg not found, creating basic DMG..."
    hdiutil create -volname "AutoClaw Installer" \
        -srcfolder dist/dmg_temp \
        -ov -format UDZO dist/AutoClaw.dmg
fi

# Cleanup
echo "[6/6] Cleaning up..."
rm -rf dist/dmg_temp

echo ""
echo "============================================"
echo "  BUILD SUCCESSFUL!"
echo "  Installer: dist/AutoClaw.dmg"
echo "============================================"
