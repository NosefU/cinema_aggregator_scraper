import datetime as dt
import glob
from pathlib import Path
from typing import List, Optional

import requests

from db.models import Theater, MovieSession
from repos.fed_movies_repo import FedMoviesRepo
from repos.movie_sessions_repo import MovieSessionsRepo
from scrapers import scraper_factory
from settings import HEADERS, MEDIA_ROOT, POSTERS_DIR


class BaseEngineException(BaseException):
    pass


class ScrapingEngine:
    """
    Движок, управляющий работой скраперов и сохраняющий данные, которые поступают от скраперов
    """
    def __init__(self, theaters: List[Theater],
                 fed_movies_repo: FedMoviesRepo, sessions_repo: MovieSessionsRepo):
        """
        :param theaters: список кинотеатров
        :param fed_movies_repo: репозиторий фильмов
        :param sessions_repo: репозиторий сеансов
        """
        self.theaters = theaters
        self.fed_movies_repo = fed_movies_repo
        self.sessions_repo = sessions_repo

    @staticmethod
    def _get_poster(idx: int) -> Optional[str]:
        """
        Возвращает путь до постера фильма по id, если таковой имеется

        :param idx: id фильма
        :return: относительный путь до картинки с постером или None
        """
        img_mask = Path(MEDIA_ROOT, POSTERS_DIR, str(idx) + '.*')
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
        :return: относительный (относительно MEDIA_ROOT) путь до скачанной картинки с постером
        """
        img_ext = img_link.split('.')[-1]
        img_response = requests.get(img_link, headers=HEADERS)
        img_data = img_response.content
        media_path = Path(MEDIA_ROOT, POSTERS_DIR, str(idx) + '.' + img_ext)
        with open(media_path, 'wb') as f:
            f.write(img_data)
        return str(media_path)

    def run(self, date: dt.date):
        """
        Запускает скрапинг сеансов по выбранным кинотеатрам и сохраняет найденные сеансы в БД

        :param date:
        :return:
        """
        raw_sessions = {}
        for theater in self.theaters:
            print(f'Scraping theater {theater}')
            scraper = scraper_factory(theater)
            scraper.run(date)
            raw_sessions[theater.id] = scraper.raw_sessions
            print(f'\tScraping finished')

        movie_sessions = []
        print('Matching movies with DB')
        for theater_id, theater_raw_sessions in raw_sessions.items():
            for raw_session in theater_raw_sessions:
                movie = self.fed_movies_repo.search_movie(title=raw_session.movie.filmname,
                                                          year=raw_session.movie.year)
                if not movie:
                    raise BaseEngineException(f'Фильм {raw_session.movie} не найден в реестре Минкульта',
                                              raw_session.movie)

                # если постера в базе нет, то скачиваем
                if not movie.posterPath and raw_session.movie.poster_link:
                    print(f'Downloading poster for {movie}')
                    poster_path = self._save_poster(movie.id, raw_session.movie.poster_link)
                    movie.posterPath = poster_path
                    self.fed_movies_repo.add_movies([movie, ])

                session = MovieSession(
                    theater_id=theater_id,
                    movie_id=movie.id,
                    hall=raw_session.hall,
                    datetime=raw_session.datetime,
                    link=raw_session.link
                )
                movie_sessions.append(session)

        self.sessions_repo.add_movie_sessions(movie_sessions)
        print(f'Added/updated {len(movie_sessions)} session(s)')
