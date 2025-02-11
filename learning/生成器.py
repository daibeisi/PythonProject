# -*- coding: utf-8 -*-
from collections.abc import Iterable, Iterator

g = (x * x for x in range(10))
print(isinstance(g, Iterable))
print(isinstance(g, Iterator))


def fib(m):
    n, a, b = 0, 0, 1
    while n < m:
        yield b
        a, b = b, a + b
        n = n + 1
    raise StopIteration


if __name__ == '__main__':
    g = fib(6)
    print(isinstance(g, Iterable))
    print(isinstance(g, Iterator))
    while 1:
        try:
            x = next(g)
            print('g:', x)
        except StopIteration as e:
            print('Generator return value:', e.value)
            break
