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
        list_total()

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
    data = get_data()
    print_all(data, sort_by)


def list_total():
    data = get_data(C.GLOBAL)
    print_total(data)


def list_country(country):
    C.COUNTRY = r'\b' + re.escape(country) + r'\b'
    data = get_data()
    print_country(data)


def get_countries():
    url = api.append_url(api.TC)
    table = get_table(url)
    countries = SortedSet(key=str.lower)

    for row in table:
        country = parse_country(row)
        countries.add(country)

    return countries


def parse_country(row):
    h, s, t = str(row[1]).strip('*').partition(',')
    return h


def get_data(total=None):
    data = SortedDict()
    queue = build_total_queue()

    for i in range(queue.qsize()):
        thread = Thread(target=get_data_thread,
                        args=(queue, data, total))
        thread.daemon = True
        thread.start()

    queue.join()

    return data


def get_data_thread(queue, data, total):
    while not queue.empty():
        q = queue.get()
        category = q[0]
        url = q[1]

        table = get_table(url)
        end = len(table[0])

        for col in range(4, end):
            for row in table[1:]:
                country = parse_country(row)

                match = re.search(C.COUNTRY, country.lower())
                if match:

                    dt = table[0][col]
                    date = format_date(dt, C.format('mdy'))

                    try:
                        n = int(row[col])
                    except ValueError:
                        pass

                    append_data(total, data, category, country, date, n)

        queue.task_done()


def append_data(total, data, category, country, date, n):
    if total is None:
        append_all(data, category, country, date, n)
    else:
        append_total(data, category, date, n)


def append_all(data, category, country, date, n):
    if country not in data:
        data[country] = SortedDict()

    if date not in data[country]:
        data[country][date] = [0, 0, 0]

    try:
        data[country][date][category] += n
    except TypeError:
        pass


def append_total(data, category, date, n):
    if date not in data:
        data[date] = [0, 0, 0]

    data[date][category] += n


def get_date():
    t = date.today()
    y = t - timedelta(days=1)

    today = format_date(t, C.format('Ymd'))
    yesterday = format_date(y, C.format('Ymd'))

    return str(today), str(yesterday)


def build_total_queue():
    queue = PriorityQueue()

    for i, url in enumerate(api.total_stats()):
        queue.put((i, url))

    return queue


def get_table(url):
    res = request(url)
    itr = csv.reader(res.splitlines())

    return list(itr)


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
    print_header(C.THEADER)

    for k, v in sort(data, param):

        key = v.keys()[-1]
        date = k
        n = v.get(key)[0]
        dead = v.get(key)[1]
        recovered = v.get(key)[2]

        print_elements(C.TTABLE, date, n, dead, recovered)


def sort(data, param):
    today, yesterday = get_date()
    e = C.sort_by(param)

    if e is not None:
        return sorted(
            data.items(),
            key=lambda c: (
                c[1].get(today)[e]
                if today in c[1]
                else c[1].get(yesterday)[e]))
    else:
        return data.items()


def print_total(data):
    print_header(C.HEADER)

    for k, v in data.items():

        date = k
        n = v[0]
        dead = v[1]
        recovered = v[2]

        print(C.TABLE.format(
            date,
            color.blue(n),
            color.red(dead),
            color.green(recovered)))


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
    TC = 'time_series_19-covid-Confirmed.csv'
    TD = 'time_series_19-covid-Deaths.csv'
    TR = 'time_series_19-covid-Recovered.csv'

    @staticmethod
    def append_url(path):
        return api.URL + api.TS + path

    @staticmethod
    def total_stats():
        return [
            api.append_url(api.TC),
            api.append_url(api.TD),
            api.append_url(api.TR)]


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

    THEADER = '{:<23s}{:>23s}{:>13s}{:>13s}'.format(
        "Country", "Confirmed", "Deaths", "Recovered")
    TTABLE = '{:<33s}{:>22s}{:>22s}{:>22s}'

    CTABLE = '{:<40s}{:<40s}'

    @staticmethod
    def format(arg):
        return {
            'mdY': '%m-%d-%Y',
            'mdy': '%m/%d/%y',
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


if __name__ == "__main__":
    main()
