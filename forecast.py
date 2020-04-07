#!/usr/bin/python
# -*- coding: utf-8 -*-

import corona
import numpy
from datetime import datetime, timedelta
from sys import argv
from scipy.optimize import curve_fit
try:
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import matplotlib.dates as mdate
except ImportError:
    pass

from scipy.special import expit, logit

ndays = 7  # ndays forecast
SHOW = True  # show graph


def main():
    country = get_params()

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

    # Get everything for plot & print
    a, k_exp, b = get_exp_func(data, cc)
    B = 0  # b  # b-value in exp function
    L, k_log, x0 = get_logistic_func(data, cc)
    xarr, yarr, dates = build_func_data(data, cc)

    # Print functions and data
    print_exp_func(a, k_exp, B)
    print_logistic_func(L, k_log, x0)
    print_forecast(L, k_log, x0, a, k_exp, B, dates, yarr, ndays)

    # Print last expected date and estimated number of confirmed cases based on logistic function
    start = datetime.strptime(dates[0], "%y-%m-%d").date()
    days = calc_last_day(k_log, x0)
    date = start + timedelta(days=days)
    conf = logistic(days, L, k_log, x0)
    print('\n{}\t{}'.format(C.LASTD, date))
    print('{}\t\t{}\n'.format(C.EST, int(conf)))

    # Plot graph
    try:
        # Generate dates for x-axis
        x_values = [start + timedelta(days=x)
                    for x in range(len(dates) + ndays)]

        # Generate y-values
        x = numpy.linspace(0, len(x_values), num=len(x_values))
        y_values_exp = exponential(x, *[a, k_exp, B])
        y_values_log = logistic(x, *[L, k_log, x0])

        # Set size
        plt.rcParams['figure.figsize'] = [16, 9]
        plt.rc('font', size=8)

        # Format x-axis & y-axis
        fig, ax = plt.subplots()
        fig.autofmt_xdate()
        formatter = mdate.DateFormatter('%y-%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.get_xaxis().set_major_locator(mdate.DayLocator(interval=7))
        ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

        plt.scatter(
            x_values[:len(xarr)],
            yarr,
            zorder=3,
            marker='o',
            s=40,
            alpha=0.75,
            edgecolors="dimgrey",
            color="lightgrey",
            label="Real")

        plt.plot(
            x_values,
            y_values_exp,
            marker='.',
            markersize=4,
            linewidth=1,
            color='firebrick',
            label="Exponential")

        plt.plot(
            x_values,
            y_values_log,
            marker='.',
            markersize=4,
            linewidth=1,
            color='green',
            label="Logistic")

        plt.grid()
        plt.legend()
        plt.xlabel("Number of days")
        plt.ylabel("Number of confirmed cases")
        plt.show()

    except Exception as e:
        print(C.ERROR)


def calc_last_day(k, x0):
    # Estimating last day with threshold very close to 1
    # Exactly 1 will take infinitely long time
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
        p0=(0, 0.1, 0),
        maxfev=100000)

    r = 5
    a, k, b = popt

    return round(a, r), round(k, r), round(b, r)


def get_logistic_func(data, country=None):
    xarr, yarr, dates = build_func_data(data, country)

    # Use maxfev to set a high number of iterations to assure it will converge
    popt, pcov = curve_fit(
        logistic,
        xarr,
        yarr,
        p0=(0, 1, 0),  # Avoid "overflow encountered in exp" (Should not affect result)
        maxfev=100000)

    r = 5
    L, k, x0 = popt

    return round(L, r), round(k, r), round(x0, r)


def build_func_data(data, country):
    dates = []
    xarr = []
    yarr = []

    for x, (k, v) in enumerate(iterate(data, country)):
        dates.append(k)

        y = int(v[0]) if country is None else int(v['TOT'][0])
        yarr.append(y)
        xarr.append(x)

    return xarr, yarr, dates


def iterate(data, country):
    return data.items() if country is None else data[country].items()


def print_exp_func(a, k, b):
    # a*e^(x*k)+b
    print('\nEXPONENTIAL: {}e^({}x)+{}'.format(a, k, b))


def print_logistic_func(L, k, x0):
    # L/(1+e^(-k*(x-x0)))
    print('\nLOGISTIC: {}/e^(-{}*(x-{}))'.format(L, k, x0))


def print_forecast(L, k_log, x0, a, k_exp, b, dates, data, ndays):
    print_header()

    for x, date in enumerate(dates):
        print_value(date, data[x], x, L, k_log, x0, a, k_exp, b)

    last = datetime.strptime(dates[-1], "%y-%m-%d")
    start = len(dates)
    end = start + ndays

    for i, x in enumerate(range(start, end)):
        date = next_date(last, i)
        print_value(date, 'NaN', x, L, k_log, x0, a, k_exp, b)


def print_value(date, real, x, L, k_log, x0, a, k_exp, b):
    log = int(logistic(x, L, k_log, x0))
    exp = int(exponential(x, a, k_exp, b))

    print(C.TABLE.format(date, real, exp, log))


def next_date(last, i):
    next_date = last + timedelta(days=(i + 1))
    date = next_date.strftime("%y-%m-%d")

    return date


def print_header():
    l, h = C.header(C.HEADER)
    print()
    print(l)
    print(h)
    print(l)


def get_params():
    try:
        return argv[1:][0].capitalize()

    except IndexError:
        return None


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
    ERROR = "\nIMPORT \"matplotlib\" TO PLOT GRAPH ?\n"
    LASTD = "LAST DAY BASED ON LOGISTIC FUNCTION:"
    EST = 'ESTIMATED INFECTED ON LAST DAY:'

    TABLE = '{:10}{:>12}{:>12}{:>12}'
    HEADER = '{:10}{:>12}{:>12}{:>12}'.format('Date', 'Real', 'Exp', 'Log')

    @staticmethod
    def header(head):
        return C.line(head), head

    @staticmethod
    def line(head):
        return '-' * len(head.expandtabs())


if __name__ == "__main__":
    main()
