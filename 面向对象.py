# -*- coding: utf-8 -*-
import datetime

class Animal:
    """动物类

    """
    __slots__ = ('_name', '__age')  # 用tuple定义实例允许绑定的属性名称
    # 类变量
    name1 = "动物类"

    def __init__(self, name, age):
        print("init")
        # 成员变量
        self._name = name
        self.__age = age

    def __new__(cls, *args, **kwargs):
        print("new")
        return super().__new__(cls)

    def __call__(self, *args, **kwargs):
        print("call")

    def __getattr__(self, path):
        return path

    def __str__(self):
        return 'Animal object (name: %s)' % self._name

    __repr__ = __str__

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self.__age

    @name.setter
    def name(self, name):
        self._name = name

    @age.setter
    def age(self, age):
        if not isinstance(age, int):
            raise ValueError('age must be an integer!')
        self.__age = age

    # 成员方法
    def eat(self):
        pass

    def __say(self):
        print("hello word")

    def __del__(self):
        print("{name}对象被清除".format(name = self.name))

    # 类方法
    @classmethod
    def get_cls_name(cls):
        return cls.name1

    # 静态方法
    @staticmethod
    def get_now_datatime():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Vertebrate(Animal):
    pass


class Invertebrate(Animal):
    pass


class Fish(Vertebrate):
    pass


class Mammal(Vertebrate):
    pass


class FlyableMixIn:
    pass


class RunnableMixIn:
    pass


if __name__ == '__main__':
    cat = Animal("cat",90)
    cat._Animal__say()
    cat._name = "111"
    cat.age = 10
    print(cat.name)
    print(dir(cat))
