# Architecture notes

A quick-reference for explaining this project out loud. Not user-facing docs (see README.md for that).

## Pitch

A CLI tool that scrapes TCGPlayer for a card's recent sale prices — useful at card shows for
quick price checks. Drives a headless browser to handle the site's JS-rendered content, then
parses and displays the sales history.

## Data flow

```
user input string
      |
      v
search_parser.py   parse_searchterm()   ->  SearchQuery (name, number, condition, pages)
      |
      v
browser.py         search_product_pages()  drives headless Chrome to search-results pages
      |                    |
      |                    v
      |            html_parser.py   get_product_links()  ->  list[Product]
      v
cli.py              choose_product()   -> disambiguate if multiple matches
      |
      v
browser.py          load_sales_data()   navigates to product, clicks to reveal sales modal
      |                    |
      |                    v
      |            html_parser.py   parse_data()  ->  list[Sale]
      v
cli.py               print via tabulate
```

## The one idea to lead with

**`html_parser.py` never imports Selenium.** It's pure functions: raw HTML string in, dataclasses
out. `browser.py` is the only module that touches the actual browser. That split is why
`tests/` can unit-test all the parsing logic (regex, BeautifulSoup selectors, the placeholder-data
detection) against static HTML fixtures — no Chrome needed in CI, no flaky network-dependent tests.

## Design decisions worth defending

| Decision | Why |
|---|---|
| Selenium + BeautifulSoup, not `requests` | TCGPlayer's sales data is rendered client-side by JS; a plain HTTP GET never sees it in the response body. Selenium renders it, BS4 parses the resulting HTML. |
| Parsing split from browser I/O | The reason above — it's what makes the code testable without spinning up a browser. |
| Config as a `dataclass` + argparse (`config.py`), not hardcoded globals | Scriptable/testable without editing source; a typed object instead of loose module-level variables. |
| `Product`, `Sale`, `SearchQuery` as dataclasses, not dicts | Typos become dev-time errors instead of `KeyError` at runtime; free `__eq__` is what makes fixture-based test assertions work at all. |

## The debugging story (best interview material)

The scraper started returning **fake-looking data** (`$0.00` prices, `12/12/12` dates) instead of
erroring — a worse failure mode than a crash, because it looks like success.

1. First hypothesis: a race condition, table not fully loaded yet. Tested by dumping the raw table
   HTML at 1s/3s/6s intervals — the placeholder was *stable*, not mid-load. Hypothesis rejected.
2. Compared manual-browser behavior to scraper behavior: manually clicking "View More Data" showed
   real sales; the scraper never did, for the exact same product/condition.
3. Confirmed by checking `navigator.userAgent` from inside the automated session — it literally
   contained `HeadlessChrome`. The site was fingerprinting the automated browser and serving
   poisoned placeholder data to it specifically, rather than blocking outright.
4. Fix: override `--user-agent` to a normal desktop Chrome string.

The arc worth telling: hypothesis → test against evidence → reject → better hypothesis → confirm →
fix. Not "I stared at it until it worked."

## What I'd change at scale

Honest, not defensive:

- `browser.py` still has a couple of fixed `time.sleep()` calls instead of explicit
  `WebDriverWait` conditions — known fragility, left as-is because the effort/risk tradeoff didn't
  justify it for a small personal tool.
- No retry/backoff on network failures — fine for a one-shot interactive CLI, not for a scheduled job.
- Scraping is inherently brittle to markup changes. A production version would want either an
  official API or a small contract test that pings the real site on a schedule to catch breakage early.
