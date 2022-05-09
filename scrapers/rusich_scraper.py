import datetime as dt
import time

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

from scrapers.models import ScrapedMovie, ScrapedSession
from scrapers.abstract_scraper import AbstractScraper
from scrapers.exceptions import BaseScraperException


class RusichScraper(AbstractScraper):
    NAME = 'rusich31'
    THEATER_BASE_URL = 'https://kinorusich.ru'
    SCHEDULE_URL = THEATER_BASE_URL + '/h/schedule/'

    def run(self, date: dt.date):
        # получаем таймстамп, ибо так хочет сайт
        datetime = dt.datetime.combine(date, dt.datetime.min.time())
        timestamp = int(datetime.timestamp())

        payload = f'?d={timestamp}'
        driver = uc.Chrome()

        # обходим защиту от ботов
        driver.set_page_load_timeout(5)
        try:
            driver.get(self.SCHEDULE_URL + payload)
            time.sleep(10)
        except TimeoutException:
            driver.execute_script("window.stop();")
        if 'Расписание' not in driver.title:
            raise BaseScraperException(f'{self.__class__.__name__}: Page not loaded. Got: {driver.title}')
        html = driver.page_source
        driver.close()

        html_doc = BeautifulSoup(html, features='html.parser')

        movie_cards = html_doc.find_all('article', {'class': 'movie-info-item'})
        for card in movie_cards:
            name_tag = card.findNext('a', {'class': 'movie-info-name'})
            name = name_tag.text

            link = self.SCHEDULE_URL + name_tag.attrs['href']

            year_tag = card.findNext('span', text='Год', attrs={'class': 'movie-info-label'})
            year_str = year_tag.parent.contents[1]
            year = year_str.replace(' – ', '')
            year = int(year) if year else None

            poster_tag = card.findNext('div', attrs={'class': 'movie-info-img'}).findNext('img')
            poster_link = self.THEATER_BASE_URL + poster_tag.attrs['src']

            movie = ScrapedMovie(filmname=name, year=year, poster_link=poster_link)

            # сеансы
            # ищем залы
            halls = card.find_all('div', attrs={'class': 'cinema-block-hall-item'})
            for hall in halls:
                hall_name = hall.findNext('div', attrs={'class': 'cinema-block-hall-number'}).text.strip()

                # ищем сеансы в зале
                hall_sessions = hall.find_all('div', attrs={'class': 'cinema-block-hall-time'})
                for hall_session in hall_sessions:
                    session_time = hall_session.contents[0].strip()
                    if session_time == 'Все сеансы на сегодня завершены':
                        break
                    session_time = dt.datetime.strptime(session_time, '%H:%M').time()
                    session_datetime = dt.datetime.combine(date, session_time)
                    self.raw_sessions.append(
                        ScrapedSession(movie=movie, hall=hall_name, datetime=session_datetime, link=link)
                    )
