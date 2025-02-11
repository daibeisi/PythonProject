#!/usr/bin/env python
# -*- coding: utf-8 -*-

def callback(*args):
    print(*args)


def caller(func, args, kwargs=None):
    if kwargs is None:
        kwargs = {}
    func(*args, **kwargs)


if __name__ == '__main__':
    caller(callback, (1, 2))
