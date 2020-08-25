from process_articles import *
import access_bz2
import queue
from typing import Iterable


def main():
    scientist_pages = list_all_pages(
        'Scientists',
        SCIENCE_KEYWORDS
    )
    musician_pages = list_all_pages(
        'Musicians',
        MUSIC_KEYWORDS
    )
    print('scientists:\n', scientist_pages)
    print('musicians:\n', musician_pages)


def list_all_pages(
        category_name: str,
        relevant_terms: Iterable[str],
        ) -> Iterable[Page]:

    relevant_terms = list(map(
        lambda term: re.compile(
            term,
            re.IGNORECASE
        ),
        relevant_terms
    ))

    # DATASTRUCTURES
    # Implicitly, I am regarding Wikipedia pages as a rose tree.
    # The root will be a category page, and the children of each
    # node are the category pages and content pages it links to.
    # This algorithm regards content pages as having no children,
    # and it ignores cycles it discovers.
    #
    # The all_articles variable is our output datastructure. 
    # We want appending to be O(1) most of the time, and we regard
    # the occasional O(n) appends to be superior to de-duplicating
    # the list at the end, or sending duplicate UPDATE commands to the db.
    all_articles = set()
    # We need nodes_checked in order to prevent ourselves from
    # traversing a cycle indefinitely. Choosing the set type gives
    # us O(1) membership tests, with the same advantages as for all_articles.
    nodes_checked = set()
    # The nodes_to_check queue tracks all of the category pages
    # we still need to traverse. Using a LIFO queue, i.e., a stack, is preferable because
    # its put and get commands are O(1). I assume the search tree is much wider
    # than it is tall, based on the category pages I've observed.
    # Thus the stack's LIFO semantics will use less memory than a FIFO structure.
    nodes_to_check = queue.LifoQueue()
    nodes_to_check.put(category_name)

    # traverse the tree unti nodes_to_check is empty
    asyncio.gather(*(NUM_CONSUMERS * [consume_queue(
        relevant_terms,
        nodes_checked,
        nodes_to_check,
        all_articles
    )]))
    return all_articles


def consume_queue(
    relevant_terms: Iterable[re.Pattern],
    nodes_checked: Iterable[str],
    nodes_to_check: Iterable[str], 
    all_articles: Iterable[Page]
    ) -> None:
    while True:
        # try to work in batches of 20, but accept smaller batches.
        # If nodes_to_check is completely empty at the beginning,
        # that indicates we have completely traversed the tree.
        node_batch = list()
        try:
            category = nodes_to_check.get_nowait()
            node_batch.append(category)
            nodes_checked.add(category)
        except queue.Empty:
            return
        for i in range(19):
            try:
                category = nodes_to_check.get_nowait()
                node_batch.append(category)
                nodes_checked.add(category)
            except queue.Empty:
                break

        # turn these page names into Page objects
        node_pages = access_bz2.find_indices(node_batch)
        access_bz2.populate_xml(node_pages)
        # add new articles to all_articles, and add
        # new, relevant categories in nodes_to_check.
        for node_page in node_pages:
            xml = None
            try:
                xml = node_page.xml
            except AttributeError:
                continue
            subcats = subcategories(xml)
            footer =  category_footer(xml)
            for category in subcats:
                if category not in nodes_checked and relevant_term_in_footer(relevant_terms, footer):
                    nodes_to_check.put(category)
            pages = pages_in_category(xml)
            for page in pages:
                if page not in all_articles:
                    print(page)
                all_articles.add(page)


if __name__ == '__main__':
    main()
