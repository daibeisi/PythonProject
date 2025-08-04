"""
测试HTTPClient的Cookie管理功能
"""

import sys
import os
import time

# 将父目录添加到路径中，以便我们可以导入http_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from http_client import HTTPClient


def test_manual_cookie_setting():
    """测试手动设置Cookie"""
    print("=== 测试手动设置Cookie ===")
    
    client = HTTPClient()
    
    try:
        # 手动设置Cookie
        client.set_cookie("httpbin.org", "/", "test_cookie", "test_value")
        client.set_cookie("httpbin.org", "/", "user_id", "12345")
        
        # 获取Cookie
        cookies = client.get_cookies("httpbin.org", "/")
        print(f"设置的Cookie: {cookies}")
        
        # 发送请求，检查Cookie是否被发送
        response = client.get("https://httpbin.org/cookies")
        print(f"服务器收到的Cookie: {response['content']['cookies']}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def test_cookie_domain_matching():
    """测试Cookie域名匹配"""
    print("\n=== 测试Cookie域名匹配 ===")
    
    client = HTTPClient()
    
    try:
        # 设置不同域名的Cookie
        client.set_cookie("example.com", "/", "example_cookie", "example_value")
        client.set_cookie(".httpbin.org", "/", "domain_cookie", "domain_value")
        
        # 检查不同域名下的Cookie
        example_cookies = client.get_cookies("example.com", "/")
        print(f"example.com的Cookie: {example_cookies}")
        
        httpbin_cookies = client.get_cookies("httpbin.org", "/")
        print(f"httpbin.org的Cookie: {httpbin_cookies}")
        
        sub_httpbin_cookies = client.get_cookies("api.httpbin.org", "/")
        print(f"api.httpbin.org的Cookie: {sub_httpbin_cookies}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def test_cookie_path_matching():
    """测试Cookie路径匹配"""
    print("\n=== 测试Cookie路径匹配 ===")
    
    client = HTTPClient()
    
    try:
        # 设置不同路径的Cookie
        client.set_cookie("httpbin.org", "/", "root_cookie", "root_value")
        client.set_cookie("httpbin.org", "/api", "api_cookie", "api_value")
        client.set_cookie("httpbin.org", "/api/v1", "v1_cookie", "v1_value")
        
        # 检查不同路径下的Cookie
        root_cookies = client.get_cookies("httpbin.org", "/")
        print(f"根路径(/)的Cookie: {root_cookies}")
        
        api_cookies = client.get_cookies("httpbin.org", "/api")
        print(f"/api路径的Cookie: {api_cookies}")
        
        v1_cookies = client.get_cookies("httpbin.org", "/api/v1")
        print(f"/api/v1路径的Cookie: {v1_cookies}")
        
        specific_cookies = client.get_cookies("httpbin.org", "/api/v1/users")
        print(f"/api/v1/users路径的Cookie: {specific_cookies}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def test_cookie_expiration():
    """测试Cookie过期"""
    print("\n=== 测试Cookie过期 ===")
    
    client = HTTPClient()
    
    try:
        # 设置即将过期的Cookie
        client.set_cookie("httpbin.org", "/", "expiring_cookie", "expiring_value", 
                         time.time() + 2)  # 2秒后过期
        client.set_cookie("httpbin.org", "/", "permanent_cookie", "permanent_value")
        
        # 检查Cookie
        cookies_before = client.get_cookies("httpbin.org", "/")
        print(f"过期前的Cookie: {cookies_before}")
        
        # 等待Cookie过期
        print("等待3秒让Cookie过期...")
        time.sleep(3)
        
        # 手动清理过期Cookie
        client.cookie_jar.clear_expired_cookies()
        
        # 再次检查Cookie
        cookies_after = client.get_cookies("httpbin.org", "/")
        print(f"过期后的Cookie: {cookies_after}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def test_clear_cookies():
    """测试清空Cookie"""
    print("\n=== 测试清空Cookie ===")
    
    client = HTTPClient()
    
    try:
        # 设置一些Cookie
        client.set_cookie("httpbin.org", "/", "cookie1", "value1")
        client.set_cookie("example.com", "/", "cookie2", "value2")
        
        # 检查Cookie
        all_cookies = client.get_cookies("httpbin.org", "/")
        print(f"清空前的Cookie: {all_cookies}")
        
        # 清空所有Cookie
        client.clear_cookies()
        
        # 再次检查Cookie
        all_cookies = client.get_cookies("httpbin.org", "/")
        print(f"清空后的Cookie: {all_cookies}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


def test_disable_cookies():
    """测试禁用Cookie功能"""
    print("\n=== 测试禁用Cookie功能 ===")
    
    # 创建禁用Cookie的客户端
    client = HTTPClient(enable_cookies=False)
    
    try:
        # 尝试设置Cookie（应该不会有任何效果）
        client.set_cookie("httpbin.org", "/", "test_cookie", "test_value")
        
        # 检查Cookie（应该为空）
        cookies = client.get_cookies("httpbin.org", "/")
        print(f"禁用Cookie时的Cookie: {cookies}")
        print(f"Cookie Jar是否存在: {client.cookie_jar is not None}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    test_manual_cookie_setting()
    test_cookie_domain_matching()
    test_cookie_path_matching()
    test_cookie_expiration()
    test_clear_cookies()
    test_disable_cookies()