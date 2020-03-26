#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import csv
import http.client
import urllib.error
from sys import argv
import urllib.request
from threading import Thread
from queue import PriorityQueue
from datetime import datetime, timedelta, date
from modules.sortedcontainers import SortedSet, SortedDict


def main():
    cmd, s = get_params()

    if cmd == C.EMPTY:
        print(C.USAGE)

    elif cmd == C.COUNTRIES:
        list_countries()

    elif cmd == C.ALL:
        list_all(s)

    elif cmd == C.GLOBAL:
        list_global()

    else:
        list_country(cmd)


def get_params():
    try:
        cmd = argv[1:][0]

        try:
            s = argv[1:][1]
        except IndexError:
            return cmd, C.EMPTY

        return cmd, s

    except IndexError:
        return C.EMPTY, C.EMPTY


def list_countries():
    cs = get_countries()

    print_countries(cs)


def list_all(sort_by):
    data = get_data(False)

    print_all(data, sort_by)


def list_global():
    data = get_data(True, True)

    print_global(data)


def list_country(country):
    c = C.regex(country)
    data = get_data(True, False, c)

    print_country(data)


def get_countries():
    url = api.append_url(api.TC)
    table = get_table(url, False)
    countries = SortedSet(key=str.lower)

    for row in table:
        country = parse_country(row)
        countries.add(country)

    return countries


def parse_country(row):
    h, s, t = str(row[1]).strip('*').partition(',')

    return h


def get_data(ALL=True, GLOBAL=False, COUNTRY=None):
    data = SortedDict()
    queue = build_queue()

    for i in range(queue.qsize()):
        thread = Thread(target=get_data_thread,
                        args=(queue, data, ALL, GLOBAL, COUNTRY))
        thread.daemon = True
        thread.start()

    queue.join()

    return data


def build_queue():
    queue = PriorityQueue()

    for i, url in enumerate(api.urls()):
        queue.put((i, url))

    return queue


def get_data_thread(queue, data, ALL, GLOBAL, COUNTRY):
    while not queue.empty():
        q = queue.get()
        category = q[0]
        url = q[1]

        table = get_table(url)
        c = r'.' if COUNTRY is None else COUNTRY

        end = len(table[0])
        start = end - 2 if not ALL else 4  # get only latest data

        for col in range(start, end):
            for row in table[1:]:
                country = parse_country(row)

                match = re.search(c, country.lower())
                if match:

                    dt = table[0][col]
                    date = parse_date(dt)  # csv files look different

                    try:
                        n = int(row[col])
                    except ValueError:
                        pass

                    append_data(GLOBAL, data, category, country, date, n)

        queue.task_done()


def parse_date(dt):
    f = C.format('mdy')
    try:
        return format_date(dt, f[0])
    except ValueError:
        return format_date(dt, f[1])


def append_data(GLOBAL, data, category, country, date, n):
    if GLOBAL:
        append_global(data, category, date, n)
    else:
        append_all(data, category, country, date, n)


def append_all(data, category, country, date, n):
    if country not in data:
        data[country] = SortedDict()

    if date not in data[country]:
        data[country][date] = [0, 0, 0]

    try:
        data[country][date][category] += n
    except TypeError:
        pass


def append_global(data, category, date, n):
    if date not in data:
        data[date] = [0, 0, 0]

    data[date][category] += n


def get_table(url, LIST=True):
    res = request(url)
    itr = csv.reader(res.splitlines())

    return list(itr) if LIST else itr


def format_date(date, format):
    time = datetime \
        .strptime(str(date), format) \
        .strftime(C.format('ymd'))

    return time


def request(url):
    try:
        return urllib.request.urlopen(url).read().decode('utf-8')

    except urllib.error.HTTPError as e:
        print("HTTPError: {}".format(e.code))

    except urllib.error.URLError as e:
        print("URLError: {}".format(e.reason))

    except http.client.HTTPException as e:
        print("HTTPException: {}".format(e))

    except Exception as e:
        print("Exception: {}".format(e))


def print_countries(countries):
    prev = ''
    for i, c in enumerate(countries):
        if i % 2 == 0:
            prev = c
        else:
            print(C.CTABLE.format(c, prev))


def print_all(data, param):
    print_header(C.GHEADER)

    keys = find_keys(data)
    for k, v in sort(data, param, keys):

        key = v.keys()[-1]

        first = k
        n = v[key][0]
        dead = v[key][1]
        recovered = v[key][2]

        print_elements(C.GTABLE, first, n, dead, recovered)


# because csv files are not synced (dates)
def find_keys(data):
    keys = []
    v = data.values()[-1]
    for i in range(-2, 0):
        keys.append(v.keys()[i])

    return keys


def sort(data, param, keys):
    e = C.sort_by(param)

    if e is not None:
        return sorted(
            data.items(),
            key=lambda c: (
                c[1][keys[0]][e]
                if keys[0] in c[1]
                else c[1][keys[1]][e]))
    else:
        return data.items()


def print_global(data):
    print_header(C.HEADER)

    for k, v in data.items():

        date = k
        n = v[0]
        dead = v[1]
        recovered = v[2]

        print_elements(C.TABLE, date, n, dead, recovered)


def print_country(data):
    if not data:
        print(C.INVALID)
    else:
        print_header(C.HEADER)

        for data in data.values():
            for k, v in data.items():

                date = k
                n = v[0]
                dead = v[1]
                recovered = v[2]

                print_elements(C.TABLE, date, n, dead, recovered)


def print_elements(body, first, n, dead, recovered):
    print(body.format(
        first,
        color.blue(n),
        color.red(dead),
        color.green(recovered)))


def print_header(header):
    l, h = C.header(header)
    print(color.dim(l))
    print(color.dim(h))
    print(color.dim(l))


class api:
    URL = 'https://raw.githubusercontent.com/CSSEGISandData' \
        '/COVID-19/master/csse_covid_19_data'

    TS = '/csse_covid_19_time_series/'
    TC = 'time_series_covid19_confirmed_global.csv'
    TD = 'time_series_covid19_deaths_global.csv'
    TR = 'time_series_covid19_recovered_global.csv'

    @staticmethod
    def append_url(path):
        return api.URL + api.TS + path

    @staticmethod
    def urls():
        return [
            api.append_url(api.TC),
            api.append_url(api.TD),
            api.append_url(api.TR)]


class C:
    EMPTY = ''
    COUNTRIES = '-l'
    ALL = '-a'
    GLOBAL = '-g'
    COUNTRY = r'.'
    INVALID = 'INVALID COUNTRY'
    USAGE = 'usage: ./corona.py [-l | -g | -a [c|d|r] | COUNTRY]'

    HEADER = '{:s}{:>17s}{:>13s}{:>13s}'.format(
        "Date", "Confirmed", "Deaths", "Recovered")
    TABLE = '{:s}{:>22s}{:>22s}{:>22s}'

    GHEADER = '{:<23s}{:>23s}{:>13s}{:>13s}'.format(
        "Country", "Confirmed", "Deaths", "Recovered")
    GTABLE = '{:<33s}{:>22s}{:>22s}{:>22s}'

    CTABLE = '{:<40s}{:<40s}'

    @staticmethod
    def regex(c):
        return r'\b' + re.escape(c) + r'\b'

    @staticmethod
    def format(arg):
        return {
            'mdY': '%m-%d-%Y',
            'mdy': ['%m/%d/%y', '%m/%d/%Y'],
            'Ymd': '%Y-%m-%d',
            'ymd': '%y-%m-%d'
        }[arg]

    @staticmethod
    def sort_by(arg):
        try:
            return {
                'c': 0,
                'd': 1,
                'r': 2
            }[arg]

        except KeyError:
            return None

    @staticmethod
    def header(head):
        return C.line(head), head

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
