# GAO Scraper

## Purpose

The [US Government Accountability Office](https://gao.gov) publishes reports on a range of topics. This scraper pulls the metadata of published reports for a given date range.

Note that it doesn't not download the actual PDF files, but links are provided in the data.

## Usage

```python
poetry install
poetry run scrape -h
```