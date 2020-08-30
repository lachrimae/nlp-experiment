from typing import Iterable
from functools import partial, reduce
from math import sqrt
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
    # We want the titles of the sections, i.e., the headers.
    headers = map(
        lambda section: section.title,
        wikitext.sections
    )
    # Some sections have no title. We need to filter None's out.
    headers = filter(
        lambda header: header is not None,
        headers
    )
    for header in headers:
        for regex in header_regexes:
            if regex.search(header):
                return True
    return False


def is_geography(wikitext) -> bool:
    return is_in_category(wikitext, GEOGRAPHY_KEYWORDS)


def is_biography(wikitext) -> bool:
    return is_in_category(wikitext, BIOGRAPHY_KEYWORDS)


def sentence_stats(plaintext) -> (float, float):
    plaintext = " ".join(plaintext.split()) # deduplicates whitespace
    # The first .split('.') gives us a list of strings.
    # I use the map->reduce idiom to split these strings further
    # without increasing the nesting depth.
    sentences = plaintext.split('.')
    sentences = reduce(list.__add__,
        map(lambda sentence: sentence.split('!'), sentences)
    )
    sentences = reduce(list.__add__,
        map(lambda sentence: sentence.split('?'), sentences)
    )
    # Finally, I split on ' ' to split each sentence into words, since
    # those are what we're counting.
    sentences = list(map(lambda sentence: sentence.split(' '), sentences))
    return length_stats(sentences)


def word_stats(plaintext) -> (float, float):
    # With no args, 'split()' splits on whitespace.
    words = plaintext.split()
    return length_stats(words)


# returns mean, stddev.
def length_stats(list_of_containers) -> (float, float):
    num_containers    = len(list_of_containers)
    container_lengths = list(map(len, list_of_containers))
    mean_length    = sum(container_lengths) / num_containers
    stddev_length  = sqrt(sum(map(lambda l: (l - mean_length)**2, container_lengths)))
    return (mean_length, stddev_length)
