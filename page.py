__author__ = 'destr'


class Page:
    def __init__(self, year, month):
        self._content = None
        self.uid = "%s_%s" % (year, month)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def text(self):
        return self._content.decode('cp1251')

    def get_uid(self):
        return self.uid

    def set_uid(self, uid):
        self.uid = uid
