"""
配置管理模块

该模块提供了一个灵活的配置管理器，支持从环境变量和配置文件中读取配置项。
环境变量的优先级高于配置文件，允许运行时覆盖配置值。

支持的配置文件格式：
- JSON (.json)
- YAML (.yaml, .yml)
- INI (.ini)

特性：
- 环境变量优先读取
- 配置值类型转换
- AES加密/解密支持
- 多种配置文件格式支持

使用示例：

1. 基本用法：
    # 从配置文件加载
    config = Config('config.json')
    value = config.get('database.host')

2. 带默认值和类型转换：
    # 获取整数类型配置，带默认值
    port = config.get('database.port', cast=int, default=5432)

3. 从环境变量读取：
    # 环境变量 DATABASE_HOST 会优先于配置文件中的 database.host
    host = config.get('database.host')

4. 加密配置值：
    # 读取加密的配置项
    password = config.get('database.password', is_secret=True)

5. 使用不同格式的配置文件：
    # JSON格式
    config = Config('config.json')

    # YAML格式
    config = Config('config.yaml')

    # INI格式
    config = Config('config.ini')

注意事项：
1. 环境变量名区分大小写
2. 配置文件中的键名不区分大小写（内部会自动转为小写）
3. 环境变量一旦被读取，就不能再被修改或删除，防止配置不一致
4. 加密功能需要提供secret_key
5. 加密使用AES CBC模式，密钥长度会自动调整为16字节
6. 布尔类型转换支持多种值：true/1/yes/false/0/no等
"""

import base64
import configparser
import json
import os
import typing
from pathlib import Path
from typing import Union, Optional

import yaml
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


class Undefined:
    """
    用于表示未定义的默认值的占位符类
    与None不同，这个类专门用于标识配置项没有默认值的情况
    """
    pass


class EnvironError(Exception):
    """
    环境变量操作异常类
    当尝试修改已经读取过的环境变量时抛出此异常
    """
    pass


class Environ(typing.MutableMapping[str, str]):
    """
    环境变量包装类，用于安全地访问和操作环境变量
    防止在运行时修改已经被读取的环境变量，避免配置不一致的问题
    """

    def __init__(self, environ: typing.MutableMapping[str, str] = os.environ):
        """
        初始化Environ实例

        :param environ: 环境变量映射，默认使用系统环境变量os.environ
        """
        self._environ = environ
        self._has_been_read: set[str] = set()

    def __getitem__(self, key: str) -> str:
        """
        获取环境变量值，并记录该变量已被读取

        :param key: 环境变量键名
        :return: 环境变量值
        """
        self._has_been_read.add(key)
        return self._environ.__getitem__(key)

    def __setitem__(self, key: str, value: str) -> None:
        """
        设置环境变量值

        :param key: 环境变量键名
        :param value: 环境变量值
        :raises EnvironError: 当该环境变量已经被读取过时抛出异常
        """
        if key in self._has_been_read:
            raise EnvironError(f"Attempting to set environ['{key}'], but the value has already been read.")
        self._environ.__setitem__(key, value)

    def __delitem__(self, key: str) -> None:
        """
        删除环境变量

        :param key: 环境变量键名
        :raises EnvironError: 当该环境变量已经被读取过时抛出异常
        """
        if key in self._has_been_read:
            raise EnvironError(f"Attempting to delete environ['{key}'], but the value has already been read.")
        self._environ.__delitem__(key)

    def __iter__(self) -> typing.Iterator[str]:
        """
        迭代环境变量键名

        :return: 环境变量键名迭代器
        """
        return iter(self._environ)

    def __len__(self) -> int:
        """
        获取环境变量数量

        :return: 环境变量总数
        """
        return len(self._environ)


# 创建全局环境变量实例
env = Environ()


class ConfigLoader:
    """
    配置加载器抽象基类
    定义配置加载器的接口规范
    """

    def load(self, path: Path) -> dict:
        """
        加载配置文件（抽象方法，需要子类实现）

        :param path: 配置文件路径
        :return: 配置字典
        :raises NotImplementedError: 子类未实现此方法时抛出
        """
        raise NotImplementedError


class JsonConfigLoader(ConfigLoader):
    """
    JSON格式配置加载器
    负责加载和解析JSON格式的配置文件
    """

    def load(self, path: Path) -> dict:
        """
        加载JSON格式配置文件

        :param path: JSON配置文件路径
        :return: 解析后的配置字典
        """
        with path.open() as f:
            return json.load(f)


class YamlConfigLoader(ConfigLoader):
    """
    YAML格式配置加载器
    负责加载和解析YAML格式的配置文件
    """

    def load(self, path: Path) -> dict:
        """
        加载YAML格式配置文件

        :param path: YAML配置文件路径
        :return: 解析后的配置字典
        """
        with path.open() as f:
            return yaml.safe_load(f)


class IniConfigLoader(ConfigLoader):
    """
    INI格式配置加载器
    负责加载和解析INI格式的配置文件
    """

    def load(self, path: Path) -> dict:
        """
        加载INI格式配置文件

        :param path: INI配置文件路径
        :return: 解析后的配置字典，格式为{section: {key: value}}
        """
        parser = configparser.ConfigParser()
        parser.read(path)
        return {section: dict(parser.items(section)) for section in parser.sections()}


class Config:
    """
    配置管理类
    支持从环境变量和配置文件中读取配置，环境变量优先于配置文件
    支持配置值的加密和解密，以及类型转换
    """

    def __init__(
            self,
            config_file: Union[str, Path, None] = None,
            secret_key: Union[str, bytes, None] = None,  # 支持字节类型的密钥
            environ: typing.Mapping[str, str] = env
    ) -> None:
        """
        初始化配置管理器

        :param config_file: 配置文件路径
        :param environ: 环境变量映射
        :param secret_key: 配置值加密的密钥
        """
        self._file_values: dict[str, str] = {}
        self._environ = environ
        self._secret_key = secret_key
        # 初始化AES加密的初始向量
        self._iv = b'\x00' * AES.block_size

        # 加载配置文件,判断是否配置和否存在
        if config_file and Path(config_file).exists():
            self._file_values = self._load_config(config_file)

    @staticmethod
    def _load_config(file_path: Union[str, Path]) -> dict:
        """
        根据文件扩展名加载对应的配置文件

        :param file_path: 配置文件路径
        :return: 解析后的配置字典
        :raises ValueError: 不支持的配置文件类型时抛出异常
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        loader_map = {
            ".json": JsonConfigLoader(),
            ".yaml": YamlConfigLoader(),
            ".yml": YamlConfigLoader(),
            ".ini": IniConfigLoader(),
        }

        if ext not in loader_map:
            raise ValueError(f"Unsupported config file type: {ext}")
        return loader_map[ext].load(path)

    def get(
            self,
            key: str,
            cast: Optional[typing.Callable[[typing.Any], typing.Any]] = None,
            default: typing.Any = Undefined,
            is_secret: bool = False,
    ) -> typing.Any:
        """获取配置值
            优先从环境变量中取配置值，环境变量中找不到时，去配置文件中取值，在配置文件和环境变量中取不到值时，
            如果默认值已设置，直接返回默认值，默认值不做解密和类型转换
        :param key: 配置键
        :param cast: 配置类型
        :param default: 配置默认值
        :param is_secret: 配置值是否加密
        :return: 配置值
        """
        if key in self._environ:
            value = self._environ[key]
        elif key.upper() in self._environ:
            value = self._environ[key.upper()]
        elif key in self._file_values:
            value = self._file_values[key]
        elif default is not Undefined:
            return default
        else:
            raise KeyError(f"Config '{key}' is missing, and has no default.")
        if is_secret:
            value = self._aes_decrypt(value)
        return self._perform_cast(key, value, cast)

    @staticmethod
    def _perform_cast(
            key: str,
            value: typing.Any,
            cast: Optional[typing.Callable[[typing.Any], typing.Any]] = None,
    ) -> typing.Any:
        """执行类型转换

        :param key: 配置键
        :param value: 配置值
        :param cast: 配置值类型
        :return: 配置值
        """
        if cast is None or value is None:
            return value
        elif cast is bool and isinstance(value, str):
            mapping = {"true": True, "1": True, "false": False, "0": False, "yes": True, "no": False,
                       "True": True, "False": False, "YES": True, "NO": False}
            value = value.lower()
            if value not in mapping:
                raise ValueError(f"Config '{key}' has value '{value}'. Not a valid bool.")
            return mapping[value]
        try:
            return cast(value)
        except (TypeError, ValueError):
            raise ValueError(f"Config '{key}' has value '{value}'. Not a valid {cast.__name__}.")

    def aes_encrypt(self, text: str) -> str:
        """
        使用 AES-GCM 加密文本并返回 Base64 编码串（格式： nonce(12) | tag(16) | ciphertext ）
        - 返回的 Base64 字符串可在另一台机器上使用相同 secret_key 解密
        :param text: 待加密明文
        :return: Base64 编码字符串（包含 nonce 和 tag）
        :raises ValueError: 未设置 secret_key 时抛出
        """
        if not self._secret_key:
            raise ValueError("Secret key is required for encryption")

        key = self._get_formatted_key()  # 派生并返回 bytes（32）
        # 推荐使用 12 字节 nonce（GCM 推荐长度）
        nonce = os.urandom(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(text.encode("utf-8"))

        packed = nonce + tag + ciphertext
        return base64.b64encode(packed).decode("utf-8")

    def _aes_decrypt(self, encoded: str) -> str:
        """
        使用 AES-GCM 解密 Base64 编码的字符串（应是 nonce|tag|ciphertext 的拼接）
        :param encoded: Base64 编码的密文
        :return: 解密后的明文字符串
        :raises ValueError: 未设置 secret_key 或解密/验证失败时抛出
        """
        if not self._secret_key:
            raise ValueError("Secret key is required for decryption")

        try:
            raw = base64.b64decode(encoded)
        except Exception as e:
            raise ValueError("Invalid base64 input for decryption") from e

        # nonce(12) | tag(16) | ciphertext(rest)
        if len(raw) < 12 + 16:
            raise ValueError("Ciphertext too short to contain nonce and tag")

        nonce = raw[:12]
        tag = raw[12:28]
        ciphertext = raw[28:]

        key = self._get_formatted_key()
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError as e:
            # 验证失败（可能是密钥错误或数据被篡改）
            raise ValueError("Decryption failed or data corrupted") from e

        return plaintext.decode("utf-8")

    def _get_formatted_key(self) -> bytes:
        """
        将用户提供的 secret_key（str 或 bytes）派生为固定长度的 AES 密钥（32 字节）
        - 使用 SHA-256 对密钥材料做一次单向散列，得到 32 字节密钥
        - 这样无论用户传入 8/16/24/32 长度的 key 都可以安全使用
        :return: 32 字节密钥（bytes）
        """
        if isinstance(self._secret_key, bytes):
            raw = self._secret_key
        else:
            raw = str(self._secret_key).encode("utf-8")
        h = SHA256.new(raw)
        return h.digest()


if __name__ == "__main__":
    config = Config('', secret_key='_2@_c-8m3cb-c_!l')
    print(config.get('/cluster/server/ip'))
