import re
from typing import Optional, List, Tuple

from sqlalchemy import func

from db.models import Fedmovie, Session


class FedMoviesRepo:
    """
    Репозиторий фильмов с данными из Реестра прокатных удостоверений фильмов Минкульта РФ
    """
    @property
    def max_id(self) -> int:
        """
        Возвращает последний id в таблице с фильмами

        :return: максимальный id фильма
        """
        with Session() as session:
            result = session.query(func.max(Fedmovie.id)).one()
            return result[0]

    @staticmethod
    def add_movies(movies: list[Fedmovie]):
        """
        Добавление фильмов в репозиторий

        :param movies: список фильмов для добавления
        """
        if not all([isinstance(movie, Fedmovie) for movie in movies]):
            raise TypeError('В списке должны быть только объекты типа Fedmovie')

        with Session() as session:
            new_movies = {movie.id: movie for movie in movies}

            # Обновляем записи, которые уже есть в БД
            for movie in session.query(Fedmovie).filter(Fedmovie.id.in_(new_movies.keys())).all():
                session.merge(new_movies.pop(movie.id))
            # добавляем все остальные
            session.bulk_save_objects(new_movies.values())

            session.commit()

    @staticmethod
    def get_movie_by_id(idx: int) -> Optional[Fedmovie]:
        """
        Поиск фильма по идентификатору записи реестра (id фильма в реестре Минкульта)

        :param idx: Идентификатор записи реестра (id фильма в реестре Минкульта)
        :return: Найденный фильм, либо None
        """
        with Session() as session:
            movie = session.get(Fedmovie, idx)
        return movie

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Fedmovie]:
        """
        Поиск фильма в репозитории по названию и году выхода

        :param title: Название фильма
        :param year: Год выхода. Поиск осуществляется в промежутке ± 1 год от переданного
        :return: Найденный фильм, либо None
        """
        with Session() as session:
            if year:
                year = int(year)
                result = session.query(Fedmovie.id, Fedmovie.filmname). \
                    filter(Fedmovie.crYearOfProduction.between(str(year - 1), str(year + 1))).all()
            else:
                result = session.query(Fedmovie.id, Fedmovie.filmname).all()

        movies = self._find_title_matches(title, result)
        if movies is None:
            return None
        with Session() as session:
            movie = session.get(Fedmovie, movies[0][0])
        return movie

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
