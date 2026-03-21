# yt2mp3 🎵

A robust, cross-platform Command Line Interface (CLI) tool for downloading YouTube videos and playlists as audio files. Powered by `yt_dlp` and `FFmpeg`.

## Features

* **Interactive CLI Menu:** Easy-to-use terminal interface for downloading, configuring, and managing audio formats.
* **Dynamic Configuration:** Set your preferred audio codec (MP3, FLAC, WAV, Opus, etc.) and quality. The script actively prevents invalid bitrate/codec combinations.
* **Automated Dependency Management:** Missing FFmpeg or yt_dlp? No problem. The script detects your OS (Windows, macOS, Linux) and can automatically attempt to install FFmpeg, using `winget`, `brew`, or `apt`, or `pip` for yt_dlp.
* **State Management:** Saves your download directory and preferred formats to a local `config.json` file.
* **Anti-Bot Spoofing:** Conditionally utilizes mobile client spoofing to bypass YouTube's bot-protection algorithms.

## Prerequisites

* **Python 3.10** or higher.
* **yt_dlp** python library.

## Installation

1. **Clone the repository:**
   
   Download the release .py file, or you can clone the repo with `git`:
   ```
   git clone https://github.com/ZonkedHobgoblin/yt2mp3
   cd yt2mp3
   ```

   That's it! The script can handle installing yt_dlp and FFmpeg itself. If you'd rather install it yourself, or the script fails, read the next steps below.
<details>
<summary><b>Step 2 - Instructions for installing yt_dlp</b></summary>
   
   Ensure you have yt_dlp installed.
   Don't worry if you don't, the script can attempt to install yt_dlp itself. If it can't, it will provide you with manual instructions on how to install yt_dlp.
   #### How to manually install yt_dlp (If you don't want to use the script)
   Windows:
   ```
   py -m pip install yt_dlp
   or
   py -m pip install -r requirements.txt
   ```
   Linux & Mac:
   ```bash
   python3 -m pip install yt_dlp
   or
   python3 -m pip install -r requirements.txt
   ```
</details>
<details>
<summary><b>Step 3 - instructions for installing FFmpeg</b></summary>
   
   Ensure you have FFmpeg on your system.
   Don't worry if you don't, the script can attempt to install FFmpeg itself. If it can't it will provide you with manual instructions on how to install FFmpeg.
   #### How to manually install FFmpeg (If you don't want to use the script)

   Windows:
   ```
   Manual FFmpeg installation:
   Option 1: Open CMD and run: winget install ffmpeg
   Option 2: Download from: https://github.com/BtbN/FFmpeg-Builds/releases
   ```
   Linux:
   ```
   Manual FFmpeg installation:
   Debian/Ubuntu: sudo apt install ffmpeg
   Arch Linux:  sudo pacman -S ffmpeg
   Fedora: sudo dnf install ffmpeg
   ```
   Mac:
   ```
   Manual FFmpeg installation:
   Step 1. Install Homebrew if missing: https://brew.sh/
   Step 2. Open terminal and run: brew install ffmpeg
   ```
</details>

## Usage
   Run the script from your terminal (or just open it to terminal in a file viewer)
   ```bash
   python yt2mp3.py
   ```

## The menu
  Once launched, if yt_dlp or ffmpeg isn't installed, you'll be greeted with an option to attempt auto installation or see manual instructions on how to.
  If both dependencies are installed, you'll instead see 4 menu options:
  * **Download**: Paste a YouTube video or playlist URL to begin extracting audio (Also works with YouTube music URLs)
  * **Config**: Change your target audio format (Like mp3, flac, etc.), adjust target bitrate (Like 128kbps, 320kbps, etc.), or set a custom download directory. The target file and qualities are not guaranteed, and are preferred options based upon what yt_dlp can get.
  * **About**: View info about the script
  * **Quit**: Stop the script

## Supported file types & qualities
<details>
<summary><b>Supported file types and their respective qualities</b></summary>
These file types are supported by yt2mp3, and it will attempt to download files as your preferred type.
   
<sup>*Please note: Even if saved as a lossless audio file or at a high bitrate, the true audio quality will remain limited by the original YouTube source stream.*</sup>

| File Type  | Qualities (kbps) |
| ------------- | ------------- |
| MP3  | 128 / 192 / 256 / 320  |
| M4A  | 128 / 192 / 256 / 320  |
| AAC  | 128 / 192 / 256 / 320  |
| Opus  | 96 / 128 / 160  |
| Vorbis  | 128 / 192  |
| Flac  | Lossless  |
| Alac  | Lossless  |
| Wav  | Lossless  |

</details>

## Roadmap
This project is actively being developed. Upcoming features include:
* [v1.0.3] **Type Hinting**: Adding type hinting for improving code reliability and IDE support.
* [v1.0.5] **OOP Refactor**: Transitioning to an object-oriented structure for better modularity.
* [v1.1.0] **Video Formats**: Support to download videos in a range of formats, along with subtitles.
* [v1.2.0] **Cookie passing**: Optional support to use your browser cookies. For YouTube Premium users, this allows access to higher audio qualities.
* [v1.3.0] **Batch Downloading**: Support for downloading entire channels, from .txts containing links, or inputting multiple URLs (No playlist needed).
* [v1.4.0] **Download Persistence**: Resuming interrupted batch downloads from where it left off.
* [v1.5.0] **Standalone Executable**: Compiling the script into an executable file so it can be used without Python.
* [v2.0.0] **GUI Migration**: Transitioning from a CLI to a full Graphical User Interface.

## ⚠️ Disclaimer
This tool is for educational and personal archiving purposes only. Please respect YouTube's Terms of Service and the copyright of content creators. Do not use this tool to distribute copyrighted material.

## Author
**Created by [zonkedhobgoblin](https://github.com/ZonkedHobgoblin)**
