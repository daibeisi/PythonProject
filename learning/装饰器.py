#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from functools import wraps


def timer(func):
    """计算函数执行时间装饰器"""
    @wraps(func)
    def wrapper(*args, **kw):
        start = time.time()
        result = func(*args, **kw)
        end = time.time()
        print(func.__name__,"耗时：", end - start)
        return result
    return wrapper

@timer
def print_hi(name):
    print(f'Hi, {name}')


if __name__ == '__main__':

    print_hi('PyCharm')