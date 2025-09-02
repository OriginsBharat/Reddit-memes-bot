from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class Meme:
    """Simple representation of a meme post."""

    url: str
    title: str
    score: int
    subreddit: str
    over_18: bool = False
    ocr_text: Optional[str] = None
    image_path: Optional[Path] = None


def filter_quality_memes(memes: Iterable[Meme], min_score: int = 500) -> List[Meme]:
    """Return only memes with score >= min_score, safe for work and image links.

    Parameters
    ----------
    memes:
        Iterable of :class:`Meme` instances.
    min_score:
        Minimum upvote score required for a meme to be kept.

    Returns
    -------
    list of Meme
        Memes meeting the quality criteria.
    """
    allowed_ext = {".jpg", ".jpeg", ".png"}
    result: List[Meme] = []
    for meme in memes:
        if meme.over_18:
            continue
        if meme.score < min_score:
            continue
        lower_url = meme.url.lower()
        if any(lower_url.endswith(ext) for ext in allowed_ext):
            result.append(meme)
    return result
