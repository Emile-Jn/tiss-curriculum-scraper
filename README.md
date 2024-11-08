# Tiss curriculum scraper
A simple python script to scrape the Tiss [page](https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?dswid=3632&dsrid=908&key=67853) 
of the Data Science master's curriculum and extract a table in which each row is a course.

To obtain a fresh version of `curriculum.tsv`, simply run `scraper.py`.

Thanks to [Daniel](https://github.com/dblasko) for setting up Github Actions in `.github/workflows` so that the curriculum is updated every day at midnight and can be manually updated with one click.
