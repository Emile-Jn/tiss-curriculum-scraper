# Tiss curriculum scraper
A simple python script to scrape the Tiss [page](https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?dswid=3632&dsrid=908&key=67853) 
of the Data Science master's curriculum and extract a table in which each row is a course.

Thanks to [Daniel](https://github.com/dblasko) for setting up Github Actions in `.github/workflows` so that the curriculum is automatically 
updated every night around 2am and can be manually updated with one click.

If you want a more recent version of the curriculum than the one obtained from the last automatic update, you can run 
the workflow by going to GitHub Actions -> Update curriculum.tsv -> Run workflow.

Some of the scraping code is inspired by the work of [Claus Kovacs](https://github.com/clauskovacs) in the repo
[higgsAT/tiss-crawler](https://github.com/higgsAT/tiss-crawler).

## Files
- `scraper.py`: The python script that scrapes the data science curriculum page and the transferable skills catalogue 
on Tiss and extracts the courses as a table.
- `table_formatting.py`: helper functions to clean the raw output of the scraping.
- `curriculum.tsv`: The resulting curriculum in tab-separated format.
- `logs.tsv`: A record of all (automatic) modifications to `curriculum.tsv`.
