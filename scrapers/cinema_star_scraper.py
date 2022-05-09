import datetime as dt
import re
import time

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from scrapers.abstract_scraper import AbstractScraper
from scrapers.exceptions import BaseScraperException
from scrapers.models import ScrapedMovie, ScrapedSession


class CinemaStarScraper(AbstractScraper):

    NAME = 'cinema_star'
    THEATER_BASE_URL = 'https://cinemastar.ru/'

    def get_html(self, date: dt.date) -> str:
        """
        Получаем HTML страницы с расписанием

        :param date: дата, за которую открываем расписание
        :return: HTML-код страницы с расписанием
        """
        self.config = dict(theater_path='cinema/belgorod/')
        driver = uc.Chrome()

        # обходим защиту от ботов
        driver.set_page_load_timeout(5)
        try:
            driver.get(self.THEATER_BASE_URL + self.config['theater_path'])
            time.sleep(10)
        except TimeoutException:
            driver.execute_script("window.stop();")
        if 'Синема Стар' not in driver.title:
            raise BaseScraperException(f'{self.__class__.__name__}: Page not loaded. Got: {driver.title}')

        # переходим на страницу с сеансами в выбранном кинотеатре
        # TODO Сделать проверку месяца - в конце месяца на дейтпикере придётся кликать "Следующий месяц"
        try:
            datepicker_button = driver.find_element(by=By.ID, value='select_date_btn')
            datepicker_button.click()
            time.sleep(0.5)  # задержка на открытие дейтпикера
            calendar_date_cell = driver.find_element(
                by=By.XPATH,
                value=f'//td[@data-month="{date.month - 1}" and @data-year="{date.year}"]'
                      f'/a[text() = "{date.day}"]'
                      f'/parent::td')
            calendar_date_cell.click()
        except NoSuchElementException as exc:
            raise BaseScraperException(
                f'{self.__class__.__name__}: Page layout was changed. Check your scraper', exc)

        time.sleep(1.5)  # задержка на прогрузку расписания через js
        html = driver.page_source
        driver.close()
        return html

    def run(self, date: dt.date) -> None:
        html = self.get_html(date)
        html_doc = BeautifulSoup(html, features='html.parser')

        schedule_node = html_doc.find('div', {'id': 'selected_date_tab'})
        movie_cards = schedule_node.find_all('div', {'class': 'movie'})
        for card in movie_cards:
            name_genre_node = card.findNext('div', {'class': 'title'})
            name_node = name_genre_node.findNext('a')
            name = name_node.text

            images_node = card.find('div', {'class': 'poster small'})
            poster_node = images_node.find('img')
            poster_link = poster_node.attrs['src']
            # https://api.kinohod.ru/c/85x130/bc/55/bc55afe6-c6f2-11ec-86ed-8cc3a0a5f004.jpg
            # api кинохода позволяет задать желаемый размер постера
            # воспользуемся этим и зададим размер 275x391
            poster_link = re.sub(r'(/)(\d{,3}x\d{,3})(/)', r'\g<1>275x391\g<3>', poster_link)

            movie = ScrapedMovie(filmname=name, year=None, poster_link=poster_link)

            # сеансы
            # залы не указаны, так что пусть будут пустые
            hall_name = ''
            # ищем сеансы в зале
            hall_sessions = card.find_all('a', attrs={'class': 'show'})
            for hall_session in hall_sessions:
                # вытаскиваем время
                session_time = hall_session.attrs['data-time']
                session_time = dt.datetime.strptime(session_time, '%H:%M').time()
                session_datetime = dt.datetime.combine(date, session_time)

                # вытаскиваем инфу для ссылки и формируем ссылку на киноход
                kh_widget = hall_session.attrs['kh:widget']
                kh_id = hall_session.attrs['kh:id']
                link = f'https://kinohod.ru/?kinohod=widget:{kh_widget},id:{kh_id}'

                self.raw_sessions.append(
                    ScrapedSession(movie=movie, hall=hall_name, datetime=session_datetime, link=link)
                )


if __name__ == '__main__':
    scraper = CinemaStarScraper()
    scraper.run(dt.date.today())
    print(scraper)
