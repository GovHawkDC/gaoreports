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
    params = {
        "_wrapper_format": "drupal_ajax",
        "f[0]": f"date:start+{start}+end+{end}",
    }

    data = {
        "view_name": "search_api_reports_and_testimonies_search",
        "view_display_id": "block_1",
        "view_args": "",
        "view_path": "/node/376",
        "view_base_path": "search-api-reports-and-testimonies-search",
        "view_dom_id": "00d5e1ae1c6bf2a5b7b2fd277d884127f2cec83d79042673c192bf801600a848",
        "pager_element": "0",
        "viewsreference[data][argument]": "",
        "viewsreference[data][limit]": "",
        "viewsreference[data][offset]": "",
        "viewsreference[data][pager]": "",
        "viewsreference[data][title]": "",
        "viewsreference[parent_entity_type]": "paragraph",
        "viewsreference[parent_entity_id]": "8921",
        "viewsreference[parent_field_name]": "field_view",
        "page": str(page_number),
        "_drupal_ajax": "1",
        "ajax_page_state[theme]": "gao",
        "ajax_page_state[theme_token]": "",
        "ajax_page_state[libraries]": "back_to_top/back_to_top_icon,back_to_top/back_to_top_js,blazy/bio.ajax,classa11y/base,classa11y/lib--bootstrap,classa11y/lib--font-awesome,classy/base,classy/messages,core/drupal.date,core/normalize,extlink/drupal.extlink,facets/drupal.facets.checkbox-widget,facets/drupal.facets.views-ajax,facets/soft-limit,gao/base,gao/block,gao/block--core,gao/block--core--page-title-block,gao/block--facets,gao/block--facets--facet-blockrt-by-agency,gao/block--facets--facet-blockrt-by-date,gao/block--facets--facet-blockrt-by-topic,gao/block--gao-core,gao/block--gao-core--fed-depository-lib-banner,gao/block--gao-core--gao-footer-info,gao/block--gao-core--gao-newsletter-signup,gao/block--gao-core--post-title-info,gao/block--gao-search,gao/block--gao-search--date-range-custom-facet,gao/block--gao-search--search-block,gao/block--system,gao/block--system--system-breadcrumb-block,gao/block--system--system-main-block,gao/block--system--system-menu-blockfooter,gao/block--system--system-menu-blockjump-to,gao/block--system--system-menu-blockmain,gao/block--system--system-menu-blockreports-testimonies,gao/block--system--system-messages-block,gao/filter-blocks,gao/node,gao/node--full,gao/node--full--page,gao/paragraph,gao/paragraph--default,gao/paragraph--default--embed-view,gao/region,gao/region--breadcrumbs,gao/region--content,gao/region--footer-1,gao/region--footer-2,gao/region--help,gao/region--navigation,gao/region--page-title,gao/region--post-title,gao/region--sidebar-one,gao/region--sidebar-one-extra,gao/region--sidebar-two,gao/region--upper-footer,gao/view,gao/view--search-api-reports-and-testimonies-search,gao/view--search-api-reports-and-testimonies-search--block-1,google_tag/gtag,google_tag/gtag.ajax,google_tag/gtm,paragraphs/drupal.paragraphs.unpublished,system/base,views/views.ajax,views/views.module",
    }

    logging.info("Fetching page %d", page_number)
    response = requests.post("https://www.gao.gov/views/ajax", params=params, data=data)

    rows = json.loads(response.content)

    for row in rows:
        if row["command"] == "insert" and row["data"] != "":
            page = lxml.html.fromstring(row["data"])
            page.make_links_absolute("https://www.gao.gov")
            items = page.xpath("//div[contains(@class,'views-row')]")
            for item in items:
                process_item(item)

            if len(items) == 0:
                logging.info("Got empty response, ending scrape")
                return False
            else:
                return True
    return False


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
