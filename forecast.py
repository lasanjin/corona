#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import corona
import numpy
import datetime
from sys import argv
from scipy.optimize import curve_fit
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass


ndays = 7  # ndays forecast
SHOW = False  # show graph


def main():
    func, country = get_params()

    if country is None:
        data = corona.get_data(True, True)
        cc = None

    else:
        c = corona.C.regex(country)
        data = corona.get_data(True, False, c)

        if not data:
            print(C.NO_COUNTRY)
            quit()

        cc = 'US' if country == 'Us' else country

    if func == C.EXP:
        a, k, b, dates, xy_data = get_exp_func(data, cc)
        B = 0  # b-value in exp function
        print_exp_func(a, k, B)

        if SHOW:
            show_graph([a, k, b], xy_data[0], xy_data[1])
        else:
            print_forecast(a, k, B, dates, ndays, C.EXP)

    elif func == C.LOG:
        L, k, x0, dates, xy_data = get_logistic_func(data, cc)
        print_exp_func(L, k, x0)

        if SHOW:
            last_day = calc_last_day(k, x0)
            show_graph([L, k, x0], xy_data[0], xy_data[1], False, last_day)
        else:
            print_forecast(L, k, x0, dates, ndays, C.LOG)

    else:
        print(C.USAGE)


def calc_last_day(k, x0):
    # Estimating last day with threshold very close to 1 (exactly 1 will take infinitely long time)
    threshold = 1.0001
    return int(round(
        (-1 / k) * numpy.log((1 - threshold) / (threshold * numpy.exp(-k) - 1)) + x0))


def exponential(x, a, k, b):
    return a * numpy.exp(x * k) + b  # a*e^(x*k)+b


def logistic(x, L, k, x0):
    return L / (1 + numpy.exp(-k * (x - x0)))  # L/(1+e^(-k*(x-x0)))


def get_exp_func(data, country=None):
    xarr, yarr, dates = build_func_data(data, country)

    # p0 = scipy.optimize.curve_fit() will gueress a value of 1 for all parameters
    # This is generally not a good idea
    # Always explicitly supply own initial guesses
    popt, pcov = curve_fit(
        exponential,
        xarr,
        yarr,
        p0=(0, 0.1, 0))

    r = 5
    a, k, b = popt

    return round(a, r), round(k, r), round(b, r), dates, [xarr, yarr]


def get_logistic_func(data, country=None):
    xarr, yarr, dates = build_func_data(data, country)

    # Use maxfev to set a high number of iterations to assure it will converge
    popt, pcov = curve_fit(
        logistic,
        xarr,
        yarr,
        maxfev=10000000,
        p0=(0, 0.1, 0))

    r = 5
    L, k, x0 = popt

    return round(L, r), round(k, r), round(x0, r), dates, [xarr, yarr]


def build_func_data(data, country):
    xarr = []
    yarr = []
    dates = []
    x = 1

    for k, v in iterate(data, country):
        dates.append(k)

        y = int(v[0]) if country is None else int(v['TOT'][0])
        yarr.append(y)
        xarr.append(x)

        x += 1

    return xarr, yarr, dates


def iterate(data, country):
    return data.items() if country is None else data[country].items()


def show_graph(popt, xarr, yarr, EXP=True, LAST_DAY=None):
    ld = len(xarr) if LAST_DAY is None else LAST_DAY
    plot_x = numpy.linspace(0, ld)
    plot_y = exponential(plot_x, *popt) if EXP else logistic(plot_x, *popt)

    plt.plot(plot_x, plot_y, 'r-')
    plt.scatter(xarr, yarr)

    plt.show()


def print_exp_func(a, k, b):
    print('{}e^({}x)+{}'.format(a, k, b))  # a*e^(x*k)+b
    print()


def print_logistic_func(L, k, x0):
    print('{}/e^(-{}*(x-{}))'.format(L, k, x0))  # L/(1+e^(-k*(x-x0)))
    print()


def print_forecast(aL, k, bx0, dates, ndays, FUNC):
    for x, date in enumerate(dates):
        print_value(date, x, aL, k, bx0, FUNC)

    last = datetime.datetime.strptime(dates[-1], "%y-%m-%d")
    start = len(dates)
    end = start + ndays

    for i, x in enumerate(range(start, end)):
        date = next_date(last, i)
        print_value(date, x, aL, k, bx0, FUNC)


def print_value(date, x, aL, k, bx0, FUNC):
    if FUNC == C.EXP:
        print('{:15}{:>10}'.format(date, int(exponential(x, aL, k, bx0))))
    else:
        print('{:15}{:>10}'.format(date, int(logistic(x, aL, k, bx0))))


def next_date(last, i):
    next_date = last + datetime.timedelta(days=(i + 1))
    date = next_date.strftime("%y-%m-%d")

    return date


def get_params():
    try:
        f = argv[1:][0]
    except IndexError:
        print(C.USAGE)
        quit()

    try:
        c = argv[1:][1].capitalize()
        return f, c

    except IndexError:
        return f, None


class C:
    NO_COUNTRY = 'NO SUCH COUNTRY'
    EXP = '-e'
    LOG = '-l'
    USAGE = 'Usage: ./forecast.py -e | -l [COUNTRY]\n' \
        '\n-e: Exponential function' \
        '\n-l: Logistic function' \
        '\n\nExamples:' \
            '\n\t\t./forecast.py -e' \
            '\n\t\t./forecast.py -l sweden'


if __name__ == "__main__":
    main()
