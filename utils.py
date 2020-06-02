#!/usr/bin/python3


def info():
    return color.green("[INFO]")


def debug():
    return color.blue("[DBUG]")


def error():
    return color.red("[ERRR]")


def warn():
    return color.yellow("[WARN]")


class color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    DEFAULT = '\033[0m'
    BOLD = "\033[1m"
    DIM = '\033[2m'

    @staticmethod
    def green(output):
        return color.GREEN + str(output) + color.DEFAULT

    @staticmethod
    def red(output):
        return color.RED + str(output) + color.DEFAULT

    @staticmethod
    def yellow(output):
        return color.YELLOW + str(output) + color.DEFAULT

    @staticmethod
    def blue(output):
        return color.BLUE + str(output) + color.DEFAULT

    @staticmethod
    def dim(output, pre=None, post=None):
        return color.DIM + \
            ('' if pre is None else pre) + \
            str(output) + \
            ('' if post is None else post) + \
            color.DEFAULT
