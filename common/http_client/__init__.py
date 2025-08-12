"""
HTTP客户端模块。

该模块提供了一个简单而功能强大的HTTP客户端，支持各种HTTP方法、
身份验证、自定义头部等功能。
"""

import json
import threading
import time
from http.client import HTTPConnection, HTTPSConnection
from typing import Dict, Any, Optional, Union
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, urlparse


class HTTPException(Exception):
    """HTTP客户端错误的自定义异常。"""
    pass


class CookieJar:
    """
    简单的Cookie管理器。
    """
    
    def __init__(self):
        """初始化Cookie管理器。"""
        self._cookies = {}
    
    def set_cookie(self, domain: str, path: str, name: str, value: str, 
                   expires: Optional[float] = None):
        """
        设置Cookie。
        
        Args:
            domain: Cookie的域名。
            path: Cookie的路径。
            name: Cookie名称。
            value: Cookie值。
            expires: 过期时间（时间戳）。
        """
        key = (domain, path, name)
        self._cookies[key] = {
            'value': value,
            'expires': expires
        }
    
    def get_cookies(self, domain: str, path: str) -> Dict[str, str]:
        """
        获取适用于指定域名和路径的Cookie。
        
        Args:
            domain: 域名。
            path: 路径。
            
        Returns:
            Cookie字典。
        """
        cookies = {}
        current_time = time.time()
        
        for (cookie_domain, cookie_path, name), cookie_data in self._cookies.items():
            # 检查域名匹配
            if not self._domain_match(domain, cookie_domain):
                continue
                
            # 检查路径匹配
            if not self._path_match(path, cookie_path):
                continue
                
            # 检查是否过期
            if cookie_data['expires'] and cookie_data['expires'] < current_time:
                continue
                
            cookies[name] = cookie_data['value']
            
        return cookies
    
    def _domain_match(self, request_domain: str, cookie_domain: str) -> bool:
        """
        检查域名是否匹配。
        
        Args:
            request_domain: 请求的域名。
            cookie_domain: Cookie的域名。
            
        Returns:
            是否匹配。
        """
        if request_domain == cookie_domain:
            return True
            
        if cookie_domain.startswith('.'):
            cookie_domain = cookie_domain[1:]
            
        return request_domain.endswith('.' + cookie_domain) or request_domain == cookie_domain
    
    def _path_match(self, request_path: str, cookie_path: str) -> bool:
        """
        检查路径是否匹配。
        
        Args:
            request_path: 请求的路径。
            cookie_path: Cookie的路径。
            
        Returns:
            是否匹配。
        """
        if cookie_path == '/':
            return True
            
        if not request_path.startswith(cookie_path):
            return False
            
        if len(request_path) == len(cookie_path):
            return True
            
        # 确保cookie路径是请求路径的前缀，且在路径分隔符处结束
        return cookie_path.endswith('/') or request_path[len(cookie_path)] == '/'
    
    def clear_expired_cookies(self):
        """清理过期的Cookie。"""
        current_time = time.time()
        expired_keys = []
        
        for key, cookie_data in self._cookies.items():
            if cookie_data['expires'] and cookie_data['expires'] < current_time:
                expired_keys.append(key)
                
        for key in expired_keys:
            del self._cookies[key]
    
    def clear(self):
        """清空所有Cookie。"""
        self._cookies.clear()


class HTTPClient:
    """
    一个简单的HTTP客户端，用于发起HTTP请求。
    
    该客户端支持各种HTTP方法、自定义头部、身份验证
    和其他常见的HTTP功能。
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30, 
                 max_retries: int = 3, max_connections: int = 10, 
                 connection_ttl: int = 300, enable_cookies: bool = True):
        """
        初始化HTTP客户端。
        
        Args:
            base_url: 所有请求的基础URL。可选。
            timeout: 请求超时时间（秒）。默认为30秒。
            max_retries: 最大重试次数。默认为3次。
            max_connections: 连接池最大连接数。默认为10，与requests库一致。
            connection_ttl: 连接最大存活时间（秒）。默认为300秒（5分钟）。
            enable_cookies: 是否启用Cookie管理。默认为True。
        """
        self.base_url = base_url.rstrip('/') if base_url else None
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_connections = max_connections
        self.connection_ttl = connection_ttl
        self.enable_cookies = enable_cookies
        self.default_headers = {
            'User-Agent': 'Python-HTTPClient/1.0',
            'Accept': '*/*'
        }
        # Cookie管理器
        self.cookie_jar = CookieJar() if enable_cookies else None
        # 连接池，按主机名存储连接
        self._connection_pool = {}
        # 跟踪连接数
        self._connection_count = {}
        # 跟踪连接创建时间
        self._connection_creation_time = {}
        # 清理线程相关
        self._cleanup_thread = None
        self._cleanup_stop_event = threading.Event()
        self._start_cleanup_thread()
        
    def _start_cleanup_thread(self):
        """
        启动后台清理线程。
        """
        if self.connection_ttl > 0:
            self._cleanup_thread = threading.Thread(target=self._cleanup_expired_connections, daemon=True)
            self._cleanup_thread.start()

    def _cleanup_expired_connections(self):
        """
        定期清理超时连接的后台线程函数。
        """
        while not self._cleanup_stop_event.wait(30):  # 每30秒检查一次
            try:
                self._remove_expired_connections()
                # 同时清理过期的Cookie
                if self.cookie_jar:
                    self.cookie_jar.clear_expired_cookies()
            except Exception:
                # 忽略清理过程中的任何异常，避免线程崩溃
                pass

    def _remove_expired_connections(self):
        """
        移除超时的连接。
        """
        current_time = time.time()
        expired_keys = []
        
        for key, connections in self._connection_pool.items():
            # 创建新的连接列表，只保留未超时的连接
            valid_connections = []
            for conn in connections:
                conn_info = self._connection_creation_time.get(id(conn))
                if conn_info:
                    created_time, _ = conn_info
                    if current_time - created_time < self.connection_ttl:
                        valid_connections.append(conn)
                    else:
                        # 关闭超时的连接
                        try:
                            conn.close()
                            self._connection_count[key] = max(0, self._connection_count.get(key, 1) - 1)
                        except:
                            pass
                        # 从创建时间跟踪中移除
                        if id(conn) in self._connection_creation_time:
                            del self._connection_creation_time[id(conn)]
                else:
                    # 没有创建时间信息的连接，假设未超时
                    valid_connections.append(conn)
            
            # 更新连接池
            self._connection_pool[key] = valid_connections
            
            # 如果连接池为空且没有活跃连接，标记为可删除
            if not valid_connections and self._connection_count.get(key, 0) <= 0:
                expired_keys.append(key)
        
        # 清理空的连接池条目
        for key in expired_keys:
            if key in self._connection_pool:
                del self._connection_pool[key]
            if key in self._connection_count:
                del self._connection_count[key]
            # 清理相关的创建时间记录
            keys_to_remove = [conn_id for conn_id, conn_info 
                             in self._connection_creation_time.items() 
                             if conn_info[1] == key]
            for conn_id in keys_to_remove:
                if conn_id in self._connection_creation_time:
                    del self._connection_creation_time[conn_id]

    def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发起GET请求。
        
        Args:
            endpoint: 要请求的端点。
            params: 要包含在请求中的查询参数。
            headers: 要包含在请求中的头部信息。
            
        Returns:
            包含状态码、头部和响应数据的字典。
            
        Raises:
            HTTPException: 如果请求失败。
        """
        url = self._build_url(endpoint, params)
        return self._make_request_with_retry('GET', url, headers=headers)

    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发起POST请求。
        
        Args:
            endpoint: 要请求的端点。
            data: 要发送的表单数据或原始数据。
            headers: 要包含在请求中的头部信息。
            json_data: 要作为application/json发送的JSON数据。
            
        Returns:
            包含状态码、头部和响应数据的字典。
            
        Raises:
            HTTPException: 如果请求失败。
        """
        url = self._build_url(endpoint)
        if json_data:
            headers = headers or {}
            headers['Content-Type'] = 'application/json'
            data = json.dumps(json_data)
        return self._make_request_with_retry('POST', url, data=data, headers=headers)

    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发起PUT请求。
        
        Args:
            endpoint: 要请求的端点。
            data: 要发送的表单数据或原始数据。
            headers: 要包含在请求中的头部信息。
            json_data: 要作为application/json发送的JSON数据。
            
        Returns:
            包含状态码、头部和响应数据的字典。
            
        Raises:
            HTTPException: 如果请求失败。
        """
        url = self._build_url(endpoint)
        if json_data:
            headers = headers or {}
            headers['Content-Type'] = 'application/json'
            data = json.dumps(json_data)
        return self._make_request_with_retry('PUT', url, data=data, headers=headers)

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发起DELETE请求。
        
        Args:
            endpoint: 要请求的端点。
            headers: 要包含在请求中的头部信息。
            
        Returns:
            包含状态码、头部和响应数据的字典。
            
        Raises:
            HTTPException: 如果请求失败。
        """
        url = self._build_url(endpoint)
        return self._make_request_with_retry('DELETE', url, headers=headers)

    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        从基础URL和端点构建完整URL。
        
        Args:
            endpoint: 要附加到基础URL的端点。
            params: 要附加到URL的查询参数。
            
        Returns:
            完整的URL字符串。
        """
        if self.base_url:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        else:
            url = endpoint

        if params:
            query_string = urlencode(params)
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}{query_string}"

        return url

    def _get_connection(self, parsed_url):
        """
        获取或创建到指定主机的HTTP连接。
        
        Args:
            parsed_url: 解析后的URL对象。
            
        Returns:
            HTTPConnection或HTTPSConnection实例。
        """
        # 构造连接键
        key = (parsed_url.scheme, parsed_url.hostname, parsed_url.port)
        
        # 检查是否超过最大连接数
        if key in self._connection_count and self._connection_count[key] >= self.max_connections:
            # 清理最旧的连接
            self._cleanup_oldest_connection(key)
        
        # 检查连接池中是否已有连接
        if key in self._connection_pool and self._connection_pool[key]:
            conn = self._connection_pool[key].pop()
            # 检查连接是否仍然有效
            try:
                # 快速检查连接是否有效
                if conn.sock:
                    conn.sock.settimeout(1)
                    conn.request("HEAD", "/")
                    resp = conn.getresponse()
                    resp.close()
                    conn.sock.settimeout(self.timeout)
                    # 更新连接计数
                    self._connection_count[key] = max(0, self._connection_count.get(key, 1) - 1)
                    # 更新连接创建时间
                    if id(conn) in self._connection_creation_time:
                        created_time, conn_key = self._connection_creation_time[id(conn)]
                        self._connection_creation_time[id(conn)] = (created_time, conn_key)
                    return conn
            except:
                # 连接无效，继续创建新连接
                # 清理无效连接的创建时间记录
                keys_to_remove = [conn_id for conn_id, conn_info 
                                 in self._connection_creation_time.items() 
                                 if conn_info[1] == key]
                for conn_id in keys_to_remove:
                    if conn_id in self._connection_creation_time:
                        del self._connection_creation_time[conn_id]
                pass
        
        # 创建新连接
        if parsed_url.scheme == "https":
            conn = HTTPSConnection(
                parsed_url.hostname, 
                parsed_url.port or 443, 
                timeout=self.timeout
            )
        else:
            conn = HTTPConnection(
                parsed_url.hostname, 
                parsed_url.port or 80, 
                timeout=self.timeout
            )
        
        # 记录连接创建时间
        conn_key = (parsed_url.scheme, parsed_url.hostname, parsed_url.port)
        self._connection_creation_time[id(conn)] = (time.time(), conn_key)
        
        # 更新连接计数
        self._connection_count[key] = self._connection_count.get(key, 0) + 1
        return conn

    def _return_connection(self, parsed_url, conn):
        """
        将连接返回到连接池。
        
        Args:
            parsed_url: 解析后的URL对象。
            conn: 要返回的连接。
        """
        key = (parsed_url.scheme, parsed_url.hostname, parsed_url.port)
        
        # 检查连接是否超时
        current_time = time.time()
        conn_info = self._connection_creation_time.get(id(conn))
        if conn_info:
            created_time, _ = conn_info
            if current_time - created_time >= self.connection_ttl:
                # 连接已超时，直接关闭
                try:
                    conn.close()
                    self._connection_count[key] = max(0, self._connection_count.get(key, 1) - 1)
                except:
                    pass
                # 清理创建时间记录
                if id(conn) in self._connection_creation_time:
                    del self._connection_creation_time[id(conn)]
                return
        
        # 初始化连接池列表
        if key not in self._connection_pool:
            self._connection_pool[key] = []
        
        # 如果连接池未满，则将连接放回池中
        if len(self._connection_pool[key]) < self.max_connections:
            self._connection_pool[key].append(conn)
        else:
            # 连接池已满，直接关闭连接
            try:
                conn.close()
                self._connection_count[key] = max(0, self._connection_count.get(key, 1) - 1)
            except:
                pass
            # 清理创建时间记录
            if id(conn) in self._connection_creation_time:
                del self._connection_creation_time[id(conn)]

    def _cleanup_oldest_connection(self, key):
        """
        清理最旧的连接。
        
        Args:
            key: 连接键。
        """
        if key in self._connection_pool and self._connection_pool[key]:
            conn = self._connection_pool[key].pop(0)
            try:
                conn.close()
                self._connection_count[key] = max(0, self._connection_count.get(key, 1) - 1)
                # 清理创建时间记录
                keys_to_remove = [conn_id for conn_id, conn_info 
                                 in self._connection_creation_time.items() 
                                 if conn_info[1] == key]
                for conn_id in keys_to_remove:
                    if conn_id in self._connection_creation_time:
                        del self._connection_creation_time[conn_id]
            except:
                pass

    def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发起HTTP请求。
        
        Args:
            method: HTTP方法（GET、POST、PUT、DELETE）。
            url: 要请求的完整URL。
            data: 要随请求发送的数据。
            headers: 要包含在请求中的头部信息。
            
        Returns:
            包含状态码、头部和响应数据的字典。
            
        Raises:
            HTTPException: 如果请求失败。
        """
        # 解析URL
        parsed_url = urlparse(url)
        
        # 准备头部信息
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # 添加Cookie头部
        if self.cookie_jar and self.enable_cookies:
            cookies = self.cookie_jar.get_cookies(parsed_url.hostname or '', parsed_url.path or '/')
            if cookies:
                cookie_header = '; '.join([f"{name}={value}" for name, value in cookies.items()])
                request_headers['Cookie'] = cookie_header
        
        # 获取连接
        conn = self._get_connection(parsed_url)
        
        # 准备路径和数据
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query
            
        request_data = None
        if isinstance(data, dict):
            request_data = urlencode(data)
            request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif isinstance(data, str):
            request_data = data

        try:
            # 发起请求
            conn.request(method, path, body=request_data, headers=request_headers)
            
            # 获取响应
            response = conn.getresponse()
            
            # 处理Set-Cookie头部
            if self.cookie_jar and self.enable_cookies:
                self._process_set_cookie_header(response.getheader('Set-Cookie', ''), 
                                              parsed_url.hostname or '', 
                                              parsed_url.path or '/')
            
            # 读取响应数据
            response_data = response.read()
            
            # 尝试解码为JSON，失败则回退为字符串
            try:
                content = json.loads(response_data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                content = response_data.decode('utf-8')
            
            # 将连接返回到连接池
            self._return_connection(parsed_url, conn)
            
            return {
                'status_code': response.status,
                'headers': dict(response.getheaders()),
                'content': content
            }
        except HTTPError as e:
            # 将连接返回到连接池
            self._return_connection(parsed_url, conn)
            raise HTTPException(f"HTTP {e.code} {e.reason} for URL: {url}") from e
        except URLError as e:
            # 连接错误，不将连接返回到连接池
            try:
                conn.close()
                key = (parsed_url.scheme, parsed_url.hostname, parsed_url.port)
                if key in self._connection_count:
                    self._connection_count[key] = max(0, self._connection_count[key] - 1)
                # 清理创建时间记录
                keys_to_remove = [conn_id for conn_id, conn_info 
                                 in self._connection_creation_time.items() 
                                 if conn_info[1] == key]
                for conn_id in keys_to_remove:
                    if conn_id in self._connection_creation_time:
                        del self._connection_creation_time[conn_id]
            except:
                pass
            raise HTTPException(f"URL错误: {e.reason}") from e
        except Exception as e:
            # 其他错误，将连接返回到连接池
            self._return_connection(parsed_url, conn)
            raise HTTPException(f"请求失败: {str(e)}") from e

    def _process_set_cookie_header(self, set_cookie_header: str, domain: str, path: str):
        """
        处理Set-Cookie头部，提取并存储Cookie。
        
        Args:
            set_cookie_header: Set-Cookie头部的值。
            domain: 默认域名。
            path: 默认路径。
        """
        if not set_cookie_header:
            return
            
        # 简单解析Set-Cookie头部（实际实现可能需要更复杂的解析）
        cookies = set_cookie_header.split(',') if isinstance(set_cookie_header, str) else []
        for cookie in cookies:
            parts = cookie.split(';')
            if not parts:
                continue
                
            # 解析cookie键值对
            cookie_part = parts[0].strip()
            if '=' not in cookie_part:
                continue
                
            name, value = cookie_part.split('=', 1)
            name = name.strip()
            value = value.strip()
            
            # 解析其他属性
            expires = None
            cookie_domain = domain
            cookie_path = path
            
            for part in parts[1:]:
                part = part.strip()
                if '=' in part:
                    attr_name, attr_value = part.split('=', 1)
                    attr_name = attr_name.strip().lower()
                    attr_value = attr_value.strip()
                    
                    if attr_name == 'expires':
                        # 简单处理过期时间（实际实现可能需要更复杂的解析）
                        try:
                            # 这里简化处理，实际应该解析HTTP日期格式
                            expires = time.time() + 3600  # 默认1小时后过期
                        except:
                            pass
                    elif attr_name == 'domain':
                        cookie_domain = attr_value
                    elif attr_name == 'path':
                        cookie_path = attr_value
            
            # 存储Cookie
            self.cookie_jar.set_cookie(cookie_domain, cookie_path, name, value, expires)

    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发起HTTP请求，支持重试机制。
        
        Args:
            method: HTTP方法（GET、POST、PUT、DELETE）。
            url: 要请求的完整URL。
            data: 要随请求发送的数据。
            headers: 要包含在请求中的头部信息。
            
        Returns:
            包含状态码、头部和响应数据的字典。
            
        Raises:
            HTTPException: 如果请求失败。
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return self._make_request(method, url, data, headers)
            except HTTPException as e:
                last_exception = e
                # 如果是客户端错误(4xx)，不重试
                if "HTTP 4" in str(e):
                    raise e
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.max_retries:
                    # 指数退避策略
                    wait_time = (2 ** attempt) + (0.1 * attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
            except Exception as e:
                last_exception = e
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.max_retries:
                    # 指数退避策略
                    wait_time = (2 ** attempt) + (0.1 * attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    raise HTTPException(f"请求失败: {str(e)}") from e
        
        # 如果所有重试都失败了
        raise HTTPException(f"请求失败，已重试{self.max_retries}次: {str(last_exception)}") from last_exception

    def set_cookie(self, domain: str, path: str, name: str, value: str, 
                   expires: Optional[float] = None):
        """
        手动设置Cookie。
        
        Args:
            domain: Cookie的域名。
            path: Cookie的路径。
            name: Cookie名称。
            value: Cookie值。
            expires: 过期时间（时间戳）。
        """
        if self.cookie_jar and self.enable_cookies:
            self.cookie_jar.set_cookie(domain, path, name, value, expires)

    def get_cookies(self, domain: str, path: str = '/') -> Dict[str, str]:
        """
        获取适用于指定域名和路径的Cookie。
        
        Args:
            domain: 域名。
            path: 路径。
            
        Returns:
            Cookie字典。
        """
        if self.cookie_jar and self.enable_cookies:
            return self.cookie_jar.get_cookies(domain, path)
        return {}

    def clear_cookies(self):
        """
        清空所有Cookie。
        """
        if self.cookie_jar and self.enable_cookies:
            self.cookie_jar.clear()

    def close(self):
        """
        关闭所有连接并清理连接池。
        """
        # 停止清理线程
        self._cleanup_stop_event.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=1)
        
        # 关闭所有连接
        for conn_list in self._connection_pool.values():
            for conn in conn_list:
                try:
                    conn.close()
                except:
                    pass
        
        # 清理所有跟踪数据
        for key in self._connection_count:
            self._connection_count[key] = 0
            
        self._connection_pool.clear()
        self._connection_creation_time.clear()

    def __del__(self):
        """
        析构时关闭所有连接。
        """
        self.close()


# 用于快速请求的便捷函数
def get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    使用默认HTTP客户端发起GET请求。
    
    Args:
        url: 要请求的URL。
        params: 要包含在请求中的查询参数。
        
    Returns:
        包含状态码、头部和响应数据的字典。
    """
    client = HTTPClient()
    try:
        return client.get(url, params)
    finally:
        client.close()


def post(
    url: str, 
    data: Optional[Union[Dict[str, Any], str]] = None,
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    使用默认HTTP客户端发起POST请求。
    
    Args:
        url: 要请求的URL。
        data: 要发送的表单数据或原始数据。
        json_data: 要作为application/json发送的JSON数据。
        
    Returns:
        包含状态码、头部和响应数据的字典。
    """
    client = HTTPClient()
    try:
        return client.post(url, data=data, json_data=json_data)
    finally:
        client.close()


def put(
    url: str, 
    data: Optional[Union[Dict[str, Any], str]] = None,
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    使用默认HTTP客户端发起PUT请求。
    
    Args:
        url: 要请求的URL。
        data: 要发送的表单数据或原始数据。
        json_data: 要作为application/json发送的JSON数据。
        
    Returns:
        包含状态码、头部和响应数据的字典。
    """
    client = HTTPClient()
    try:
        return client.put(url, data=data, json_data=json_data)
    finally:
        client.close()


def delete(url: str) -> Dict[str, Any]:
    """
    使用默认HTTP客户端发起DELETE请求。
    
    Args:
        url: 要请求的URL。
        
    Returns:
        包含状态码、头部和响应数据的字典。
    """
    client = HTTPClient()
    try:
        return client.delete(url)
    finally:
        client.close()