from typing import Iterable
from access_bz2 import get_articles, find_indices
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


def consume_queue(
    relevant_terms: Iterable[re.Pattern],
    nodes_checked: Iterable[str],
    nodes_to_check: Iterable[str], 
    all_articles: Iterable[str]
    ) -> None:
    while True:
        # try to work in batches of 20, but accept smaller batches.
        # If nodes_to_check is completely empty at the beginning,
        # that indicates we have completely traversed the tree.
        node_batch = list()
        try:
            category = nodes_to_check.pop()
            node_batch.append(category)
            nodes_checked.add(category)
        except IndexError:
            return
        for i in range(19):
            try:
                category = nodes_to_check.pop()
                node_batch.append(category)
                nodes_checked.add(category)
            except IndexError:
                break

        # turn these page names into Page objects
        node_pages = find_indices(node_batch)
        node_xmls  = get_articles(node_pages)
        # add new articles to all_articles, and add
        # new, relevant categories in nodes_to_check.
        for xml in node_xmls:
            subcats = subcategories(xml)
            footer =  category_footer(xml)
            for category in subcats:
                if category not in nodes_checked and relevant_term_in_footer(relevant_terms, footer):
                    nodes_to_check.push(category)
            pages = pages_in_category(xml)
            for page in pages:
                if page not in all_articles:
                    print(page)
                all_articles.add(page)
