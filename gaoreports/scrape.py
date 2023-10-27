import argparse
import datetime
import json
import logging
import lxml.html
import os
import re
import requests

logging.basicConfig(level=logging.INFO)


def clean_id(id: str) -> str:
    # NSIAD/AIMD-00-329 is nsiadaimd-00-329
    return id.replace("/", "")


def process_item(item: lxml.html.HtmlElement) -> None:
    link = item.xpath(".//h4[contains(@class,'c-search-result__header')]/a")[0]
    title = link.xpath("text()")[0]
    title = re.sub(r"\s+", " ", title)
    url = link.xpath("@href")[0]

    gao_id = item.xpath(".//span[contains(@class, 'd-block')]/text()")[0].strip()

    # some items have an empty d-block, e.g. d25791
    if gao_id == "":
        gao_id = re.findall(f"gao\.gov/products/(.*)", url, flags=re.IGNORECASE)[0]

    if gao_id == "":
        logging.error("Unable to fetch GAO ID.")
        return

    gao_id = clean_id(gao_id)

    summary = item.xpath(
        "string(.//div[contains(@class, 'c-search-result__summary')])"
    ).strip()

    published = item.xpath(".//span[contains(@class,'text-small')]/time/@datetime")[0]
    released = item.xpath(".//span[contains(@class,'text-small')]/time/@datetime")[1]

    logging.info("%s %s %s", gao_id, title, url)

    product_url = f"https://www.gao.gov/products/{gao_id}"
    logging.info("GET %s", product_url)

    product_page = requests.get(product_url).content
    product_page = lxml.html.fromstring(product_page)
    product_page.make_links_absolute(product_url)

    links = []
    versions = product_page.xpath(
        "//section[contains(@class, 'js-endpoint-full-report')]//a"
    )
    for version in versions:
        version_name = version.xpath("string(.)").strip()
        version_url = version.xpath("@href")[0]
        links.append({"title": version_name, "url": version_url})

    topics = set()

    # GAO uses two sets of tags, a "topic" and zero or more "subjects"
    primary = product_page.xpath(
        "//div[contains(@class,'views-field-field-topic')]/div/a"
    )
    for tag in primary:
        topics.add(tag.xpath("text()")[0].strip())

    tags = product_page.xpath(
        "//div[contains(@class,'views-field-field-subject-term')]/div/span"
    )
    for tag in tags:
        topics.add(tag.xpath("text()")[0].strip())

    # can't json serialize the set
    topics = list(topics)

    # type is currently hardcoded, in case we want to add the others later
    # types include "Reports & Testimonies" "Bid Protest", "Appropriations Law", "Other Legal Function", "Other"
    output = {
        "gao_id": gao_id,
        "published": published,
        "released": released,
        "summary": summary,
        "title": title,
        "topics": topics,
        "type": "reports-testimonies",
        "url": url,
        "versions": links,
    }

    logging.info("SAVE %s", gao_id)

    save(output)


def save(output):
    date = datetime.datetime.strptime(output["published"], "%Y-%m-%dT%H:%M:%SZ")
    date = datetime.datetime.strftime(date, "%Y-%m-%d")

    path = f"data/{date}"
    filename = f"{path}/{output['gao_id']}.json"

    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.isfile(filename):
        with open(filename, "w") as f:
            json.dump(output, f)


def search_page(start: str, end: str, page_number: int) -> bool:
    search_url = "https://www.gao.gov/reports-testimonies"

    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    end = datetime.datetime.strptime(end, "%Y-%m-%d")

    start = round(datetime.datetime.timestamp(start))
    end = round(datetime.datetime.timestamp(end))

    params = {
        "page": page_number,
        "f[0]": f"rt_date_range_gui:(min:{start},max:{end})",
    }

    logging.info("Fetching page %d", page_number)
    response = requests.get(search_url, params=params)

    if response.status_code != 200:
        logging.error(f"Got HTTP {response.status_code} response code, ending scrape")
        return False

    page = lxml.html.fromstring(response.content)
    page.make_links_absolute(search_url)

    rows = page.xpath("//div[contains(@class,'gao-filter')]//div[contains(@class,'views-row')]")
    for row in rows:
        process_item(row)

    if len(rows) == 0:
        logging.info("Got search page, ending scrape")
        return False
    else:
        return True


def scrape() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "start", type=str, help="Scrape documents published after, YYYY-mm-dd"
    )
    parser.add_argument(
        "end", type=str, help="Scrape documents published before, YYYY-mm-dd"
    )

    args = parser.parse_args()

    page_number = 0

    while True:
        res = search_page(args.start, args.end, page_number)

        if res == False:
            logging.info("Empty page found, scrape complete.")
            return

        page_number += 1
