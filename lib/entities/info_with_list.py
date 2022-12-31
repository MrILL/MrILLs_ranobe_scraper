from dataclasses import dataclass

from .info import Info
from .chapters_list import ChaptersList

@dataclass
class InfoWithList:
    domain: str
    info: Info
    chapters_list: ChaptersList
