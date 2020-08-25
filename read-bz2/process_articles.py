from typing import Iterable
import re
from wikitypes import Page
from xml.etree import ElementTree as ET
import wikitextparser


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
    title = page_xml.find('title').text
    for page in pages:
        if page.name == title:
            return page
    return None


def get_wikitext(page_xml: ET.Element) -> str:
    try:
        out = page_xml.find('revision').find('text').text
    except AttributeError:
        try:
            print(page_xml.getchildren())
        except:
            pass


def belongs_to_category(page: Page, category: Page) -> bool:
    xml = page.xml
    if xml is None:
        populate_xml([page])
        xml = page.xml
    text = get_wikitext(xml)
    links = wtp.parse(text).wikilinks
    if category.name in [link.title for link in links]:
        return True
    else:
        return False
