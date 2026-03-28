# Tiss curriculum scraper
A small Python project to scrape the TISS [page](https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?dswid=3632&dsrid=908&key=67853)
of the Data Science master's curriculum and extract a table in which each row is a course.

Thanks to [Daniel](https://github.com/dblasko) for setting up Github Actions in `.github/workflows` so that the curriculum is automatically 
updated every night around 2am and can be manually updated with one click.

If you want a more recent version of the curriculum than the one obtained from the last automatic update, you can run 
the workflow by going to GitHub Actions -> Update curriculum.tsv -> Run workflow.

Some of the scraping code is inspired by the work of [Claus Kovacs](https://github.com/clauskovacs) in the repo
[higgsAT/tiss-crawler](https://github.com/higgsAT/tiss-crawler).

## Files
- `tiss_curriculum_scraper/`: package containing the scraping, formatting, storage, and CLI logic.
- `scraper.py`: compatibility wrapper and CLI entry point.
- `table_formatting.py`: compatibility wrapper for formatting helpers.
- `curriculum.tsv`: The resulting curriculum in tab-separated format.
- `logs.tsv`: A record of all (automatic) modifications to `curriculum.tsv`.

## Development

Install dependencies with `uv`:

```bash
uv sync --extra dev
```

Run the scraper:

```bash
uv run tiss-curriculum-scraper
```

Run tests:

```bash
uv run pytest
```
