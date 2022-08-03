# -*- coding: utf-8 -*-
from enum import Enum

Month = Enum('Month', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))
print(Month)
for name, member in Month.__members__.items():
    print(name, '=>', member, ',', member.value)

from enum import Enum, unique


@unique
class Weekday(Enum):
    Sun = 0  # Sun的value被设定为0
    Mon = 1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6


def fn(self, name='world'):  # 先定义函数
    print('Hello, %s.' % name)


Hello = type('Hello', (object,), dict(hello=fn))  # 创建Hello class
fun = dir(Hello)
print(fun)


# metaclass是类的模板，所以必须从`type`类型派生：
class ListMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        """
        :param name:类的名字
        :param bases:类继承的父类集合
        :param attrs:类的方法集合
        """
        attrs['add'] = lambda self, value: self.append(value)
        return type.__new__(mcs, name, bases, attrs)


class MyList(list, metaclass=ListMetaclass):
    pass
