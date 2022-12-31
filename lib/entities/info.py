from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Info(dict):
    domain: str
    url: str
    title: str

    slug: Optional[str] = None
    description: Optional[str] = None
    title_alt: Optional[str] = None

    # Additional fields
    type: Optional[str] = None
    format: Optional[str] = None
    publish_year: Optional[int] = None
    status: Optional[str] = None
    translation_status: Optional[str] = None
    author: Optional[str] = None
    artist: Optional[str] = None
    publishing_by: Optional[str] = None
    age_restriction: Optional[str] = None
    alt_titles: Optional[List[str]] = None
    tags: Optional[List[str]] = None
