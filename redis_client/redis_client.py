import redis
import logging
from redis.exceptions import ConnectionError, TimeoutError


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0, password=None, socket_timeout=None):
        """
        初始化Redis客户端
        :param host: Redis服务器地址
        :param port: Redis服务器端口
        :param db: 数据库编号
        :param password: 密码
        :param socket_timeout: 套接字超时时间
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout
        self.client = None
        self.connect()

    def connect(self):
        """
        连接到Redis服务器
        """
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                socket_timeout=self.socket_timeout
            )
            self.client.ping()  # 测试连接是否成功
            logging.info("Connected to Redis successfully.")
        except ConnectionError as e:
            logging.error(f"Failed to connect to Redis: {e}")
        except TimeoutError as e:
            logging.error(f"Connection timed out: {e}")

    def set_key(self, key, value, ex=None, px=None, nx=False, xx=False):
        """
        设置键值对
        :param key: 键名
        :param value: 键值
        :param ex: 过期时间（秒）
        :param px: 过期时间（毫秒）
        :param nx: 如果设置为True，则只有在键不存在时才设置
        :param xx: 如果设置为True，则只有在键存在时才设置
        """
        try:
            result = self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            logging.debug(f"Set key '{key}' with value '{value}'. Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Failed to set key '{key}': {e}")
            return False

    def get_key(self, key):
        """
        获取键值
        :param key: 键名
        :return: 键值或None
        """
        try:
            value = self.client.get(key)
            logging.debug(f"Got key '{key}' with value '{value}'.")
            return value
        except Exception as e:
            logging.error(f"Failed to get key '{key}': {e}")
            return None

    def delete_key(self, *keys):
        """
        删除键
        :param keys: 键名列表
        :return: 删除的键的数量
        """
        try:
            count = self.client.delete(*keys)
            logging.debug(f"Deleted keys {keys}. Count: {count}")
            return count
        except Exception as e:
            logging.error(f"Failed to delete key(s) {keys}: {e}")
            return 0

    def exists(self, *keys):
        """
        检查键是否存在
        :param keys: 键名列表
        :return: 存在的键的数量
        """
        try:
            count = self.client.exists(*keys)
            logging.debug(f"Checked existence of keys {keys}. Count: {count}")
            return count
        except Exception as e:
            logging.error(f"Failed to check existence of key(s) {keys}: {e}")
            return 0

    def close(self):
        """
        关闭连接
        """
        if self.client:
            self.client.close()
            logging.info("Redis connection closed.")

# 使用示例
if __name__ == "__main__":
    redis_client = RedisClient(host='localhost', port=6379, password=None)
    redis_client.set_key('test_key', 'test_value', ex=10)
    print(redis_client.get_key('test_key'))
    redis_client.delete_key('test_key')
    redis_client.close()
