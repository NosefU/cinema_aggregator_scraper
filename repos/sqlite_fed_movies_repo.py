import sqlite3
from dataclasses import asdict
from typing import Optional

from models import FedMovie
from repos.abstract_fed_movies_repo import AbstractFedMoviesRepo


class SQLiteFedMoviesRepo(AbstractFedMoviesRepo):
    """
    SQLite3 репозиторий фильмов
    с данными из Реестра прокатных удостоверений фильмов Минкульта РФ
    """

    config_pragmas = """PRAGMA foreign_key = ON;"""

    tables = {
        'fedMovie': """
                CREATE TABLE fedMovie (
                    id INTEGER PRIMARY KEY,
                    cardNumber VARCHAR(20) NOT NULL,
                    foreignName VARCHAR(100),
                    filmname VARCHAR(100) NOT NULL,
                    studio VARCHAR(200),
                    crYearOfProduction VARCHAR(10),
                    director VARCHAR(50),
                    scriptAuthor VARCHAR(50),
                    composer VARCHAR(50),
                    durationMinute INTEGER,
                    durationHour INTEGER,
                    ageCategory VARCHAR(50),
                    annotation TEXT,
                    countryOfProduction VARCHAR(30),
                    ageLimit INTEGER
                );
            """,
    }

    def __init__(self, config: dict):
        self.path = config['path']

    def init_repo(self):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.executescript(self.config_pragmas)

            for table_name, sql_script in self.tables.items():
                # проверяем, существует ли таблица
                cursor.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name=:table_name;
                    """,
                    {'table_name': table_name}
                )
                exists = cursor.fetchone()
                # если не существует, то создаём
                if not exists:
                    cursor.executescript(sql_script)

    def add_movies(self, movies: list[FedMovie]):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                REPLACE INTO fedMovie
                (
                id, 
                cardNumber, 
                foreignName, 
                filmname, 
                studio, 
                crYearOfProduction, 
                director, 
                scriptAuthor, 
                composer, 
                durationMinute, 
                durationHour, 
                ageCategory, 
                annotation, 
                countryOfProduction, 
                ageLimit
                )
                VALUES
                (
                :id, 
                :cardNumber, 
                :foreignName, 
                :filmname, 
                :studio, 
                :crYearOfProduction, 
                :director, 
                :scriptAuthor, 
                :composer, 
                :durationMinute, 
                :durationHour, 
                :ageCategory, 
                :annotation, 
                :countryOfProduction, 
                :ageLimit
                );
                """,
                [asdict(movie) for movie in movies]
            )

    def get_movie_by_id(self, idx: int) -> Optional[FedMovie]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM fedMovie WHERE id = ?;""", (idx, ))
            result = cursor.fetchone()
            if result is None:
                return None
            return FedMovie(**result)

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[FedMovie]:
        year = int(year)
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            if year:
                cursor.execute(
                    """
                    SELECT id, filmname
                    FROM fedMovie 
                    WHERE crYearOfProduction BETWEEN ? and ?;
                    """,
                    (year-1, year + 1)
                )
            else:
                cursor.execute("""SELECT id, filmname FROM fedMovie;""")
            result = cursor.fetchall()
            movies = self._find_title_matches(title, result)

            if movies is None:
                return None
            return self.get_movie_by_id(movies[0][0])