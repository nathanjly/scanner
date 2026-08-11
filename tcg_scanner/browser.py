"""Selenium driver setup and page navigation."""

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tcg_scanner.config import Config
from tcg_scanner.html_parser import Product, Sale, get_product_links, has_next_page, parse_data

logger = logging.getLogger(__name__)

CHROME_BINARY = "/usr/bin/google-chrome"
# Headless Chrome's default UA advertises "HeadlessChrome", which TCGPlayer uses to
# detect scrapers and serve poisoned placeholder sales data instead of blocking outright.
DESKTOP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)


class SalesDataUnavailable(Exception):
    """Raised when the sales table for a product/condition can't be loaded."""


def build_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-agent={DESKTOP_USER_AGENT}")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=chrome_options)


def _search_url(name: str, page: int, *, include_japanese_cards: bool) -> str:
    query = name.replace(" ", "+")
    if include_japanese_cards:
        return f"https://www.tcgplayer.com/search/all/product?&q={query}&page={page}"
    return f"https://www.tcgplayer.com/search/pokemon/productLineName=pokemon&q={query}&page={page}"


def search_product_pages(driver: webdriver.Chrome, name: str, number: str, config: Config) -> list[Product]:
    """Search result pages for products whose ID contains `number`."""
    products: list[Product] = []
    page = 1
    while page <= config.max_pages:
        logger.info("Checking page %d...", page)
        driver.get(_search_url(name, page, include_japanese_cards=config.include_japanese_cards))

        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results")))
        except TimeoutException:
            logger.warning("Timed out while looking for products on page %d", page)

        html = driver.page_source
        products.extend(get_product_links(html, number, page, ignore_jumbo_cards=config.ignore_jumbo_cards))

        if not config.look_for_multiple_products and products:
            break
        if not has_next_page(html, page):
            break
        page += 1

    return products


def load_sales_data(driver: webdriver.Chrome, product_url: str) -> tuple[list[Sale], bool]:
    """Navigate to a product page and extract its recent-sales table.

    Returns (sales, condition_filter_failed) -- the latter is True if the requested
    condition had no sales and TCGPlayer fell back to showing unfiltered results.
    Raises SalesDataUnavailable if the page doesn't load the expected elements.
    """
    driver.get(product_url)

    try:
        view_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "modal__activator"))
        )
    except TimeoutException:
        raise SalesDataUnavailable("Timed out waiting for data to load. Please try again.")

    time.sleep(1)  # let the condition-filter result (or "no results") banner settle
    condition_filter_failed = bool(driver.find_elements(By.CLASS_NAME, "no-result__heading"))

    view_more_button.click()
    time.sleep(1)  # let the sales table populate after the click

    try:
        table_elem = driver.find_element(By.CLASS_NAME, "latest-sales-table__tbody")
    except NoSuchElementException:
        raise SalesDataUnavailable("Sales data table did not load. Please try again.")

    return parse_data(table_elem.get_attribute("outerHTML")), condition_filter_failed
