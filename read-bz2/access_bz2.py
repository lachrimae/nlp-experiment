#import wikitextparser
import re
import bz2
from typing import Iterable
from wikitypes import Page
from process_articles import match_page
import xml.etree.ElementTree as ET


INDEX_LOCATION = '../data/enwiki-20200801-pages-articles-multistream-index.txt'
DUMP_LOCATION = '../data/enwiki-20200801-pages-articles-multistream.xml.bz2'
FIVE_MEGABYTES = 5000000


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


def populate_xml(pages: Iterable[Page]) -> None:
    offsets = map(lambda page: page.offset, pages)
    last_reader = None
    with open(DUMP_LOCATION, mode='rb') as dump_bytes:
        for offset in offsets:
            reader = bz2.BZ2Decompressor()
            pages_of_interest = filter(
                lambda page: page.offset == offset,
                pages
            )
            dump_bytes.seek(offset)
            # we can't open the whole file, but I've observed that the
            # streams tend to be one megabyte long. With a fudge factor of five,
            five_mb_of_stream = dump_bytes.read(FIVE_MEGABYTES)
            five_mb_decompressed = reader.decompress(five_mb_of_stream)
            well_formed_xml = f'<pages>{five_mb_decompressed}</pages>'
            print(well_formed_xml.replace('\\n', '\n'))
            etree_pages = ET.fromstring(well_formed_xml).findall('page')

            for etree_page in etree_pages:
                maybe_match = match_page(etree_page, pages_of_interest)
                if maybe_match is not None:
                    maybe_match.xml = etree_page
