import datetime as dt

import requests
from bs4 import BeautifulSoup

from scrapers.abstract_scraper import AbstractScraper
from scrapers.exceptions import BaseScraperException
from scrapers.models import ScrapedMovie, ScrapedSession
from settings import HEADERS


class KinobelScraper(AbstractScraper):
    NAME = 'kinobel'
    THEATER_BASE_URL = 'https://kinobel.ru'
    SCHEDULE_PATH = '/kinoteatry'

    def run(self, date: dt.date):
        # преобразуем дату в строку, чтобы искать соответствующий тег на странице
        date_str = date.strftime('%Y-%m-%d')

        response = requests.get(
            self.THEATER_BASE_URL + self.SCHEDULE_PATH + self.config['theater_path'],
            headers=HEADERS
        )
        if response.status_code != 200:
            raise BaseScraperException(f'{self.__class__.__name__}: Response status != 200', response)

        html_doc = BeautifulSoup(response.text, features='html.parser')
        day_schedule = html_doc.find('div', {'id': f'sp-showtime-tab-{date_str}'})

        movie_cards = day_schedule.find_all('div', {'class': 'movie-schedule'})

        for card in movie_cards:
            name_node = card.findNext('a', {'class': 'schedule-movie-name'})
            name = name_node.text

            movie = ScrapedMovie(filmname=name, year=None, poster_link=None)

            link = self.THEATER_BASE_URL + name_node.attrs['href']

            # сеансы
            # залы не указаны, так что пусть будут пустые
            hall_name = ''
            # ищем сеансы в зале
            hall_sessions = card.find_all('li', attrs={'class': 'time-select__item'})
            for hall_session in hall_sessions:
                # вытаскиваем время
                session_time = hall_session.attrs['data-session-time']
                session_time = dt.datetime.strptime(session_time, '%H:%M').time()
                session_datetime = dt.datetime.combine(date, session_time)

                self.raw_sessions.append(
                    ScrapedSession(movie=movie, hall=hall_name, datetime=session_datetime, link=link)
                )


if __name__ == '__main__':
    scraper = KinobelScraper()
    scraper.run(dt.date.today())
    print(scraper)
