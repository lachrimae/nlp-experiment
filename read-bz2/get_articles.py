from typing import Iterable
import bz2
import re
from wikitypes import Page
from xml.etree import ElementTree as ET


DUMP_LOCATION = '../data/enwiki-20200801-pages-articles-multistream.xml.bz2'
ONE_MEGABYTE = 10000000


def get_articles(pages: Iterable[Page]) -> Iterable[ET.Element]:
    output = list()
    articles_found = {page: False for page in pages}
    offsets = map(lambda page: page.offset, pages)
    last_reader = None
    with open(DUMP_LOCATION, mode='rb') as dump_bytes:
        for offset in offsets:
            reader = bz2.BZ2Decompressor()
            #    with bz2.open(DUMP_LOCATION, mode='rb') as dump:
            pages_of_interest = filter(
                lambda page: page.offset == offset,
                pages
            )
            dump_bytes.seek(offset)
            root_xml = None
            if last_reader is None:
                root_xml = ET.fromstring(reader.decompress(dump_bytes))
            else:
                root_xml = ET.fromstring(reader.decompress(last_reader.unused_data))
            last_reader = reader
            root_xml = ET.fromstring(xml_raw)
            # THE THINGS AFTER THIS NOTE HAVE TO BE CHANGED
            while False in articles_found.values():
                line = dump.readline()
                if line == '': # EOF
                    break
                elif line != b'\n': # the separator between wikipedia articles
                    last_article += line
                    continue
                print(last_article)
                xml = ET.fromstring(last_article)
                maybe_page = match_page(xml, pages_of_interest)
                if maybe_page is not None:
                    articles_found[maybe_page] = True
                    output.append(xml)
                last_article = b''
    return output


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


def consume_queue(
    relevant_terms: Iterable[re.Pattern],
    nodes_checked: Iterable[str],
    nodes_to_check: Iterable[str], 
    all_articles: Iterable[str]
    ) -> None:
    while True:
        # try to work in batches of 20, but accept smaller batches
        # if nodes_to_check is completely empty at the beginning,
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
        # add new articles to all_articles;
        # add new, relevant categories in nodes_to_check.
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


def relevant_term_in_footer(relevant_terms: Iterable[str], footer: Iterable[str]) -> bool:
    for term in relevant_terms:
        for footer_entry in footer:
            if term.search(footer_entry):
                return True
    return False


def list_all_pages(
        category_name: str,
        relevant_terms: Iterable[str],
        ) -> Iterable[Page]:
    search_root = get_articles([category_name])

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
    # We want appending to be O(1) most of the time, but we don't want duplicates.
    # Thus the set type is ideal.
    all_articles = set()
    # We need nodes_checked in order to prevent ourselves from
    # traversing a cycle indefinitely. Choosing the set type gives
    # us O(1) membership tests, with the same advantages as for all_articles.
    nodes_checked = set()
    # The nodes_to_check queue tracks all of the category pages
    # we still need to traverse. Using a list as a stack is preferable because
    # its push and pop commands are O(1). I assume the search tree is much wider
    # than it is tall, based on the category pages I've observed.
    # Thus the stack's LIFO semantics will use less memory than a FIFO structure.
    nodes_to_check = list()
    nodes_to_check.push(category_name)

    # traverse the tree unti nodes_to_check is empty
    consume_queue(
        relevant_terms,
        nodes_checked,
        nodes_to_check,
        all_articles
    )
    return all_articles
