import re
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict

from models import FedMovie


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

    @staticmethod
    def _normalize_title(title: str) -> str:
        """
        Нормализует название фильма для дальнейшего поиска по репозиторию

        :param title: Название фильма
        :return: Нормализованное название фильма
        """
        title = re.sub(r'(\W+)', ' ', title)
        title = title.translate(str.maketrans({'Ё': 'Е', 'Й': 'И', 'ё': 'е', 'й': 'и', }))
        title = title.strip()
        title = title.lower()
        return title

    def _find_title_matches(self, title: str, movies: List[Tuple[int, str]]) -> Optional[List[Tuple[int, str]]]:
        """
        Ищет в переданном списке фильмов наиболее близкие к title названия

        :param title: Название фильма
        :param movies: список фильмов в формате [(id_фильма, название_фильма), ]
        :return: список найденных фильмов в формате [(id_фильма, название_фильма), ]
        """
        norm_title = self._normalize_title(title)
        movies = [[idx, db_title, 0] for idx, db_title in movies]
        for idx, repo_title, _ in movies:
            if repo_title == norm_title:
                return self.get_movie_by_id(idx)

        # алгоритм разбивает на слова искомое название и название из списка и считает количество совпадающих слов
        for i, movie in enumerate(movies):
            repo_title = self._normalize_title(movie[1])
            repo_title_words = repo_title.split()
            for title_word in norm_title.split():
                if title_word in repo_title_words:
                    repo_title_words.remove(title_word)
                    movies[i][2] += 1

        # сортируем по количеству совпадающих слов (по убыванию)
        movies.sort(key=lambda elem: elem[2], reverse=True)

        if movies[0][2] == 0:  # если совпадений не нашлось, то возвращаем None
            return None
        # возвращаем фильмы с наибольшим количеством совпадений
        max_matches = movies[0][2]
        return [tuple(movie[:-1]) for movie in movies if movie[2] == max_matches]
