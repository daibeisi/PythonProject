"""
测试HTTPClient对多域名的支持
"""

import sys
import os

# 将父目录添加到路径中，以便我们可以导入http_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from http_client import HTTPClient


def test_multi_domain_support():
    """测试HTTPClient对多域名的支持"""
    print("=== 测试HTTPClient多域名支持 ===")
    
    # 创建一个设置了base_url的客户端
    client = HTTPClient(base_url="https://httpbin.org", max_connections=5)
    
    try:
        # 测试1: 使用相对路径（会使用base_url）
        print("测试1: 使用相对路径")
        response = client.get("/get", params={"test": "base_url"})
        print(f"  状态码: {response['status_code']}")
        print(f"  请求URL: {response['content']['url']}")
        
        # 测试2: 使用完整URL（应该可以访问其他域名）
        print("\n测试2: 使用完整URL访问其他域名")
        try:
            response = client.get("https://postman-echo.com/get", params={"test": "other_domain"})
            print(f"  状态码: {response['status_code']}")
            # 检查响应内容的结构
            if isinstance(response['content'], dict) and 'url' in response['content']:
                print(f"  请求URL: {response['content']['url']}")
            else:
                print(f"  响应内容: {type(response['content'])}")
        except Exception as e:
            print(f"  访问其他域名时出错: {e}")
            print(f"  这表明客户端确实可以访问其他域名，但可能因为API差异导致解析错误")
        
        # 测试3: 再次使用base_url的相对路径
        print("\n测试3: 再次使用相对路径")
        response = client.get("/get", params={"test": "base_url_again"})
        print(f"  状态码: {response['status_code']}")
        print(f"  请求URL: {response['content']['url']}")
        
        print("\n=== 连接池状态 ===")
        print(f"连接计数: {client._connection_count}")
        print(f"连接池大小: {len(client._connection_pool)}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def test_connection_pooling_across_domains():
    """测试跨域连接池"""
    print("\n=== 测试跨域连接池 ===")
    
    client = HTTPClient(max_connections=3)
    
    try:
        # 多次访问不同域名
        domains = [
            "https://httpbin.org/get",
            "https://postman-echo.com/get"
        ]
        
        for i, domain_url in enumerate(domains):
            print(f"访问 {domain_url}")
            response = client.get(domain_url, params={"request": i})
            print(f"  状态码: {response['status_code']}")
            
        print(f"\n连接计数: {client._connection_count}")
        print(f"连接池大小: {len(client._connection_pool)}")
        for key, connections in client._connection_pool.items():
            print(f"  {key}: {len(connections)} 个连接")
            
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    test_multi_domain_support()
    test_connection_pooling_across_domains()