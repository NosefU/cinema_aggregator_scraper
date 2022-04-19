from __future__ import annotations

from dataclasses import dataclass
import datetime as dt
from typing import Optional


@dataclass
class ScrapedMovie:
    """
    Модель сырых данных о фильме
    """
    filmname: str
    poster_link: Optional[str]
    year: Optional[int]

    def __repr__(self):
        return f'ScrapedMovie: {self.filmname}, ({self.year})'


@dataclass
class ScrapedSession:
    """
    Модель сырых данных о сеансе
    """
    movie: ScrapedMovie
    hall: str
    datetime: dt.datetime
    link: str
