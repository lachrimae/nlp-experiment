from typing import Iterable
import re
from wikitypes import Page
from xml.etree import ElementTree as ET
import wikitextparser


GEOGRAPHY_KEYWORDS = list(map(
    lambda kw: re.compile(kw, re.IGNORECASE),
    [
        'geography',
        'economy',
        'demographics',
        'culture',
        'climate',
        'government'
    ]
))


BIOGRAPHY_KEYWORDS = list(map(
    lambda kw: re.compile(kw, re.IGNORECASE),
    [
        'career',
        'marriage',
        'children',
        'early years',
        'death',
        'works',
        'life'
    ]
))


def match_page(page_xml: ET.Element, pages: Iterable[Page]) -> Page:
    title = page_xml.find('title').text
    for page in pages:
        if page.name == title:
            return page
    return None


def get_wikitext(page_xml: ET.Element) -> str:
    out = page_xml.find('revision').find('text').text
    return out


def is_in_category(wikitext, header_regexes) -> bool:
    headers = map(
        lambda section: section.title,
        wikitext.sections
    )
    for header in headers:
        for r in header_regexes:
            if r.search(header):
                return True
    return False


def is_geography(wikitext) -> bool:
    return is_in_category(wikitext, GEOGRAPHY_KEYWORDS)


def is_biography(wikitext) -> bool:
    return is_in_category(wikitext, BIOGRAPHY_KEYWORDS)
