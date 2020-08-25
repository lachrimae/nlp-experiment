#import wikitextparser
import re
import bz2
import random
from typing import Iterable
from wikitypes import Page
import wikitextparser as wtp
from process_articles import match_page, get_wikitext
import xml.etree.ElementTree as ET


INDEX_LOCATION = '../data/enwiki-20200801-pages-articles-multistream-index.txt'
DUMP_LOCATION = '../data/enwiki-20200801-pages-articles-multistream.xml.bz2'
FIVE_MEGABYTES = 5000000


# The index file is a sequence of lines of the form '1480303199:694953:Category:Scientists'.
# We want to be able to extract the indices of a bunch of articles all at once.
def get_indices_semirandom(quantity: int) -> Iterable[Page]:
    output = list()
    # This regex matches on an article name, and helps us extract offset and pageid.
    regex = re.compile(rf'^(?P<offset>\d+):(?P<pageid>\d+):(?P<name>.+)$')
    count = 0
    with open(INDEX_LOCATION, mode='r') as index_file:
        # Loop as long as some questions are unanswered.
        while count < quantity:
            line = index_file.readline()
            # The following test indicates we've reached EOF
            if line == '':
                break
            if random.random() < 0.05:
                maybe_match = regex.match(line)
                if maybe_match is not None:
                    count += 1
                    name = maybe_match.group('name')
                    page = Page(
                        maybe_match.group('pageid'), 
                        name, 
                        maybe_match.group('offset')
                    )
                    output.append(page)
    return output


def belongs_to_category(page: Page, category: Page) -> bool:
    xml = page.xml
    if xml is None:
        populate_xml([page])
        xml = page.xml
    text = str(get_wikitext(xml))
    links = wtp.parse(text).wikilinks
    if category.name in [Page.clean_title(link.title) for link in links]:
        return True
    else:
        return False


def populate_xml(pages: Iterable[Page]) -> None:
    offsets = map(lambda page: page.offset, pages)
    matched_one = False
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
            well_formed_xml = b'<pages>%b</pages>' % five_mb_decompressed
            etree_pages = ET.fromstring(well_formed_xml.decode('utf-8')).findall('page')

            for etree_page in etree_pages:
                maybe_match = match_page(etree_page, pages)
                if maybe_match is not None:
                    matched_one = True
                    maybe_match.xml = etree_page
    if not matched_one:
        print(pages[0].name)
