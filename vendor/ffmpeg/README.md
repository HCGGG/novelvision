# FFmpeg 便携二进制文件

请从 https://www.ffmpeg.org/download.html 或 https://www.gyan.dev/ffmpeg/builds/ 下载 Windows 静态构建：

- `ffmpeg.exe`
- `ffprobe.exe`

将两个文件放入此目录 (`vendor/ffmpeg/`)。

构建时，`build_exe.py` 会自动将这些文件复制到输出目录或嵌入到 exe 中。

运行时，VideoComposer 会优先使用此目录下的 ffmpeg，无需系统安装。