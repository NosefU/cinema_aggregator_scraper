from dataclasses import asdict
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from models import FedMovie
from repos.abstract_fed_movies_repo import AbstractFedMoviesRepo


class PostgresFedMoviesRepo(AbstractFedMoviesRepo):
    """
    PostgreSQL репозиторий фильмов
    с данными из Реестра прокатных удостоверений фильмов Минкульта РФ
    """

    tables = {
        'fedMovie': """
                CREATE TABLE fedMovie (
                    "id" INTEGER PRIMARY KEY,
                    "cardNumber" VARCHAR(20) NOT NULL,
                    "foreignName" VARCHAR,
                    "filmname" VARCHAR NOT NULL,
                    "studio" VARCHAR,
                    "crYearOfProduction" VARCHAR,
                    "director" VARCHAR,
                    "scriptAuthor" VARCHAR,
                    "composer" VARCHAR,
                    "durationMinute" INTEGER,
                    "durationHour" INTEGER,
                    "ageCategory" VARCHAR,
                    "annotation" TEXT,
                    "countryOfProduction" VARCHAR,
                    "ageLimit" INTEGER
                );
            """,
    }

    def __init__(self, config: dict):
        self.db_name = config['db_name']
        self.db_user = config['db_user']
        self.db_password = config['db_password']
        self.db_host = config['db_host']

    def init_repo(self):
        with psycopg2.connect(dbname=self.db_name, user=self.db_user,
                              password=self.db_password, host=self.db_host) as conn:
            cursor = conn.cursor()

            for table_name, sql_script in self.tables.items():
                # проверяем, существует ли таблица
                cursor.execute(
                    """                    
                    SELECT EXISTS (
                       SELECT FROM information_schema.tables
                       WHERE  table_schema = 'public'
                       AND    table_name   = %(table_name)s
                    );
                    
                    """,
                    {'table_name': table_name.lower()}
                )
                exists = cursor.fetchone()[0]
                # если не существует, то создаём
                if not exists:
                    cursor.execute(sql_script)

    def add_movies(self, movies: list[FedMovie]):
        with psycopg2.connect(dbname=self.db_name, user=self.db_user,
                              password=self.db_password, host=self.db_host) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                DELETE FROM fedMovie WHERE "id" = %(id)s;                
                INSERT INTO fedMovie
                (
                "id", 
                "cardNumber", 
                "foreignName", 
                "filmname", 
                "studio", 
                "crYearOfProduction", 
                "director", 
                "scriptAuthor", 
                "composer", 
                "durationMinute", 
                "durationHour", 
                "ageCategory", 
                "annotation", 
                "countryOfProduction", 
                "ageLimit"
                )
                VALUES
                (
                %(id)s, 
                %(cardNumber)s, 
                %(foreignName)s, 
                %(filmname)s, 
                %(studio)s, 
                %(crYearOfProduction)s, 
                %(director)s, 
                %(scriptAuthor)s, 
                %(composer)s, 
                %(durationMinute)s, 
                %(durationHour)s, 
                %(ageCategory)s, 
                %(annotation)s, 
                %(countryOfProduction)s, 
                %(ageLimit)s
                );
                """,
                [asdict(movie) for movie in movies]
            )

    def get_movie_by_id(self, idx: int) -> Optional[FedMovie]:
        with psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,
                              host=self.db_host, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM fedMovie WHERE id = %s;""", (idx, ))
            result = cursor.fetchone()
            if result is None:
                return None
            return FedMovie(**result)

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[FedMovie]:
        year = int(year)
        with psycopg2.connect(dbname=self.db_name, user=self.db_user,
                              password=self.db_password, host=self.db_host) as conn:
            cursor = conn.cursor()
            if year:
                cursor.execute(
                    """
                    SELECT id, filmname
                    FROM fedMovie 
                    WHERE "crYearOfProduction" BETWEEN %s and %s;
                    """,
                    (str(year-1), str(year + 1))
                )
            else:
                cursor.execute("""SELECT id, filmname FROM fedMovie;""")
            result = cursor.fetchall()
            movies = self._find_title_matches(title, result)

            if movies is None:
                return None
            return self.get_movie_by_id(movies[0][0])

    @property
    def max_id(self) -> int:
        with psycopg2.connect(dbname=self.db_name, user=self.db_user,
                              password=self.db_password, host=self.db_host) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT MAX(id)
                FROM fedMovie
                """
            )
            result = cursor.fetchone()
            return result[0]


# if __name__ == '__main__':
#     import csv
#
#     repo = PostgresFedMoviesRepo(db_config)
#     repo.init_repo()
#
#     movies = []
#     with open('../data-7-structure-4.csv', 'r', encoding='UTF-8') as f, sqlite3.connect('fed_movies.db') as conn:
#         reader = csv.DictReader(f, delimiter=',')
#         for row in reader:
#             movies.append(FedMovie.from_fed_csv(row))
#
#     repo.add_movies(movies)
#     print(repo.search_movie('Салют-7 (режиссерская версия)', 2017))
