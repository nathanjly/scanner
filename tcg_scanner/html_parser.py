"""Pure HTML parsing logic (BeautifulSoup only, no browser dependency)."""

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# TCGPlayer serves these exact placeholder values (instead of a real row) when a
# product/condition doesn't have enough recent sales history to show.
PLACEHOLDER_DATE = "12/12/12"

_NEXT_PAGE_LINK_CLASS = (
    "is-active router-link-exact-active tcg-button tcg-button--md "
    "tcg-standard-button tcg-standard-button--flat"
)


@dataclass(frozen=True)
class Product:
    name: str
    set_name: str
    product_id: str
    url: str
    market_price: str


@dataclass(frozen=True)
class Sale:
    price: str
    date: str
    quantity: str
    condition: str


def get_product_links(html: str, number: str, page: int, *, ignore_jumbo_cards: bool) -> list[Product]:
    """Extract products on a search-results page whose ID contains `number`."""
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.find("section", class_="search-results")
    if search_results is None:
        logger.warning("Could not find search-results section on page %d; page markup may have changed", page)
        return []

    products = []
    for card in search_results.find_all("div", class_="product-card"):
        product_id = next(
            (span.text.strip() for span in card.find_all("span") if span.text.startswith("#")),
            None,
        )
        if not product_id or number not in product_id:
            continue

        set_elem = card.find("h4", class_="product-card__set-name")
        set_name = set_elem.text.strip() if set_elem else "Unknown Set"
        if ignore_jumbo_cards and "Jumbo Cards" in set_name:
            continue

        link = card.find("a", href=True)
        if not link:
            continue

        name_elem = card.find("span", class_="product-card__title truncate")
        market_price_elem = card.find("span", class_="product-card__market-price--value")

        products.append(
            Product(
                name=name_elem.text.strip() if name_elem else "Unknown Product",
                set_name=set_name,
                product_id=product_id,
                url=link["href"],
                market_price=market_price_elem.text.strip() if market_price_elem else "N/A",
            )
        )
        logger.info("Found matching product on page %d", page)

    return products


def has_next_page(html: str, current_page: int) -> bool:
    """Check whether a page number greater than `current_page` is available."""
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.find("div", class_="tcg-pagination__pages")
    if pagination is None:
        return False

    has_more = any(
        int(link.text.strip()) > current_page
        for link in pagination.find_all("a", class_=_NEXT_PAGE_LINK_CLASS)
        if link.text.strip().isdigit()
    )
    if not has_more:
        logger.info("No page %d found", current_page + 1)
    return has_more


def parse_data(html: str) -> list[Sale]:
    """Extract sale rows from a product's 'latest sales' table."""
    soup = BeautifulSoup(html, "html.parser")
    sales_table = soup.find("tbody", class_="latest-sales-table__tbody")
    if sales_table is None:
        logger.warning("Could not find latest-sales-table__tbody; page markup may have changed")
        return []

    sales = []
    for sale in sales_table.find_all("tr"):
        price_td = sale.find("td", class_="latest-sales-table__tbody__price")
        date_td = sale.find("td", class_="latest-sales-table__tbody__date")
        # Site markup really does use a single underscore here, unlike the other cells.
        quantity_td = sale.find("td", class_="latest-sales-table__tbody_quantity")

        # The condition tooltip's target div has children, so grab only its direct text node.
        toggle = sale.select_one(".tcg-tooltip__toggle, .tcg-tooltiptoggle")
        condition_text_node = toggle.find(string=True, recursive=False) if toggle else None

        sales.append(
            Sale(
                price=price_td.text.strip() if price_td else "N/A",
                date=date_td.text.strip() if date_td else "N/A",
                quantity=quantity_td.text.strip() if quantity_td else "N/A",
                condition=condition_text_node.strip() if condition_text_node else "N/A",
            )
        )

    return sales


def is_placeholder_data(sales: list[Sale]) -> bool:
    """True if every row is TCGPlayer's 'not enough sales history' placeholder."""
    return bool(sales) and all(sale.date == PLACEHOLDER_DATE for sale in sales)
