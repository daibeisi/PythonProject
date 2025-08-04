import copy


# 抽象原型（可选的）
class Prototype:
    def clone(self):
        return copy.deepcopy(self)


# 具体原型
class Robot(Prototype):
    def __init__(self, name, color, skills):
        self.name = name
        self.color = color
        self.skills = skills  # 列表类型

    def add_skill(self, skill):
        self.skills.append(skill)

    def __str__(self):
        return f"Robot(name={self.name}, color={self.color}, skills={self.skills})"


# 创建原型对象
original_robot = Robot("Alpha", "Red", ["Run", "Jump"])
print(f"Original: {original_robot}")

# 克隆原型对象
cloned_robot = original_robot.clone()
cloned_robot.name = "Beta"
cloned_robot.color = "Blue"
cloned_robot.add_skill("Shoot")

print(f"Cloned:   {cloned_robot}")
print(f"Original: {original_robot}")  # 原对象未受影响（深拷贝）
