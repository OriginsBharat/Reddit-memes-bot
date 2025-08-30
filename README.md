# Reddit Meme Compilation Bot

This project automatically gathers high-quality memes from several Reddit
subreddits, generates narration using a cloned voice, compiles the memes
into a 40–60 second video and uploads the result to YouTube Shorts.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set required environment variables:
   - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`
   - `YT_CLIENT_SECRETS_FILE` (path to OAuth2 client secrets JSON)
   - `VOICE_SAMPLE` (path to a voice sample – WAV or MP3)
   - `SUBREDDITS` (comma separated list; default is a curated set)

   On Windows Command Prompt use `set VARIABLE=value` (PowerShell: `$Env:VARIABLE="value"`),
   replacing `export` from the examples.
3. Run the bot:
   ```bash
   python meme_bot.py
   ```

Downloaded files are stored in a temporary directory and removed after
uploading. Previously processed meme URLs are stored in `processed_memes.txt`
to avoid duplicate uploads. NSFW posts are filtered out automatically.

The first time text-to-speech runs, the model
`tts_models/multilingual/multi-dataset/xtts_v2` will be downloaded, which may
take some time and disk space.

## Testing

Unit tests cover the meme quality filter:

```bash
pytest
```
