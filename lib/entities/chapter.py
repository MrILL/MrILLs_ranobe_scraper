from typing import Optional
from dataclasses import dataclass

@dataclass
class Chapter:
    domain: str
    url: str
    volume: int
    nomer: int
    title: str
    content: str

    # url sources to prev & next chapters
    prev: Optional[str]
    next: Optional[str]
