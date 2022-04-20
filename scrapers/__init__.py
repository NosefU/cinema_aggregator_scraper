from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models import Theater
from scrapers.rusich_scraper import RusichScraper
from scrapers.sputnik_cinema_scraper import SputnikScraper

SCRAPERS = {
    'rusich31': RusichScraper,
    'sputnik_cinema31': SputnikScraper
}


def scraper_factory(theater: 'Theater'):
    scraper = SCRAPERS.get(theater.scraper)
    if not scraper:
        return None
    return scraper(theater.scraper_config)
