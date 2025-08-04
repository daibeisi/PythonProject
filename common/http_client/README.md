# HTTP客户端

一个简单而功能强大的Python HTTP客户端，支持各种HTTP方法、身份验证、自定义头部等功能。

## 功能特性

- 支持GET、POST、PUT、DELETE方法
- JSON和表单数据处理
- 自定义头部支持
- 基础URL配置
- 查询参数处理
- 错误处理和自定义异常
- 超时配置
- 高级连接池机制（复用TCP连接）
- 自动重试机制
- 后台线程定期清理超时连接
- Cookie自动管理
- 便捷函数用于快速请求
- 全面的测试覆盖

## 安装

无需额外依赖。仅使用Python标准库。

## 高级功能

### 连接池机制

当前实现包含一个高级的连接池机制，可以复用与同一主机的连接，提高性能并减少资源消耗：

1. **连接复用**：对同一主机的多个请求会复用相同的TCP连接
2. **连接限制**：可以限制每个主机的最大连接数（默认为10，与requests库一致）
3. **连接管理**：自动管理连接的生命周期和清理

默认的连接池大小设置为10，这个值与广泛使用的requests库中的默认值相同，经过了大量生产环境的验证，适合大多数应用场景。

### 重试机制

客户端内置了智能重试机制：

1. **自动重试**：默认情况下，请求失败时会自动重试最多3次
2. **指数退避**：重试间隔采用指数退避策略，减少服务器压力
3. **智能判断**：客户端错误(4xx)不会重试，只重试网络错误和服务器错误(5xx)

### 后台线程定期清理

为防止连接泄漏和资源浪费，客户端实现了后台线程定期清理超时连接：

1. **自动清理**：后台线程每30秒检查一次超时连接并自动清理
2. **可配置超时**：默认连接超时时间为300秒（5分钟），可通过`connection_ttl`参数配置
3. **资源优化**：及时释放长时间空闲的连接，避免资源浪费

### Cookie管理

客户端内置了Cookie管理功能，可以自动处理Cookie的存储和发送：

1. **自动处理**：自动解析响应中的Set-Cookie头部并存储Cookie
2. **智能匹配**：根据域名和路径自动匹配并发送相应的Cookie
3. **过期管理**：自动清理过期的Cookie
4. **手动控制**：支持手动设置和获取Cookie

## 使用方法

### 基本使用

```python
from http_client import get, post, put, delete

# 简单的GET请求
response = get("https://httpbin.org/get")
print(response['status_code'])  # 200
print(response['content'])      # 响应数据

# 带JSON数据的POST请求
response = post("https://httpbin.org/post", json_data={"key": "value"})
print(response['status_code'])  # 200
```

### 使用HTTPClient类

```python
from http_client import HTTPClient

# 创建客户端实例
client = HTTPClient(
    base_url="https://api.example.com", 
    timeout=30,
    max_retries=3,
    max_connections=10,   # 默认值与requests库一致
    connection_ttl=300,   # 连接5分钟后超时
    enable_cookies=True   # 启用Cookie管理（默认）
)

try:
    # 带查询参数的GET请求
    response = client.get("/users", params={"page": 1, "limit": 10})

    # 带JSON数据的POST请求
    response = client.post("/users", json_data={"name": "John", "email": "john@example.com"})

    # PUT请求
    response = client.put("/users/123", json_data={"name": "John Doe"})

    # DELETE请求
    response = client.delete("/users/123")

    # 自定义头部
    headers = {"Authorization": "Bearer token123"}
    response = client.get("/protected", headers=headers)
    
    # 手动设置Cookie
    client.set_cookie("example.com", "/", "session_id", "abc123")
    
    # 获取Cookie
    cookies = client.get_cookies("example.com", "/")
finally:
    # 关闭连接池中的所有连接
    client.close()
```

### Cookie管理示例

```python
from http_client import HTTPClient

client = HTTPClient()

# 手动设置Cookie
client.set_cookie("httpbin.org", "/", "user_id", "12345")
client.set_cookie("httpbin.org", "/api", "api_key", "secret_key")

# 发送请求时会自动包含匹配的Cookie
response = client.get("https://httpbin.org/cookies")
print(response['content']['cookies'])  # 显示服务器收到的Cookie

# 获取特定域名和路径的Cookie
cookies = client.get_cookies("httpbin.org", "/")
print(cookies)

# 清空所有Cookie
client.clear_cookies()

# 禁用Cookie功能
client_no_cookies = HTTPClient(enable_cookies=False)
```

### 响应格式

所有方法都返回具有以下结构的字典：

```python
{
    "status_code": 200,           # HTTP状态码
    "headers": {...},             # 响应头部
    "content": {...}              # 响应内容（解析后的JSON或字符串）
}
```

## 错误处理

客户端为所有HTTP相关错误抛出`HTTPException`：

```python
from http_client import get, HTTPException

try:
    response = get("https://httpbin.org/status/404")
except HTTPException as e:
    print(f"请求失败: {e}")
```

## 运行测试

```bash
python -m unittest http_client.test_http_client
```

## API参考

### HTTPClient

#### `__init__(base_url=None, timeout=30, max_retries=3, max_connections=10, connection_ttl=300, enable_cookies=True)`
初始化HTTP客户端。

- `base_url`: 所有请求的基础URL（可选）
- `timeout`: 请求超时时间（秒，默认：30）
- `max_retries`: 最大重试次数（默认：3）
- `max_connections`: 连接池最大连接数（默认：10，与requests库一致）
- `connection_ttl`: 连接最大存活时间（秒，默认：300）
- `enable_cookies`: 是否启用Cookie管理（默认：True）

#### `get(endpoint, params=None, headers=None)`
发起GET请求。

- `endpoint`: 请求端点
- `params`: 查询参数（可选）
- `headers`: 自定义头部（可选）

#### `post(endpoint, data=None, headers=None, json_data=None)`
发起POST请求。

- `endpoint`: 请求端点
- `data`: 表单数据或原始数据（可选）
- `headers`: 自定义头部（可选）
- `json_data`: 要发送的JSON数据（可选）

#### `put(endpoint, data=None, headers=None, json_data=None)`
发起PUT请求。

- `endpoint`: 请求端点
- `data`: 表单数据或原始数据（可选）
- `headers`: 自定义头部（可选）
- `json_data`: 要发送的JSON数据（可选）

#### `delete(endpoint, headers=None)`
发起DELETE请求。

- `endpoint`: 请求端点
- `headers`: 自定义头部（可选）

#### `set_cookie(domain, path, name, value, expires=None)`
手动设置Cookie。

- `domain`: Cookie的域名
- `path`: Cookie的路径
- `name`: Cookie名称
- `value`: Cookie值
- `expires`: 过期时间（时间戳，可选）

#### `get_cookies(domain, path='/')`
获取适用于指定域名和路径的Cookie。

- `domain`: 域名
- `path`: 路径

#### `clear_cookies()`
清空所有Cookie。

#### `close()`
关闭所有连接并清理连接池。使用完客户端后应调用此方法。

### 便捷函数

#### `get(url, params=None)`
使用默认HTTP客户端发起GET请求。

#### `post(url, data=None, json_data=None)`
使用默认HTTP客户端发起POST请求。

#### `put(url, data=None, json_data=None)`
使用默认HTTP客户端发起PUT请求。

#### `delete(url)`
使用默认HTTP客户端发起DELETE请求。

便捷函数会自动管理连接生命周期，无需手动调用close()。

## 生产环境使用建议

1. **复用客户端实例**：在需要发送多个请求时，应复用同一个客户端实例以充分利用连接池
2. **合理设置连接数**：默认的10个连接对于大多数应用已经足够，高并发场景可适当增加
3. **及时关闭连接**：使用完客户端后调用[close()](file:///d:/PycharmProjects/PythonProject/http_client/__init__.py#L307-L316)方法释放资源
4. **配置重试机制**：根据服务端的稳定性合理设置重试次数
5. **调整连接超时**：根据应用需求调整`connection_ttl`参数，避免长时间占用无用连接
6. **Cookie管理**：对于需要会话管理的应用，确保启用Cookie功能

## 示例

参见 `example.py` 获取更多详细的使用示例。