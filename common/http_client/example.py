"""
HTTP客户端使用示例。

本模块演示了如何使用HTTP客户端进行各种类型的请求。
"""

import sys
import os
import time

# 将父目录添加到路径中，以便我们可以导入http_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from http_client import HTTPClient, get, post, put, delete


def example_basic_requests():
    """演示基本的HTTP请求。"""
    print("=== 基本HTTP请求 ===")
    
    # 使用便捷函数
    try:
        # GET请求
        response = get("https://httpbin.org/get")
        print(f"GET状态码: {response['status_code']}")
        # 仅打印部分内容以避免输出过于冗长
        print(f"收到响应: {type(response['content'])}")
    except Exception as e:
        print(f"错误: {e}")


def example_client_with_base_url():
    """演示使用带基础URL的客户端。"""
    print("\n=== 带基础URL的客户端 ===")
    
    # 使用基础URL创建客户端
    client = HTTPClient(base_url="https://httpbin.org")
    
    try:
        # 带参数的GET请求
        response = client.get("/get", params={"key": "value", "test": "123"})
        print(f"带参数GET请求状态码: {response['status_code']}")
        print(f"发送的参数: {response['content']['args']}")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def example_post_requests():
    """演示POST请求。"""
    print("\n=== POST请求 ===")
    
    client = HTTPClient()
    
    try:
        # 发送表单数据的POST请求
        response = client.post(
            "https://httpbin.org/post",
            data={"name": "test", "value": "123"}
        )
        print(f"发送表单数据POST请求状态码: {response['status_code']}")
        
        # 发送JSON数据的POST请求
        response = client.post(
            "https://httpbin.org/post",
            json_data={"name": "test", "value": "123"}
        )
        print(f"发送JSON数据POST请求状态码: {response['status_code']}")
        print(f"发送的JSON数据: {response['content']['json']}")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def example_put_and_delete():
    """演示PUT和DELETE请求。"""
    print("\n=== PUT和DELETE请求 ===")
    
    client = HTTPClient()
    
    try:
        # PUT请求
        response = client.put(
            "https://httpbin.org/put",
            json_data={"id": 1, "name": "updated"}
        )
        print(f"PUT请求状态码: {response['status_code']}")
        
        # DELETE请求
        response = client.delete("https://httpbin.org/delete")
        print(f"DELETE请求状态码: {response['status_code']}")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def example_custom_headers():
    """演示使用自定义头部。"""
    print("\n=== 自定义头部 ===")
    
    client = HTTPClient()
    
    try:
        # 带自定义头部的请求
        headers = {
            "X-Custom-Header": "MyValue",
            "Authorization": "Bearer token123"
        }
        response = client.get("https://httpbin.org/headers", headers=headers)
        print(f"自定义头部请求状态码: {response['status_code']}")
        print("自定义头部发送成功")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def example_connection_pooling():
    """演示连接池的优势。"""
    print("\n=== 连接池示例 ===")
    
    # 使用连接池的客户端
    client = HTTPClient(base_url="https://httpbin.org", max_connections=5)
    
    print("使用连接池发送多个请求:")
    try:
        start_time = time.time()
        
        # 发送多个请求以展示连接复用
        for i in range(3):
            response = client.get("/get", params={"request": i})
            print(f"  请求 {i+1} 状态码: {response['status_code']}")
            
        end_time = time.time()
        print(f"总耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def example_connection_reuse():
    """演示连接复用的优势。"""
    print("\n=== 连接复用示例 ===")
    
    # 复用同一个客户端实例发送多个请求
    # 这样可以确保使用相同的配置和上下文
    client = HTTPClient(base_url="https://httpbin.org", timeout=10)
    
    print("使用同一个客户端实例发送多个请求:")
    try:
        # 发送多个请求
        for i in range(3):
            response = client.get("/get", params={"request": i})
            print(f"  请求 {i+1} 状态码: {response['status_code']}")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()
    
    print("\n对比每次都创建新实例:")
    try:
        # 每次都创建新实例（不推荐用于频繁请求）
        for i in range(3):
            new_client = HTTPClient(base_url="https://httpbin.org", timeout=10)
            response = new_client.get("/get", params={"request": i})
            print(f"  请求 {i+1} 状态码: {response['status_code']}")
            new_client.close()
    except Exception as e:
        print(f"错误: {e}")


def example_retry_mechanism():
    """演示重试机制。"""
    print("\n=== 重试机制示例 ===")
    
    # 创建一个配置了重试机制的客户端
    client = HTTPClient(
        base_url="https://httpbin.org",
        max_retries=3,  # 最多重试3次
        timeout=5
    )
    
    try:
        # 发送一个正常的请求
        response = client.get("/get", params={"test": "retry"})
        print(f"正常请求状态码: {response['status_code']}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def example_advanced_configuration():
    """演示高级配置选项。"""
    print("\n=== 高级配置示例 ===")
    
    # 创建一个配置了所有选项的客户端
    client = HTTPClient(
        base_url="https://httpbin.org",
        timeout=30,          # 30秒超时
        max_retries=5,       # 最多重试5次
        max_connections=20   # 最大连接数20
    )
    
    try:
        print("使用高级配置的客户端发送请求:")
        response = client.get("/get", params={"config": "advanced"})
        print(f"请求状态码: {response['status_code']}")
        print("请求成功完成")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    example_basic_requests()
    example_client_with_base_url()
    example_post_requests()
    example_put_and_delete()
    example_custom_headers()
    example_connection_reuse()
    example_connection_pooling()
    example_retry_mechanism()
    example_advanced_configuration()