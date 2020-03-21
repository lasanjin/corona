#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import http.client
import urllib.error
from sys import argv
import urllib.request
from threading import Thread
from queue import PriorityQueue
from collections import OrderedDict
from datetime import datetime, timedelta, date
from modules.sortedcontainers import SortedSet, SortedDict


def main():
    p = get_params()

    if p == C.EMPTY:
        print(C.HOWTO)

    elif p == C.LIST:
        list_countries()

    elif p == C.SUM:
        list_total_confirmed()

    else:
        list_country(p)


def get_params():
    try:
        return ' '.join(argv[1:]).lower()
    except IndexError:
        return C.DEFAULT


def list_country(country):
    C.COUNTRY = country
    data = get_data()
    print_data(data)


def list_countries():
    cs = get_countries()
    print_countries(cs)
    quit()


def list_total_confirmed():
    t = get_total_confirmed()
    print_total_confirmed(t)
    quit()


def get_countries():
    table = get_csv()
    countries = SortedSet(key=str.lower)

    for row in table:
        h, s, t = str(row[1]).strip('*').partition(',')
        countries.add(h)

    return countries


def get_total_confirmed():
    table = list(get_csv())
    total = []

    end = len(table[0])
    count = 0

    for i in range(4, end):
        for row in table[1:]:
            count += int(row[i])

        date = table[0][i]
        time = format_time(date, C.format(2))
        total.append((time, count))

        count = 0

    return total


def get_data():
    data = SortedDict()
    queue = build_queue()

    for i in range(queue.qsize()):
        thread = Thread(target=get_data_thread,
                        args=(queue, data))
        thread.daemon = True
        thread.start()

    queue.join()

    return data


def build_queue():
    queue = PriorityQueue()

    for dt in C.DATE_RANGE:
        d = dt.strftime(C.format(0))
        queue.put(d)

    return queue


def get_data_thread(queue, data):
    while not queue.empty():
        dt = queue.get()

        table = get_csv(dt)

        for row in table:
            if str(row[1]).lower() == C.COUNTRY:

                # row[2] date is wrong in some cases (stick to date of csv)
                date = format_time(dt, C.format(0))
                n = int(row[3])
                dead = int(row[4])
                recovered = int(row[5])

                append_data(data, date, n, dead, recovered)

        queue.task_done()


def append_data(data, date, n, dead, recovered):
    if date in data:
        data[date][0] += n
        data[date][1] += dead
        data[date][2] += recovered
    else:
        data[date] = [n, dead, recovered]


def get_csv(dt=None):
    url = api.stats(dt) if dt else api.countries()
    res = request(url)
    table = csv.reader(res.splitlines())

    return table


def format_time(time, format):
    time = datetime \
        .strptime(time, format) \
        .strftime(C.format(1))

    return time


def daterange(start, end):
    for n in range(int((end - start).days) + 1):
        yield start + timedelta(n)


def request(url):
    try:
        return urllib.request.urlopen(url).read().decode('utf-8')

    # return '', because todays data may not be available yet
    except urllib.error.HTTPError as e:
        # print("HTTPError: {}".format(e.code))
        return ''

    except urllib.error.URLError as e:
        # print("URLError: {}".format(e.reason))
        return ''

    except http.client.HTTPException as e:
        # print("HTTPException: {}".format(e))
        return ''

    except Exception as e:
        # print("Exception: {}".format(e))
        return ''


def print_data(data):
    if not data:
        print('{} "{}"'.format(
            C.NO,
            C.COUNTRY))
    else:
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


def print_countries(countries):
    prev = ''
    for i, c in enumerate(countries):
        if i % 2 == 0:
            prev = c
        else:
            print(C.CTABLE.format(c, prev))


def print_total_confirmed(total):
    print_header(C.TOT_HEADER)

    for i in total:
        print(C.TOT_TABLE.format(
            color.dim(i[0]),
            color.blue(i[1])))


def print_header(header):
    l, h = C.header(header)
    print(color.dim(l))
    print(color.dim(h))
    print(color.dim(l))


class api:
    URL = 'https://raw.githubusercontent.com/CSSEGISandData' \
        '/COVID-19/master/csse_covid_19_data'
    STATS = '/csse_covid_19_daily_reports/'
    COUNTRIES = '/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'

    @staticmethod
    def stats(date):
        return api.URL + api.STATS + date + '.csv'

    @staticmethod
    def countries():
        return api.URL + api.COUNTRIES


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
    HOWTO = './corona.py [-s|-l|<country>]'
    LIST = '-l'
    SUM = '-s'
    DEFAULT = 'sweden'
    COUNTRY = None
    NO = 'No data on:'
    START_DATE = date(2020, 2, 1)
    END_DATE = date.today()
    DATE_RANGE = daterange(START_DATE, END_DATE)
    HEADER = '{:s}{:>17s}{:>13s}{:>13s}'.format(
        "Date", "Confirmed", "Deaths", "Recovered")
    TABLE = '{:s}{:>22s}{:>22s}{:>22s}'
    CTABLE = '{:<40s}{:<40s}'
    TOT_TABLE = '{:<20s}{:>20s}'
    TOT_HEADER = '{:s}{:>19s}'.format("Date", "Confirmed")

    @staticmethod
    def format(arg):
        return {
            0: '%m-%d-%Y',
            1: '%y-%m-%d',
            2: '%m/%d/%y'
        }[arg]

    @staticmethod
    def header(head):
        return C.line(head), head

    @staticmethod
    def line(head):
        return '-' * len(head.expandtabs())


if __name__ == "__main__":
    main()
