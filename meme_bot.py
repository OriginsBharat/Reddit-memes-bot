"""Automated meme compilation and upload bot.

This script fetches high-quality memes from predefined subreddits,
converts the meme titles to speech using a cloned voice, compiles the
images and narration into a short video, uploads it to YouTube Shorts
and finally removes temporary downloads.

Environment variables required:
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
    YT_CLIENT_SECRETS_FILE - path to OAuth2 client secrets JSON
    VOICE_SAMPLE - path to a WAV file of the desired cloned voice

Note: user must install requirements from requirements.txt and provide
API credentials. This script is a template and may require adjustments
for production use.
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
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips

# Imports placed inside functions to avoid heavy dependency errors during import
# (e.g. when running unit tests without the libraries installed).

from quality import Meme, filter_quality_memes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_SUBREDDITS = [
    "memes",
    "dankmemes",
    "wholesomememes",
    "IndianDankMemes",
    "animememes",
    "ProgrammerHumor",
    "SchoolMemes",
    "gamingmemes",
]

MIN_UPVOTES = int(os.getenv("MIN_UPVOTES", "1000"))
DISPLAY_TIME = int(os.getenv("DISPLAY_TIME", "5"))
PROCESSED_FILE = Path("processed_memes.txt")


def load_subreddits() -> List[str]:
    env_val = os.getenv("SUBREDDITS")
    if env_val:
        return [s.strip() for s in env_val.split(",") if s.strip()]
    return DEFAULT_SUBREDDITS


def load_processed() -> Set[str]:
    if PROCESSED_FILE.exists():
        return set(PROCESSED_FILE.read_text().splitlines())
    return set()


def save_processed(urls: Iterable[str]) -> None:
    with PROCESSED_FILE.open("a") as f:
        for url in urls:
            f.write(url + "\n")


def fetch_memes(subreddits: List[str]) -> List[Meme]:
    """Fetch memes from Reddit using PRAW."""
    import praw  # imported here to keep dependency optional

    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "meme-bot"),
    )

    processed = load_processed()
    memes: List[Meme] = []
    for subreddit in subreddits:
        try:
            for post in reddit.subreddit(subreddit).top(time_filter="day", limit=25):
                if post.url in processed:
                    continue
                memes.append(
                    Meme(post.url, post.title, post.score, subreddit, post.over_18)
                )
            time.sleep(2)
        except Exception as exc:
            logger.error("Failed to fetch from %s: %s", subreddit, exc)
    return filter_quality_memes(memes, MIN_UPVOTES)


def download_memes(memes: List[Meme], folder: Path) -> Tuple[List[Path], List[Meme]]:
    """Download meme images to a folder."""
    paths: List[Path] = []
    kept: List[Meme] = []
    for i, meme in enumerate(memes):
        try:
            response = requests.get(meme.url, timeout=15)
            response.raise_for_status()
            ext = os.path.splitext(meme.url)[1]
            path = folder / f"meme_{i}{ext}"
            with open(path, "wb") as f:
                f.write(response.content)
            paths.append(path)
            kept.append(meme)
        except Exception as exc:
            logger.warning("Failed to download %s: %s", meme.url, exc)
    return paths, kept


def generate_tts(memes: List[Meme], folder: Path, speaker_wav: str) -> Tuple[List[Path], List[Meme]]:
    """Generate narration audio files for each meme title."""
    from TTS.api import TTS  # imported lazily

    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    audio_paths: List[Path] = []
    kept: List[Meme] = []
    for i, meme in enumerate(memes):
        try:
            audio_path = folder / f"meme_{i}.wav"
            tts.tts_to_file(
                text=meme.title,
                speaker_wav=speaker_wav,
                language="en",
                file_path=str(audio_path),
            )
            audio_paths.append(audio_path)
            kept.append(meme)
        except Exception as exc:
            logger.warning("TTS failed for %s: %s", meme.title, exc)
    return audio_paths, kept


def create_video(images: List[Path], audios: List[Path], output: Path) -> None:
    """Combine images and narration into a single video."""
    clips = []
    for img, audio in zip(images, audios):
        img_clip = ImageClip(str(img)).set_duration(DISPLAY_TIME)
        audio_clip = AudioFileClip(str(audio))
        img_clip = img_clip.set_audio(audio_clip)
        clips.append(img_clip)
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(output), fps=24, codec="libx264", preset="ultrafast")


def upload_to_youtube(video: Path, title: str, description: str = "") -> None:
    """Upload video to YouTube Shorts using the Data API."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None
    token_path = Path("token.pickle")
    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("YT_CLIENT_SECRETS_FILE"), scopes
            )
            creds = flow.run_console()
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "23",  # comedy
            },
            "status": {"privacyStatus": "public"},
        },
        media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True),
    )
    response = None
    while response is None:
        try:
            _, response = request.next_chunk()
        except Exception as exc:
            logger.error("Upload failed: %s", exc)
            break


def main() -> None:
    voice_sample = os.getenv("VOICE_SAMPLE")
    if not voice_sample:
        raise RuntimeError("VOICE_SAMPLE environment variable not set")

    subreddits = load_subreddits()
    logger.info("Using subreddits: %s", ", ".join(subreddits))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        images_dir = tmpdir_path / "images"
        audios_dir = tmpdir_path / "audio"
        images_dir.mkdir()
        audios_dir.mkdir()

        speaker_wav_path = Path(voice_sample)
        if speaker_wav_path.suffix.lower() != ".wav":
            converted = tmpdir_path / "speaker.wav"
            AudioFileClip(str(speaker_wav_path)).write_audiofile(str(converted))
            speaker_wav = str(converted)
        else:
            speaker_wav = voice_sample

        memes = fetch_memes(subreddits)[:8]
        image_paths, memes = download_memes(memes, images_dir)
        audio_paths, memes = generate_tts(memes, audios_dir, speaker_wav)
        video_path = tmpdir_path / "output.mp4"
        create_video(image_paths, audio_paths, video_path)
        title = f"Reddit Meme Compilation - {date.today().isoformat()}"
        subs = sorted({m.subreddit for m in memes})
        description = "Memes from: " + ", ".join(subs) + "\n" + "\n".join(
            m.title for m in memes
        )
        upload_to_youtube(video_path, title=title, description=description)
        save_processed(m.url for m in memes)

        # temporary directory automatically cleaned up


if __name__ == "__main__":
    main()
