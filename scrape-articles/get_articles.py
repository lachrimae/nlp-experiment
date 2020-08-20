#!/usr/bin/env python
from typing import Iterable
import requests as r
import re
import queue
import asyncio
import bs4
from functools import partial
from bs4 import BeautifulSoup

WIKIPEDIA_PREFIX = 'https://en.wikipedia.org/wiki/'
NUM_CONSUMERS = 100


async def get_wiki(session: r.Session, page_name: str) -> r.Response:
    url = WIKIPEDIA_PREFIX + page_name
    for i in range(len(page_name)):
        if page_name[i] == ' ':
            page_name[i] = '_'
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, session.get, url
    )


def get_wiki_blocking(session: r.Session, page_name: str) -> r.Response:
    for i in range(len(page_name)):
        if page_name[i] == ' ':
            page_name[i] = '_'
    return session.get(WIKIPEDIA_PREFIX + page_name)


async def get_category_page(session: r.Session, category_name: str) -> r.Response:
    return await get_wiki(session, 'Category:' + category_name)


def get_category_page_blocking(session: r.Session, category_name: str) -> r.Response:
    return get_wiki_blocking(session, 'Category:' + category_name)


async def subcategories(html: BeautifulSoup) -> Iterable[str]:
    loop = asyncio.get_event_loop()
    toggles = loop.run_in_executor(
        None,
        partial(
            html.find_all,
            'span', 
            **{'class': 'CategoryTreeToggle'}
        )
    )
    return map(
        lambda toggle: toggle['data-ct-title'],
        await toggles
    )


async def pages_in_category(html: BeautifulSoup) -> Iterable[str]:
    loop = asyncio.get_event_loop()
    mw_pages_future = loop.run_in_executor(
        None,
        partial(html.find, 'div', id='mw-pages')
    )
    mw_pages = await mw_pages_future
    try:
        category_groups_future = loop.run_in_executor(
            None,
            partial(
                mw_pages.find_all,
                'div',
                **{'class': 'mw-category-group'}
            )
        )
    except AttributeError:
        return set()
    category_groups = await category_groups_future
    pages = map(lambda page: page.find('a')['href'], category_groups)
    return pages


async def category_footer(html: BeautifulSoup) -> Iterable [str]:
    loop = asyncio.get_event_loop()
    cat_links_future = loop.run_in_executor(
        None,
        partial(
            html.find,
            'div',
            **{'id': 'mw-normal-catlinks', 'class': 'mw-normal-catlinks'}
        )
    )
    cat_links = await cat_links_future
    try:
        li = cat_links.find_all('li')
    except AttributeError:
        return list()
    links = map(lambda l: l.find('a')['href'], li)
    category_article_names = map(strip_internal_link, links)
    # turn 'Category:Nanjing_Metro' into 'Nanjing_Metro'
    # By design, I know there won't be any spaces or underscores
    # in 'Scientists' or 'Musicians', so I don't have to be too
    # rigorous here.
    return list(map(lambda name: name[9:], category_article_names))


def article_entity(html: BeautifulSoup) -> Iterable [str]:
    return set()


# Turn '/wiki/Category:Nanjing_Metro' into 'Category:Nanjing_Metro'
def strip_internal_link(internal_link: str) -> str:
    return internal_link[6:]


async def consume_queue(
        relevant_terms: Iterable[re.Pattern],
        sess: r.Session,
        nodes_checked: Iterable[str],
        nodes_to_check: Iterable[str], 
        all_articles: Iterable[str]
        ) -> None:
    loop = asyncio.get_event_loop()
    while True:
        try:
            category = nodes_to_check.get(timeout=3)
        except queue.Empty:
            return
        nodes_checked.add(category)
        response = await get_category_page(sess, category)
        soup_future = loop.run_in_executor(
            None,
            BeautifulSoup,
            response.text,
            'html.parser'
        )
        soup = await soup_future
        subcats = await subcategories(soup)
        footer = await category_footer(soup)
        for category in subcats:
            if category in nodes_checked:
                #print('decided the category was checked already: ', category)
                continue
            elif not relevant_term_in_footer(relevant_terms, footer):
                #print('decided the category had insufficient footer-relevance: ', category)
                continue
            nodes_to_check.put(category)
        pages = await pages_in_category(soup)
        for page in pages:
            if True: #root_node_name in article_entity(soup):
                all_articles.add(page)


def relevant_term_in_footer(relevant_terms, footer) -> bool:
    for term in relevant_terms:
        for footer_entry in footer:
            if term.search(footer_entry):
                return True
    return False


async def list_all_pages(category_name: str, relevant_terms: Iterable[str]) -> Iterable[str]:
    loop = asyncio.get_event_loop()
    sess = r.Session()
    search_root = get_category_page_blocking(sess, category_name)
    soup = BeautifulSoup(search_root.text, 'html.parser')

    relevant_terms = list(map(
        lambda term: re.compile(
            term,
            re.IGNORECASE
        ),
        relevant_terms
    ))


    # DATASTRUCTURES
    # We want appending to be O(1) and we don't want duplicates.
    all_articles = set()
    # We don't want to get stuck in a graph cycle; set()
    # allows O(1) membership testing.
    nodes_checked = set()
    # I expect the search tree to be much wider than it is tall.
    # Thus LIFO will keep space complexity low as we traverse
    # the tree.
    nodes_to_check = queue.LifoQueue()

    # Get children of root
    for page in await pages_in_category(soup):
        all_articles.add(page)
    for category in await subcategories(soup):
        nodes_to_check.put(category)

    tasks = asyncio.gather(
        *([
            consume_queue(
            relevant_terms,
            sess,
            nodes_checked,
            nodes_to_check,
            all_articles
        )]*NUM_CONSUMERS)
    )
    await tasks

    return all_articles
