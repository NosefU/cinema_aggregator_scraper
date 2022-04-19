from sqlalchemy.exc import IntegrityError

from db.models import Session, MovieSession


class MovieSessionsRepo:
    """
    Репозиторий сеансов
    """
    @staticmethod
    def add_movie_sessions(movie_sessions: list[MovieSession]):
        """
        Добавление фильмов в репозиторий

        :param movie_sessions: список сеансов для добавления
        """
        if not all([isinstance(movie_session, MovieSession) for movie_session in movie_sessions]):
            raise TypeError('В списке должны быть только объекты типа MovieSession')

        with Session() as session:
            for movie_session in movie_sessions:
                # сейвимся вложенной сессией и пытаемся пропихнуть объект в БД.
                # Если натыкаемся на constraint составного ключа (то есть такой сеанс уже есть в БД),
                # то просто идём дальше.
                # Если что-то другое - пробрасываем исключение дальше
                try:
                    with session.begin_nested():
                        session.add(movie_session)
                except IntegrityError as exc:
                    if exc.orig.diag.constraint_name != 'session_unique':
                        raise
            session.commit()
