def f(x):
    return x * x
r = map(f, [1, 2, 3, 4, 5, 6, 7, 8, 9])
print(list(r))


from functools import reduce
print(reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]))


def is_odd(n):
    return n % 2 == 1

a = filter(is_odd, [1, 2, 4, 5, 6, 9, 10, 15])
print(list(a))