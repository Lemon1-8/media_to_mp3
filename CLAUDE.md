# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Qoder 是 Windows 桌面工具：用户拖放音视频文件，转换为 MP3 格式，打包为独立 exe。

**技术栈**: Python 3.12 + PyQt5 (GUI) + FFmpeg (转换引擎) + mutagen (ID3 标签) + PyInstaller (打包)

## 常用命令

```bash
# 开发运行
python run.py

# 运行全部测试
python -m pytest tests/ -v

# 运行单个测试文件
python -m pytest tests/test_queue_manager.py -v

# 运行单个测试用例
python -m pytest tests/test_queue_manager.py::TestQueueManager::test_add_supported_file -v

# 构建 exe（需要 tools/ffmpeg/ffmpeg.exe）
python -m PyInstaller packaging/build.spec

# 一键构建（自动安装 PyInstaller、清理旧构建）
packaging\build.bat
```

## 项目结构

```
src/
├── main.py                  # 入口: QApplication + MainWindow
├── ui/                      # PyQt5 界面层
│   ├── main_window.py       # 顶层窗口，组装所有子组件
│   ├── file_drop_widget.py  # 拖放区 + 浏览按钮
│   ├── queue_widget.py      # 队列表格 + 进度条 + 右键菜单
│   ├── settings_panel.py    # 比特率/输出目录/保留元数据选项
│   └── about_dialog.py      # 关于对话框
├── core/                    # 业务逻辑层
│   ├── converter.py         # 转换编排器，串行遍历队列
│   ├── ffmpeg_wrapper.py    # QProcess 封装，进度解析，错误映射
│   └── queue_manager.py     # 队列增删改查、去重
└── utils/                   # 基础设施
    ├── format_registry.py   # 支持格式字典（类别 + MIME）
    ├── file_utils.py        # 格式检测、路径清理、输出路径生成
    ├── metadata_handler.py  # mutagen ID3 标签读写
    └── resource_manager.py  # FFmpeg 路径解析（开发/打包双模式）
tests/
├── test_format_registry.py
├── test_file_utils.py
├── test_ffmpeg_wrapper.py
├── test_metadata_handler.py
└── test_queue_manager.py
tools/ffmpeg/                # FFmpeg 二进制（构建 exe 时需要）
packaging/
├── build.spec               # PyInstaller 打包配置
├── build.bat                # 一键构建脚本
└── version.py               # 版本号
```

## 架构

### 模块依赖关系

```
main.py → main_window.py
main_window.py → file_drop_widget.py, queue_widget.py, settings_panel.py, about_dialog.py
main_window.py → queue_manager.py, converter.py
converter.py → ffmpeg_wrapper.py, metadata_handler.py, file_utils.py, resource_manager.py
queue_manager.py → file_utils.py
file_drop_widget.py → format_registry.py, file_utils.py
queue_widget.py → file_utils.py
file_utils.py → format_registry.py
```

### 数据流

```
用户拖放文件 → FileDropWidget.dropEvent()
    → QueueManager.add_files() → is_supported_format() 过滤 → QueuedFile 入队
    → queue_changed 信号 → QueueWidget._refresh() 更新表格

点击"开始转换" → SettingsPanel._on_convert()
    → MainWindow._on_convert() → ConverterEngine.start()

ConverterEngine._process_next()   # 查找下一个 pending 文件
    → FFmpegWrapper.convert()     # QProcess 启动 FFmpeg
    → 解析 stdout 获取 out_time_us= 进度
    → 解析 stderr 获取 Duration
    → progress_updated 信号 → ConverterEngine._on_progress()
        → QueueManager.update_status() → queue_changed → QueueWidget 刷新进度条
    → finished 信号 → ConverterEngine._on_file_done()
        → MetadataHandler.write_tags() 写 ID3 标签
        → 递归调用 _process_next() 处理下一个文件
    → 全部完成 → all_finished 信号 → MainWindow 弹出汇总对话框
```

转换是严格串行的：`_processing` 标志防止 `_process_next` 重入，每完成一个文件才处理下一个。

### 信号连接图

```
FFmpegWrapper          ConverterEngine        UI
───────────            ───────────────        ──
progress_updated  ──→  _on_progress
                        → queue_progress ──→  MainWindow 状态栏
                        → file_progress  ──→  MainWindow 状态栏
phase_changed     ──→  _on_phase
                        → phase_changed  ──→  MainWindow 状态栏
finished          ──→  _on_file_done
                        → file_finished  ──→  (预留)
error_occurred    ──→  _on_file_error → _on_file_done(False, ...)
                        → file_finished
                        → _process_next → all_finished(全部完成) → 汇总对话框
```

### FFmpegWrapper 错误映射

`KNOWN_ERROR_PATTERNS` 将 FFmpeg stderr 输出映射为用户友好的中文消息：

| stderr 特征 | 用户消息 |
|---|---|
| `Permission denied` | 文件被其他程序占用 |
| `No space left on device` | 磁盘空间不足 |
| `Invalid data found when processing` | 源文件格式无法识别或已损坏 |
| `Decoder not found` | 缺少解码器，不支持的格式 |
| `does not contain any audio stream` | 该文件不含音轨 |
| 其他 | 取最后一行 stderr 截断到 200 字符 |

### 关键约定

- **status 枚举**: `QueuedFile.status` 使用字符串 `"pending"` / `"converting"` / `"done"` / `"error"`
- **状态修改必须通过 `QueueManager.update_status()`** 以保证 `queue_changed` 信号发出，表格 UI 才能刷新
- `add_files()` 内部调用 `is_supported_format()` 过滤，重复文件基于归一化路径（`\\`→ `/`）去重
- **输出文件名规则**: `{basename}_{bitrate}kbps.mp3`，碰撞时追加 `_{counter}`（如 `song_192kbps_1.mp3`）
- 所有路径处理使用 `os.path`，非手动字符串操作
- FFmpeg 的 Duration 信息在 stderr 解析，进度（`out_time_us=`）在 stdout 解析

### 资源路径解析

`resource_manager.get_ffmpeg_path()` 区分两种模式：
- **开发模式**（`sys.frozen` 为 False）：`<项目根>/tools/ffmpeg/ffmpeg.exe`
- **打包模式**（`sys.frozen` 为 True）：`sys._MEIPASS/tools/ffmpeg/ffmpeg.exe`

## 打包

`packaging/build.spec` 使用 PyInstaller COLLECT（onedir 模式），关键配置：
- **datas**: 打包 `tools/ffmpeg/` 目录到 `_internal/tools/ffmpeg/`
- **hiddenimports**: `PyQt5.sip`、`mutagen`
- **excludes**: `QtWebEngine`、`QtNetwork`、`QtMultimedia`、`numpy`、`PIL` 等大型冗余包
- **console**: `False`（无终端窗口）
- **upx**: `False`

构建产物在 `dist/Qoder/`，将整个目录复制到任何 Windows 机器即可运行（无 Python 依赖）。

## 测试

- 使用 pytest，无需 mock 库（纯逻辑测试用正则/路径操作，Qt 部分用 QCoreApplication fixture）
- Qt 相关的 fixture 使用 `scope="module"`，复用 `QCoreApplication` 实例
- `test_ffmpeg_wrapper.py` 仅测试正则表达式解析，不启动 QProcess
- `test_file_utils.py` 使用 `tempfile.TemporaryDirectory` 测试文件名碰撞场景
- `test_metadata_handler.py` 只测试边界情况（不存在的文件、空元数据），实际读写依赖 mutagen
