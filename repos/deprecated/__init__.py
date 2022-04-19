import os
from typing import Optional

from repos.deprecated.postgres_fed_movies_repo import PostgresFedMoviesRepo
from repos.deprecated.postgres_sessions_repo import PostgresSessionsRepo
from repos.deprecated.postgres_theaters_repo import PostgresTheatersRepo
from repos.deprecated.sqlite_fed_movies_repo import SQLiteFedMoviesRepo


def fed_movies_repo_factory(config: Optional[dict] = None):
    if not config:
        config = os.environ

    dialect = config.get('DB_DIALECT')
    if dialect == 'sqlite':
        repo_config = {'path': config['DB_PATH']}
        return SQLiteFedMoviesRepo(config=repo_config)
    elif dialect == 'postgres':
        repo_config = {
            'db_name': config['DB_NAME'],
            'db_user': config['DB_USER'],
            'db_password': config['DB_PASSWORD'],
            'db_host': config['DB_HOST'],
        }
        return PostgresFedMoviesRepo(config=repo_config)
    else:
        return None


def sessions_repo_factory(config: Optional[dict] = None):
    if not config:
        config = os.environ

    dialect = config.get('DB_DIALECT')
    # if dialect == 'sqlite':
    #     repo_config = {'path': config['DB_PATH']}
    #     return PostgresSessionsRepo(config=repo_config)
    if dialect == 'postgres':
        repo_config = {
            'db_name': config['DB_NAME'],
            'db_user': config['DB_USER'],
            'db_password': config['DB_PASSWORD'],
            'db_host': config['DB_HOST'],
        }
        return PostgresSessionsRepo(config=repo_config)
    else:
        return None


def theaters_repo_factory(config: Optional[dict] = None):
    if not config:
        config = os.environ

    dialect = config.get('DB_DIALECT')
    # if dialect == 'sqlite':
    #     repo_config = {'path': config['DB_PATH']}
    #     return PostgresSessionsRepo(config=repo_config)
    if dialect == 'postgres':
        repo_config = {
            'db_name': config['DB_NAME'],
            'db_user': config['DB_USER'],
            'db_password': config['DB_PASSWORD'],
            'db_host': config['DB_HOST'],
        }
        return PostgresTheatersRepo(config=repo_config)
    else:
        return None
