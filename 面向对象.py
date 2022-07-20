import datetime

class Animal:
    """动物类

    """
    # 类变量
    name1 = "动物类"

    def __init__(self, name):
        # 成员变量
        self._name = name

    def __new__(cls, *args, **kwargs):
        print("new")
        return super().__new__(cls)

    def __call__(self, *args, **kwargs):
        print("call")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    # 成员方法
    def eat(self):
        pass

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


if __name__ == '__main__':

    cat = Animal("cat")
    print(cat.name)