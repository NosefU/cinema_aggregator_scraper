"""
Обновляет данные о фильмах, вытаскивая их через API минкульта РФ
"""

import dataclasses
import os

import requests

from models import FedMovie
from repos import fed_movies_repo_factory
from settings import HEADERS

DATA_URL = 'https://opendata.mkrf.ru/v2/register_movies/7'
REQ_PARAMS_TEMPLATE = 'f={{"nativeId":{{"$gte":{max_id}}}}}'


if __name__ == '__main__':
    fed_movies_db = fed_movies_repo_factory()
    params = REQ_PARAMS_TEMPLATE.format(max_id=fed_movies_db.max_id)
    headers = HEADERS.copy()
    headers.update({'X-API-KEY': os.environ['MKRF_API_KEY']})

    response = requests.get(DATA_URL, params=params, headers=headers)
    if response.status_code != 200:
        raise requests.exceptions.InvalidURL(f'MKRF update data downloading error: {response.status_code}')

    movies = []
    movie_fields = [field.name for field in dataclasses.fields(FedMovie)]
    for raw_movie in response.json()['data']:
        movie_data = raw_movie['data']['general']
        movie_params = {k: v for k, v in movie_data.items() if k in movie_fields}
        movies.append(FedMovie(**movie_params))

    print(movies)
    fed_movies_db.add_movies(movies)
