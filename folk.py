#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules.bs4 import BeautifulSoup
from modules import requests


def main():
    page = get_data()
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table')
    tbody = table.find_all('tbody')
    tr = table.find_all('tr')
    td = table.find_all('td')

    data = {}
    for i in tr[1:-1]:
        place = i.select('td')[0].text
        n = i.select('td')[1].text

        data[place] = int(n)

    print_data(data)


def get_data():
    url = api.API
    page = requests.get(url)

    return page


def print_data(data):
    print()

    for v in sorted(data, key=data.get):
        print(const.FORMAT.format(v, data[v]))

    print(const.FORMAT.format("TOTALT", sum(data.values())))
    print()


class api:
    API = 'https://www.folkhalsomyndigheten.se/' \
        'smittskydd-beredskap/utbrott/aktuella-utbrott/' \
        'covid-19/aktuellt-epidemiologiskt-lage/'


class const:
    FORMAT = '{:<15s}{:>10d}'


if __name__ == "__main__":
    main()
