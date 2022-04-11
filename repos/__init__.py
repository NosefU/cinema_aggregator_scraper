import os
from typing import Optional

from repos.postgres_fed_movies_repo import PostgresFedMoviesRepo
from repos.sqlite_fed_movies_repo import SQLiteFedMoviesRepo


def fed_movies_repo_factory(config: Optional[dict] = None):
    if not config:
        config = os.environ

    dialect = config.get('DB_DIALECT')
    if dialect == 'sqlite':
        repo_config = {'path': config['DB_PATH']}
        return SQLiteFedMoviesRepo(config=repo_config)
    elif dialect == 'postgresql':
        repo_config = {
            'db_name': config['DB_NAME'],
            'db_user': config['DB_USER'],
            'db_password': config['DB_PASSWORD'],
            'db_host': config['DB_HOST'],
        }
        return PostgresFedMoviesRepo(config=repo_config)
    else:
        return None
