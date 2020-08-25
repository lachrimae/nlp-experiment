from functools import total_ordering

@total_ordering
class Page:
    def __init__(self, pageid: int, name: str, offset: int):
        self.pageid = int(pageid)
        Page.clean_title(name)
        self.name = name
        self.offset = int(offset)
        self.xml = None

    def __eq__(self, other):
        return self.pageid == other.pageid

    def __hash__(self):
        return hash(self.pageid)

    def __lt__(self, other):
        return self.pageid < other.pageid

    def __repr__(self):
        return 'Page({0})'.format(self.name)

    def has_xml(self):
        return self.xml is not None

    @staticmethod
    def clean_title(title: str) -> None:
        title.replace('&amp;', '&').replace('&quot;', '"')
        return title
