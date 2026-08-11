from tcg_scanner.cli import choose_product, format_product_url
from tcg_scanner.html_parser import Product


def test_format_product_url_unspecified_condition():
    url = format_product_url("/product/605092/charizard-ex", "unspecified")
    assert url == "https://www.tcgplayer.com/product/605092/charizard-ex"


def test_format_product_url_with_condition():
    url = format_product_url("/product/605092/charizard-ex", "lp")
    assert url == "https://www.tcgplayer.com/product/605092/charizard-ex&Condition=Lightly+Played"


def test_choose_product_single_match_returns_without_prompting():
    product = Product(name="Charizard EX", set_name="Base Set", product_id="#001/021", url="/x", market_price="$1")
    result, index = choose_product([product])
    assert result is product
    assert index == 0
