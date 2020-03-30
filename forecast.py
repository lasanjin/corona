#!/usr/bin/python
# -*- coding: utf-8 -*-

import corona
import numpy
import datetime
from sys import argv
from scipy.optimize import curve_fit


def main():
    country = get_params()

    if country is None:
        data = corona.get_data(True, True)

    else:
        c = corona.C.regex(country)
        data = corona.get_data(True, True, c)

    a, k, b, dates = get_function(data, country)
    ndays = 0  # ndays forecast
    _b = 0  # b-value in exp function

    print_function(a, k, dates, _b)
    print_forecast(a, k, dates, ndays, _b)


def get_params():
    try:
        return argv[1:][0].capitalize()

    except IndexError:
        return None


def exponential(x, a, k, b):
    return a * numpy.exp(x * k) + b  # a*e^(x*k)+b


def get_function(data, country):
    xarr = []
    yarr = []
    dates = []
    x = 1

    for k, v in data.items():
        y = int(v[0])

 #       if y > 0:
        yarr.append(y)
        xarr.append(x)
        dates.append(k)

        x += 1

    # p0 = scipy.optimize.curve_fit() will gueress a value of 1 for all parameters
    # This is generally not a good idea
    # Always explicitly supply own initial guesses
    popt, pcov = curve_fit(exponential, xarr, yarr, p0=(0, 0.1, 0))
    r = 5
#    print(popt, pcov)
#    quit()

    return round(popt[0], r), round(popt[1], r), round(popt[2], r), dates


def print_function(a, k, dates, b=0):
    print('{}e^({}x) + {}'.format(a, k, b))  # a*e^(x*k)+b
    print()


def print_forecast(a, k, dates, n, b=0):
    for x, date in enumerate(dates):
        print('{}\t{}'.format(date, int(a * numpy.exp(x * k) + b)))

    last = datetime.datetime.strptime(dates[-1], "%y-%m-%d")

    start = len(dates)
    end = start + n

    for i, x in enumerate(range(start, end)):
        date = next_date(last, i)

        print('{}\t{}'.format(date, int(a * numpy.exp(x * k) + b)))


def next_date(last, i):
    next_date = last + datetime.timedelta(days=(i + 1))
    date = next_date.strftime("%y-%m-%d")

    return date


if __name__ == "__main__":
    main()