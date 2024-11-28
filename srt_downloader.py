import os
import subprocess

def parse_m3u8(file_path):
    """
    Parse an M3U8 file and extract video URLs.

    Args:
        file_path (str): Path to the M3U8 file.

    Returns:
        list: A list of video URLs.
    """
    video_urls = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                video_urls.append(line)
    return video_urls

def download_hindi_subtitles_fast(video_url, output_dir="subtitles", subtitle_language="hin"):
    """
    Downloads Hindi subtitles quickly from a video/streaming source using ffmpeg.

    Args:
        video_url (str): The URL or path of the video/playlist.
        output_dir (str): Directory to save the subtitles.
        subtitle_language (str): Language code for subtitles (default is "hin" for Hindi).
    """
    os.makedirs(output_dir, exist_ok=True)

    # Extract a safe filename for the subtitles
    filename = os.path.basename(video_url).split('.')[0]
    output_file = os.path.join(output_dir, f"{filename}_subtitles.srt")

    try:
        # Optimized ffmpeg command to fetch only subtitle streams
        command = [
            "ffmpeg",
            "-i", video_url,
            "-map", f"0:s:m:language:{subtitle_language}",
            "-c:s", "srt",
            "-f", "srt",
            output_file
        ]

        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)

        print(f"Hindi subtitles downloaded successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg execution for {video_url}. Ensure the video contains Hindi subtitles.")
        print(e)
    except Exception as e:
        print(f"An error occurred for {video_url}:")
        print(e)

if __name__ == "__main__":
    m3u8_file = "m3u8_urls.txt"
    output_dir =  "subtitles"

    video_urls = parse_m3u8(m3u8_file)

    for video_url in video_urls:
        print(f"Processing video URL: {video_url}")
        download_hindi_subtitles_fast(video_url, output_dir)

    print("Subtitle download process complete.")
