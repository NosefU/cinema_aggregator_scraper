import datetime as dt

import requests
from bs4 import BeautifulSoup

from scrapers.models import ScrapedMovie, ScrapedSession
from scrapers.abstract_scraper import AbstractScraper
from scrapers.exceptions import BaseScraperException
from settings import HEADERS


class SputnikScraper(AbstractScraper):
    NAME = 'sputnik_cinema31'
    THEATER_BASE_URL = 'https://sputnik-cinema.ru/'

    def run(self, date: dt.date):
        # преобразуем дату в строку, чтобы искать соответствующий тег на странице
        date_str = date.strftime('%Y-%m-%d')

        payload = {'city': self.config['city_no'], }
        response = requests.get(self.THEATER_BASE_URL, params=payload, headers=HEADERS)
        if response.status_code != 200:
            raise BaseScraperException(f'{self.__class__.__name__}: Response status != 200', response)

        html_doc = BeautifulSoup(response.text, features='html.parser')
        day_schedule = html_doc.find('div', {'class': 'films', 'data-date': date_str})

        movie_cards = day_schedule.find_all('div', {'class': 'film flex'})
        for card in movie_cards:
            name_tag = card.findNext('div', {'class': 'film__title'})
            name = name_tag.text

            # ссылок на конкретные сеансы нет, поэтому единственное, что мы можем -
            # получить общую ссылку на фильм на сайте кинотеатра
            link_tag = card.findNext('a', {'class': 'film__head'})
            link = link_tag.attrs['href'] + f'?city={self.config["city_no"]}'

            # год выхода фильма на сайте не пишут(
            year = None

            poster_tag = card.findNext('img', attrs={'class': 'film__poster-image'})
            poster_link = poster_tag.attrs['src']

            movie = ScrapedMovie(filmname=name, year=year, poster_link=poster_link)

            # сеансы
            # В белгородском кинотеатре два зала: синий и красный.
            # А в грайворонском залы просто пронумерованы
            # Но информацию о том, в каком зале проходит конкретный сеанс можно вытащить
            # только из js-модалки рамблер кассы.
            # Оставлю это до того момента, пока не прикручу селениум,
            # а до тех пусть будет пустой зал
            # TODO прикрутить селениум и вытаскивать название зала из модального окна рамблер-кассы
            hall_name = ''
            # ищем сеансы в зале
            hall_sessions = card.find_all(['div', 'span'], attrs={'class': 'schedule__seance'})
            for hall_session in hall_sessions:
                session_time = hall_session.text
                session_time = dt.datetime.strptime(session_time, '%H:%M').time()
                session_datetime = dt.datetime.combine(date, session_time)
                self.raw_sessions.append(
                    ScrapedSession(movie=movie, hall=hall_name, datetime=session_datetime, link=link)
                )
