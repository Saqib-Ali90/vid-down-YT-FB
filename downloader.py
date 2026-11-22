import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
import re

# Appearance settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class VideoDownloaderApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Universal Video Downloader (YouTube & Facebook)")
        self.geometry("620x460")
        self.resizable(False, False)

        # State variables
        self.download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.format_map = {}  # Maps dropdown display text -> yt-dlp format_id
        self.video_title = ""

        self._build_ui()

    def _build_ui(self):
        # Title Header
        self.header_label = ctk.CTkLabel(
            self, text="Video Downloader", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.pack(pady=(20, 5))

        self.sub_label = ctk.CTkLabel(
            self,
            text="Supports YouTube, Facebook, and more",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.sub_label.pack(pady=(0, 20))

        # URL Input Frame
        self.url_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=30)

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Paste YouTube or Facebook video URL here...",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.fetch_btn = ctk.CTkButton(
            self.url_frame,
            text="Fetch Qualities",
            height=40,
            width=130,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_fetch_thread,
        )
        self.fetch_btn.pack(side="right")

        # Video Info Label
        self.title_label = ctk.CTkLabel(
            self,
            text="Ready to fetch video details...",
            font=ctk.CTkFont(size=13, slant="italic"),
            wraplength=540,
            text_color="#A0A0A0",
        )
        self.title_label.pack(pady=(15, 10), padx=30)

        # Quality Dropdown Frame
        self.quality_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quality_frame.pack(fill="x", padx=30, pady=5)

        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Select Quality:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.quality_label.pack(side="left", padx=(0, 15))

        self.quality_dropdown = ctk.CTkOptionMenu(
            self.quality_frame,
            values=["Fetch a link first..."],
            width=380,
            height=35,
            state="disabled",
        )
        self.quality_dropdown.pack(side="right", fill="x", expand=True)

        # Save Location Frame
        self.folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_frame.pack(fill="x", padx=30, pady=15)

        self.folder_label = ctk.CTkLabel(
            self.folder_frame,
            text=f"Save to: {self.download_folder}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        self.folder_label.pack(side="left", fill="x", expand=True)

        self.browse_btn = ctk.CTkButton(
            self.folder_frame,
            text="Change Folder",
            width=110,
            height=28,
            fg_color="#3B3B3B",
            hover_color="#4F4F4F",
            command=self.choose_folder,
        )
        self.browse_btn.pack(side="right")

        # Download Button
        self.download_btn = ctk.CTkButton(
            self,
            text="Download Video",
            height=45,
            width=240,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2FA572",
            hover_color="#106A43",
            state="disabled",
            command=self.start_download_thread,
        )
        self.download_btn.pack(pady=(15, 15))

        # Progress Bar & Status
        self.progress_bar = ctk.CTkProgressBar(self, width=540, height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(5, 5))

        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="#4DA8DA"
        )
        self.status_label.pack(pady=(0, 15))

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_label.configure(text=f"Save to: {self.download_folder}")

    def start_fetch_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please paste a valid video URL.")
            return

        self.fetch_btn.configure(state="disabled", text="Fetching...")
        self.download_btn.configure(state="disabled")
        self.quality_dropdown.configure(state="disabled", values=["Loading formats..."])
        self.quality_dropdown.set("Loading formats...")
        self.status_label.configure(text="Extracting available streams...")
        self.progress_bar.set(0)

        threading.Thread(target=self.fetch_formats, args=(url,), daemon=True).start()

    def fetch_formats(self, url):
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.video_title = info.get("title", "Unknown Video")
                formats = info.get("formats", [])

                self.format_map.clear()
                dropdown_options = []

                # Always offer Best Automatic Quality & Audio Only at the top
                best_label = "Best Available Quality (Auto MP4)"
                self.format_map[best_label] = "bestvideo+bestaudio/best"
                dropdown_options.append(best_label)

                audio_label = "Audio Only (Best MP3/M4A)"
                self.format_map[audio_label] = "bestaudio/best"
                dropdown_options.append(audio_label)

                # Parse specific resolutions
                seen_resolutions = set()
                # Sort formats by height descending
                valid_videos = [
                    f
                    for f in formats
                    if f.get("vcodec") != "none" and f.get("height") is not None
                ]
                valid_videos.sort(
                    key=lambda x: (x.get("height", 0), x.get("fps", 0)), reverse=True
                )

                for f in valid_videos:
                    height = f.get("height")
                    fps = f.get("fps", "")
                    ext = f.get("ext", "mp4")
                    filesize = f.get("filesize") or f.get("filesize_approx")

                    res_key = f"{height}p{fps}"
                    if res_key in seen_resolutions:
                        continue
                    seen_resolutions.add(res_key)

                    size_str = (
                        f" (~{filesize / (1024*1024):.1f} MB)" if filesize else ""
                    )
                    fps_str = f" {int(fps)}fps" if fps and fps > 30 else ""
                    label = f"{height}p{fps_str} [{ext.upper()}]{size_str}"

                    # Combine specific video stream height with best audio
                    self.format_map[label] = (
                        f"bestvideo[height={height}]+bestaudio/best[height={height}]/best"
                    )
                    dropdown_options.append(label)

                self.after(0, self._on_fetch_success, dropdown_options)

        except Exception as e:
            self.after(0, self._on_fetch_error, str(e))

    def _on_fetch_success(self, options):
        self.title_label.configure(
            text=f"Title: {self.video_title}",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.quality_dropdown.configure(state="normal", values=options)
        self.quality_dropdown.set(options[0])
        self.fetch_btn.configure(state="normal", text="Fetch Qualities")
        self.download_btn.configure(state="normal")
        self.status_label.configure(text="Select your desired quality and click Download.")

    def _on_fetch_error(self, error_msg):
        self.fetch_btn.configure(state="normal", text="Fetch Qualities")
        self.quality_dropdown.configure(values=["Failed to fetch"])
        self.quality_dropdown.set("Failed to fetch")
        self.status_label.configure(text="Error fetching video.")
        messagebox.showerror(
            "Fetch Error",
            f"Could not retrieve video details.\n\nDetails:\n{error_msg[:300]}",
        )
    def clean_video_title(self, raw_title: str) -> str:
        text = (raw_title or "video").splitlines()[0].strip()

        # 1. Strip URLs and hashtags (#tag)
        text = re.sub(
            r"(?:https?://\S+|www\.\S+|youtu\.be/\S+)",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"#\S+", " ", text)

        # 2. Split into segments by '|' or '·' or spaced dashes
        segments = [s.strip() for s in re.split(r"\s*(?:\||·|\s[-–—]\s)\s*", text) if s.strip()]

        stat_only = re.compile(
            r"^(?:[\d.,]+\s*[KMBkmb]?\s*(?:views?|likes?|reactions?|comments?|shares?)(?:\s*(?:and|&|,|·|-|\|)?\s*)?)+$",
            re.IGNORECASE,
        )

        cleaned_segments = []
        for seg in segments:
            # Remove leading stat prefixes inside a segment
            seg_clean = re.sub(
                r"^(?:[\d.,]+\s*[KMBkmb]?\s*(?:views?|likes?|reactions?|comments?|shares?)\s*(?:·|-|\|)?\s*)+",
                "",
                seg,
                flags=re.IGNORECASE,
            ).strip()
            if seg_clean and not stat_only.match(seg_clean):
                cleaned_segments.append(seg_clean)

        # 3. Pick the best segment: if there are multiple, prefer a short/medium title segment
        # over a long paragraph-like description
        if cleaned_segments:
            short_or_medium = [s for s in cleaned_segments if 3 <= len(s) <= 75]
            if short_or_medium:
                chosen = short_or_medium[0]
            else:
                chosen = cleaned_segments[0]
        else:
            chosen = text

        # 4. Sanitize Windows-illegal filename characters & collapse spaces
        chosen = re.sub(r'[\\/:*?"<>|]+', " ", chosen)
        chosen = re.sub(r"\s+", " ", chosen).strip(" .-_")

        # 5. Cap final filename length cleanly
        return chosen[:65].strip() if chosen else "video"
    
    def start_download_thread(self):
        url = self.url_entry.get().strip()
        selected_label = self.quality_dropdown.get()
        format_selector = self.format_map.get(selected_label, "best")
        is_audio_only = "Audio Only" in selected_label

        self.download_btn.configure(state="disabled", text="Downloading...")
        self.fetch_btn.configure(state="disabled")
        self.quality_dropdown.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")

        threading.Thread(
            target=self.download_video,
            args=(url, format_selector, is_audio_only),
            daemon=True,
        ).start()

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")

            if total:
                percent = downloaded / total
                self.after(0, self.progress_bar.set, percent)
                self.after(
                    0,
                    self.status_label.configure,
                    {
                        "text": f"Downloading: {percent*100:.1f}%  |  Speed: {speed}  |  ETA: {eta}"
                    },
                )
        elif d["status"] == "finished":
            self.after(0, self.progress_bar.set, 1.0)
            self.after(
                0,
                self.status_label.configure,
                {"text": "Merging audio & video streams... Please wait."},
            )

    def download_video(self, url, format_selector, is_audio_only):
        safe_title = self.clean_video_title(self.video_title)
        output_template = os.path.join(self.download_folder, f"{safe_title}.%(ext)s")

        ydl_opts = {
            "format": format_selector,
            "outtmpl": {"default": output_template},
            "windowsfilenames": True,
            "progress_hooks": [self.progress_hook],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        if is_audio_only:
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        else:
            ydl_opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self._on_download_complete)
        except Exception as e:
            self.after(0, self._on_download_error, str(e))

    def _on_download_complete(self):
        self.download_btn.configure(state="normal", text="Download Video")
        self.fetch_btn.configure(state="normal")
        self.quality_dropdown.configure(state="normal")
        self.status_label.configure(text="Download Complete!")
        messagebox.showinfo(
            "Success", f"Saved successfully to:\n{self.download_folder}"
        )

    def _on_download_error(self, error_msg):
        self.download_btn.configure(state="normal", text="Download Video")
        self.fetch_btn.configure(state="normal")
        self.quality_dropdown.configure(state="normal")
        self.status_label.configure(text="Download failed.")
        messagebox.showerror("Download Error", f"An error occurred:\n{error_msg[:300]}")


if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()