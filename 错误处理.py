# -*- coding: utf-8 -*-


class FooError(ValueError):
    pass


import logging


def foo(s):
    return 10 / int(s)


def bar(s):
    return foo(s) * 2


def main():
    try:
        bar('0')
    except ZeroDivisionError as e:
        logging.error('除数为0')
    except Exception as e:
        logging.exception(e)
    else:
        logging.info('normal')


main()
print('END')
