import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quality import Meme, filter_quality_memes


def test_filter_quality_memes():
    memes = [
        Meme(url="http://example.com/a.jpg", title="A", score=1200, subreddit="memes"),
        Meme(url="http://example.com/b.gif", title="B", score=1500, subreddit="memes"),
        Meme(url="http://example.com/c.png", title="C", score=400, subreddit="memes"),
        Meme(url="http://example.com/d.png", title="D", score=2000, subreddit="memes", over_18=True),
    ]
    result = filter_quality_memes(memes, min_score=500)
    assert len(result) == 1
    assert result[0].title == "A"
