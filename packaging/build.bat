@echo off
chcp 65001 >nul
echo ====== Qoder Build Script ======
echo.

python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] 安装 PyInstaller...
    pip install pyinstaller
)

if not exist "tools\ffmpeg\ffmpeg.exe" (
    echo [ERROR] FFmpeg binary not found at tools\ffmpeg\ffmpeg.exe
    echo 请下载 ffmpeg.exe 并放置到 tools\ffmpeg\ 目录
    pause
    exit /b 1
)

echo [INFO] 清理上次构建...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo [INFO] 开始构建...
python -m PyInstaller packaging/build.spec

if %errorlevel% equ 0 (
    echo.
    echo ====== Build successful! ======
    echo Output: dist\Qoder\
    echo Run: dist\Qoder\Qoder.exe
) else (
    echo.
    echo [ERROR] Build failed!
)

pause
