from tcg_scanner.html_parser import Product, Sale, get_product_links, has_next_page, is_placeholder_data, parse_data

SEARCH_RESULTS_HTML = """
<section class="search-results">
  <div class="product-card">
    <span>#001/021</span>
    <span class="product-card__title truncate">Charizard EX</span>
    <h4 class="product-card__set-name">XYA: M Charizard-EX Mega Battle Deck</h4>
    <span class="product-card__market-price--value">$12.40</span>
    <a href="/product/605092/charizard-ex">link</a>
  </div>
  <div class="product-card">
    <span>#001/021</span>
    <span class="product-card__title truncate">Charizard EX (Jumbo)</span>
    <h4 class="product-card__set-name">Jumbo Cards Promo</h4>
    <span class="product-card__market-price--value">$5.00</span>
    <a href="/product/999999/charizard-ex-jumbo">link</a>
  </div>
</section>
"""

PAGINATION_HTML = """
<div class="tcg-pagination__pages">
  <a class="is-active router-link-exact-active tcg-button tcg-button--md tcg-standard-button tcg-standard-button--flat">3</a>
</div>
"""

# Real markup captured from TCGPlayer's "no real sales history" placeholder response.
PLACEHOLDER_SALES_HTML = """
<tbody class="latest-sales-table__tbody">
  <tr>
    <td class="latest-sales-table__tbody__date">12/12/12</td>
    <td class="latest-sales-table__tbody__condition"><div class="tcg-tooltip__toggle">LP Foil</div></td>
    <td class="latest-sales-table__tbody_quantity">3</td>
    <td class="latest-sales-table__tbody__price">$0.00</td>
  </tr>
  <tr>
    <td class="latest-sales-table__tbody__date">12/12/12</td>
    <td class="latest-sales-table__tbody__condition"><div class="tcg-tooltip__toggle">MP</div></td>
    <td class="latest-sales-table__tbody_quantity">1</td>
    <td class="latest-sales-table__tbody__price">$0.00</td>
  </tr>
</tbody>
"""

REAL_SALES_HTML = """
<tbody class="latest-sales-table__tbody">
  <tr>
    <td class="latest-sales-table__tbody__date">8/9/26</td>
    <td class="latest-sales-table__tbody__condition"><div class="tcg-tooltip__toggle">NM</div></td>
    <td class="latest-sales-table__tbody_quantity">1</td>
    <td class="latest-sales-table__tbody__price">$14.25</td>
  </tr>
</tbody>
"""


def test_get_product_links_matches_and_filters_jumbo():
    products = get_product_links(SEARCH_RESULTS_HTML, "001/021", page=1, ignore_jumbo_cards=True)
    assert products == [
        Product(
            name="Charizard EX",
            set_name="XYA: M Charizard-EX Mega Battle Deck",
            product_id="#001/021",
            url="/product/605092/charizard-ex",
            market_price="$12.40",
        )
    ]


def test_get_product_links_includes_jumbo_when_not_ignored():
    products = get_product_links(SEARCH_RESULTS_HTML, "001/021", page=1, ignore_jumbo_cards=False)
    assert len(products) == 2


def test_get_product_links_no_match_returns_empty():
    assert get_product_links(SEARCH_RESULTS_HTML, "999/999", page=1, ignore_jumbo_cards=True) == []


def test_get_product_links_missing_search_results_section_returns_empty():
    assert get_product_links("<div>not a results page</div>", "001/021", page=1, ignore_jumbo_cards=True) == []


def test_has_next_page_true_when_higher_page_exists():
    assert has_next_page(PAGINATION_HTML, current_page=1) is True


def test_has_next_page_false_on_last_page():
    assert has_next_page(PAGINATION_HTML, current_page=3) is False


def test_has_next_page_missing_pagination_returns_false():
    assert has_next_page("<div>no pagination here</div>", current_page=1) is False


def test_parse_data_extracts_rows():
    sales = parse_data(REAL_SALES_HTML)
    assert sales == [Sale(price="$14.25", date="8/9/26", quantity="1", condition="NM")]


def test_parse_data_missing_table_returns_empty():
    assert parse_data("<div>no table here</div>") == []


def test_is_placeholder_data_true_for_all_placeholder_rows():
    assert is_placeholder_data(parse_data(PLACEHOLDER_SALES_HTML)) is True


def test_is_placeholder_data_false_for_real_rows():
    assert is_placeholder_data(parse_data(REAL_SALES_HTML)) is False


def test_is_placeholder_data_false_for_empty():
    assert is_placeholder_data([]) is False
