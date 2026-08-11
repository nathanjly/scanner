# TCGPlayer Sales Data Scanner

This program allows you to search for Pokémon cards on TCGPlayer, select the correct product from search results, and view recent sales data for the selected card and condition. Card traders may find this tool useful at card shows.

## Features

- Search for cards by name, number, condition, and pages to search (e.g., "sylveon vmax #075/203 nm p5")
- Select from multiple matching products (with set and market price info)
- View recent sales data (price, date, quantity, condition)
- Outputs sales data in a readable table

## Requirements

- Python 3.8+
- Google Chrome browser

## Installation

1. **Clone or download this repository.**
   - If downloading the zip, be sure to unzip the folder before running.

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the program:**
   ```bash
   python scanner.py
   ```
   - You will be prompted for a card search in the format: "[card name] #[number] [optional:condition] p[optional:pages to search]"
        - Name, number, and condition are case-insensitive.
        - The number argument must include "#", followed immediately by a number like 001/021 or a term like TG05/TG30.
        - Condition keyword is one of the following: nm, lp, mp, hp, d
            - nm = nearly mint, lp = lightly played, mp = moderately played, hp = heavily played, d = damaged
        - The pages keyword argument must include a lowercase "p", followed by # of pages you want to view.
        - You can omit the condition to default viewing any condition.
        - You can omit the pages argument to default to viewing 1 page.

        - Example: Enter card search (or type 'exit' to quit): charizard ex #001/021 lp p5
        - This searches 5 pages for the term "charizard ex", looks for the number "001/021" and in the condition "Lightly Played".
        - A term like "charizard ex #xy17" will also work, searching only the first page, and looking for any condition.

   - The browser will open and load TCGPlayer search results.
   - If multiple products match, you will be prompted in the terminal to select one. 
        - If needed, click away from brower and into terminal, then type the selection.

2. **View Results:**
   - The five most recent sales data will be displayed in the terminal.

## Notes

- The browser runs headless (no visible window); the terminal is the only UI.
- Search results are better if you can specify in the name "ex" or "vmax".

## Configuration

Behavior toggles are CLI flags instead of source edits:

```bash
python scanner.py --max-pages 3 --include-jumbo --exclude-japanese --look-for-multiple
```

Run `python scanner.py --help` for the full list. Defaults: `--max-pages 5`, jumbo cards excluded, Japanese cards included, and search stops at the first matching product.

## Project structure

```
scanner.py              # entry point
tcg_scanner/
  config.py              # CLI flag parsing
  search_parser.py        # parses/validates the search query string
  html_parser.py           # BeautifulSoup parsing (no browser dependency)
  browser.py                # Selenium driver setup and page navigation
  cli.py                     # interactive loop tying it together
tests/                      # pytest unit tests for the pure-logic modules
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

Tests cover query parsing and HTML parsing against static fixtures — no live network or browser calls.

## Troubleshooting

- If you see errors about missing modules, run `pip install -r requirements.txt` again.
- Sometimes a search query will not return a result, even though that card technically exists in TCGplayer. 
      - This is because TCGplayer may move product listings around randomly.
      - As this program checks a specified number of pages, the card of interest may be placed in a deeper page.
      - Rerunning the query can fix this issue.
- If you encounter any bugs or errors, please let me know so I can fix them. Contact: omnirivani@gmail.com

