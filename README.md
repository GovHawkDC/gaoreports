# GAO Scraper

## Purpose

The [US Government Accountability Office](https://gao.gov) publishes reports on a range of topics. This scraper pulls the metadata of published reports for a given date range.

Note that it doesn't not download the actual PDF files, but links are provided in the data.

## Data files

This scraper will (hopefully!) run nightly as a github action, and automatically commit any newly found data to the data/ directory.

Backdata will be added to the repository as time allows

The JSON files are of a fair simple format, here's an example:

```json 
{
    "gao_id": "GAO-23-106585",
    "published": "2023-06-30T12:00:00Z",
    "released": "2023-06-30T08:00:00Z",
    "summary": "In FY 2022, federal agencies made an estimated $247 billion in payment errors\u2014payments that either should not have been made or that were made in the incorrect amount. But some agencies have made progress reducing the number of such errors in their programs. This report\u2014the second in a series of quarterly reports\u2014examines how these agencies worked to reduce payment errors. Some agencies improved the accountability...",
    "title": "Improper Payments: Programs Reporting Reductions Had Taken Corrective Actions That Shared Common Features",
    "topics": [
        "Chief financial officers",
        "Veterans affairs",
        "Auditing and Financial Management",
        "Compliance oversight",
        "Medicare",
        "Beneficiaries",
        "Agency evaluations",
        "Lessons learned",
        "Payment errors",
        "Improper payments",
        "Internal controls"
    ],
    "type": "reports-testimonies",
    "url": "https://www.gao.gov/products/gao-23-106585",
    "versions": [
        {
            "title": "Highlights Page (2 pages)",
            "url": "https://www.gao.gov/assets/gao-23-106585-highlights.pdf"
        },
        {
            "title": "Full Report (28 pages)",
            "url": "https://www.gao.gov/assets/gao-23-106585.pdf"
        },
        {
            "title": "Accessible PDF (30 pages)",
            "url": "https://www.gao.gov/assets/830/827115.pdf"
        }
    ]
}
```

## Manual Usage

The scraper can be run manually with:

```python
poetry install
poetry run scrape -h
```