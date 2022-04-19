from abc import ABC, abstractmethod
from typing import Optional

from scrapers.models import FedMovie


class AbstractFedMoviesRepo(ABC):
    """
    Абстрактный репозиторий фильмов
    с данными из Реестра прокатных удостоверений фильмов Минкульта РФ
    """
    @abstractmethod
    def __init__(self, config: dict): pass

    @abstractmethod
    def init_repo(self):
        """ Инициализация репозитория """
        pass

    @abstractmethod
    def add_movies(self, movies: list[FedMovie]):
        """
        Добавление фильмов в репозиторий

        :param movies: список фильмов для добавления
        """
        pass

    @abstractmethod
    def get_movie_by_id(self, idx: int) -> Optional[FedMovie]:
        """
        Поиск фильма по идентификатору записи реестра (id фильма в реестре Минкульта)

        :param idx: Идентификатор записи реестра (id фильма в реестре Минкульта)
        :return: Найденный фильм, либо None
        """
        pass

    @abstractmethod
    def search_movie(self, title: str, year: Optional[int]) -> Optional[FedMovie]:
        """
        Поиск фильма в репозитории по названию и году выхода

        :param title: Название фильма
        :param year: Год выхода. Поиск осуществляется в промежутке ± 1 год от переданного
        :return: Найденный фильм, либо None
        """
        pass


