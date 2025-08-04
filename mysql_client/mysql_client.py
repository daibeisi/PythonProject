"""MySQL 数据库连接客户端
    
这个模块提供了一个封装了 MySQL 数据库操作的客户端类。主要特性：
1. 使用连接池管理数据库连接
2. 支持基本的 CRUD 操作
3. 支持参数化查询，防止 SQL 注入
4. 支持上下文管理器（with 语句）
5. 自动事务管理和异常处理
6. 返回字典格式的查询结果

使用示例:
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'test_db'
    }

    # 使用上下文管理器
    with MySQLClient(**db_config) as db:
        result = db.fetch_all("SELECT * FROM users")
        print(result)

依赖:
    - PyMySQL
    - DBUtils

作者: daibeisi
版本: 1.0.0
日期: 2025-02-20
"""

import pymysql
from pymysql.cursors import DictCursor
from typing import Any, Dict, List, Optional, Union
from dbutils.pooled_db import PooledDB
# 在文件开头添加自定义异常类
class MySQLClientError(Exception):
    """MySQL客户端基础异常"""
    pass

class ConnectionError(MySQLClientError):
    """连接相关异常"""
    pass

class ExecuteError(MySQLClientError):
    """SQL执行相关异常"""
    pass

class SQLInjectionError(MySQLClientError):
    """SQL注入相关异常"""
    pass

class MySQLClient:
    _pool = None

    def __init__(
            self,
            host: str,
            user: str,
            password: str,
            database: str,
            port: int = 3306,
            charset: str = 'utf8mb4',
            min_cached: int = 5,
            max_cached: int = 20,
            max_connections: int = 100
    ) -> None:
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'charset': charset,
            'cursorclass': DictCursor
        }
        self.pool_config = {
            'mincached': min_cached,      # 初始化时，连接池中最小连接数
            'maxcached': max_cached,      # 连接池中最大闲置连接数
            'maxconnections': max_connections,  # 连接池允许的最大连接数
            'blocking': True,             # 连接池中没有可用连接时，是否阻塞等待
            'ping': 0                     # ping MySQL服务端，检查服务是否可用
        }
        self.conn = None
        self.cursor = None
        self._init_pool()

    def _init_pool(self) -> None:
        """初始化连接池"""
        if MySQLClient._pool is None:
            MySQLClient._pool = PooledDB(pymysql, **self.pool_config, **self.config)

    def connect(self) -> None:
        """从连接池获取连接"""
        try:
            self.conn = MySQLClient._pool.connection()
            self.cursor = self.conn.cursor()
        except Exception as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    def _validate_sql(self, sql: str) -> None:
        """验证SQL语句安全性"""
        try:
            dangerous_patterns = [
                r';\s*\w+',  # 多语句执行
                r'--\s*$',   # 行注释
                r'/\*.*?\*/', # 块注释
                r'xp_\w+',   # 扩展存储过程
            ]
            sql_upper = sql.upper()
            for pattern in dangerous_patterns:
                if re.search(pattern, sql_upper, re.IGNORECASE):
                    raise SQLInjectionError(f"SQL语句包含不安全的模式: {sql}")
        except Exception as e:
            if not isinstance(e, SQLInjectionError):
                raise ExecuteError(f"SQL验证失败: {str(e)}")
            raise

    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """执行SQL语句"""
        try:
            self._validate_sql(sql)
            
            if not self.conn:
                self.connect()
                
            row_count = self.cursor.execute(sql, params)
            self.conn.commit()
            return row_count
        except MySQLClientError:
            # 直接向上传播自定义异常
            raise
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise ExecuteError(f"SQL执行失败: {str(e)}")

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入数据"""
        try:
            # 验证表名和字段名
            if not re.match(r'^[a-zA-Z0-9_]+$', table):
                raise SQLInjectionError(f"不安全的表名: {table}")
            
            for field in data.keys():
                if not re.match(r'^[a-zA-Z0-9_]+$', field):
                    raise SQLInjectionError(f"不安全的字段名: {field}")
            
            fields = ','.join(data.keys())
            values = ','.join(['%s'] * len(data))
            sql = f"INSERT INTO {table} ({fields}) VALUES ({values})"
            return self.execute(sql, tuple(data.values()))
        except MySQLClientError:
            raise
        except Exception as e:
            raise ExecuteError(f"插入数据失败: {str(e)}")
        except Exception as e:
            raise Exception(f"SQL执行失败: {str(e)}")

    def update(self, table: str, data: Dict[str, Any], condition: str, params: tuple) -> int:
        """更新数据
        
        参数:
            table: 表名
            data: 要更新的数据字典
            condition: WHERE条件
            params: 条件参数

        Returns:
            更新成功的行数
        """
        set_fields = ','.join([f"{k}=%s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_fields} WHERE {condition}"
        return self.execute(sql, tuple(data.values()) + params)

    def delete(self, table: str, condition: str, params: Optional[tuple] = None) -> int:
        """删除数据
        Args:
            table: 表名
            condition: WHERE条件
            params: 条件参数

        Returns:
            删除成功的行数
        """
        sql = f"DELETE FROM {table} WHERE {condition}"
        return self.execute(sql, params)

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


if __name__ == '__main__':
    # 使用示例
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'test_db'
    }

    # 方式1：使用上下文管理器
    with MySQLClient(**db_config) as db:
        # 查询数据
        result = db.fetch_all("SELECT * FROM users WHERE age > %s", (18,))
        print(result)

        # 插入数据
        data = {'name': 'Tom', 'age': 20}
        db.insert('users', data)

        # 更新数据
        update_data = {'age': 21}
        db.update('users', update_data, 'name = %s', ('Tom',))

        # 删除数据
        db.delete('users', 'name = %s', ('Tom',))

    # 方式2：手动管理连接
    db = MySQLClient(**db_config)
    try:
        db.connect()
        result = db.fetch_one("SELECT * FROM users LIMIT 1")
        print(result)
    finally:
        db.close()