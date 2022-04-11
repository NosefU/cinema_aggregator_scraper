import datetime as dt
import glob
from pathlib import Path
from typing import List, Optional

import requests

from models import Theater, Session
from repos.abstract_fed_movies_repo import AbstractFedMoviesRepo
from settings import POSTERS_PATH, HEADERS


class BaseEngineException(BaseException):
    pass


class ScrapingEngine:
    def __init__(self, theaters: List[Theater], fed_movies_repo: AbstractFedMoviesRepo):
        self.theaters = theaters
        self.fed_movies_repo = fed_movies_repo
        self.sessions = []

    @staticmethod
    def _get_poster(idx: int) -> Optional[str]:
        """
        Возвращает путь до постера фильма по id, если таковой имеется

        :param idx: id фильма
        :return: относительный путь до картинки с постером или None
        """
        img_mask = Path(POSTERS_PATH, str(idx) + '.*')
        images = glob.glob(str(img_mask))
        if images:
            return images[0]
        return None

    @staticmethod
    def _save_poster(idx: int, img_link: str) -> str:
        """
        Сохраняет постер

        :param idx: id фильма
        :param img_link: ссылка на постер
        :return: относительный путь до скачанной картинки с постером
        """
        img_ext = img_link.split('.')[-1]
        img_response = requests.get(img_link, headers=HEADERS)
        img_data = img_response.content
        img_path = Path(POSTERS_PATH, str(idx) + '.' + img_ext)
        with open(img_path, 'wb') as f:
            f.write(img_data)
        return str(img_path)

    def run(self, date: dt.date):
        raw_sessions = {}
        for theater in self.theaters:
            scraper = theater.scraper()
            scraper.run(date)
            raw_sessions[theater] = scraper.raw_sessions

        for theater, theater_raw_sessions in raw_sessions.items():
            for raw_session in theater_raw_sessions:
                movie = self.fed_movies_repo.search_movie(title=raw_session.movie.filmname,
                                                          year=raw_session.movie.year)
                if not movie:
                    raise BaseEngineException(f'Фильм {raw_session.movie} не найден в реестре Минкульта',
                                              raw_session.movie)

                # если постера в базе нет, то скачиваем
                poster_path = self._get_poster(movie.id)
                if not poster_path:
                    poster_path = self._save_poster(movie.id, raw_session.movie.poster_link)
                    # TODO добавить путь до постера в таблицу БД

                session = Session(
                    theater_id=theater.id,
                    movie=movie,
                    hall=raw_session.hall,
                    datetime=raw_session.datetime,
                    link=raw_session.link
                )
                self.sessions.append(session)
