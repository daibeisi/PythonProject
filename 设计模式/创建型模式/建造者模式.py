# Product
class Computer:
    def __init__(self):
        self.cpu = None
        self.memory = None
        self.storage = None

    def __str__(self):
        return f"CPU: {self.cpu}, Memory: {self.memory}, Storage: {self.storage}"


# Builder
class Builder:
    def build_cpu(self): pass

    def build_memory(self): pass

    def build_storage(self): pass

    def get_result(self): pass


# ConcreteBuilder
class GamingComputerBuilder(Builder):
    def __init__(self):
        self.computer = Computer()

    def build_cpu(self):
        self.computer.cpu = "Intel i9"

    def build_memory(self):
        self.computer.memory = "32GB DDR5"

    def build_storage(self):
        self.computer.storage = "1TB NVMe SSD"

    def get_result(self):
        return self.computer


# Director
class Director:
    def __init__(self, builder: Builder):
        self._builder = builder

    def construct(self):
        self._builder.build_cpu()
        self._builder.build_memory()
        self._builder.build_storage()
        return self._builder.get_result()


if __name__ == "__main__":
    # 使用
    builder = GamingComputerBuilder()
    director = Director(builder)
    computer = director.construct()

    print(computer)
    # 输出: CPU: Intel i9, Memory: 32GB DDR5, Storage: 1TB NVMe SSD
