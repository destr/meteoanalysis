#!/usr/bin/env python
# coding: utf-8
__author__ = 'destr'


import matplotlib as mpl
mpl.use('Agg')
from matplotlib import rc
font = {'family': 'Droid Sans, Verdana',
        'weight': 'normal',
        'size': 8}
rc('font', **font)

import matplotlib.pyplot as plt
import time
import bs4
import datetime
import logging
import requests
import textwrap
from argparse import ArgumentParser
from pagestorage import PageStorage
from page import Page
#http://www.pogodaiklimat.ru/weather.php?id=27618&bday=1&fday=31&amonth=2&ayear=2015


class MeteoAnalysis:
    def __init__(self):
        self.opt = None
        self.base_url = 'http://www.pogodaiklimat.ru/weather.php?id=27618&bday=1&fday=31&amonth={0}&ayear={1}'
        self.storage = PageStorage()
        self.data = {}
        self.days = [
            '', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'
        ]

    def main(self):
        cmdparser = ArgumentParser(description='Meteo data parser and analyser')

        cmdparser.add_argument('--load-html', dest='loadhtml', action='store_true', help='Load html data from web')
        cmdparser.add_argument('--parse-html', dest='parsehtml', action='store_true', help='Parse html data')

        self.opt = cmdparser.parse_args()

        self._setup_logger()

        if self.opt.loadhtml:
            self._load_html()

        if self.opt.parsehtml:
            self._parse_html()

    def _parse_html(self):
        logging.getLogger().info("Parse Page")
        for month, year in self._date_range():

            p = Page(year, month)
            try:
                self.storage.load(p)
            except Exception as e:
                #logging.getLogger().exception(e)
                break
            self._parse(p, year)

        print(self.data)
        self._calc_stat()

    def _parse(self, page, year):
        soup = bs4.BeautifulSoup(page.text)

        table = soup.find('table', {'border': '0', 'cellpadding': '2', 'cellspacing': '1'})
        if not table:
            logging.getLogger().error("Not found content table")

        for row in table.findAll('tr')[1:]:
            col = row.findAll('td')

            date = col[1].getText() + "." + str(year)
            date = date.rjust(10, '0')

            key = datetime.datetime.strptime(date, "%d.%m.%Y")
            if key not in self.data:
                self.data[key] = 0

            value = col[17].getText()
            if not value:
                value = 0.0

            value = float(value)
            self.data[key] += value

    def _calc_stat(self):
        values = dict()
        for date, value in self.data.items():
            key = date.isoweekday()
            if key not in values:
                values[key] = 0
            if value > 0:
                values[key] += 1

        result = list()
        for key, value in values.items():
            result.append((self.days[key], value))

        self._plot_hist(result, 'Дождливые дни', 'Дни', 'result.png', True)


    @staticmethod
    def _plot_hist(values, title, xlabel, filename, no_wrap=False):
        plt.xkcd()
        plt.xlabel(xlabel)

        y_pos = range(len(values))
        plt.figure(figsize=(5, 4))
        count_values = [y for (x, y) in values]
        ticks_values = list()
        plt.ylim([-1, len(values)])
        for (x, y) in values:
            if no_wrap:
                ticks_values.append(x)
            else:
                ticks_values = textwrap.fill(x, 12)
        rects = plt.barh(y_pos, count_values, align='center', alpha=0.4)
        plt.yticks(y_pos, ticks_values)
        #plt.minorticks_on()

        plt.title(title)


        # for rect in rects:
        #     width = int(rect.get_width())
        #
        #     rankstr = str(width)
        #     if width < 2:
        #         xloc = width + 10
        #         clr = 'black'
        #         align = 'left'
        #     else:
        #         xloc = 0.98*width
        #         clr = 'white'
        #         align = 'right'
        #
        #     yloc = rect.get_y()+rect.get_height()/2.0
        #     plt.text(xloc, yloc, rankstr, horizontalalignment=align,
        #              verticalalignment='center', color=clr)


        plt.savefig(filename)

    def _date_range(self):
        for year in range(2011, 2015):
            for month in range(4, 10):
                yield (month, year)

    def _load_html(self):
        now = datetime.datetime.now()

        for month, year in self._date_range():
            url = self.base_url.format(month, year)
            p = Page(year, month)
            if year == now.year and month > now.month:
                return

            self._load_page(url, p)
            time.sleep(1)

    def _load_page(self, url, page):
        logging.getLogger().info("Load page by url {0}".format(url))

        r = requests.get(url)

        page.content = r.content
        self.storage.save(page)
        return page

    def _setup_logger(self):
        log_formater = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()

        root_logger.setLevel("INFO")

        file_handler = logging.FileHandler("meteoanalysis.log")
        file_handler.setFormatter(log_formater)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formater)
        root_logger.addHandler(console_handler)

if __name__ == "__main__" :
    m = MeteoAnalysis()

    m.main()
    exit(0)

