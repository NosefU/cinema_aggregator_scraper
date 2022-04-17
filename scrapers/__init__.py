from models import Theater
from scrapers.rusich_scraper import RusichScraper

SCRAPERS = {
    'rusich31': RusichScraper
}


def scraper_factory(theater: Theater):
    theater.scraper = SCRAPERS.get(theater.scraper)
    return theater
