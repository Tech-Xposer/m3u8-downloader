
# M3U8 Downloader App 
M3U8 Downloader is a simple graphical user interface (GUI) application built with Python and Tkinter. It allows you to download videos from an M3U8 playlist, with the ability to manage the downloads, export video information to a CSV file, and adjust the number of simultaneous downloads.

## Features

- **Select M3U8 Playlist**: Load an M3U8 playlist file.
- **Select Destination Folder**: Choose a folder to save the downloaded videos.
- **Simultaneous Downloads**: Configure how many videos to download simultaneously (1-5).
- **Download Videos**: Start downloading the videos from the playlist.
- **Refresh Database**: Refresh the list of downloaded videos from the database.
- **Export to CSV**: Export the video database to a CSV file.
- **Status Updates**: View real-time download status.

## Requirements

- Python 3.x
- Tkinter (comes pre-installed with Python)
- `requests` library (for making HTTP requests)
- `ffmpeg` (for downloading the videos)

You can install the required Python dependencies using:

```bash
pip install -r requirements.txt
```

A GUI-based application for downloading videos from M3U8 playlists. This app uses FFmpeg to download videos and includes a database to track download statuses. Built with Python and Tkinter, it’s easy to use and works offline.



# How to Build the App for Windows


## Build .exe File for Windows

To convert your Python application into an executable `.exe` file for Windows, follow these steps. This will allow you to distribute the app without requiring the user to install Python.

## Prerequisites

1. **Install Python 3.x**: Make sure Python 3.x is installed on your system. You can check the installation by running:

    ```bash
    python --version
    ```

2. **Install Required Packages**: Install the necessary Python packages for your project (e.g., `requests`, `tkinter`, etc.) by running:

    ```bash
    pip install -r requirements.txt
    ```

3. **Install PyInstaller**: To create the `.exe` file, install PyInstaller by running:

    ```bash
    pip install pyinstaller
    ```

4. **Ensure FFmpeg is Installed**: Since the app uses `ffmpeg`, make sure FFmpeg is installed and added to your system's PATH. Test the installation by running:

    ```bash
    ffmpeg -version
    ```

    If it's not installed, you can download it from [FFmpeg official site](https://ffmpeg.org/download.html) and follow the installation instructions.



## Building the Executable File

### Step 1: Navigate to Your Project Directory

Open your command prompt or terminal and navigate to the directory where your main Python script (`main.py`) is located.

```bash
cd path\to\your\project
```

### Step 2: Run PyInstaller Command

```
python3 -m PyInstaller --onefile --noconsole --add-data "videos.db:." --icon=icon.png M3u8_Downloader.py

```

### Step 3: Locate the Executable
Once PyInstaller finishes building the executable, you will find the .exe file inside the dist folder within your project directory.


This structure represents the important folders and files in the project:
- `build/` contains temporary build files generated during the process.
- `dist/` is where the executable file (`M3u8_Downloader.exe`) will be located.
- `M3u8_Downloader.py` is the main script for your application.
- `requirements.txt` lists all the dependencies for the project.
- `icon.png` is the custom application icon (optional).
