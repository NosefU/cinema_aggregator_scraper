from typing import TYPE_CHECKING

from scrapers.cinema_star_scraper import CinemaStarScraper
from scrapers.kinobel_scraper import KinobelScraper

if TYPE_CHECKING:
    from db.models import Theater
from scrapers.rusich_scraper import RusichScraper
from scrapers.sputnik_cinema_scraper import SputnikScraper

SCRAPERS = {
    'rusich31': RusichScraper,
    'sputnik_cinema31': SputnikScraper,
    'cinema_star': CinemaStarScraper,
    'kinobel': KinobelScraper
}


def scraper_factory(theater: 'Theater'):
    scraper = SCRAPERS.get(theater.scraper)
    if not scraper:
        return None
    return scraper(theater.scraper_config)
