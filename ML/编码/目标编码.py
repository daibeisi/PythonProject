"""目标编码
目标编码是机器学习中处理分类数据的另一种技术。它涉及用该类别的目标变量（即您想要预测的变量）的平均值（或其他聚合）替换分类变量中的每个类别。
目标编码背后的想法是它可以捕捉分类变量和目标变量之间的关系，从而提高机器学习模型的预测性能。
"""
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# create a sample dataset with a categorical variable and a target variable
data = {'color': ['red', 'green', 'blue', 'red', 'green'],
   'target': [1, 0, 1, 0, 1]}
df = pd.DataFrame(data)

# create a label encoder object and fit it to the data
label_encoder = LabelEncoder()
label_encoder.fit(df['color'])

# transform the categorical variable using the label encoder
df['color_encoded'] = label_encoder.transform(df['color'])

# create a mean encoder object and fit it to the transformed data
mean_encoder = df.groupby('color_encoded')['target'].mean().to_dict()

# map the mean encoded values to the categorical variable
df['color_encoded'] = df['color_encoded'].map(mean_encoder)

# print the encoded data
print(df)
