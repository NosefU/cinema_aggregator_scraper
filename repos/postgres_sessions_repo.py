from dataclasses import asdict

import psycopg2

from models import Session


class PostgresSessionsRepo:
    """
    PostgreSQL репозиторий сеансов
    """

    tables = {
        'session': """
                create table session
                (
                    id         serial      primary key,
                    theater_id integer     not null      references theater on delete cascade,
                    movie_id   integer     not null      references fedmovie on delete cascade,
                    hall       varchar,
                    datetime   timestamp,
                    link       varchar,
                    constraint session_pk
                        unique (theater_id, movie_id, hall, datetime)
                );
                
                create index session_datetime_index  on session (datetime desc);
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

    def add_sessions(self, sessions: list[Session]):
        with psycopg2.connect(dbname=self.db_name, user=self.db_user,
                              password=self.db_password, host=self.db_host) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT INTO session
                (
                "theater_id",
                "movie_id",
                "hall",
                "datetime",
                "link"
                )
                VALUES
                (
                %(theater_id)s, 
                %(movie_id)s, 
                %(hall)s, 
                %(datetime)s, 
                %(link)s
                )

                ON CONFLICT DO NOTHING;
                """,
                [asdict(session) for session in sessions]
            )
