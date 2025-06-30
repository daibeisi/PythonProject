import matplotlib
matplotlib.use('TkAgg')  # 或者 'Qt5Agg'
import matplotlib.pyplot as plt
import numpy as np

# Generate random data
random_data = np.random.randn(1000)

# Create the histogram
plt.figure(figsize=(10, 6))  # Set the figure size
plt.hist(random_data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.title('Histogram Example')
plt.grid(True)  # Add grid lines for better readability
plt.show()

# Optionally, save the figure to a file
# plt.savefig('histogram_example.png', dpi=300)

