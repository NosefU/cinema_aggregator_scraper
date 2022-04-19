"""
Обновляет данные о фильмах, вытаскивая их через API минкульта РФ
"""

import os

import requests
from sqlalchemy import inspect

from db.models import Fedmovie
from repos.fed_movies_repo import FedMoviesRepo
from settings import HEADERS

DATA_URL = 'https://opendata.mkrf.ru/v2/register_movies/7'
REQ_PARAMS_TEMPLATE = 'f={{"nativeId":{{"$gte":{max_id}}}}}'


if __name__ == '__main__':
    fed_movies_db = FedMoviesRepo()
    params = REQ_PARAMS_TEMPLATE.format(max_id=fed_movies_db.max_id)
    headers = HEADERS.copy()
    headers.update({'X-API-KEY': os.environ['MKRF_API_KEY']})

    response = requests.get(DATA_URL, params=params, headers=headers)
    if response.status_code != 200:
        raise requests.exceptions.InvalidURL(f'MKRF update data downloading error: {response.status_code}')

    movie_fields = [column.key for column in inspect(Fedmovie).attrs]

    movies = []
    for raw_movie in response.json()['data']:
        movie_data = raw_movie['data']['general']
        movie_params = {k: v for k, v in movie_data.items() if k in movie_fields}
        movies.append(Fedmovie(**movie_params))

    print(f'Added/updated {len(movies)} movie(s):\n\t', end='')
    print(*movies, sep='\t\n')
    fed_movies_db.add_movies(movies)
