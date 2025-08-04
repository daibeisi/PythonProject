import requests
import numpy as np
import json

# Triton Server的URL
triton_server_url = "http://172.18.18.177:8000/v2/models/yolov8s/infer"

# 准备输入数据
# 假设模型需要一个名为"INPUT0"的输入，数据类型为FP32，形状为(1, 3, 224, 224)
input_data = np.random.rand(1, 3, 640, 640).astype(np.float32)

# 构建HTTP请求的JSON体
headers = {"Content-Type": "application/json"}
request_body = {
    "inputs": [
        {
            "name": "images",
            "shape": input_data.shape,
            "datatype": "FP32",
            "data": input_data.flatten().tolist()
        }
    ]
}

# 发送HTTP POST请求
while 1:
    response = requests.post(triton_server_url, headers=headers, data=json.dumps(request_body))

    # 检查响应状态码
    if response.status_code == 200:
        # 解析响应
        response_json = response.json()
        outputs = response_json["outputs"]
        for output in outputs:
            output_name = output["name"]
            output_data = np.array(output["data"]).reshape(output["shape"])
            print(f"Output {output_name}: {output_data}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
