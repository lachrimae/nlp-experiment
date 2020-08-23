from functools import total_ordering

@total_ordering
class Page:
    def __init__(self, pageid: int, name: str, offset: int):
        self.pageid = int(pageid)
        self.name = name
        self.offset = int(offset)
        self.xml = None

    def __eq__(self, other):
        return self.pageid == other.pageid

    def __hash__(self):
        return hash(self.pageid)

    def __lt__(self, other):
        return self.pageid < other.pageid

    def has_xml(self):
        return self.xml is not None
