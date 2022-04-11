import datetime as dt
from pprint import pprint

from engine import ScrapingEngine
from models import Theater
from repos import fed_movies_repo_factory
from scrapers.rusich_scraper import RusichScraper

THEATERS = [
    Theater(id=1,
            name='Русич',
            city='Белгород',
            address='пр. Ватутина, 8',
            timezone='+3',
            scraper=RusichScraper
            ),
]

if __name__ == '__main__':
    fed_movies_db = fed_movies_repo_factory()
    date = dt.date.today() + dt.timedelta(hours=24)
    engine = ScrapingEngine(theaters=THEATERS, fed_movies_repo=fed_movies_db)
    engine.run(date)

    pprint(engine.sessions)
