import base64
import configparser
import json
import os
import typing
from pathlib import Path

import yaml
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class Undefined:
    pass


class EnvironError(Exception):
    pass


class Environ(typing.MutableMapping[str, str]):
    def __init__(self, environ: typing.MutableMapping[str, str] = os.environ):
        self._environ = environ
        self._has_been_read: set[str] = set()

    def __getitem__(self, key: str) -> str:
        self._has_been_read.add(key)
        return self._environ.__getitem__(key)

    def __setitem__(self, key: str, value: str) -> None:
        if key in self._has_been_read:
            raise EnvironError(f"Attempting to set environ['{key}'], but the value has already been read.")
        self._environ.__setitem__(key, value)

    def __delitem__(self, key: str) -> None:
        if key in self._has_been_read:
            raise EnvironError(f"Attempting to delete environ['{key}'], but the value has already been read.")
        self._environ.__delitem__(key)

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)


env = Environ()


class ConfigLoader:
    def load(self, path: Path) -> dict:
        raise NotImplementedError


class JsonConfigLoader(ConfigLoader):
    def load(self, path: Path) -> dict:
        with path.open() as f:
            return json.load(f)


class YamlConfigLoader(ConfigLoader):
    def load(self, path: Path) -> dict:
        with path.open() as f:
            return yaml.safe_load(f)


class IniConfigLoader(ConfigLoader):
    def load(self, path: Path) -> dict:
        parser = configparser.ConfigParser()
        parser.read(path)
        return {section: dict(parser.items(section)) for section in parser.sections()}


class Config:
    def __init__(
            self,
            config_file: str | Path | None = None,
            secret_key: str | bytes | None = None,  # 支持字节类型的密钥
            environ: typing.Mapping[str, str] = env
    ) -> None:
        """
        :param config_file: 配置文件路径
        :param environ: 环境变量
        :param secret_key: 配置值加密的密钥
        """
        self.file_values: dict[str, str] = {}
        self.environ = environ
        self._secret_key = secret_key
        self._iv = b'\x00' * AES.block_size

        if config_file:
            self._file_values = self._load_config(config_file)

    @staticmethod
    def _load_config(file_path: str | Path) -> dict:
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
        cast: typing.Callable[[typing.Any], typing.Any] | None = None,
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
        if key in self.environ:
            value = self.environ[key]
        elif key in self.file_values:
            value = self.file_values[key]
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
        cast: typing.Callable[[typing.Any], typing.Any] | None = None,
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
        if not self._secret_key:
            raise ValueError("Secret key is required for encryption")
        key = self._get_formatted_key()
        cipher = AES.new(key, AES.MODE_CBC, self._iv)
        encrypted_bytes = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    def _aes_decrypt(self, text: str) -> str:
        if not self._secret_key:
            raise ValueError("Secret key is required for decryption")
        key = self._get_formatted_key()
        cipher = AES.new(key, AES.MODE_CBC, self._iv)
        decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(text)), AES.block_size)
        return decrypted_bytes.decode("utf-8")

    def _get_formatted_key(self) -> bytes:
        if isinstance(self._secret_key, bytes):
            key = self._secret_key
        else:
            key = self._secret_key.encode("utf-8")
        return key.ljust(16)[:16]


if __name__ == "__main__":
    config = Config('', secret_key='_2@_c-8m3cb-c_!l')
    print(config.get('/cluster/server/ip'))

