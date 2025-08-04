"""
测试HTTPClient的后台线程清理机制
"""

import sys
import os
import time

# 将父目录添加到路径中，以便我们可以导入http_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from http_client import HTTPClient


def test_cleanup_thread():
    """测试后台线程清理机制"""
    print("=== 测试后台线程清理机制 ===")
    
    # 创建一个连接TTL很短的客户端（2秒）
    client = HTTPClient(
        base_url="https://httpbin.org",
        connection_ttl=2,  # 2秒后连接过期
        max_connections=5
    )
    
    try:
        print(f"客户端创建完成，连接TTL: {client.connection_ttl}秒")
        print(f"清理线程是否存活: {client._cleanup_thread.is_alive()}")
        
        # 发送几个请求来创建连接
        print("\n发送请求创建连接...")
        for i in range(3):
            response = client.get("/get", params={"test": f"request_{i}"})
            print(f"  请求 {i+1} 状态码: {response['status_code']}")
        
        print(f"\n当前连接池状态:")
        print(f"  连接计数: {client._connection_count}")
        print(f"  连接池大小: {len(client._connection_pool)}")
        for key, connections in client._connection_pool.items():
            print(f"    {key}: {len(connections)} 个连接")
        
        print("\n等待3秒让连接超时...")
        time.sleep(3)
        
        # 手动触发一次清理
        client._remove_expired_connections()
        
        print(f"\n清理后连接池状态:")
        print(f"  连接计数: {client._connection_count}")
        print(f"  连接池大小: {len(client._connection_pool)}")
        for key, connections in client._connection_pool.items():
            print(f"    {key}: {len(connections)} 个连接")
        
        print("\n再发送一个请求...")
        response = client.get("/get", params={"test": "after_cleanup"})
        print(f"  请求状态码: {response['status_code']}")
        
        print(f"\n最终连接池状态:")
        print(f"  连接计数: {client._connection_count}")
        print(f"  连接池大小: {len(client._connection_pool)}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\n客户端已关闭")


def test_normal_ttl():
    """测试正常的连接TTL（较长的超时时间）"""
    print("\n=== 测试正常连接TTL ===")
    
    # 创建一个连接TTL正常的客户端（10分钟）
    client = HTTPClient(
        base_url="https://httpbin.org",
        connection_ttl=600,  # 10分钟后连接过期
        max_connections=5
    )
    
    try:
        print(f"客户端创建完成，连接TTL: {client.connection_ttl}秒")
        print(f"清理线程是否存活: {client._cleanup_thread.is_alive()}")
        
        # 发送几个请求来创建连接
        print("\n发送请求创建连接...")
        for i in range(2):
            response = client.get("/get", params={"test": f"normal_{i}"})
            print(f"  请求 {i+1} 状态码: {response['status_code']}")
        
        print(f"\n当前连接池状态:")
        print(f"  连接计数: {client._connection_count}")
        print(f"  连接池大小: {len(client._connection_pool)}")
        for key, connections in client._connection_pool.items():
            print(f"    {key}: {len(connections)} 个连接")
            
        # 检查创建时间记录
        print(f"\n创建时间记录数量: {len(client._connection_creation_time)}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\n客户端已关闭")


if __name__ == "__main__":
    test_cleanup_thread()
    test_normal_ttl()