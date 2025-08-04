class Operation:
    _number_a = None
    _number_b = None

    @classmethod
    def get_number_a(cls):
        return cls._number_a

    @classmethod
    def get_number_b(cls):
        return cls._number_b

    @classmethod
    def set_number_a(cls, value):
        cls._number_a = value

    @classmethod
    def set_number_b(cls, value):
        cls._number_b = value

    @classmethod
    def get_result(cls):
        pass


class OperationAdd(Operation):

    @classmethod
    def get_result(cls):
        return cls._number_a + cls._number_b


class OperationSub(Operation):

    @classmethod
    def get_result(cls):
        return cls._number_a - cls._number_b


class OperationMul(Operation):

    @classmethod
    def get_result(cls):
        return cls._number_a * cls._number_b


class OperationDiv(Operation):

    @classmethod
    def get_result(cls):
        if cls._number_b == 0:
            raise ZeroDivisionError("除数不能为0")
        return cls._number_a / cls._number_b


class OperationFactory(Operation):

    @staticmethod
    def create_operation(operation):
        if operation == "+":
            return OperationAdd()
        if operation == "-":
            return OperationSub()
        if operation == "*":
            return OperationMul()
        if operation == "/":
            return OperationDiv()


if __name__ == '__main__':
    operation = OperationFactory.create_operation("/")
    operation.set_number_a(1)
    operation.set_number_b(100)
    print(operation.get_result())