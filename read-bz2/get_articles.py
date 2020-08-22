#!/usr/bin/env python
from typing import Iterable
import re
import queue
import wikitextparser as w


WIKIPEDIA_PREFIX = 'https://en.wikipedia.org/wiki/'


 def get_wiki(session: r.Session, page_name: str) -> r.Response:
    url = WIKIPEDIA_PREFIX + page_name
    for i in range(len(page_name)):
        if page_name[i] == ' ':
            page_name[i] = '_'
        None, session.get, url


def get_wiki_blocking(session: r.Session, page_name: str) -> r.Response:
    for i in range(len(page_name)):
        if page_name[i] == ' ':
            page_name[i] = '_'
    return session.get(WIKIPEDIA_PREFIX + page_name)


 def get_category_page(session: r.Session, category_name: str) -> r.Response:
    return  get_wiki(session, 'Category:' + category_name)


def get_category_page_blocking(session: r.Session, category_name: str) -> r.Response:
    return get_wiki_blocking(session, 'Category:' + category_name)


 def subcategories(html: BeautifulSoup) -> Iterable[str]:
        None,
        partial(
            html.find_all,
            'span', 
            **{'class': 'CategoryTreeToggle'}
        )
    return map(
        lambda toggle: toggle['data-ct-title'],
         toggles
    )


 def pages_in_category(html: BeautifulSoup) -> Iterable[str]:
        None,
        partial(html.find, 'div', id='mw-pages')
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


 def category_footer(html: BeautifulSoup) -> Iterable [str]:
        None,
        partial(
            html.find,
            'div',
            **{'id': 'mw-normal-catlinks', 'class': 'mw-normal-catlinks'}
        )
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


def article_entity(html: BeautifulSoup) -> Iterable [str]:
    return set()


# Turn '/wiki/Category:Nanjing_Metro' into 'Category:Nanjing_Metro'
def strip_internal_link(internal_link: str) -> str:
    return internal_link[6:]


 def consume_queue(
        relevant_terms: Iterable[re.Pattern],
        sess: r.Session,
        nodes_checked: Iterable[str],
        nodes_to_check: Iterable[str], 
        all_articles: Iterable[str]
    ) -> None:
    while True:
        try:
            category = nodes_to_check.get_nowait()
        except queue.Empty:
            return
        nodes_checked.add(category)
        response =  get_category_page(sess, category)
            None,
            BeautifulSoup,
            response.text,
            'html.parser'
        soup =  soup_future
        subcats =  subcategories(soup)
        footer =  category_footer(soup)
        for category in subcats:
            if category not in nodes_checked and relevant_term_in_footer(relevant_terms, footer):
                nodes_to_check.put(category)
        pages =  pages_in_category(soup)
        for page in pages:
            if page not in all_articles:
                print(page)
                all_articles.add(page)


def relevant_term_in_footer(relevant_terms, footer) -> bool:
    for term in relevant_terms:
        for footer_entry in footer:
            if term.search(footer_entry):
                return True
    return False


 def list_all_pages(
        category_name: str,
        relevant_terms: Iterable[str],
    ) -> Iterable[str]:
    sess = r.Session()
    search_root = get_category_page_blocking(sess, category_name)

    relevant_terms = list(map(
        lambda term: re.compile(
            term,
            re.IGNORECASE
        ),
        relevant_terms
    ))


    # DATASTRUCTURES
    # Implicitly, we are regarding Wikipedia pages as a rose tree.
    # The root will be a category page, and the children of each
    # node are the category pages and content pages it links to.
    # This algorithm regards content pages as having no children,
    # and it ignores cycles it discovers.
    #
    # Th all_articles variable is our output datastructure. 
    # We want appending  to be O(1), and we don't want duplicates.
    # Thus the set type is ideal.
    all_articles = set()
    # We need nodes_checked in order to prevent ourselves from
    # traversing a cycle indefinitely. Choosing the set type gives
    # us O(1) membership tests.
    nodes_checked = set()
    # The nodes_to_check queue tracks all of the category pages
    # we still need to traverse. I assume the search tree is much wider
    # than it is tall, based on the category pages I've observed.
    # Thus LIFO will keep space complexity low as we traverse the tree.
    # Our get and put operations are O(1).
    nodes_to_check = queue.LifoQueue()
    nodes_to_check.put(category_name)


    # traverse the tree until
    # nodes_to_check is empty
    consume_queue(
        relevant_terms,
        sess,
        nodes_checked,
        nodes_to_check,
        all_articles
    )
    return all_articles
