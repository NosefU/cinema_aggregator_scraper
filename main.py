import datetime as dt

from engine import ScrapingEngine
from repos import fed_movies_repo, theaters_repo, movie_sessions_repo


if __name__ == '__main__':
    theaters_repo = theaters_repo.TheatersRepo()
    theaters = theaters_repo.get_theaters_by_city('Белгород')

    fed_movies_db = fed_movies_repo.FedMoviesRepo()
    sessions_repo = movie_sessions_repo.MovieSessionsRepo()
    scraping_engine = ScrapingEngine(theaters=theaters, fed_movies_repo=fed_movies_db, sessions_repo=sessions_repo)

    date = dt.date.today() + dt.timedelta(hours=24)
    scraping_engine.run(date)
