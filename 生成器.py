# -*- coding: utf-8 -*-


g = (x * x for x in range(10))

def fib(m):
    n, a, b = 0, 0, 1
    while n < m:
        yield b
        a, b = b, a + b
        n = n + 1
    return 'done'


if __name__ == '__main__':
    g = fib(6)
    while 1:
        try:
            x = next(g)
            print('g:', x)
        except StopIteration as e:
            print('Generator return value:', e.value)
            break