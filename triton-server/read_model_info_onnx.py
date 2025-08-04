# encoding: utf-8
"""
--------------------------------
Name:     xxx.py
Author:   cpy
Date:     2024/06/xx
Company:  Schinper
Description: 读取模型信息，用于生成配置
--------------------------------
"""

# ''' Standard library '''
# from typing import List, Dict, Tuple, Any

# ''' Third party Library '''
from jinja2 import Template
import onnx
import onnxruntime
import numpy as np


# ''' Custom Library '''


def exist_dynamic_param(dim) -> bool:
    """
    是否存在动态参数
    :param dim: 描述张量形状（shape）中的一个维度
    :return:
    """
    '''
    更多：
    1. 在 ONNX（Open Neural Network Exchange）模型中，描述张量形状的术语是 shape。张量的形状（shape）是指张量在各个维度上的大小。
    每个维度的大小可以用具体的数值、动态参数（dim_param）或固定值（dim_value）来表示。
    2.在 ONNX（Open Neural Network Exchange）模型中，dim 是用来描述张量形状（shape）中的一个维度。每个 dim 可以包含两种类型的值：
        dim_value：表示该维度的具体大小，是一个固定的整数值。
        dim_param：表示该维度的大小是动态的，具体值在推理时通过参数传递。
    术语解释
        dim：表示张量形状中的一个维度。
        dim_value：表示维度的具体大小，是一个固定的整数值。
        dim_param：表示维度的大小是动态的，具体值在推理时通过参数传递。
    '''
    for i in dim:
        if i.dim_param:
            print(f"Warn，发现动态参数：{dim}")
            return True
    return False


def parse_onnx_model(model_path: str, format_input="FORMAT_NONE"):
    """
    解析 ONNX 模型以提取输入和输出信息。
    :param model_path: ONNX 模型文件路径
    :param format_input: 数据格式，默认格式：FORMAT_NONE
    :return: 包含输入和输出信息的字典
    """
    model = onnx.load(model_path)
    inputs = []
    outputs = []

    inp = model.graph.input[-1]
    if exist_dynamic_param(inp.type.tensor_type.shape.dim):
        raise AttributeError(f"错误，input中存在动态参数，需手动确认参数: {inp}")
    # out = model.graph.output[-1]
    # if exist_dynamic_param(out.type.tensor_type.shape.dim):
    #     raise AttributeError(f"错误，output中存在动态参数，需手动确认参数: {out}")

    # 解析输入
    for inp in model.graph.input[-1:]:
        print("*" * 50)
        # print(inp.type.tensor_type.shape)
        # print(inp.type.tensor_type.shape[0])
        shape = [
            dim.dim_value if dim.dim_value > 0 else -1
            for dim in inp.type.tensor_type.shape.dim
        ]
        data_type = f"TYPE_{onnx.helper.tensor_dtype_to_np_dtype(inp.type.tensor_type.elem_type).name.upper()}"
        inputs.append(
            {
                "name": inp.name,
                "data_type": data_type,
                # "format": "FORMAT_NONE",  # 默认格式
                "format": format_input,  # 默认格式
                "dims": shape,
                "reshape": shape,  # 默认 reshape 与 dims 相同
            }
        )
    # 解析输出
    for out in model.graph.output[-1:]:
        print(out)
        # 尝试解析输出维度信息
        try:
            print([dim.dim_value for dim in out.type.tensor_type.shape.dim])
            shape = [
                dim.dim_value if dim.dim_value > 0 else -1
                for dim in out.type.tensor_type.shape.dim
            ]
        except AttributeError:
            # 如果无法解析，设置默认值
            # shape = [-1, -1, -1]
            raise AttributeError(f"异常，如果无法解析output: {out}")

        data_type = f"TYPE_{onnx.helper.tensor_dtype_to_np_dtype(out.type.tensor_type.elem_type).name.upper()}"
        outputs.append(
            {
                "name": out.name,
                "data_type": data_type,
                "dims": shape,
                "reshape": shape,  # 默认 reshape 与 dims 相同
            }
        )

    return {"inputs": inputs, "outputs": outputs}


def generate_config_pbtxt(
        model_name: str,
        platform: str,
        max_batch_size: int,
        model_info: dict,
        instance_groups: list,
        template_path: str = "config_template.pbtxt",
) -> str:
    """
    使用 Jinja2 模板生成 config.pbtxt 文件。
    :param model_name: 模型名称
    :param platform: 模型平台
    :param max_batch_size: 最大批量大小
    :param model_info: 从模型提取的输入和输出信息
    :param instance_groups: 实例组列表，每个元素是包含字段 {count, kind, gpus} 的字典
    :param template_path: 模板文件路径
    :return: 生成的 config.pbtxt 字符串
    """
    inputs = model_info["inputs"]
    outputs = model_info["outputs"]

    with open(template_path, "r") as template_file:
        template_content = template_file.read()

    # template = Template(template_content, trim_blocks=True, lstrip_blocks=True)
    template = Template(template_content)
    rendered_content = template.render(
        model_name=model_name,
        platform=platform,
        max_batch_size=max_batch_size,
        inputs=inputs,
        outputs=outputs,
        instance_groups=instance_groups,
    )

    return rendered_content


def get_onnx_model_parameters(model_path):
    # 加载 ONNX 模型
    model = onnx.load(model_path)

    # 初始化统计信息
    total_params = 0
    total_size_bytes = 0

    # 遍历模型的所有参数
    for initializer in model.graph.initializer:
        # 获取参数的形状
        param_shape = initializer.dims
        # 计算参数数量
        param_count = np.prod(param_shape)
        total_params += param_count

        # 获取参数数据类型大小（默认为 float32，即 4 字节）
        param_dtype = onnx.mapping.TENSOR_TYPE_TO_NP_TYPE[initializer.data_type]
        param_size = param_count * np.dtype(param_dtype).itemsize
        total_size_bytes += param_size

    # 转换为 MB 单位
    total_size_mb = total_size_bytes / (1024 ** 2)

    # 预测占用现存
    p

    return total_size_mb


# 捕获每层激活值
def get_activations(model_path):
    # 加载 ONNX 模型
    session = onnxruntime.InferenceSession(model_path)

    # 创建一个随机输入
    input_name = session.get_inputs()[0].name
    input_shape = session.get_inputs()[0].shape
    input_data = np.random.rand(*[dim if dim is not None else 1 for dim in input_shape]).astype(np.float32)
    intermediate_sizes = []
    outputs = [output.name for output in session.get_outputs()]
    ort_outs = session.run(outputs, {input_name: input_data})

    for out in ort_outs:
        # 计算每个输出张量的大小
        intermediate_sizes.append(out.size * out.itemsize)
    return sum(intermediate_sizes)


# 示例用法
def run():
    # 模型路径
    # model_path = "C:\\Users\\admin\\PycharmProjects\\pythonProject\\models\\yolov5m\\yolov5m.onnx"
    model_path = "C:\\Users\\admin\\Desktop\\yolov8x-seg\\1\\model.onnx"
    # model_path = "model/densenet_onnx.onnx"
    params_count, params_size_mb = get_onnx_model_parameters(model_path)
    print(f"参数数量: {params_count}, 参数大小: {params_size_mb:.2f} MB")
    activations_size = get_activations(model_path)
    print(f"中间激活值占用内存约为: {activations_size / 1024 ** 2:.2f} MB")



    # # 模型名称
    # model_name = "example_model"
    #
    # # 解析模型
    # platform = "onnxruntime_onnx"
    # model_info = parse_onnx_model(model_path)
    #
    # # 配置参数
    # max_batch_size = 0
    # instance_groups = [{"count": 1, "kind": "KIND_GPU", "gpus": [0]}]
    #
    # # 模板路径
    # config_template_path = "C:\\Users\\admin\\PycharmProjects\\pythonProject\\triton\\config_template.pbtxt"
    #
    # # 生成配置
    # config = generate_config_pbtxt(
    #     model_name=model_name,
    #     platform=platform,
    #     max_batch_size=max_batch_size,
    #     model_info=model_info,
    #     instance_groups=instance_groups,
    #     template_path=config_template_path,
    # )
    #
    # print("Generated config.pbtxt:")
    # print(config)
    #
    # # 保存到文件
    # with open("config.pbtxt", "w") as f:
    #     f.write(config)


if __name__ == "__main__":
    run()
