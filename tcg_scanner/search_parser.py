"""Parsing and validation of the user's search-query string."""

import re
from dataclasses import dataclass

# Matches e.g. "charizard ex #105/112 nm p5". Name is greedy up to "#<number>",
# followed by an optional condition word, followed by an optional "p<N>"/"pg<N>"/"page<N>".
SEARCH_PATTERN = re.compile(
    r"(.+)\s+#([\w/]+)(?:\s+(?!p(?:age)?\d*|pg\d*)(\w+))?(?:\s+(?:p|pg|page)\s*(\d+))?\s*$",
    re.IGNORECASE,
)

CONDITIONS = {
    "nm": "Near Mint",
    "lp": "Lightly Played",
    "mp": "Moderately Played",
    "hp": "Heavily Played",
    "d": "Damaged",
}
UNSPECIFIED_CONDITION = "unspecified"


@dataclass(frozen=True)
class SearchQuery:
    name: str
    number: str
    condition: str
    pages: int


def parse_searchterm(search: str, default_pages: int) -> SearchQuery:
    """Parse a query like 'charizard ex #105/112 nm p4' into its parts.

    Raises ValueError if the string doesn't match the expected format, or names
    an unrecognized condition.
    """
    match = SEARCH_PATTERN.match(search.strip())
    if not match:
        raise ValueError("Search term must be in a format like 'charizard ex #105/112 nm p4'")

    name, number, condition, pages = match.groups()
    condition = condition.lower() if condition else UNSPECIFIED_CONDITION
    if condition != UNSPECIFIED_CONDITION and condition not in CONDITIONS:
        valid = ", ".join(sorted(CONDITIONS))
        raise ValueError(f"Unrecognized condition '{condition}'. Must be one of: {valid}")

    return SearchQuery(
        name=name.strip(),
        number=number.strip().upper(),
        condition=condition,
        pages=int(pages) if pages else default_pages,
    )
