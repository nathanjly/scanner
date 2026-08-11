"""Runtime configuration, sourced from CLI flags instead of hardcoded globals."""

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    look_for_multiple_products: bool
    max_pages: int
    ignore_jumbo_cards: bool
    include_japanese_cards: bool


def parse_args(argv: list[str] | None = None) -> Config:
    parser = argparse.ArgumentParser(
        description="Search TCGPlayer for a card and display its recent sales data."
    )
    parser.add_argument(
        "--look-for-multiple",
        action="store_true",
        help="Keep searching through --max-pages even after a match is found, "
        "to surface all matching products instead of just the first.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Default number of search-result pages to check when a query doesn't specify 'p<N>' (default: 5).",
    )
    parser.add_argument(
        "--include-jumbo",
        action="store_true",
        help="Include jumbo card listings in search results (excluded by default).",
    )
    parser.add_argument(
        "--exclude-japanese",
        action="store_true",
        help="Exclude Japanese card listings from search results (included by default).",
    )
    args = parser.parse_args(argv)

    return Config(
        look_for_multiple_products=args.look_for_multiple,
        max_pages=args.max_pages,
        ignore_jumbo_cards=not args.include_jumbo,
        include_japanese_cards=not args.exclude_japanese,
    )
