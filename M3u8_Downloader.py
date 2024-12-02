import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import os
import subprocess
import csv
from threading import Thread
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests  # Ensure this library is installed


class M3U8DownloaderApp:

    def __init__(self, root):
        self.root = root
        self.root.title("M3U8 Downloader")
        self.root.geometry("600x500")

        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos.db")
        self.txt_file = None
        self.dest_folder = None
        self.subtitles_folder = None

        # Setup the UI
        self.create_menu()
        self.create_widgets()

        # Initialize the database
        self.init_db()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open M3U8 File", command=self.select_txt_file)
        file_menu.add_command(label="Export to CSV", command=self.export_db_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Readme", command=self.show_readme)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Set the menu
        self.root.config(menu=menu_bar)

    def create_widgets(self):
        self.txt_file_button = tk.Button(self.root, text="Select M3U8 Playlist File", command=self.select_txt_file)
        self.txt_file_button.pack(pady=10)

        self.dest_folder_button = tk.Button(self.root, text="Select Destination Folder", command=self.select_destination_folder)
        self.dest_folder_button.pack(pady=10)

        self.download_button = tk.Button(self.root, text="Download Videos", command=self.start_download_thread)
        self.download_button.pack(pady=10)


        self.db_listbox_label = tk.Label(self.root, text="Database Entries:")
        self.db_listbox_label.pack(pady=5)

        self.db_listbox = tk.Listbox(self.root, height=8, width=50)
        self.db_listbox.pack(pady=5)

        self.refresh_button = tk.Button(self.root, text="Refresh Database", command=self.refresh_db_list)
        self.refresh_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Status: Waiting for input...", wraplength=300)
        self.status_label.pack(pady=10)

        # Dropdown to select the number of simultaneous downloads
        self.concurrent_downloads_label = tk.Label(self.root, text="Simultaneous Downloads:")
        self.concurrent_downloads_label.pack(pady=5)

        self.concurrent_downloads_var = tk.IntVar(value=1)  # Default value is 1
        self.concurrent_downloads_menu = tk.OptionMenu(self.root, self.concurrent_downloads_var, *[1, 2, 3, 4, 5])
        self.concurrent_downloads_menu.pack(pady=5)

    def init_db(self):
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

            self.subtitle_folder = os.path.join(self.dest_folder, "subtitles")
            os.makedirs(self.subtitle_folder, exist_ok=True)

            self.update_status(f"Destination folder selected: {folder_path}\nSubtitles folder created: {self.subtitle_folder}")


    def start_download_thread(self):
        if self.txt_file and self.dest_folder:
            self.update_status("Downloading...")
            Thread(target=self.download_videos).start()
        else:
            messagebox.showwarning("Missing Information", "Please select both a playlist file and destination folder.")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
        self.root.update_idletasks()

    def download_videos(self):
        with open(self.txt_file, 'r') as file:
            self.lines_iterator = iter(file.readlines())
            video_infos = []

            for line in self.lines_iterator:
                if line.startswith("#EXTINF:"):
                    video_info = self.parse_video_info(line)
                    print(video_info)
                    if video_info:
                        video_infos.append(video_info)

            max_threads = self.concurrent_downloads_var.get()

            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                future_to_video = {executor.submit(self.download_video, info): info for info in video_infos}

                for future in as_completed(future_to_video):
                    try:
                        future.result()
                    except Exception as e:
                        video_info = future_to_video[future]
                        print(f"Error downloading {video_info['name']}: {e}")

    def parse_video_info(self, line):
        try:
            video_info = {}
            pattern = r'(tvg-\w+|group-title)="(.*?)"'
            attributes = re.findall(pattern, line)
            for key, value in attributes:
                if key == 'tvg-name':
                    video_info['name'] = self.sanitize_filename(value)
                elif key == 'tvg-logo':
                    video_info['logo'] = value
                elif key == 'group-title':
                    video_info['group_title'] = value
            video_info['url'] = next(self.lines_iterator).strip()
            return video_info
        except Exception as e:
            print(f"Error parsing video info: {e}")
            return {}

    def sanitize_filename(self, filename):
        return re.sub(r'[<>:"/\\|?*]', '', filename.replace(" ", "_"))

    def download_video(self, video_info):
        video_url = video_info['url']
        video_name = video_info['name']
        video_path = os.path.join(self.dest_folder, f"{video_name}.mp4")
        subtitle_path = os.path.join(self.subtitle_folder, f"{video_name}_eng.srt")

        try:
            logo_path = os.path.join(self.dest_folder, f"{video_info['name']}.png")
            self.download_logo(video_info['logo'], logo_path)
            subprocess.run(['ffmpeg', '-i', video_url, '-c', 'copy', video_path], check=True)
            self.save_video_info(video_info, 'Downloaded')
            self.update_status(f"Downloaded: {video_name}")
            #downloading subtitles
            subprocess.run(['ffmpeg', '-i', video_url, '-map', '0:s:m:language:eng', subtitle_path], check=True)
            self.update_status(f"Downloaded subtitles: {video_name}")

        except Exception as e:
            self.save_video_info(video_info, 'Failed')
            self.update_status(f"Failed: {video_name}")

    def save_video_info(self, video_info, status):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO videos (name, status, logo, group_title)
            VALUES (?, ?, ?, ?)
        ''', (video_info.get('name', ''), status, video_info.get('logo', ''), video_info.get('group_title', '')))
        conn.commit()
        conn.close()

    def refresh_db_list(self):
        self.db_listbox.delete(0, tk.END)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name, status FROM videos")
        rows = c.fetchall()
        conn.close()
        for name, status in rows:
            self.db_listbox.insert(tk.END, f"{name} ({status})")

    def export_db_to_csv(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM videos")
        rows = c.fetchall()
        with open('video_info.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Name', 'Status', 'Logo', 'Group Title'])
            writer.writerows(rows)
        conn.close()
        self.update_status("Database exported to video_info.csv.")

    def show_about(self):
        messagebox.showinfo("About", "M3U8 Downloader\nVersion 1.0\nCreated by Ashutosh Sharma")

    def show_readme(self):
        readme_text = "This application downloads videos from M3U8 playlists.\n\n" \
                      "1. Use 'Open M3U8 File' to load a playlist.\n" \
                      "2. Set a destination folder.\n" \
                      "3. Start downloading.\n" \
                      "4. Export database to CSV using the 'Export to CSV' option."
        messagebox.showinfo("Readme", readme_text)

    def download_logo(self, logo_url, save_path):
        try:
            response = requests.get(logo_url, stream=True, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Ensure the folder exists
            with open(save_path, 'wb') as logo_file:
                for chunk in response.iter_content(1024):
                    logo_file.write(chunk)
            self.update_status(f"Logo saved: {save_path}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download logo: {e}")
            self.update_status(f"Failed to download logo: {logo_url}")


if __name__ == "__main__":
    root = tk.Tk()
    app = M3U8DownloaderApp(root)
    root.mainloop()
