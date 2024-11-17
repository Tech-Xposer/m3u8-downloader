import tkinter as tk
import re
from tkinter import filedialog, messagebox
import sqlite3
import os
import subprocess
import csv
from threading import Thread
import os

class M3U8DownloaderApp:

    def __init__(self, root):
        self.root = root
        self.root.title("M3U8 Downloader")
        self.root.geometry("500x400")
        
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos.db")
        
        # Setup the UI
        self.create_widgets()

        # Initialize the database
        self.init_db()

    def create_widgets(self):
        # Button to select M3U8 playlist file
        self.txt_file_button = tk.Button(self.root, text="Select M3U8 Playlist File", command=self.select_txt_file)
        self.txt_file_button.pack(pady=10)

        # Button to select destination folder
        self.dest_folder_button = tk.Button(self.root, text="Select Destination Folder", command=self.select_destination_folder)
        self.dest_folder_button.pack(pady=10)

        # Button to start downloading videos
        self.download_button = tk.Button(self.root, text="Download Videos", command=self.start_download_thread)
        self.download_button.pack(pady=10)

        # Button to export database to CSV
        self.export_button = tk.Button(self.root, text="Export Database to CSV", command=self.export_db_to_csv)
        self.export_button.pack(pady=10)

        # Listbox to view the database contents
        self.db_listbox_label = tk.Label(self.root, text="Database Entries:")
        self.db_listbox_label.pack(pady=5)

        self.db_listbox = tk.Listbox(self.root, height=8, width=50)
        self.db_listbox.pack(pady=5)

        # Button to refresh the listbox
        self.refresh_button = tk.Button(self.root, text="Refresh Database", command=self.refresh_db_list)
        self.refresh_button.pack(pady=10)

        # Status label to display ongoing operations
        self.status_label = tk.Label(self.root, text="Status: Waiting for input...", wraplength=300)
        self.status_label.pack(pady=10)

    def init_db(self):
        # Initialize SQLite database with the required table
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS videos ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, 
                status TEXT, 
                logo TEXT, 
                group_title TEXT
            ) 
        ''')
        conn.commit()
        conn.close()

    def select_txt_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.txt_file = file_path
            self.update_status(f"Playlist file selected: {file_path}")

    def select_destination_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.dest_folder = folder_path
            self.update_status(f"Destination folder selected: {folder_path}")

    def start_download_thread(self):
        # This will start the download process in a separate thread
        if hasattr(self, 'txt_file') and hasattr(self, 'dest_folder'):
            self.update_status("Downloading...")
            Thread(target=self.download_videos).start()
        else:
            messagebox.showwarning("Missing Information", "Please select both a playlist file and destination folder.")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
    def sanitize_filename(self, filename):
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")
        # Remove characters not allowed in file names
        return re.sub(r'[<>:"/\\|?*]', '', filename)

    def parse_video_info(self, line):
        video_info = {}
        try:
            # Regex to extract attributes like tvg-name, tvg-logo, and group-title
            pattern = r'(\w+-\w+|group-title)="(.*?)"'
            attributes = re.findall(pattern, line)

            for key, value in attributes:
                if key == 'tvg-name':
                    video_info['name'] = self.sanitize_filename(value)
                elif key == 'tvg-logo':
                    video_info['logo'] = value
                elif key == 'group-title':
                    video_info['group_title'] = value

            # Get the video URL from the next line
            video_info['url'] = next(self.lines_iterator).strip()

            return video_info
        except Exception as e:
            print(f"Error parsing video info: {e}")
            return {}

    def download_video(self, video_info):
        video_url = video_info['url']
        video_name = video_info['name']
        dest_folder = self.dest_folder

        # Create a valid file path
        video_file_path = os.path.join(dest_folder, f"{video_name}.mp4")

        try:
            # Using FFmpeg to download the video
            command = ['ffmpeg', '-i', video_url, '-c', 'copy', video_file_path]
            subprocess.run(command, check=True)
            
            self.save_video_info(video_info, 'Downloaded')
            self.update_status(f"Downloaded: {video_name}")
        except Exception as e:
            print(f"Error downloading {video_name}: {e}")
            self.save_video_info(video_info, 'Failed')
            self.update_status(f"Failed: {video_name}")

    def download_videos(self):
        # Open the M3U file and process the contents
        with open(self.txt_file, 'r') as file:
            self.lines_iterator = iter(file.readlines())
            for line in self.lines_iterator:
                if line.startswith("#EXTINF:"):
                    video_info = self.parse_video_info(line)
                    if video_info:
                        self.download_video(video_info)

    def save_video_info(self, video_info, status):
        # Insert the video information into the database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO videos (name, status, logo, group_title)
            VALUES (?, ?, ?, ?)
        ''', (video_info.get('name', ''), status, video_info.get('logo', ''), video_info.get('group_title', '')))
        conn.commit()
        conn.close()

    def refresh_db_list(self):
        # Refresh the listbox with the latest database entries
        self.db_listbox.delete(0, tk.END)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, name, status FROM videos")
        rows = c.fetchall()
        conn.close()

        # Add the video names and statuses to the listbox
        for row in rows:
            self.db_listbox.insert(tk.END, f"{row[1]} ({row[2]})")

    def export_db_to_csv(self):
        # Export the database content to CSV
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM videos")
        rows = c.fetchall()

        with open('video_info.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['ID', 'Name', 'Status', 'Logo', 'Group Title'])
            csv_writer.writerows(rows)

        conn.close()
        self.update_status("Database exported to video_info.csv.")

def run_app():
    root = tk.Tk()
    app = M3U8DownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
