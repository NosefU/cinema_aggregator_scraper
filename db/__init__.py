import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL


def db_engine_factory(config: Optional[dict] = None, **kwargs) -> Engine:
    """
    Фабкика движков для sqlalchemy

    :param config: словарь с параметрами подключения к postgresql. По умолчанию берётся из переменных окружения
    :param kwargs: аргументы, которые передаются в create_engine

    :return: инициализированный движок sqlalchemy
    """
    if not config:
        config = os.environ
    db_config = {
        'drivername': 'postgresql+psycopg2',
        'username': config['DB_USER'],
        'password': config['DB_PASSWORD'],
        'host': config['DB_HOST'],
        # 'port': '5000',
        'database': config['DB_NAME']
        # 'query': {'encoding': 'utf-8'}
    }
    url = URL.create(**db_config)
    engine = create_engine(url, **kwargs)
    return engine


if __name__ == '__main__':
    engine = db_engine_factory()
