class Pair:
    """键值对"""

    def __init__(self, key: int, val: str):
        self.key = key
        self.val = val


class ArrayHashMap:
    """基于数组实现的哈希表"""

    def __init__(self):
        """构造方法"""
        # 初始化数组，包含 100 个桶
        self.buckets: list[Pair | None] = [None] * 100

    @staticmethod
    def __hash_func(key: int) -> int:
        """哈希函数"""
        index = key % 100
        return index

    def get(self, key: int) -> str | None:
        """查询操作"""
        index: int = self.__hash_func(key)
        pair: Pair = self.buckets[index]
        if pair is None:
            return None
        return pair.val

    def put(self, key: int, val: str):
        """添加操作"""
        pair = Pair(key, val)
        index: int = self.__hash_func(key)
        self.buckets[index] = pair

    def remove(self, key: int):
        """删除操作"""
        index: int = self.__hash_func(key)
        # 置为 None ，代表删除
        self.buckets[index] = None

    def items(self) -> list[tuple[int, str]]:
        for pair in self.buckets:
            if pair is not None:
                yield pair.key, pair.val

    def keys(self) -> list[int]:
        """获取所有键"""
        result = []
        for pair in self.buckets:
            if pair is not None:
                result.append(pair.key)
        return result

    def values(self) -> list[str]:
        """获取所有值"""
        result = []
        for pair in self.buckets:
            if pair is not None:
                result.append(pair.val)
        return result

    def print(self):
        """打印哈希表"""
        for pair in self.buckets:
            if pair is not None:
                print(pair.key, "->", pair.val)

    def __setitem__(self, key: int, val: str):
        self.put(key, val)

    def __getitem__(self, key: int) -> str:
        return self.get(key)

    def __delitem__(self, key: int):
        self.remove(key)

    def __contains__(self, key: int) -> bool:
        return self.get(key) is not None

    def __iter__(self):
        for pair in self.buckets:
            if pair is not None:
                yield pair.key, pair.val

    def __len__(self) -> int:
        return len(self.keys())

    def __str__(self) -> str:
        return str(self.items())

    def __repr__(self) -> str:
        return str(self.items())

    def __next__(self):
        for pair in self.buckets:
            if pair is not None:
                yield pair.key, pair.val
        raise StopIteration

    def pop(self, key: int) -> str:
        val: str = self.get(key)
        self.remove(key)
        return val


if __name__ == '__main__':
    # 初始化哈希表
    hmap: ArrayHashMap = ArrayHashMap()

    # 添加操作
    # 在哈希表中添加键值对 (key, value)
    hmap[12836] = "小哈"
    hmap[15937] = "小啰"
    hmap[16750] = "小算"
    hmap[13276] = "小法"
    hmap[10583] = "小鸭"

    # 查询操作
    # 向哈希表中输入键 key ，得到值 value
    name: str = hmap[15937]

    # 删除操作
    # 在哈希表中删除键值对 (key, value)
    hmap.pop(10583)

    # 遍历哈希表
    # 遍历键值对 key->value
    for key, value in hmap.items():
        print(key, "->", value)
    # 单独遍历键 key
    for key in hmap.keys():
        print(key)
    # 单独遍历值 value
    for value in hmap.values():
        print(value)
