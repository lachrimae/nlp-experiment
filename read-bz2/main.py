from process_articles import consume_queue


SCIENCE_KEYWORDS = ['Scien', 'physic', 'biolog', 'geolog', 'paleontolog', 'archaeolog', 'chemist', 'astronom', 'cosmolog', 'ecolog', 'oceanograph', 'meteorolog', 'biochem', 'botan', 'zoolog']
MUSIC_KEYWORDS = ['music', 'sing', 'guitar', 'bass', 'brass', 'flaut', 'flute', 'string', 'instrument', 'ophone', 'pian', 'keyboard', 'funk', 'jazz', 'country', 'bluegrass', 'pop']


def main():
    scientist_pages = list_all_pages(
        'Scientists',
        SCIENCE_KEYWORDS
    )
    musician_pages = list_all_pages(
        'Musicians',
        MUSIC_KEYWORDS
    )


def list_all_pages(
        category_name: str,
        relevant_terms: Iterable[str],
        ) -> Iterable[Page]:
    search_root = get_pages([category_name])

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
    process.consume_queue(
        relevant_terms,
        nodes_checked,
        nodes_to_check,
        all_articles
    )
    return all_articles


if __name__ == '__main__':
    main()
