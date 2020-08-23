#import wikitextparser
import re
from typing import Iterable
from wikitypes import Page


INDEX_LOCATION = '../data/enwiki-20200801-pages-articles-multistream-index.txt'


# The index file is a sequence of lines of the form '1480303199:694953:Category:Scientists'.
# We want to be able to extract the indices of a bunch of articles all at once.
def find_indices(names: Iterable[str]) -> Iterable[Page]:
    output = list()
    found_pages = {name: False for name in names}
    # This regex matches on an article name, and helps us extract offset and pageid.
    regexes = [re.compile(rf'^(?P<offset>\d+):(?P<pageid>\d+):(?P<name>{re.escape(n)})$') for n in names]
    with open(INDEX_LOCATION, 'r') as index_file:
        # Loop as long as some questions are unanswered.
        while False in found_pages.values():
            line = index_file.readline()
            # The following test indicates we've reached EOF
            if line == '':
                break
            for regex in regexes:
                maybe_match = regex.match(line)
                if maybe_match is not None:
                    name = maybe_match.group('name')
                    found_pages[name] = True
                    page = Page(
                        maybe_match.group('pageid'), 
                        name, 
                        maybe_match.group('offset')
                    )
                    output.append(page)
    # be silent if some questions went unanswered.
    return output
