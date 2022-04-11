from __future__ import annotations

from dataclasses import dataclass
import datetime as dt
from typing import Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.abstract_scraper import AbstractScraper


@dataclass
class ScrapedMovie:
    filmname: str
    poster_link: Optional[str]
    year: Optional[int]

    def __repr__(self):
        return f'ScrapedMovie: {self.filmname}, ({self.year})'


@dataclass
class ScrapedSession:
    movie: ScrapedMovie
    hall: str
    datetime: dt.datetime
    link: str


@dataclass
class Session:
    theater_id: int  # Theater.id
    movie: FedMovie  # for future: FedMovie.id
    hall: str
    datetime: dt.datetime
    link: Optional[str]


@dataclass
class Theater:
    id: int
    name: str
    city: str
    address: str
    timezone: str  # TODO нужна ли? Если да, то как лучше реализовать?
    scraper: Type[AbstractScraper]
    scraper_args: Optional[dict] = None

    def __hash__(self):
        return hash('Theater ' + str(self.id))


@dataclass
class FedMovie:
    """
    Модель фильма, с данными из Реестра прокатных удостоверений фильмов Минкульта РФ
    https://opendata.mkrf.ru/opendata/7705851331-register_movies/
    """
    id: int
    cardNumber: str
    foreignName: Optional[str]
    filmname: str
    studio: Optional[str]
    crYearOfProduction: Optional[str]
    director: Optional[str]
    scriptAuthor: Optional[str]
    composer: Optional[str]
    durationMinute: Optional[int]
    durationHour: Optional[int]
    ageCategory: Optional[str]
    annotation: Optional[str]
    countryOfProduction: Optional[str]
    ageLimit: Optional[int]

    @classmethod
    def from_fed_csv(cls, row: dict) -> FedMovie:
        """
        Конвертирует словарь со строкой из бд в объект фильма

        :param row: словарь со строкой из csv-выгрузки из реестра
        :return: объект фильма
        """
        duration_minute = row['Продолжительность демонстрации, минуты']
        duration_minute = int(duration_minute) if duration_minute != '' else None
        duration_hour = row['Продолжительность демонстрации, часы']
        duration_hour = int(duration_hour) if duration_hour != '' else None
        age_limit = row['Возрастная категория (число)'].strip()
        age_limit = int(age_limit) if age_limit != '' else None

        return cls(
            id=row['Идентификатор записи реестра'],
            cardNumber=row['Номер удостоверения'].strip(),
            foreignName=row['Hаименование на иностранном языке'].strip(),
            filmname=row['Название фильма'].strip(),
            studio=row['Студия-производитель'].strip(),
            crYearOfProduction=row['Год производства'].strip(),
            director=row['Режиссер'].strip(),
            scriptAuthor=row['Сценарист'].strip(),
            composer=row['Композитор'].strip(),
            durationMinute=duration_minute,
            durationHour=duration_hour,
            ageCategory=row['Возрастная категория'].strip(),
            annotation=row['Аннотация'].strip(),
            countryOfProduction=row['Страна производства'].strip(),
            ageLimit=age_limit
        )

    def __repr__(self):
        return f'FedMovie(id={self.id}, {self.filmname}, {self.crYearOfProduction})'

# if __name__ == '__main__':
#     pass
    # import csv
    # import re
    # import sqlite3
    # from abc import ABC, abstractmethod
    # from dataclasses import asdict, dataclass
    # from typing import Optional

    # fed_movies_db = SQLiteFedMoviesRepo({'path': 'fed_movies.db'})
    # fed_movies_db.init_repo()
    # movies = []
    # with open('data-7-structure-4.csv', 'r', encoding='UTF-8') as f, sqlite3.connect('fed_movies.db') as conn:
    #     reader = csv.DictReader(f, delimiter=',')
    #     for row in reader:
    #         movies.append(FedMovie.from_fed_csv(row))
    #
    # fed_movies_db.add_movie(movies)
    # print(fed_movies_db.search_movie('Салют-7 (режиссерская версия)', 2017))

