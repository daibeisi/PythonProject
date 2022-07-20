#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import reduce


class Tool:
    @staticmethod
    def list_uniq(lis_:list) -> list:
        """列表去重"""
        return list(set(lis_))

    @staticmethod
    def list_keep_uniq(lis_:list) -> list:
        """列表保持原排序去重"""
        return sorted(set(lis_), key=lis_.index)

    @staticmethod
    def list_intersection(lis1_:list, lis2_:list) -> set:
        """列表相交元素集合"""
        return set(lis1_) & set(lis2_)

    @staticmethod
    def is_in_list(val_, lis_:list) -> bool:
        """值是否在列表中"""
        return val_ in set(lis_)

    @staticmethod
    def list_element2str(lis:list) -> list:
        """列表元素转化为字符串"""
        return list(map(lambda x: str(x), lis))

    @staticmethod
    def factorial(n:int) -> int:
        """阶乘"""
        return reduce(lambda x,y: x*y, range(1,n+1))

    @staticmethod
    def is_contain_chinese(check_str):
        """ 判断字符串中是否包含中文
        :param check_str: {str} 需要检测的字符串
        :return: {bool} 包含返回True， 不包含返回False
        """
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

if __name__ == '__main__':
    l1 = [1,7,2,3,'f',3,4,5,6,7]
    print(Tool.list_uniq(l1))
    print(Tool.list_keep_uniq(l1))
    l2 = ['a',2,9,853,'k']
    print(Tool.list_intersection(l1,l2))
    print(Tool.is_in_list(2,l2))
    print(Tool.list_element2str(l2))
    print(Tool.factorial(3))
    print(Tool.is_contain_chinese('dedqwe大'))