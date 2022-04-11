from abc import ABC, abstractmethod
import datetime as dt
from typing import List

from models import ScrapedSession


class AbstractScraper(ABC):
    """
    Абстрактный класс скрапера
    """
    def __init__(self):
        self.raw_sessions: List[ScrapedSession] = []

    @abstractmethod
    def run(self, date: dt.date) -> None:
        """
        Скрапит со страницы кинотеатра данные о сеансах на определённую дату.
        Складывает найденные сеансы ScrapedSession в список self.sessions

        :param date: дата, на которую скрапятся данные о сеансах
        """
        pass
