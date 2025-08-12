import json
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, Tuple, Iterator

import etcd3

logger = logging.getLogger(__name__)


class EtcdClient:
    """Etcd 客户端类

    提供etcd连接管理、键值操作、监听等功能
    """

    def __init__(self, host: str = 'localhost', port: int = 2379,
                 user: Optional[str] = None, password: Optional[str] = None,
                 ca_cert: Optional[str] = None, cert_key: Optional[str] = None,
                 cert_cert: Optional[str] = None, timeout: int = 10,
                 grpc_options: Optional[Dict] = None) -> None:
        """
        初始化etcd客户端

        Args:
            host (str): etcd服务器地址
            port (int): etcd服务器端口
            user (Optional[str]): 用户名
            password (Optional[str]): 密码
            ca_cert (Optional[str]): CA证书路径
            cert_key (Optional[str]): 客户端私钥路径
            cert_cert (Optional[str]): 客户端证书路径
            timeout (int): 连接超时时间（秒）
            grpc_options (Optional[Dict]): gRPC选项

        Returns:
            None

        Raises:
            None
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.ca_cert = ca_cert
        self.cert_key = cert_key
        self.cert_cert = cert_cert
        self.timeout = timeout
        self.grpc_options = grpc_options or {}

        self.client: Optional[etcd3.Etcd3Client] = None
        self._watch_threads: Dict = {}
        self._connected = False
        self.data: Dict = {}

    def connect(self) -> bool:
        """
        连接到etcd服务器
        """
        try:
            self.client = etcd3.client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                ca_cert=self.ca_cert,
                cert_key=self.cert_key,
                cert_cert=self.cert_cert,
                timeout=self.timeout,
                grpc_options=self.grpc_options
            )

            # 测试连接
            self.client.status()
            self._connected = True
            logger.info(f"成功连接到etcd服务器: {self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"连接etcd服务器失败: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """断开etcd连接"""
        try:
            if self.client:
                self.client.close()
                self.client = None

            self._connected = False
            logger.info("已断开etcd连接")

        except Exception as e:
            logger.error(f"断开etcd连接时发生错误: {str(e)}")

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self.client is not None

    def _ensure_connected(self) -> bool:
        """确保已连接，如果未连接则尝试连接"""
        if not self.is_connected():
            return self.connect()
        return True

    @contextmanager
    def transaction(self) -> Iterator:
        """
        事务上下文管理器

        Args:
            None

        Yields:
            etcd3.Txn: 事务对象

        Raises:
            ConnectionError: 无法连接到etcd服务器
        """
        if not self._ensure_connected():
            raise ConnectionError("无法连接到etcd服务器")

        txn = self.client.transactions.txn()
        try:
            yield txn
        except Exception as e:
            logger.error(f"事务执行失败: {str(e)}")
            raise

    def put(self, key: str, value: Any, lease: Optional[int] = None) -> bool:
        """
        设置键值对

        Args:
            key (str): 键
            value (Any): 值（会自动序列化为JSON）
            lease (Optional[int]): 租约ID

        Returns:
            bool: 是否设置成功

        Raises:
            None
        """
        if not self._ensure_connected():
            return False

        try:
            # 如果值不是字符串，则序列化为JSON
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)

            self.client.put(key, value, lease=lease)
            logger.debug(f"设置键值对成功: {key} = {value}")
            return True

        except Exception as e:
            logger.error(f"设置键值对失败 {key}: {str(e)}")
            return False

    def import_json(self, json_str: str = None, clear_existing: bool = True) -> bool:
        """
        从JSON字符串导入数据到etcd

        Args:
            json_str (str): 输入JSON字符串
            clear_existing (bool): 是否清空现有数据

        Returns:
            bool: 是否导入成功

        Raises:
            None
        """
        if json_str is None:
            data = self.data
        else:
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("输入的JSON字符串无效")
                return False

        if not self._ensure_connected():
            return False

        try:
            if clear_existing:
                # 删除所有现有键
                self.client.delete_prefix('/')

            # 导入数据
            for key, value in data.items():
                self.put(key, value)

            logger.info("已成功从JSON字符串导入数据到etcd")
            return True
        except Exception as e:
            logger.error(f"从JSON字符串导入数据到etcd 失败: {str(e)}")
            return False

    def import_data(self, input_file: str, clear_existing: bool = True) -> bool:
        """
        从JSON文件导入数据到etcd

        Args:
            input_file (str): 输入JSON文件路径
            clear_existing (bool): 是否清空现有数据

        Returns:
            bool: 是否导入成功

        Raises:
            None
        """
        if not self._ensure_connected():
            return False

        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if clear_existing:
                # 删除所有现有键
                self.client.delete_prefix('/')

            for key, value in data.items():
                self.put(key, value)

            logger.info(f"已成功从文件 {input_file} 导入数据到etcd")
            return True

        except Exception as e:
            logger.error(f"从文件 {input_file} 导入数据到etcd 失败: {str(e)}")
            return False

    def export_data(self, output_file: str) -> bool:
        """
        从etcd导出数据到JSON文件

        Args:
            output_file (str): 输出JSON文件路径

        Returns:
            bool: 是否导出成功

        Raises:
            None
        """
        if not self._ensure_connected():
            return False

        try:
            data = {}
            for value, metadata in self.client.get_all():
                key = metadata.key.decode('utf-8')
                try:
                    # 尝试解析JSON
                    parsed_value = json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # 如果不是JSON，保存原始字符串
                    parsed_value = value.decode('utf-8')
                data[key] = parsed_value

            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            logger.info(f"已成功从etcd导出数据到文件 {output_file}")
            return True

        except Exception as e:
            logger.error(f"从etcd导出数据到文件 {output_file} 失败: {str(e)}")
            return False

    def get(self, key: str, serializable: bool = False) -> Optional[Any]:
        """
        获取键对应的值

        Args:
            key (str): 键
            serializable (bool): 是否使用可序列化读取

        Returns:
            Optional[Any]: 值（自动反序列化JSON），如果不存在返回None

        Raises:
            None
        """
        if not self._ensure_connected():
            return None

        try:
            value, metadata = self.client.get(key, serializable=serializable)
            if value is None:
                return None

            # 尝试反序列化JSON
            try:
                return json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # 如果不是JSON，返回原始字符串
                return value.decode('utf-8')

        except Exception as e:
            logger.error(f"获取键值失败 {key}: {str(e)}")
            return None

    def get_with_metadata(self, key: str) -> Tuple[Optional[Any], Optional[Dict]]:
        """
        获取键对应的值和元数据

        Args:
            key (str): 键

        Returns:
            Tuple[Optional[Any], Optional[Dict]]: (值, 元数据字典)

        Raises:
            None
        """
        if not self._ensure_connected():
            return None, None

        try:
            value, metadata = self.client.get(key)
            if value is None:
                return None, None

            # 尝试反序列化JSON
            try:
                parsed_value = json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                parsed_value = value.decode('utf-8')

            # 构建元数据字典
            meta_dict = {
                'key': metadata.key.decode('utf-8') if metadata.key else None,
                'create_revision': metadata.create_revision,
                'mod_revision': metadata.mod_revision,
                'version': metadata.version,
                'lease_id': metadata.lease_id
            }

            return parsed_value, meta_dict

        except Exception as e:
            logger.error(f"获取键值和元数据失败 {key}: {str(e)}")
            return None, None

    def delete(self, key: str, prefix: bool = False) -> bool:
        """
        删除键

        Args:
            key (str): 键
            prefix (bool): 是否按前缀删除

        Returns:
            bool: 是否删除成功

        Raises:
            None
        """
        if not self._ensure_connected():
            return False

        try:
            deleted = self.client.delete(key, prefix=prefix)
            logger.debug(f"删除键成功: {key}, 删除数量: {deleted}")
            return True

        except Exception as e:
            logger.error(f"删除键失败 {key}: {str(e)}")
            return False

    def get_prefix(self, prefix: str, sort_order: Optional[str] = None,
                   sort_target: str = 'key') -> Dict[str, Any]:
        """
        获取指定前缀的所有键值对

        Args:
            prefix (str): 键前缀
            sort_order (Optional[str]): 排序顺序 ('ascend' 或 'descend')
            sort_target (str): 排序目标 ('key', 'version', 'create', 'mod', 'value')

        Returns:
            Dict[str, Any]: 键值对字典

        Raises:
            None
        """
        if not self._ensure_connected():
            return {}

        try:
            result = {}
            for value, metadata in self.client.get_prefix(
                    prefix, sort_order=sort_order, sort_target=sort_target
            ):
                key = metadata.key.decode('utf-8')

                # 尝试反序列化JSON
                try:
                    parsed_value = json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    parsed_value = value.decode('utf-8')

                result[key] = parsed_value

            return result

        except Exception as e:
            logger.error(f"获取前缀键值对失败 {prefix}: {str(e)}")
            return {}

    def get_cluster_status(self) -> Optional[Dict]:
        """
        获取集群状态

        Args:
            None

        Returns:
            Optional[Dict]: 集群状态信息

        Raises:
            None
        """
        if not self._ensure_connected():
            return None

        try:
            status = self.client.status()
            return {
                'version': status.version,
                'db_size': status.db_size,
                'leader': status.leader,
                'raft_index': status.raft_index,
                'raft_term': status.raft_term
            }

        except Exception as e:
            logger.error(f"获取集群状态失败: {str(e)}")
            return None

    def __enter__(self) -> 'EtcdClient':
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """上下文管理器退出"""
        self.disconnect()

    def __del__(self) -> None:
        """析构函数"""
        try:
            self.disconnect()
        except:
            pass