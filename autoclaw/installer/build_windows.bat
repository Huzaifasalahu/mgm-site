@echo off
REM AutoClaw Windows Installer Build Script
REM Builds the Windows .exe installer using PyInstaller and NSIS

echo ============================================
echo  AutoClaw Windows Installer Builder
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

REM Install dependencies
echo [1/5] Installing Python dependencies...
pip install -r requirements.txt

REM Build with PyInstaller
echo [2/5] Building executable with PyInstaller...
pyinstaller main.spec --clean

if not exist "dist\main.exe" (
    echo ERROR: PyInstaller build failed
    exit /b 1
)

REM Prepare NSIS build directory
echo [3/5] Preparing NSIS build files...
mkdir nsis_build
copy dist\main.exe nsis_build\
copy main.py nsis_build\
copy agent.py nsis_build\
copy tools.py nsis_build\
xcopy /E /I skills nsis_build\skills
xcopy /E /I ui nsis_build\ui
copy installer\nsis_installer.nsi nsis_build\
copy installer\GPL-3.0.txt nsis_build\
copy README.md nsis_build\

REM Build NSIS installer
echo [4/5] Building NSIS installer...
cd nsis_build
makensis /V2 nsis_installer.nsi
cd ..

REM Move final installer
echo [5/5] Finalizing...
if exist "nsis_build\AutoClaw_Setup.exe" (
    move nsis_build\AutoClaw_Setup.exe dist\
    echo.
    echo ============================================
    echo  BUILD SUCCESSFUL!
    echo  Installer: dist\AutoClaw_Setup.exe
    echo ============================================
) else (
    echo ERROR: NSIS build failed
    exit /b 1
)

REM Cleanup
echo.
echo Cleaning up temporary files...
rmdir /s /q nsis_build

pause
