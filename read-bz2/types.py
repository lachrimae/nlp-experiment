class Page:
    def __init__(pageid: int, name: str, offset: int):
        self.pageid, self.name, self.offset = pageid, name, offset

    def __eq__(self, other):
        return self.pageid == other.pageid

    def __hash__(self):
        return hash(self.pageid)
