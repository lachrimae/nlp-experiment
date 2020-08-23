from typing import Iterable
import bz2
from types import Page
from xml.etree import ElementTree as ET


DUMP_LOCATION = '../data/enwiki-20200801-pages-articles-multistream.xml.bz2'
ONE_MB = 1000000


def get_articles(pages: Iterable[Page]): Iterable[str]) -> Iterable[ET.Element]:
    output = list()
    articles_found = {page: False for page in pages}
    offsets = map(lambda page: page.offset, pages)
    reader = bz2.BZ2Decompressor()
    with bz2.open(DUMP_LOCATION, mode='rb') as dump:
        for offset in offsets:
            pages_of_interest = filter(
                lambda page: page.offset == offset,
                pages
            )
            dump.seek(offset)
            last_article = b''
            while False in articles_found.values():
                line = dump.readline()
                if line == '': # EOF
                    break
                elif line != b'\n': # the separator between wikipedia articles
                    last_article += line
                    continue
                xml = ET.fromstring(last_article)
                maybe_page = match_page(xml, pages_of_interest)
                if maybe_page is not None:
                    articles_found[maybe_page] = True
                    output.append(xml)
                last_article = b''
    return output


