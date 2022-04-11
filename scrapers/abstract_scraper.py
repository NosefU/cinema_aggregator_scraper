from abc import ABC, abstractmethod
from typing import List

from models import ScrapedSession


class AbstractScraper(ABC):
    """
    Абстрактный класс скрапера
    """
    def __init__(self):
        self.raw_sessions: List[ScrapedSession] = []

    @abstractmethod
    def run(self, date_stamp: str) -> None:
        """
        Скрапит со страницы кинотеатра данные о сеансах на определённую дату.
        Складывает найденные сеансы ScrapedSession в список self.sessions

        :param date_stamp: дата, на которую скрапятся данные о сеансах
        """
        pass
