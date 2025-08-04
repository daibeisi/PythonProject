# pip install ultralytics onnx
from ultralytics import YOLO

# 加载预训练的 YOLO 模型
model = YOLO('C:\\Users\\admin\\Desktop\\yolo11s-obb.pt')

# 导出模型为 ONNX 格式
model.export(format='onnx')