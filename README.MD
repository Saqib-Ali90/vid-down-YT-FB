# Universal Video Downloader (YouTube & Facebook)

A lightweight desktop GUI built with CustomTkinter and yt-dlp that lets you fetch available video qualities from YouTube and Facebook links, choose a resolution or audio-only mode from a dropdown, and download with live progress tracking.

## Prerequisites

1. Python 3.9+
2. FFmpeg (required for merging high-resolution video/audio streams into `.mp4` and converting audio to `.mp3`):
   - Windows (winget):** `winget install Gyan.FFmpeg` *(restart your terminal/shell afterward)*
   - macOS (Homebrew):** `brew install ffmpeg`
   - Linux (Ubuntu/Debian):** `sudo apt install ffmpeg`

## Installation & Usage

1. Clone the repository:
   ```bash
   git clone [https://github.com/Saqib-Ali90/vid-down-YT-FB.git](https://github.com/Saqin-Ali90/vid-down-YT-FB.git)
   cd yt-fb-video-downloader
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python downloader.py
   ```

## Building a Standalone `.exe` (Windows)

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --collect-all customtkinter --name "VideoDownloader" downloader.py
```

The executable will be generated inside the `dist/` folder.

## Disclaimer

Please respect copyright laws and the terms of service of the platforms you download from. Only download content you have permission to save. this is just a demostartion project