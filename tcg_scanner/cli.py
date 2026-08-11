"""Interactive command-line loop: prompts the user, drives the browser, prints results."""

import logging
import time

from tabulate import tabulate

from tcg_scanner.browser import SalesDataUnavailable, build_driver, load_sales_data, search_product_pages
from tcg_scanner.config import Config, parse_args
from tcg_scanner.html_parser import Product, Sale, is_placeholder_data
from tcg_scanner.search_parser import CONDITIONS, UNSPECIFIED_CONDITION, parse_searchterm

logger = logging.getLogger(__name__)


def choose_product(products: list[Product]) -> tuple[Product, int]:
    """Prompt the user to pick a product if more than one matched."""
    if len(products) == 1:
        return products[0], 0

    print("\nMultiple products found with same number:")
    for idx, product in enumerate(products):
        print(
            f"{idx + 1}: {product.name} | Set: {product.set_name} | "
            f"Market Price: {product.market_price} | ID: {product.product_id}"
        )

    while True:
        try:
            choice = int(input("Select product number to lookup: ")) - 1
        except ValueError:
            print("Please enter a valid number.")
            continue
        if 0 <= choice < len(products):
            return products[choice], choice
        print("Invalid selection. Try again.")


def format_product_url(product_url: str, condition: str) -> str:
    """Append the TCGPlayer condition-filter query param, if a specific condition was requested."""
    base = "https://www.tcgplayer.com" + product_url
    if condition == UNSPECIFIED_CONDITION:
        return base
    return f"{base}&Condition={CONDITIONS[condition].replace(' ', '+')}"


def _print_loading_message(msg: str) -> None:
    print(msg, end="", flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print()


def _print_sales_table(sales: list[Sale]) -> None:
    rows = [{"Price": s.price, "Date": s.date, "Quantity": s.quantity, "Condition": s.condition} for s in sales]
    print(tabulate(rows, headers="keys", tablefmt="pretty"))


def _run(driver, config: Config) -> None:
    while True:
        search = input("\nEnter card search (or type 'exit' to quit): ")
        if search.strip().lower() == "exit":
            print("Exiting...")
            return

        try:
            query = parse_searchterm(search, config.max_pages)
        except ValueError as e:
            print(e)
            continue

        print(
            f"Searching for: name='{query.name}', number='{query.number}', "
            f"condition='{query.condition}', pages to search={query.pages}"
        )

        products = search_product_pages(driver, query.name, query.number, config)
        if not products:
            print(
                f"Could not find that product within {query.pages} pages. "
                "Retry your query or increase --max-pages.\n"
            )
            continue

        product, _ = choose_product(products)
        product_url = format_product_url(product.url, query.condition)

        _print_loading_message("Loading product data")
        try:
            sales, condition_filter_failed = load_sales_data(driver, product_url)
        except SalesDataUnavailable as e:
            print(e)
            continue

        display_condition = UNSPECIFIED_CONDITION if condition_filter_failed else query.condition
        if condition_filter_failed:
            print(
                f"***No search results found for condition: '{query.condition}'. "
                "Now displaying recent 5 sales without condition filter.***"
            )

        print(f"\nSales Data for: {product.name} #{query.number}, condition: {display_condition}")
        print(f"Market Price: {product.market_price}")
        if is_placeholder_data(sales):
            print("No real recent sales data available for this product/condition.")
            continue

        _print_sales_table(sales)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    config = parse_args()
    driver = build_driver()
    try:
        _run(driver, config)
    finally:
        driver.quit()
