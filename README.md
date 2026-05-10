# Qoder - 音视频转 MP3 工具

![Python](https://img.shields.io/badge/Python-3.12-blue) ![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green) ![FFmpeg](https://img.shields.io/badge/Engine-FFmpeg-orange)

Qoder 是 Windows 桌面工具，支持拖放或浏览添加音视频文件，一键批量转换为 MP3 格式。转换后保留 ID3 元数据（标题、艺术家、专辑等）。

## 功能

- **拖放添加** — 直接拖拽文件或文件夹到窗口
- **批量转换** — 支持多文件排队，串行依次转换
- **格式广泛** — 支持 MP3、WAV、FLAC、OGG、AAC、WMA、M4A、MP4、AVI、MKV、MOV、WebM、FLV、3GP
- **ID3 标签保留** — 自动读取源文件元数据并写入输出 MP3
- **比特率可选** — 128 / 192 / 256 / 320 kbps
- **输出目录可选** — 输出到源文件夹或自定义目录
- **进度显示** — 实时进度条，错误原因中文提示
- **独立 exe** — 打包后无需安装 Python 或 FFmpeg

## 下载

自行构建，或从 [Releases](https://github.com/Lemon1-8/media_to_mp3/releases) 页面下载。

## 开发

### 环境要求

- Python 3.12+
- FFmpeg（精简版约 10-30MB，置于 `tools/ffmpeg/ffmpeg.exe`）

### 安装依赖

```bash
pip install pyqt5 mutagen pyinstaller
```

### 运行

```bash
python run.py
```

### 测试

```bash
python -m pytest tests/ -v
```

### 构建 exe

```bash
packaging\build.bat
```

或手动执行：

```bash
python -m PyInstaller packaging/build.spec
```

构建产物在 `dist/Qoder/`，可直接复制到其他 Windows 电脑运行。

## 技术栈

| 组件 | 用途 |
|------|------|
| Python 3.12 | 开发语言 |
| PyQt5 | 桌面 GUI |
| FFmpeg | 音视频转换引擎 |
| mutagen | ID3 元数据读写 |
| PyInstaller | 打包为独立 exe |

本工具使用了 [FFmpeg](https://ffmpeg.org/)，根据 LGPL/GPL 许可证分发。
