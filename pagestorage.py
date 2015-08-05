__author__ = 'destr'

import os
import logging


class PageStorage:
    def __init__(self):
        self.path = 'pages'
        self._dir_structure()

    def _dir_structure(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        return self.path

    def save(self, page):
        filename = self._filename_by_page(page)
        f = open(filename, 'wb')
        f.write(page.content)
        f.close()

    def _filename_by_page(self, page):
        subdir = self._dir_structure()

        filename = os.path.join(subdir, page.uid + ".html")
        return filename

    def load(self, page):
        filename = self._filename_by_page(page)
        logging.getLogger().debug("Load page from filename {0}".format(filename))
        with open(filename, 'rb') as f:
            page.content = f.read()


