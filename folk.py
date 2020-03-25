#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules.bs4 import BeautifulSoup
from modules import requests


def main():
    page = get_page()
    data = parse_data(page)

    print_data(data)


def get_page():
    url = api.API
    page = requests.get(url)

    return page


def parse_data(page):
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table')
    tbody = table.find_all('tbody')
    tr = table.find_all('tr')

    data = dict()
    for i in tr[1:]:
        td = i.select('td')

        region = td[0].text
        n = td[1].text.replace(' ', '')
        d = td[4].text

        data[region] = [int(n), int(d)]

    return data


def print_data(data):
    print_header()

    for k, v in sorted(data.items(), key=lambda k: k[1][0]):
        print(
            C.TABLE.format(
                k,
                color.blue(v[0]),
                color.red(v[1])))


def print_header():
    line = C.line(C.HEADER)
    head = C.HEADER

    print(color.dim(line))
    print(color.dim(head))
    print(color.dim(line))


class api:
    API = 'https://www.folkhalsomyndigheten.se/' \
        'smittskydd-beredskap/utbrott/aktuella-utbrott/' \
        'covid-19/aktuellt-epidemiologiskt-lage/'


class C:
    TABLE = '{:<15s}{:>19s}{:>19s}'
    HEADER = '{:<15s}{:>10s}{:>10s}'.format(
        'Region', 'Fall', 'Avlidna')

    @staticmethod
    def line(head):
        return '-' * len(head.expandtabs())


class color:
    DEFAULT = '\033[0m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    DIM = '\033[2m'

    @staticmethod
    def dim(output):
        return color.DIM + str(output) + color.DEFAULT

    @staticmethod
    def green(output):
        return color.GREEN + str(output) + color.DEFAULT

    @staticmethod
    def blue(output):
        return color.BLUE + str(output) + color.DEFAULT

    @staticmethod
    def red(output):
        return color.RED + str(output) + color.DEFAULT


if __name__ == "__main__":
    main()
