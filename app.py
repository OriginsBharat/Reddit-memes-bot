import tkinter as tk
from tkinter import ttk, filedialog
import threading
import logging
from pathlib import Path
import shutil

from meme_bot import MemeBot

# --- Logger Setup ---
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)
        self.text_widget.after(0, append)

import json

class Settings:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.config = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self, config):
        self.config = config
        with open(self.filename, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_video_counter(self):
        return self.config.get("video_counter", 0)

    def increment_video_counter(self):
        counter = self.get_video_counter() + 1
        self.config["video_counter"] = counter
        self.save(self.config)

class MemeBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meme Bot")
        self.root.geometry("800x600")
        self.video_path = None
        self.settings = Settings()

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Controls ---
        self.controls_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        self.controls_frame.pack(fill=tk.X, pady=5)

        self.generate_button = ttk.Button(self.controls_frame, text="Generate Video", command=self.start_video_generation_thread)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.download_button = ttk.Button(self.controls_frame, text="Download Video", command=self.download_video, state=tk.DISABLED)
        self.download_button.pack(side=tk.LEFT, padx=5)

        self.settings_button = ttk.Button(self.controls_frame, text="Settings", command=self.open_settings)
        self.settings_button.pack(side=tk.RIGHT, padx=5)

    def open_settings(self):
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("500x300")

        frame = ttk.Frame(self.settings_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a dictionary to hold the entry widgets
        self.setting_entries = {}

        settings_to_create = [
            ("reddit_client_id", "Reddit Client ID:"),
            ("reddit_client_secret", "Reddit Client Secret:"),
            ("reddit_user_agent", "Reddit User Agent:"),
            ("reddit_username", "Reddit Username:"),
            ("reddit_password", "Reddit Password:"),
        ]

        for key, text in settings_to_create:
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            label = ttk.Label(row, text=text, width=20)
            label.pack(side=tk.LEFT)
            entry = ttk.Entry(row)
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            entry.insert(0, self.settings.get(key, ""))
            self.setting_entries[key] = entry

        # Voice Sample
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=2)
        label = ttk.Label(row, text="Voice Sample:", width=20)
        label.pack(side=tk.LEFT)
        self.voice_sample_var = tk.StringVar(value=self.settings.get("voice_sample", ""))
        voice_entry = ttk.Entry(row, textvariable=self.voice_sample_var, state="readonly")
        voice_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        browse_button = ttk.Button(row, text="Browse...", command=self.browse_voice_sample)
        browse_button.pack(side=tk.RIGHT)

        # Save and Cancel buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.settings_window.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def browse_voice_sample(self):
        path = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav")],
            title="Select Voice Sample"
        )
        if path:
            self.voice_sample_var.set(path)

    def save_settings(self):
        new_config = {key: entry.get() for key, entry in self.setting_entries.items()}
        new_config["voice_sample"] = self.voice_sample_var.get()
        self.settings.save(new_config)
        self.settings_window.destroy()

        # --- Progress Log ---
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Progress", padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, height=10, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure logging
        self.log_text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_text_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.log_text_handler)
        logging.getLogger().setLevel(logging.INFO)

    def start_video_generation_thread(self):
        self.generate_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')

        config = self.settings.load()
        if not all(key in config for key in ["reddit_client_id", "reddit_client_secret", "voice_sample"]):
            logging.error("Please configure your settings first.")
            self.generate_button.config(state=tk.NORMAL)
            return

        video_counter = self.settings.get_video_counter()
        thread = threading.Thread(target=self.generate_video, args=(config, video_counter))
        thread.start()

    def generate_video(self, config, video_counter):
        try:
            # This is a blocking call, run in a thread
            bot = MemeBot(config, video_counter)
            self.video_path = bot.run()
            logging.info(f"Video generation complete! Path: {self.video_path}")
            self.download_button.config(state=tk.NORMAL)
            self.settings.increment_video_counter()
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)
        finally:
            self.generate_button.config(state=tk.NORMAL)

    def download_video(self):
        if not self.video_path:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")],
            initialfile=self.video_path.name,
            title="Save Video As"
        )

        if save_path:
            try:
                shutil.copy(self.video_path, save_path)
                logging.info(f"Video saved to {save_path}")
            except Exception as e:
                logging.error(f"Failed to save video: {e}")


if __name__ == "__main__":
    import os
    # Create dummy voice file for testing if it doesn't exist
    if not Path("test_voice.wav").exists():
        with open("test_voice.wav", "w") as f:
            f.write("")

    root = tk.Tk()
    app = MemeBotApp(root)
    root.mainloop()
