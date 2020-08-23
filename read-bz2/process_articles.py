from typing import Iterable
import re
from wikitypes import Page
from xml.etree import ElementTree as ET


def subcategories(xml: ET.Element) -> Iterable[str]:
#        None,
#        partial(
#            html.find_all,
#            'span', 
#            **{'class': 'CategoryTreeToggle'}
#        )
    return map(
        lambda toggle: toggle['data-ct-title'],
         toggles
    )


def pages_in_category(xml: ET.Element) -> Iterable[str]:
#
#        None,
#        partial(html.find, 'div', id='mw-pages')
    mw_pages =  mw_pages_future
    try:
            None,
            partial(
                mw_pages.find_all,
                'div',
                **{'class': 'mw-category-group'}
            )
    except AttributeError:
        return set()
    category_groups =  category_groups_future
    pages = map(
        lambda page: strip_internal_link(page.find('a')['href']),
        category_groups
    )
    return pages


def category_footer(xml: ET.Element) -> Iterable [str]:
#        None,
#        partial(
#            html.find,
#            'div',
#            **{'id': 'mw-normal-catlinks', 'class': 'mw-normal-catlinks'}
#        )
    cat_links =  cat_links_future
    try:
        li = cat_links.find_all('li')
    except AttributeError:
        return list()
    links = map(lambda l: l.find('a')['href'], li)
    category_article_names = map(strip_internal_link, links)
    # turn 'Category:Nanjing_Metro' into 'Nanjing_Metro'
    # By design, I know there won't be any spaces or underscores
    # in 'Scientists' or 'Musicians', so I don't have to worry
    # about transforming back and forth between human-readable
    # names and the names as stored in Wikipedia's backend.
    return list(map(lambda name: name[9:], category_article_names))


# Turn '/wiki/Category:Nanjing_Metro' into 'Category:Nanjing_Metro'
def strip_internal_link(internal_link: str) -> str:
    return internal_link[6:]


def relevant_term_in_footer(relevant_terms: Iterable[str], footer: Iterable[str]) -> bool:
    for term in relevant_terms:
        for footer_entry in footer:
            if term.search(footer_entry):
                return True
    return False


def match_page(page_xml: ET.Element, pages: Iterable[Page]) -> Page:
    def _match_page(page_xml: ET.Element, page: Page) -> bool:
        title = page_xml.get('title')
        if title == page.name:
            return True
        try:
            redirect = page_xml.find('redirect').attrib['title']
            if redirect == page.name:
                return True
        except AttributeError:
            pass
        return False
    for page in pages:
        if _match_page(page_xml, page):
            return page
    return None
