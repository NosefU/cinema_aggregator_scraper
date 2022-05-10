"""
Обновляет данные о фильмах, вытаскивая их через API минкульта РФ
"""

import os
import datetime as dt

import requests
from sqlalchemy import inspect

from db.models import Fedmovie
from repos.fed_movies_repo import FedMoviesRepo
from settings import HEADERS

DATA_URL = 'https://opendata.mkrf.ru/v2/register_movies/7'
REQ_PARAMS_TEMPLATE = 'f={{"modified":{{"$gt":"{date}"}}}}'


if __name__ == '__main__':
    fed_movies_db = FedMoviesRepo()

    update_from_date = (dt.date.today() - dt.timedelta(days=30)).strftime('%Y-%m-%d')
    headers = HEADERS.copy()
    headers.update({'X-API-KEY': os.environ['MKRF_API_KEY']})

    movies = []
    next_url = DATA_URL
    params = REQ_PARAMS_TEMPLATE.format(date=update_from_date)
    while next_url:
        print(next_url)
        response = requests.get(next_url, params=params, headers=headers)
        if response.status_code != 200:
            raise requests.exceptions.InvalidURL(f'MKRF update data downloading error: {response.status_code}')

        movie_fields = [column.key for column in inspect(Fedmovie).attrs]

        for raw_movie in response.json()['data']:
            movie_data = raw_movie['data']['general']
            movie_params = {k: v for k, v in movie_data.items() if k in movie_fields}
            movie_params['durationMinute'] = movie_params['durationMinute'].strip() or None
            movie_params['durationHour'] = movie_params['durationHour'].strip() or None
            movie_params['ageLimit'] = movie_params['ageLimit'].strip() or None
            movies.append(Fedmovie(**movie_params))

        next_url = response.json().get('nextPage')
        params = None

    print(f'Added/updated {len(movies)} movie(s):\n\t', end='')
    print(*movies, sep='\n\t')
    fed_movies_db.add_movies(movies)
