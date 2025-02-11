"""独热编码
独热编码是机器学习中处理分类数据的一种流行技术。它涉及为每个类别创建一个二进制向量，其中向量的每个元素代表该类别的存在或不存在。
例如，如果我们有一个颜色的分类变量，其值为红色、蓝色和绿色，独热编码将分别创建三个二进制向量：[1, 0, 0]、[0, 1, 0] 和 [0, 0, 1]。
"""
import pandas as pd

# Creating a sample dataset with a categorical variable
data = {'color': ['red', 'green', 'blue', 'red', 'green']}
df = pd.DataFrame(data)

# Performing one-hot encoding
one_hot_encoded = pd.get_dummies(df['color'], prefix='color')

# Combining the encoded data with the original data
df = pd.concat([df, one_hot_encoded], axis=1)

# Drop the original categorical variable
df = df.drop('color', axis=1)

# Print the encoded data
print(df)