# encoding: utf-8
"""
--------------------------------
Name:     xxx.py
Author:   cpy
Date:     2024/11/18
Company:  Schinper
Description: Triton Server Client工具类
--------------------------------
"""

# ''' Standard library '''
from typing import List, Optional

# ''' Third party Library '''
from loguru import logger
import tritonclient.http as http_client


# ''' Custom Library '''


class TritonClientHttp:
    """
    同步 Triton Client 工具类，支持 HTTP 协议。
    """

    def __init__(self, url: str):
        """
        初始化 TritonClientHttp 实例

        :param url: Triton Inference Server 地址，格式为 'hostname:port'。
        """
        self.url = url
        self.client = http_client.InferenceServerClient(url=url, verbose=False)

    def get_model_list(self) -> List[str]:
        """
        获取服务器上所有已加载模型的列表。

        :return: 已加载模型的名称列表。
        """
        try:
            # 获取模型仓库索引，返回一个包含模型名称的列表
            response = self.client.get_model_repository_index()
            return [model['name'] for model in response]
        except Exception as e:
            logger.exception(f"Error fetching model list: {e}")
        return []

    def load_model(self, model_name: str) -> bool:
        """
        加载指定模型。

        :param model_name: 要加载的模型名称。
        :return: 加载是否成功。
        """
        try:
            if not self.client.is_model_ready(model_name):
                # 加载模型
                self.client.load_model(model_name)
        except Exception as e:
            logger.exception(f"Error loading model {model_name}: {e}")
            return False
        return True

    def unload_model(self, model_name: str) -> bool:
        """
        卸载指定模型。

        :param model_name: 要卸载的模型名称。
        :return: 卸载是否成功。
        """
        try:
            # 卸载模型
            self.client.unload_model(model_name)
            return True
        except Exception as e:
            logger.exception(f"Error unloading model {model_name}: {e}")
        return False

    def is_model_loaded(self, model_name: str) -> Optional[bool]:
        """
        判断指定模型是否已加载。

        :param model_name: 要检查的模型名称。
        :return: 如果模型已加载，返回 True，否则返回 False，异常返回 None。
        """
        try:
            return self.client.is_model_ready(model_name)
        except Exception as e:
            logger.exception(f"Error checking if model {model_name} is loaded: {e}")
        return None

    def get_model_metadata(self, model_name: str) -> Optional[dict]:
        """
        获取模型元数据
        :param model_name: 模型名称
        :return: 模型元数据字典
        """
        try:
            return self.client.get_model_metadata(model_name=model_name)
        except Exception as e:
            logger.exception(f"Error getting model metadata {model_name}: {e}")
        return None

    def get_model_config(self, model_name: str) -> Optional[dict]:
        """
        获取模型配置
        :param model_name: 模型名称
        :return: 模型配置字典
        """
        try:
            return self.client.get_model_config(model_name=model_name)
        except Exception as e:
            logger.exception(f"Error getting model config {model_name}: {e}")
        return None


# 示例用法：
def main():
    # 假设 Triton 服务器运行在 localhost:8000
    triton_client = TritonClientHttp(url='172.18.18.177:8000')

    # 模型名称
    model_name = 'yolov8s'

    # 获取模型列表
    models = triton_client.get_model_list()
    logger.info(f"Loaded models: {models}")

    # # 加载模型
    # success = triton_client.load_model(model_name)
    # logger.info(f"Model '{model_name}' loaded: {success}")

    # # 检查模型是否已加载
    is_loaded = triton_client.is_model_loaded(model_name)
    logger.info(f"Is model '{model_name}' loaded: {is_loaded}")

    # # 获取模型元信息
    # info = triton_client.get_model_metadata(model_name)
    # logger.info(f"Model '{model_name}' metadata: {info}")
    #
    # # 获取模型配置信息
    # config = triton_client.get_model_config(model_name)
    # logger.info(f"Model '{model_name}' config: {config}")

    # for model in models:
    #     success = triton_client.unload_model(model)
    # 卸载模型
    # success = triton_client.unload_model(model_name)
    # logger.info(f"Model '{model_name}' unloaded: {success}")


if __name__ == '__main__':
    main()
