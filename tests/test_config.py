import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from meme_bot import load_subreddits


def test_load_subreddits_env_var(monkeypatch):
    monkeypatch.setenv("SUBREDDITS", "a,b , c")
    assert load_subreddits() == ["a", "b", "c"]
