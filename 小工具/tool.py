#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import reduce


class Tool:
    @staticmethod
    def list_uniq(lis_: list) -> list:
        """列表去重"""
        return list(set(lis_))

    @staticmethod
    def list_keep_uniq(lis_: list) -> list:
        """列表保持原排序去重"""
        return sorted(set(lis_), key=lis_.index)

    @staticmethod
    def list_intersection(lis1_: list, lis2_: list) -> set:
        """列表相交元素集合"""
        return set(lis1_) & set(lis2_)

    @staticmethod
    def is_in_list(val_, lis_: list) -> bool:
        """值是否在列表中"""
        return val_ in set(lis_)

    @staticmethod
    def list_element2str(lis: list) -> list:
        """列表元素转化为字符串"""
        return list(map(lambda x: str(x), lis))

    @staticmethod
    def factorial(n: int) -> int:
        """阶乘"""
        return reduce(lambda x, y: x * y, range(1, n + 1))

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

    @staticmethod
    def bubble_sort(lis):
        """ 冒泡排序

        :param lis:
        :return:
        """
        for i in range(len(lis) - 1):
            for j in range(len(lis) - 1 - i):
                if lis[j] > lis[j + 1]:
                    lis[j], lis[j + 1] = lis[j + 1], lis[j]
        return lis

    @staticmethod
    def dict_list_sort(dict_list, size):
        """ 字典列表排序

        :param dict_list:
        :return:
        """
        dict_list.sort(key=size)
        return dict_list

    @staticmethod
    def binary_search(lis, value):
        """ 二分查找

        :param value:
        :return:
        """
        left = 0
        right = int(len(lis) - 1)
        while left < right:
            mid = int((right + left) / 2)
            if lis[mid] == value:
                return mid
            elif lis[mid] > value:
                right = mid
            else:
                left = mid
        else:
            if left == right and lis[left] == value:
                return left
            return None


if __name__ == '__main__':
    l1 = [1, 7, 2, 3, 3, 4, 5, 6, 7]
    # print(Tool.list_uniq(l1))
    # print(Tool.list_keep_uniq(l1))
    # l2 = ['a',2,9,853,'k']
    # print(Tool.list_intersection(l1,l2))
    # print(Tool.is_in_list(2,l2))
    # print(Tool.list_element2str(l2))
    # print(Tool.factorial(3))
    # print(Tool.is_contain_chinese('dedqwe大'))
    # print(Tool.bubble_sort(l1))
    print(Tool.binary_search([], 1))
    print(Tool.binary_search([1], 1))
    print(Tool.binary_search([2], 1))
    print(Tool.binary_search([1, 2, 3], 1))
    # student_score_list = [
    #     {
    #         'name': u"张三",
    #         'score': '85'
    #     },
    #     {
    #         'name': u"李四",
    #         'score': '60'
    #     },
    #     {
    #         'name': u"王五",
    #         'score': '70'
    #     }
    # ]
    #
    # def size(s):
    #     return int(s['score'])
    #
    # print(Tool.dict_list_sort(student_score_list, size))
