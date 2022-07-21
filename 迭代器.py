# -*- coding: utf-8 -*-
"""
凡是可作用于for循环的对象都是Iterable类型，Python的for循环本质上就是将Iterable转化为Iterator，通过不断调用next()函数实现的

凡是可作用于next()函数的对象都是Iterator类型，它们表示一个惰性计算的序列；

集合数据类型如list、dict、str等是Iterable但不是Iterator，不过可以通过iter()函数获得一个Iterator对象。
"""

from collections.abc import Iterable, Iterator

print(isinstance([1,2,3], Iterable))
print(isinstance([1,2,3], Iterator))
print(isinstance(iter([1,2,3]), Iterator))

for _ in [1,2,3]:
    print(_)

# ==============for循环等价于下面的=====================

# 首先获得Iterator对象:
iter_ = iter([1, 2, 3])
# 循环:
while 1:
    try:
        # 获得下一个值:
        print(next(iter_))
    except StopIteration:
        # 遇到StopIteration就退出循环
        break


class TestIter:
    def __init__(self, length):
        self.lis = [i for i in range(length)]
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.count < len(self.lis):
            ret = self.lis[self.count]
            self.count += 1
            return ret
        else:
            raise StopIteration

a = TestIter(3)
print(next(a))
print(next(a))
print(next(a))
print(isinstance(a, Iterable))
print(isinstance(a, Iterator))
pass