import datetime as dt
from pprint import pprint

from engine import ScrapingEngine
from models import Theater
from repos import fed_movies_repo_factory, theaters_repo_factory, sessions_repo_factory
from scrapers import scraper_factory
from scrapers.rusich_scraper import RusichScraper

THEATERS = [
    Theater(id=1,
            name='Русич',
            city='Белгород',
            address='пр. Ватутина, 8',
            scraper=RusichScraper
            ),
]

if __name__ == '__main__':
    theaters_repo = theaters_repo_factory()
    theaters = theaters_repo.get_theaters_by_city('Белгород')
    theaters = [scraper_factory(theater) for theater in theaters]

    fed_movies_db = fed_movies_repo_factory()
    sessions_repo = sessions_repo_factory()
    date = dt.date.today() + dt.timedelta(hours=24)
    engine = ScrapingEngine(theaters=THEATERS, fed_movies_repo=fed_movies_db, sessions_repo=sessions_repo)
    engine.run(date)
