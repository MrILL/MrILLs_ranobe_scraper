from typing import Optional, List
from dataclasses import dataclass

@dataclass
class ChaptersListUnit:
    url: str
    title: str

    added_at: Optional[str] = None

@dataclass
class ChaptersList:
    domain: str
    url: str
    chapters: List[ChaptersListUnit]
