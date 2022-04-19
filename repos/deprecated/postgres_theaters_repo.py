from dataclasses import asdict
from typing import Optional, List

import psycopg2
from psycopg2.extras import RealDictCursor

from scrapers.models import Theater


class PostgresTheatersRepo:
    """
    PostgreSQL репозиторий кинотеатров
    """

    tables = {
        'theater': """
                create table theater
                (
                    id             serial    primary key,
                    name           varchar   not null,
                    address        varchar,
                    scraper_kwargs json,
                    city           varchar,
                    scraper        varchar   not null
                );
                
                create index theater_city_index on theater (city);
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

    def add_theaters(self, theaters: list[Theater]):
        with psycopg2.connect(dbname=self.db_name, user=self.db_user,
                              password=self.db_password, host=self.db_host) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                DELETE FROM theater WHERE "id" = %(id)s;                
                INSERT INTO theater
                (
                "id",
                "name",
                "city",
                "address",
                "scraper",
                "scraper_kwargs"
                )
                VALUES
                (
                %(id)s, 
                %(name)s, 
                %(city)s, 
                %(address)s, 
                %(scraper.name)s, 
                %(scraper_kwargs)s
                );
                """,
                [asdict(theater).update({'scraper': theater.scraper.name}) for theater in theaters]
            )

    def get_theater_by_id(self, idx: int) -> Optional[Theater] :
        with psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,
                              host=self.db_host, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM theater WHERE id = %s;""", (idx, ))
            result = cursor.fetchone()
            if result is None:
                return None
            return Theater(**result)

    def get_theaters_by_city(self, city: str) -> Optional[List[Theater]] :
        with psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,
                              host=self.db_host, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM theater WHERE city = %s;""", (city, ))
            results = cursor.fetchall()
            if results is None:
                return None


            return [Theater(**result) for result in results]
