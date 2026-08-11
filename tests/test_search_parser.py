import pytest

from tcg_scanner.search_parser import SearchQuery, parse_searchterm


def test_full_query():
    query = parse_searchterm("charizard ex #105/112 nm p5", default_pages=1)
    assert query == SearchQuery(name="charizard ex", number="105/112", condition="nm", pages=5)


def test_defaults_condition_and_pages_when_omitted():
    query = parse_searchterm("charizard ex #xy17", default_pages=3)
    assert query.condition == "unspecified"
    assert query.pages == 3


def test_condition_without_explicit_page():
    query = parse_searchterm("sylveon vmax #075/203 lp", default_pages=2)
    assert query.condition == "lp"
    assert query.pages == 2


def test_case_insensitive_and_whitespace_tolerant():
    query = parse_searchterm("  Charizard EX   #001/021   LP   P5  ", default_pages=1)
    assert query.number == "001/021"
    assert query.condition == "lp"
    assert query.pages == 5


def test_missing_number_raises():
    with pytest.raises(ValueError):
        parse_searchterm("charizard ex", default_pages=1)


def test_unrecognized_condition_raises():
    with pytest.raises(ValueError, match="Unrecognized condition"):
        parse_searchterm("charizard ex #001/021 zz", default_pages=1)
