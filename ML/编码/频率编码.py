"""频率编码
频率编码是机器学习中处理分类数据的另一种技术。它涉及用数据集中的频率（或计数）替换分类变量中的每个类别。频率编码背后的想法是，
出现频率更高的类别可能对机器学习算法更重要或更有信息量。
"""
import pandas as pd

# create a sample dataset with a categorical variable
data = {'color': ['red', 'green', 'blue', 'red', 'green']}
df = pd.DataFrame(data)

# calculate the frequency of each category in the categorical variable
freq = df['color'].value_counts(normalize=True)

# replace each category with its frequency
df['color_freq'] = df['color'].map(freq)

# drop the original categorical variable
df = df.drop('color', axis=1)

# print the encoded data
print(df)