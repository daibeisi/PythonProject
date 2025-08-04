"""
HTTP客户端的单元测试。
"""

import sys
import os
import unittest
from unittest.mock import patch, Mock

# 将父目录添加到路径中，以便我们可以导入http_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from http_client import HTTPClient, HTTPException


class TestHTTPClient(unittest.TestCase):
    """HTTPClient类的测试用例。"""

    def setUp(self):
        """设置测试夹具。"""
        self.client = HTTPClient()
        self.base_url_client = HTTPClient(base_url="https://api.example.com")

    def tearDown(self):
        """清理测试夹具。"""
        self.client.close()
        self.base_url_client.close()

    def test_init(self):
        """测试客户端初始化。"""
        # 测试默认初始化
        client = HTTPClient()
        self.assertIsNone(client.base_url)
        self.assertEqual(client.timeout, 30)
        self.assertEqual(client.max_retries, 3)
        self.assertEqual(client.max_connections, 10)
        client.close()
        
        # 测试带参数的初始化
        client = HTTPClient(
            base_url="https://api.example.com",
            timeout=15,
            max_retries=5,
            max_connections=20
        )
        self.assertEqual(client.base_url, "https://api.example.com")
        self.assertEqual(client.timeout, 15)
        self.assertEqual(client.max_retries, 5)
        self.assertEqual(client.max_connections, 20)
        client.close()
        
        # 测试带尾部斜杠的基础URL初始化
        client = HTTPClient(base_url="https://api.example.com/")
        self.assertEqual(client.base_url, "https://api.example.com")
        client.close()

    def test_build_url_without_base_url(self):
        """测试不带基础URL的URL构建。"""
        url = self.client._build_url("/test")
        self.assertEqual(url, "/test")
        
        url = self.client._build_url("https://example.com/test")
        self.assertEqual(url, "https://example.com/test")

    def test_build_url_with_base_url(self):
        """测试带基础URL的URL构建。"""
        url = self.base_url_client._build_url("/test")
        self.assertEqual(url, "https://api.example.com/test")
        
        url = self.base_url_client._build_url("test")
        self.assertEqual(url, "https://api.example.com/test")

    def test_build_url_with_params(self):
        """测试带查询参数的URL构建。"""
        params = {"key": "value", "test": "123"}
        
        url = self.client._build_url("/test", params)
        # 参数可以是任意顺序
        self.assertIn("key=value", url)
        self.assertIn("test=123", url)
        self.assertIn("/test?", url)
        
        # 测试带现有查询字符串的情况
        url = self.client._build_url("/test?existing=param", params)
        self.assertIn("existing=param", url)
        self.assertIn("key=value", url)
        self.assertIn("test=123", url)

    def test_get_request(self):
        """测试GET请求。"""
        # 模拟响应
        mock_response = Mock()
        mock_response.read.return_value = b'{"test": "response"}'
        mock_response.status = 200
        mock_response.getheaders.return_value = [("Content-Type", "application/json")]
        
        # 模拟连接
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_conn.sock = None  # 模拟新连接
        
        # 替换_get_connection方法
        original_get_connection = self.client._get_connection
        original_return_connection = self.client._return_connection
        self.client._get_connection = Mock(return_value=mock_conn)
        self.client._return_connection = Mock()
        
        try:
            result = self.client.get("https://example.com/test")
            
            # 验证结果
            self.assertEqual(result['status_code'], 200)
            self.assertEqual(result['content'], {"test": "response"})
            self.assertIn("Content-Type", result['headers'])
        finally:
            self.client._get_connection = original_get_connection
            self.client._return_connection = original_return_connection

    def test_post_request_with_json(self):
        """测试带JSON数据的POST请求。"""
        # 模拟响应
        mock_response = Mock()
        mock_response.read.return_value = b'{"result": "created"}'
        mock_response.status = 201
        mock_response.getheaders.return_value = [("Content-Type", "application/json")]
        
        # 模拟连接
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_conn.sock = None  # 模拟新连接
        
        # 替换_get_connection方法
        original_get_connection = self.client._get_connection
        self.client._get_connection = Mock(return_value=mock_conn)
        
        try:
            result = self.client.post(
                "https://example.com/test",
                json_data={"name": "test"}
            )
            
            # 验证结果
            self.assertEqual(result['status_code'], 201)
            self.assertEqual(result['content'], {"result": "created"})
        finally:
            self.client._get_connection = original_get_connection

    def test_put_request(self):
        """测试PUT请求。"""
        # 模拟响应
        mock_response = Mock()
        mock_response.read.return_value = b'{"result": "updated"}'
        mock_response.status = 200
        mock_response.getheaders.return_value = [("Content-Type", "application/json")]
        
        # 模拟连接
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_conn.sock = None  # 模拟新连接
        
        # 替换_get_connection方法
        original_get_connection = self.base_url_client._get_connection
        self.base_url_client._get_connection = Mock(return_value=mock_conn)
        
        try:
            result = self.base_url_client.put("/test", json_data={"id": 1, "name": "updated"})
            
            # 验证结果
            self.assertEqual(result['status_code'], 200)
            self.assertEqual(result['content'], {"result": "updated"})
        finally:
            self.base_url_client._get_connection = original_get_connection

    def test_delete_request(self):
        """测试DELETE请求。"""
        # 模拟响应
        mock_response = Mock()
        mock_response.read.return_value = b'{"result": "deleted"}'
        mock_response.status = 200
        mock_response.getheaders.return_value = [("Content-Type", "application/json")]
        
        # 模拟连接
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_conn.sock = None  # 模拟新连接
        
        # 替换_get_connection方法
        original_get_connection = self.client._get_connection
        self.client._get_connection = Mock(return_value=mock_conn)
        
        try:
            result = self.client.delete("https://example.com/test")
            
            # 验证结果
            self.assertEqual(result['status_code'], 200)
            self.assertEqual(result['content'], {"result": "deleted"})
        finally:
            self.client._get_connection = original_get_connection

    def test_http_error_handling(self):
        """测试HTTP错误处理。"""
        # 模拟HTTP错误
        mock_conn = Mock()
        mock_conn.request.side_effect = HTTPException("HTTP 404 Not Found for URL: https://example.com/test")
        mock_conn.sock = None  # 模拟新连接
        
        # 替换连接管理方法
        original_get_connection = self.client._get_connection
        original_return_connection = self.client._return_connection
        self.client._get_connection = Mock(return_value=mock_conn)
        self.client._return_connection = Mock()
        
        try:
            with self.assertRaises(HTTPException) as context:
                self.client.get("https://example.com/test")
            
            self.assertIn("HTTP 404 Not Found", str(context.exception))
        finally:
            self.client._get_connection = original_get_connection
            self.client._return_connection = original_return_connection

    def test_url_error_handling(self):
        """测试URL错误处理。"""
        # 模拟URL错误，通过模拟_make_request方法
        original_make_request = self.client._make_request
        self.client._make_request = Mock(side_effect=HTTPException("URL错误: Network error"))
        
        try:
            with self.assertRaises(HTTPException) as context:
                self.client.get("https://example.com/test")
            
            self.assertIn("URL错误", str(context.exception))
        finally:
            self.client._make_request = original_make_request


if __name__ == '__main__':
    unittest.main()