#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import csv
import json
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
        cs = get_countries()
        print_countries(cs)

    elif cmd == C.ALL:
        data = get_data(False)
        print_all(data, s)

    elif cmd == C.GLOBAL:
        data = get_data(True, True)
        print_global(data)

    else:
        c = C.regex(cmd)
        data = get_data(True, False, c)
        print_country(data)

    # jd = json.dumps(data, indent=2, ensure_ascii=False)  # Testing purposes


def get_countries():
    url = api.append_url(api.TC)
    table = get_table(url, False)
    countries = SortedSet(key=str.lower)

    for row in table:
        country = parse_country_name(row)
        countries.add(country)

    return countries


def parse_country_name(row):
    h, s, t = str(row[1]).strip('*').partition(',')

    return h


def get_data(ALL=True, GLOBAL=False, COUNTRY=None):
    data = SortedDict()
    queue = build_queue()  # thread for each csv document

    for i in range(queue.qsize()):
        thread = Thread(target=get_data_thread,
                        args=(queue, data, ALL, GLOBAL, COUNTRY))
        thread.daemon = True
        thread.start()

    queue.join()

    apppend_percentage(data, GLOBAL, COUNTRY)  # possible when threads finish

    return data


def apppend_percentage(data, GLOBAL, COUNTRY):
    if not GLOBAL and COUNTRY is None:
        for k, v in data.items():
            date = v.keys()[-1]
            v[date]['%'][0] = calc_percentage(
                v[date]['TOT'][0], v[date]['TOT'][1])


def calc_percentage(n, dead):
    try:
        p = round(100 * dead / n, 1)
        return 0 if p == 0.0 else p

    except ZeroDivisionError as e:
        return 0


def build_queue():
    queue = PriorityQueue()

    for category, url in enumerate(api.urls()):
        queue.put((category, url))

    return queue


def get_data_thread(queue, data, ALL, GLOBAL, COUNTRY):
    while not queue.empty():
        q = queue.get()
        category = q[0]
        url = q[1]

        table = get_table(url)
        end = len(table[0])
        start = end - 2 if not ALL else 4  # get only latest data (2 days)

        prev = dict()  # new cases
        for col in range(start, end):  # for each date, iterate all countries

            dt = table[0][col]
            date = parse_date(dt)  # csv files look different

            if GLOBAL and date not in data:  # don't overwrite data
                data[date] = [0] * 3

            for row in table[1:]:

                try:
                    n = int(row[col])
                except ValueError:
                    n = 0

                if GLOBAL:
                    # {date: [n, dead, recovered]}
                    data[date][category] += n

                else:
                    country = parse_country_name(row)
                    match = True \
                        if COUNTRY is None \
                        else re.search(COUNTRY, country.lower())

                    if match:
                        append_data(data, category, country, date, n)
                        append_new_cases(prev, data, category,
                                         country, date, n)

        queue.task_done()


def append_data(data, category, country, date, n):
    if country not in data:
        data[country] = SortedDict()

    if date not in data[country]:
        data[country][date] = dict()

    if 'TOT' not in data[country][date]:
        data[country][date]['TOT'] = [0] * 3
        data[country][date]['%'] = [0]  # [] for sorting reasons

    # {country: {date: {'TOT' [n, dead, recovered]}}}
    data[country][date]['TOT'][category] += n


def append_new_cases(prev, data, category, country, date, n):
    if country not in prev:
        prev[country] = [0] * 3

    if 'NEW' not in data[country][date]:
        # {country: {date: {'NEW' [n, dead, recovered]}}}
        data[country][date]['NEW'] = [0] * 3

    current = data[country][date]['TOT'][category]
    data[country][date]['NEW'][category] += \
        current - prev[country][category]

    prev[country][category] = current


def parse_date(dt):
    f = C.format('mdy')
    try:
        return format_date(dt, f[0])
    except ValueError:
        return format_date(dt, f[1])


def format_date(date, format):
    time = datetime \
        .strptime(str(date), format) \
        .strftime(C.format('ymd'))

    return time


def print_countries(countries):
    prev = ''
    for i, c in enumerate(countries):
        if i % 2 == 0:
            prev = c
        else:
            print(C.CTABLE.format(c, prev))


def print_all(data, param):
    print_header(C.AHEADER)

    keys = find_keys(data)  # csv files are not always synced (dates)
    for k, v in sort(data, param, keys):

        date = v.keys()[-1]  # csv files are not always synced (dates)
        first = k

        n = v[date]['TOT'][0]
        dead = v[date]['TOT'][1]
        recovered = v[date]['TOT'][2]

        new_n = v[date]['NEW'][0]
        new_d = v[date]['NEW'][1]
        new_r = v[date]['NEW'][2]

        p = v[date]['%'][0]

        print_elements(first, n, new_n, dead, new_d, recovered, new_r, p, True)


def find_keys(data):
    keys = []
    v = data.values()[-1]
    for i in range(-2, 0):
        keys.append(v.keys()[i])

    return keys


def sort(data, param, keys):
    s = C.sort_by(param)

    if s is not None:
        return sorted(
            data.items(),
            key=lambda c: (
                c[1][keys[1]][s[0]][s[1]]
                if keys[1] in c[1]
                else c[1][keys[0]][s[0]][s[1]]))
    else:
        return data.items()


def print_global(data):
    print_header(C.GHEADER)

    prev = [0] * 3
    for k, v in data.items():

        date = k
        n = v[0]
        dead = v[1]
        recovered = v[2]

        new_n = n - prev[0]
        new_d = dead - prev[1]
        new_r = recovered - prev[2]

        print_elements(date, n, new_n, dead, new_d, recovered, new_r)

        prev[0] = n
        prev[1] = dead
        prev[2] = recovered


def print_country(data):
    if not data:
        print(C.INVALID)
    else:
        print_header(C.GHEADER)

        prev = [0] * 3
        for country in data.values():
            for k, v in country.items():

                date = k
                n = v['TOT'][0]
                dead = v['TOT'][1]
                recovered = v['TOT'][2]

                new_n = v['NEW'][0]
                new_d = v['NEW'][1]
                new_r = v['NEW'][2]

                print_elements(date, n, new_n, dead, new_d,
                               recovered, new_r, None)


def print_elements(first, n, new_n, dead, new_d, recovered, new_r, p=None, ALL=False):
    f = C.ATABLE if ALL else C.GTABLE
    p = calc_percentage(n, dead) if p is None else p

    print(f.format(
        first,
        color.blue(n),
        color.dim(new_n, '+'),
        color.red(str(dead)),
        color.dim(str(p), None, '%'),
        color.dim(new_d, '+'),
        color.green(recovered),
        color.dim(new_r, '+')))


def print_header(header):
    l, h = C.header(header)
    print(color.dim(l))
    print(color.dim(h))
    print(color.dim(l))


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


def get_table(url, LIST=True):
    res = request(url)
    itr = csv.reader(res.splitlines())

    return list(itr) if LIST else itr


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
    USAGE = 'Usage: ./corona.py [-l | -g | -a [c|d|r|cn|dn|rn|p] | COUNTRY]\n' \
        '\n-l: List countries' \
        '\n-g: List global data' \
        '\n-a: List all countries data' \
            '\n\t\tc:  Cases' \
            '\n\t\td:  Dead:' \
            '\n\t\tr:  Recovered' \
            '\n\t\t*n: New cases' \
            '\n\t\tp:  Percentage' \
        '\n\nExamples:' \
            '\n\t\t./corona.py -g' \
            '\n\t\t./corona.py -a cn' \
            '\n\t\t./corona.py sweden'
    CTABLE = '{:<40s}{:<40s}'
    GTABLE = '{:<15}{:>16}{:>19}{:>20}{:>15}{:>19}{:>20}{:>19}'
    GHEADER = '{:<11s}{:>11s}{:>11s}{:>11s}{:>7}{:>11s}{:>11s}{:>11s}'.format(
        "Date", "Confirmed", "C. New", "Deaths", "%", "D. New", "Recovered", "R. New")
    ATABLE = '{:<32}{:>16}{:>19}{:>20}{:>15}{:>19}{:>20}{:>19}'
    AHEADER = '{:<28s}{:>11s}{:>11s}{:>11s}{:>7}{:>11s}{:>11s}{:>11s}'.format(
        "Date", "Confirmed", "C. New", "Deaths", "%", "D. New", "Recovered", "R. New")

    @staticmethod
    def regex(c):
        return r'\b' + re.escape(str(c).lower()) + r'\b'

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
                'c': ['TOT', 0],
                'd': ['TOT', 1],
                'r': ['TOT', 2],
                'cn': ['NEW', 0],
                'dn': ['NEW', 1],
                'rn': ['NEW', 2],
                'p': ['%', 0]
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
    def dim(output, pre=None, post=None):
        return color.DIM + \
            ('' if pre is None else pre) + \
            str(output) + \
            ('' if post is None else post) + \
            color.DEFAULT

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
