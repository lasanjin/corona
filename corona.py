#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import http.client
import urllib.error
import urllib.request
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta, date


def main():
    data = get_data()
    print_data(data)


def get_data():
    data = []
    queue = build_queue()

    for i in range(queue.qsize()):
        thread = Thread(target=get_data_thread,
                        args=(queue, data))
        thread.daemon = True
        thread.start()

    queue.join()

    return data


def build_queue():
    queue = Queue()

    for dt in const.DATE_RANGE:
        d = dt.strftime("%m-%d-%Y")
        queue.put(d)

    return queue


def get_data_thread(queue, data):
    while not queue.empty():
        dt = queue.get()

        table = get_csv(dt)

        for row in table:
            if row[1] == const.COUNTRY:

                # row[2] date is wrong in some cases (stick to date of csv)
                date = format_time(dt)
                n = row[3]
                dead = row[4]
                recovered = row[5]

                data.append((date, n, dead, recovered))

        queue.task_done()


def get_csv(dt):
    url = api.url(dt)
    res = request(url)

    if res is not None:
        table = csv.reader(res.splitlines())
    else:
        table = ''

    return table


def format_time(time):
    format = '%m-%d-%Y'
    # format = '%Y-%m-%dT%H:%M:%S'
    time = datetime \
        .strptime(time, format) \
        .strftime('%y-%m-%d')

    return time


def daterange(start, end):
    for n in range(int((end - start).days)+1):
        yield start + timedelta(n)


def request(url):
    try:
        return urllib.request.urlopen(url).read().decode('utf-8')

    # skip printing, because todays data may not be available yet
    except urllib.error.HTTPError as e:
        #print("HTTPError: {}".format(e.code))
        return

    except urllib.error.URLError as e:
        #print("URLError: {}".format(e.reason))
        return

    except http.client.HTTPException as e:
        #print("HTTPException: {}".format(e))
        return

    except Exception as e:
        #print("Exception: {}".format(e))
        return


def print_data(data):
    print()
    print_header()

    for data in sorted(data, key=lambda tup: tup[0]):

        date = str(data[0])
        n = str(data[1])
        dead = str(data[2])
        recovered = str(data[3])

        print(const.TABLE.format(
            date,
            color.blue(n),
            color.red(dead),
            color.green(recovered)))

    print()


def print_header():
    print(color.dim(const.LINE))
    print(color.dim(const.HEADER))
    print(color.dim(const.LINE))


class api:
    API = 'https://raw.githubusercontent.com/' \
        'CSSEGISandData/COVID-19/master/' \
        'csse_covid_19_data/csse_covid_19_daily_reports/'

    @staticmethod
    def url(date):
        return api.API + date + '.csv'


class color:
    DEFAULT = '\033[0m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    DIM = '\033[2m'

    @staticmethod
    def dim(output):
        return color.DIM + output + color.DEFAULT

    @staticmethod
    def green(output):
        return color.GREEN + output + color.DEFAULT

    @staticmethod
    def blue(output):
        return color.BLUE + output + color.DEFAULT

    @staticmethod
    def red(output):
        return color.RED + output + color.DEFAULT


class const:
    COUNTRY = 'Sweden'
    START_DATE = date(2020, 2, 1)
    END_DATE = date.today()
    DATE_RANGE = daterange(START_DATE, END_DATE)
    TABLE = '{:s}{:>22s}{:>22s}{:>22s}'
    HEADER = '{:s}{:>17s}{:>13s}{:>13s}'.format(
        "Date", "Confirmed", "Deaths", "Recovered")
    LINE = '-' * len(HEADER.expandtabs())


if __name__ == "__main__":
    main()
