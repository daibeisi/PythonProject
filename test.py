#!/usr/bin/env python
import os
import cProfile
import random

lln = [random.random() for _ in range(100000)]

def f1(lis):
    l1_ = sorted(lis)
    l2_ = [i for i in l1_ if i < 0.5]
    return l2_


def f2(lis):
    l1_ = [i for i in lis if i > 0.5]
    l2_ = sorted(l1_)
    return l2_


def f3(lis):
    l1_ = [i*i for i in lis]
    l2_ = sorted(l1_)
    return [i for i in l2_ if i < (0.5*0.5)]

def main():
    # cProfile.run('f1(lln)')
    名字 = "陈帅"
    print(名字)
    # cProfile.run('f2(lln)')
    # cProfile.run('f3(lln)')


if __name__ == '__main__':
    main()
    exit(0)