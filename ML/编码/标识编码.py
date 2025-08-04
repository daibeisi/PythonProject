"""标识编码
标签编码是机器学习中处理分类数据的另一种技术。它涉及为分类变量中的每个类别分配一个唯一的数值，数值的顺序基于类别的顺序。
例如，假设我们有一个分类变量“大小”，它有三个类别：“小”、“中”和“大”。使用标签编码，我们将分别为这些类别分配值 0、1 和 2。
"""
from sklearn.preprocessing import LabelEncoder

# create a sample dataset with a categorical variable
data = ['small', 'medium', 'large', 'small', 'large']

# create a label encoder object
label_encoder = LabelEncoder()

# fit and transform the data using the label encoder
encoded_data = label_encoder.fit_transform(data)

# print the encoded data
print(encoded_data)
