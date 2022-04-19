from typing import Optional, List

from db.models import Theater, Session


class TheatersRepo:
    """
    Репозиторий кинотеатров
    """

    @staticmethod
    def add_theaters(theaters: list[Theater]):
        """
        Добавление кинотеатров в репозиторий

        :param theaters: список сеансов для добавления
        """
        if not all([isinstance(theater, Theater) for theater in theaters]):
            raise TypeError('В списке должны быть только объекты типа Theater')

        with Session() as session:
            session.bulk_save_objects(theaters)
            session.commit()

    @staticmethod
    def get_theater_by_id(idx: int) -> Optional[Theater]:
        """
        Поиск кинотеатра по id

        :param idx: id кинотеатра
        :return: Найденный кинотеатр, либо None
        """
        with Session() as session:
            movie = session.get(Theater, idx)
        return movie

    @staticmethod
    def get_theaters_by_city(city: str) -> Optional[List[Theater]]:
        """
        Выборка кинотеатров по городу

        :param city: Город
        :return: Список найденных кинотеатров, либо None
        """
        with Session() as session:
            results = session.query(Theater).filter(Theater.city == city).all()
        return results
