import torch

# 加载模型
model_path = "C:\\Users\\admin\\PycharmProjects\\pythonProject\\models\\yolov5s\\yolov5s.pt"
model = torch.load(model_path, map_location=torch.device('cpu'))  # 使用 CPU 加载模型

# 获取模型参数数量
total_params = sum(p.numel() for p in model['model'].parameters())
print(f"YOLOv5s 模型的总参数数量: {total_params}")