"""
This module contains the core logic for the meme compilation bot.
It is designed to be used by a GUI application.
"""
from __future__ import annotations

import os
import tempfile
import logging
import time
from pathlib import Path
from typing import Iterable, List, Set, Tuple
from datetime import date

import requests
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip

from quality import Meme, filter_quality_memes

logger = logging.getLogger(__name__)

class MemeBot:
    def __init__(self, config, video_counter=0):
        self.config = config
        self.video_counter = video_counter
        self.processed_file = Path("processed_memes.txt")

    def load_processed(self) -> Set[str]:
        if self.processed_file.exists():
            return set(self.processed_file.read_text().splitlines())
        return set()

    def save_processed(self, urls: Iterable[str]) -> None:
        with self.processed_file.open("a") as f:
            for url in urls:
                f.write(url + "\n")

    def fetch_memes(self, subreddits: List[str]) -> List[Meme]:
        """Fetch memes from Reddit using PRAW."""
        import praw

        reddit = praw.Reddit(
            client_id=self.config["reddit_client_id"],
            client_secret=self.config["reddit_client_secret"],
            user_agent=self.config["reddit_user_agent"],
        )

        processed = self.load_processed()
        memes: List[Meme] = []
        keywords = {"relatable", "school"}

        for subreddit in subreddits:
            try:
                for post in reddit.subreddit(subreddit).top(time_filter="day", limit=100):
                    if post.url in processed:
                        continue
                    memes.append(
                        Meme(post.url, post.title, post.score, subreddit, post.over_18)
                    )
                time.sleep(2)
            except Exception as exc:
                logger.error("Failed to fetch from %s: %s", subreddit, exc)

        memes.sort(
            key=lambda m: (
                any(k in m.title.lower() for k in keywords),
                m.score,
            ),
            reverse=True,
        )

        return filter_quality_memes(memes, self.config.get("min_upvotes", 500))

    def download_memes(self, memes: List[Meme], folder: Path) -> List[Meme]:
        """Download meme images to a folder and update meme objects."""
        kept: List[Meme] = []
        for i, meme in enumerate(memes):
            try:
                response = requests.get(meme.url, timeout=15)
                response.raise_for_status()
                ext = os.path.splitext(meme.url)[1]
                path = folder / f"meme_{i}{ext}"
                with open(path, "wb") as f:
                    f.write(response.content)
                meme.image_path = path
                kept.append(meme)
            except Exception as exc:
                logger.warning("Failed to download %s: %s", meme.url, exc)
        return kept

    def extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from an image using Tesseract OCR."""
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(image_path))
        except Exception as exc:
            logger.error("OCR failed for %s: %s", image_path, exc)
            return ""

    def generate_tts(self, memes: List[Meme], folder: Path, speaker_wav: str) -> Tuple[List[Path], List[Meme]]:
        """Generate narration using OCR text, falling back to title."""
        from TTS.api import TTS

        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=False)
        audio_paths: List[Path] = []
        kept: List[Meme] = []
        for i, meme in enumerate(memes):
            try:
                text_to_speak = meme.ocr_text.strip() if meme.ocr_text else meme.title
                if not text_to_speak:
                    logger.warning("No text to speak for meme %s", meme.url)
                    continue

                audio_path = folder / f"meme_{i}.wav"
                tts.tts_to_file(
                    text=text_to_speak,
                    speaker_wav=speaker_wav,
                    language="en",
                    file_path=str(audio_path),
                )
                audio_paths.append(audio_path)
                kept.append(meme)
            except Exception as exc:
                logger.warning("TTS failed for %s: %s", text_to_speak, exc)
        return audio_paths, kept

    def create_video(self, images: List[Path], audios: List[Path], output: Path, video_counter: int) -> None:
        """Combine images and narration into a single video with title and end screens."""
        logger.info(f"Creating video number {video_counter + 1}")

        # Create meme clips
        meme_clips = []
        for img, audio in zip(images, audios):
            img_clip = ImageClip(str(img)).set_duration(self.config.get("display_time", 5))
            audio_clip = AudioFileClip(str(audio))
            img_clip = img_clip.set_audio(audio_clip)
            meme_clips.append(img_clip)

        main_compilation = concatenate_videoclips(meme_clips, method="compose")

        # Create title screen
        title_text = f"Memes i found on reddit #{video_counter + 1}"
        title_clip = TextClip(title_text, fontsize=70, color='white', size=main_compilation.size).set_duration(3)
        animation = VideoFileClip("endscreen_animation.gif", has_mask=True).resize(height=150).set_pos(("center", "center"))
        title_screen = CompositeVideoClip([title_clip, animation])

        # Create end screen
        end_text = "Please subscribe and share!"
        end_clip = TextClip(end_text, fontsize=70, color='white', size=main_compilation.size).set_duration(3)
        end_screen = CompositeVideoClip([end_clip, animation.set_start(0)])

        # Concatenate all parts
        final_video = concatenate_videoclips([title_screen, main_compilation, end_screen])
        final_video.write_videofile(str(output), fps=24, codec="libx264", preset="ultrafast")

    def upvote_memes(self, memes: List[Meme]):
        """Upvote the memes that were used in the video."""
        import praw

        try:
            reddit = praw.Reddit(
                client_id=self.config["reddit_client_id"],
                client_secret=self.config["reddit_client_secret"],
                user_agent=self.config["reddit_user_agent"],
                username=self.config["reddit_username"],
                password=self.config["reddit_password"],
            )
            for meme in memes:
                try:
                    submission = reddit.submission(url=meme.url)
                    submission.upvote()
                    logger.info(f"Upvoted meme: {meme.url}")
                except Exception as exc:
                    logger.error(f"Failed to upvote meme {meme.url}: {exc}")
        except Exception as exc:
            logger.error(f"Failed to initialize Reddit for upvoting: {exc}")

    def run(self) -> Path:
        """
        Runs the entire video generation process.
        Returns the path to the generated video.
        """
        subreddits = self.config.get("subreddits", [
            "memes", "dankmemes", "IndianDankMemes", "animememes",
            "wholesomememes"
        ])
        logger.info("Using subreddits: %s", ", ".join(subreddits))

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            images_dir = tmpdir_path / "images"
            audios_dir = tmpdir_path / "audio"
            images_dir.mkdir()
            audios_dir.mkdir()

            speaker_wav = self.config["voice_sample"]

            memes = self.fetch_memes(subreddits)[:8]
            memes = self.download_memes(memes, images_dir)

            for meme in memes:
                if meme.image_path:
                    meme.ocr_text = self.extract_text_from_image(meme.image_path)

            audio_paths, memes = self.generate_tts(memes, audios_dir, speaker_wav)

            if not memes:
                raise Exception("No memes with audio could be processed.")

            video_path = tmpdir_path / "output.mp4"
            image_paths = [meme.image_path for meme in memes if meme.image_path]

            self.create_video(image_paths, audio_paths, video_path, self.video_counter)

            self.save_processed(m.url for m in memes)
            self.upvote_memes(memes)

            # The video is in a temporary directory, so we need to move it
            # to a permanent location before the directory is cleaned up.
            final_video_path = Path.cwd() / f"meme_compilation_{date.today().isoformat()}.mp4"
            video_path.rename(final_video_path)

            return final_video_path
