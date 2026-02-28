import os
import sqlite3
import pymysql
import pymongo
import tempfile
import json
import hashlib
import base64
import winreg
import urllib3
import ssl
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from datetime import datetime
from cryptography.fernet import Fernet
from webdav3.client import Client
from copy import deepcopy
from .data_struct import Data, Store
from ..config import Config


class BaseTools:
    config = Config()

    def __init__(self):
        self.store = Store()

    def load(self):
        self._load_data()

    def save(self):
        self._save_data()

    def clear(self):
        self._clear_data()
        self.store = Store()

    @property
    def data(self) -> Store:
        return deepcopy(self.store)

    @classmethod
    def get_tools(cls):
        if cls.config.data_save_type == "txt":
            return TxtTools()
        elif cls.config.data_save_type == "sqlite":
            return SqliteTools()
        elif cls.config.data_save_type == "mysql":
            return MysqlTools()
        elif cls.config.data_save_type == "mongodb":
            return MongodbTools()
        else:
            return TxtTools()

    @classmethod
    def test_connection(cls) -> bool:
        return False

    def _load_data(self):
        pass

    def _save_data(self):
        pass

    def _clear_data(self):
        pass


# txt工具
class TxtTools(BaseTools):

    def __init__(self):
        super().__init__()
        self.path = self.config.txt_path

    @classmethod
    def test_connection(cls, path: str) -> bool:
        try:
            with open(path + "/data.txt", "a", encoding="utf-8") as f:
                pass
            return True
        except Exception:
            return False

    def _load_data(self):
        try:
            with open(self.path + "/data.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip(" \n").split("\t")
                    if len(parts) == 4:
                        parts = [part.replace("\\n", "\n") for part in parts]
                        self.store.add(Data(*parts))
        except FileNotFoundError:
            # 创建文件
            with open(self.path + "/data.txt", "w", encoding="utf-8") as f:
                pass

    def _save_data(self):
        with open(self.path + "/data.txt", "w", encoding="utf-8") as f:
            for datas in self.store:
                data = [str(item).replace("\n", "\\n") for item in datas.to_list()]
                f.write("\t".join(data) + "\n")

    def _clear_data(self):
        if os.path.exists(self.path + "/data.txt"):
            os.remove(self.path + "/data.txt")


# sqlite工具
class SqliteTools(BaseTools):

    def __init__(self):
        super().__init__()
        self.path = self.config.sqlite_path

    @classmethod
    def test_connection(cls, path: str) -> bool:
        try:
            conn = sqlite3.connect(path + "/data.db")
            conn.close()
            return True
        except Exception:
            return False

    def get_connection(self):
        conn = sqlite3.connect(self.path + "/data.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                name TEXT,
                account TEXT,
                password TEXT,
                note TEXT
            )
            """
        )
        return conn, cursor

    def _load_data(self):
        conn, cursor = self.get_connection()
        cursor.execute("SELECT name, account, password, note FROM accounts")
        rows = cursor.fetchall()
        for row in rows:
            self.store.add(Data(*row))
        conn.close()

    def _save_data(self):
        conn, cursor = self.get_connection()
        cursor.execute("DELETE FROM accounts")
        for i, data in enumerate(self.store):
            cursor.execute(
                "INSERT INTO accounts (id, name, account, password, note) VALUES (?, ?, ?, ?, ?)",
                [i + 1, *data.to_list()],
            )
        conn.commit()
        conn.close()

    def _clear_data(self):
        if os.path.exists(self.path + "/data.db"):
            os.remove(self.path + "/data.db")


# mysql工具
class MysqlTools(BaseTools):

    def __init__(self):
        super().__init__()
        self.host = self.config.mysql_host
        self.username = self.config.mysql_username
        self.password = self.config.mysql_password
        self.port = self.config.mysql_port

    @classmethod
    def test_connection(
        cls,
        host: str,
        username: str,
        password: str,
        port: int = 3306,
    ) -> bool:
        try:
            conn = pymysql.connect(
                host=host,
                user=username,
                password=password,
                port=port,
            )
            conn.close()
            return True
        except Exception:
            return False

    def get_connection(self):
        conn = pymysql.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            port=self.port,
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS account_manager;")
        conn.select_db("account_manager")
        return conn, cursor

    def __init_database__(self):
        conn, cursor = self.get_connection()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255),
                account VARCHAR(255),
                password VARCHAR(255),
                note TEXT
            );
            """
        )
        conn.commit()
        conn.close()

    def _load_data(self):
        self.__init_database__()
        conn, cursor = self.get_connection()
        cursor.execute("SELECT name, account, password, note FROM accounts")
        rows = cursor.fetchall()
        for row in rows:
            self.store.add(Data(*row))
        conn.close()

    def _save_data(self):
        self.__init_database__()
        conn, cursor = self.get_connection()
        cursor.execute("DELETE FROM accounts")
        for i, data in enumerate(self.store):
            cursor.execute(
                "INSERT INTO accounts (id, name, account, password, note) VALUES (%s, %s, %s, %s, %s)",
                [i + 1, *data.to_list()],
            )
        conn.commit()
        conn.close()

    def _clear_data(self):
        conn, cursor = self.get_connection()
        cursor.execute("DROP TABLE IF EXISTS accounts")
        conn.commit()
        conn.close()


# mongodb工具
class MongodbTools(BaseTools):

    def __init__(self):
        super().__init__()
        self.host = self.config.mongodb_host
        self.username = self.config.mongodb_username
        self.password = self.config.mongodb_password
        self.port = self.config.mongodb_port

    @classmethod
    def test_connection(
        cls,
        host: str,
        username: str,
        password: str,
        port: int = 27017,
    ) -> bool:
        try:
            conn = pymongo.MongoClient(
                host=host,
                port=port,
                username=username,
                password=password,
                serverSelectionTimeoutMS=3000,
            )
            conn.server_info()  # 强制连接
            conn.close()
            return True
        except Exception:
            return False

    def get_connection(self):
        conn = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            serverSelectionTimeoutMS=3000,
        )
        db = conn["account_manager"]
        collection = db["accounts"]
        return conn, db, collection

    def _load_data(self):
        conn, db, collection = self.get_connection()
        # 查询所有name, account, password, note字段
        rows = collection.find(
            {}, {"_id": 0, "name": 1, "account": 1, "password": 1, "note": 1}
        )
        for item in rows:
            self.store.add(
                Data(
                    item.get("name"),
                    item.get("account"),
                    item.get("password"),
                    item.get("note"),
                )
            )
        conn.close()

    def _save_data(self):
        conn, db, collection = self.get_connection()
        collection.delete_many({})
        for data in self.store:
            collection.insert_one(
                {
                    "name": data.name,
                    "account": data.account,
                    "password": data.password,
                    "note": data.note,
                }
            )
        conn.close()

    def _clear_data(self):
        conn, db, collection = self.get_connection()
        collection.drop()
        conn.close()


# 系统代理工具
def get_system_proxy() -> dict:
    """
    获取系统代理设置
    :return: 代理配置字典，格式: {"http": "http://proxy:port", "https": "https://proxy:port"}
    """
    try:

        # 从Windows注册表直接读取代理设置
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            try:
                proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
                if not proxy_enable:
                    return {}

                proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")

                # 解析ProxyServer值
                # 格式可能是: "127.0.0.1:7890" 或 "http=127.0.0.1:7890;https=127.0.0.1:7890"
                proxy_config = {}

                if ";" in proxy_server:
                    # 多个代理配置
                    for entry in proxy_server.split(";"):
                        if "=" in entry:
                            protocol, addr = entry.split("=", 1)
                            protocol = protocol.strip().lower()
                            addr = addr.strip()
                            if protocol in ["http", "https"]:
                                # 确保地址有协议前缀
                                if not addr.startswith("http"):
                                    addr = f"{protocol}://{addr}"
                                proxy_config[protocol] = addr
                else:
                    # 单一代理地址
                    if not proxy_server.startswith("http"):
                        # 默认应用于http和https
                        proxy_server = f"http://{proxy_server}"
                    proxy_config["http"] = proxy_server
                    proxy_config["https"] = proxy_server

                return proxy_config if proxy_config else {}
            except WindowsError:
                return {}
    except Exception as e:
        print(f"获取系统代理失败: {e}")
        return {}


def create_webdav_client_with_proxy(options: dict):
    """
    创建带代理支持的WebDAV客户端
    :param options: WebDAV客户端选项
    :return: 配置好的Client对象
    """
    try:
        # 禁用所有SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 获取系统代理
        proxies = get_system_proxy()

        # 如果有代理，设置环境变量
        if proxies:
            print(f"为WebDAV客户端配置代理: {proxies}")
            # 设置环境变量方式的代理
            for protocol, proxy_url in proxies.items():
                os_var_lower = f"{protocol}_proxy"
                os_var_upper = os_var_lower.upper()
                os.environ[os_var_lower] = proxy_url
                os.environ[os_var_upper] = proxy_url

            # 禁用SSL验证
            os.environ["PYTHONHTTPSVERIFY"] = "0"

        # 为选项添加代理配置
        if proxies:
            options["proxies"] = proxies

        # 创建客户端
        client = Client(options)

        # 配置Session - 禁用所有SSL验证
        client.session.verify = False
        client.verify = False

        # 创建禁用SSL验证的适配器
        class NoSSLVerifyHTTPAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                ctx = create_urllib3_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                kwargs["ssl_context"] = ctx
                return super().init_poolmanager(*args, **kwargs)

            def proxy_manager_for(self, proxy, **proxy_kwargs):
                ctx = create_urllib3_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                proxy_kwargs["ssl_context"] = ctx
                return super().proxy_manager_for(proxy, **proxy_kwargs)

        # 挂载适配器到所有协议
        adapter = NoSSLVerifyHTTPAdapter()
        client.session.mount("http://", adapter)
        client.session.mount("https://", adapter)

        # 配置代理到Session
        if proxies:
            client.session.proxies.update(proxies)

        return client
    except Exception as e:
        print(f"创建WebDAV客户端失败: {e}")
        raise


# 加密工具类
class EncryptionTools:
    """
    数据加密工具
    密钥生成规则: base64(sha256(password + timestamp))的前32个字符
    """

    @staticmethod
    def generate_key(password: str, timestamp: str = None) -> bytes:
        """
        生成Fernet加密密钥
        :param password: WebDAV密码
        :param timestamp: 时间戳字符串（格式: YYYYMMDD_HHMMSS）
        :return: Fernet密钥
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 结合密码和时间戳生成密钥
        key_source = (password + timestamp).encode("utf-8")
        # 使用SHA256进行哈希
        hash_obj = hashlib.sha256(key_source)
        # 转换为base64格式的Fernet密钥
        # Fernet密钥必须是32字节的base64编码
        key_bytes = hash_obj.digest()[:32]
        key = base64.urlsafe_b64encode(key_bytes)
        return key

    @staticmethod
    def encrypt_data(data: str, password: str, timestamp: str = None) -> dict:
        """
        加密数据
        :param data: 要加密的JSON数据字符串
        :param password: WebDAV密码
        :param timestamp: 时间戳（如果为None，则使用当前时间）
        :return: 包含加密数据和时间戳的字典
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # 生成密钥
            key = EncryptionTools.generate_key(password, timestamp)

            # 创建Fernet实例
            cipher = Fernet(key)

            # 加密数据
            encrypted_data = cipher.encrypt(data.encode("utf-8"))

            # 返回加密数据和时间戳（时间戳用于解密时重新生成密钥）
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode("utf-8"),
                "timestamp": timestamp,
                "encrypted": True,
            }
        except Exception as e:
            print(f"加密失败: {e}")
            return None

    @staticmethod
    def decrypt_data(encrypted_dict: dict, password: str) -> str:
        """
        解密数据
        :param encrypted_dict: 包含加密数据和时间戳的字典
        :param password: WebDAV密码
        :return: 解密后的原始JSON字符串
        """
        try:
            # 获取时间戳和加密数据
            timestamp = encrypted_dict.get("timestamp")
            encrypted_data_b64 = encrypted_dict.get("encrypted_data")

            if not timestamp or not encrypted_data_b64:
                raise ValueError("缺少解密所需的参数")

            # 使用相同的密钥生成方式
            key = EncryptionTools.generate_key(password, timestamp)

            # 创建Fernet实例
            cipher = Fernet(key)

            # 解密数据
            encrypted_data = base64.b64decode(encrypted_data_b64)
            decrypted_data = cipher.decrypt(encrypted_data)

            return decrypted_data.decode("utf-8")
        except Exception as e:
            print(f"解密失败: {e}")
            return None


# webdav备份工具
class WebDAVTools:
    config = Config()

    def __init__(self):
        self.protocol = self.config.webdav_protocol
        self.host = self.config.webdav_host
        self.port = self.config.webdav_port
        self.path = self.config.webdav_path
        self.account = self.config.webdav_account
        self.password = self.config.webdav_password

    @classmethod
    def test_connection(
        cls,
        protocol: str,
        host: str,
        port: str,
        path: str,
        account: str,
        password: str,
    ) -> bool:
        """测试WebDAV连接"""
        try:
            # 构建WebDAV URL
            url = f"{protocol}://{host}:{port}/{path}"

            options = {
                "webdav_hostname": url,
                "webdav_login": account,
                "webdav_password": password,
                "webdav_timeout": 10,
            }

            client = create_webdav_client_with_proxy(options)

            # 尝试多种方法测试连接
            test_methods = [
                lambda: client.list(),  # 尝试列出根目录
                lambda: client.check("/"),  # 尝试检查根目录
                lambda: client.info("/"),  # 尝试获取根目录信息
                lambda: client.valid(),  # 尝试验证连接
            ]

            for i, test_method in enumerate(test_methods):
                try:
                    result = test_method()
                    print(f"✓ 连接成功（方法 {i+1}）")
                    return True
                except Exception as e:
                    if i == len(test_methods) - 1:
                        # 最后一个方法仍然失败
                        raise
                    # 继续尝试下一个方法
                    continue

            return True
        except Exception as e:
            print(f"WebDAV连接测试失败: {e}")
            return False

    def backup_data(self, data_tools) -> bool:
        """
        备份数据到WebDAV服务器（加密）
        :param data_tools: DataTool实例，包含要备份的数据
        :return: 备份是否成功
        """
        try:
            # 构建WebDAV URL
            url = f"{self.protocol}://{self.host}:{self.port}/{self.path}"

            options = {
                "webdav_hostname": url,
                "webdav_login": self.account,
                "webdav_password": self.password,
                "webdav_timeout": 30,
            }

            client = create_webdav_client_with_proxy(options)

            # 确保备份目录存在
            backup_dir = "AccountManager_Backup/"
            if not client.check(backup_dir):
                client.mkdir(backup_dir)

            # 生成备份文件名（包含时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 将数据转换为JSON格式
            backup_data = {
                "data": [data.to_dict() for data in data_tools.store],
                "backup_time": datetime.now().isoformat(),
                "version": self.config.version,
            }

            # 序列化为JSON字符串
            backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2)

            # 使用密码和时间戳加密数据
            encrypted_result = EncryptionTools.encrypt_data(
                backup_json, self.password, timestamp
            )

            if encrypted_result is None:
                print("数据加密失败")
                return False

            # 将加密数据写入临时文件
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", delete=False, suffix=".json"
            ) as tmp_file:
                json.dump(encrypted_result, tmp_file, ensure_ascii=False, indent=2)
                tmp_path = tmp_file.name

            try:
                # 上传到WebDAV
                backup_filename = f"{backup_dir}backup_{timestamp}.json"
                client.upload_sync(remote_path=backup_filename, local_path=tmp_path)

                # 同时保存一个最新备份副本
                latest_backup = f"{backup_dir}latest_backup.json"
                client.upload_sync(remote_path=latest_backup, local_path=tmp_path)

                return True
            finally:
                # 删除临时文件
                os.unlink(tmp_path)

        except Exception as e:
            print(f"WebDAV备份失败: {e}")
            return False

    def restore_data(self, data_tools: "DataTool") -> bool:
        """
        从WebDAV服务器恢复数据（解密）
        :param data_tools: DataTool实例，用于保存恢复的数据
        :return: 恢复是否成功
        """
        try:
            # 构建WebDAV URL
            url = f"{self.protocol}://{self.host}:{self.port}/{self.path}"

            options = {
                "webdav_hostname": url,
                "webdav_login": self.account,
                "webdav_password": self.password,
                "webdav_timeout": 30,
            }

            client = create_webdav_client_with_proxy(options)

            # 下载最新备份
            backup_dir = "AccountManager_Backup/"
            latest_backup = f"{backup_dir}latest_backup.json"

            if not client.check(latest_backup):
                print("未找到备份文件")
                return False
            # 下载到临时文件（使用二进制模式）
            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, suffix=".json"
            ) as tmp_file:
                tmp_path = tmp_file.name

            try:
                # monkey-patch download_file 以兼容不返回content-length的服务器
                from webdav3.urn import Urn
                from webdav3.exceptions import (
                    OptionNotValid,
                    RemoteResourceNotFound as _RRNF,
                )

                def _patched_download_file(
                    remote_path, local_path, progress=None, progress_args=()
                ):
                    urn = Urn(remote_path)
                    if client.is_dir(urn.path()):
                        raise OptionNotValid(name="remote_path", value=remote_path)
                    if os.path.isdir(local_path):
                        raise OptionNotValid(name="local_path", value=local_path)
                    if not client.check(urn.path()):
                        raise _RRNF(urn.path())
                    with open(local_path, "wb") as local_file:
                        response = client.execute_request("download", urn.quote())
                        # 兼容不返回content-length的服务器
                        total = int(response.headers.get("content-length", 0))
                        current = 0
                        if callable(progress):
                            progress(current, total, *progress_args)
                        for block in response.iter_content(
                            chunk_size=client.chunk_size
                        ):
                            local_file.write(block)
                            current += len(block)
                            if callable(progress):
                                progress(current, total, *progress_args)

                client.download_file = _patched_download_file
                client.download_sync(remote_path=latest_backup, local_path=tmp_path)

                # # 下载到临时文件
                # with tempfile.NamedTemporaryFile(
                #     mode="w", encoding="utf-8", delete=False, suffix=".json"
                # ) as tmp_file:
                #     tmp_path = tmp_file.name

                # try:
                #     client.download_sync(remote_path=latest_backup, local_path=tmp_path)

                # 读取备份数据（加密数据）
                with open(tmp_path, "r", encoding="utf-8") as f:
                    encrypted_data = json.load(f)

                # 检查是否为加密数据
                if encrypted_data.get("encrypted"):
                    # 解密数据
                    backup_json = EncryptionTools.decrypt_data(
                        encrypted_data, self.password
                    )

                    if backup_json is None:
                        print("数据解密失败")
                        return False

                    # 解析JSON
                    backup_data = json.loads(backup_json)
                else:
                    # 如果不是加密数据，直接使用（向后兼容）
                    backup_data = encrypted_data

                # 清空当前数据
                data_tools.store.clear()

                # 恢复数据
                for item in backup_data.get("data", []):
                    data = Data(
                        item.get("name", ""),
                        item.get("account", ""),
                        item.get("password", ""),
                        item.get("note", ""),
                    )
                    data_tools.store.add(data)

                # 保存到当前存储
                data_tools.save_data()

                return True
            finally:
                # 删除临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            print(f"WebDAV恢复失败: {e}")
            return False

    def list_backups(self) -> list:
        """
        列出所有备份文件
        :return: 备份文件列表
        """
        try:
            url = f"{self.protocol}://{self.host}:{self.port}/{self.path}"

            options = {
                "webdav_hostname": url,
                "webdav_login": self.account,
                "webdav_password": self.password,
                "webdav_timeout": 10,
            }

            client = create_webdav_client_with_proxy(options)

            backup_dir = "AccountManager_Backup/"
            if not client.check(backup_dir):
                return []

            # 列出备份目录中的所有文件
            files = client.list(backup_dir)
            # 过滤出备份文件（排除目录本身和latest_backup.json）
            backups = [
                f for f in files if f.startswith("backup_") and f.endswith(".json")
            ]
            return sorted(backups, reverse=True)  # 按时间倒序排列

        except Exception as e:
            print(f"列出备份失败: {e}")
            return []


class DataTool:

    def __init__(self):
        self.config = Config()
        self.__init_data__()

    def __init_data__(self):
        self.tools = BaseTools.get_tools()
        self.tools.load()
        self.store = self.tools.data
        # 注意：不要在这里调用save()，因为self.tools.store仍然是空的
        # self.tools.save()

    def insert_data(self, data: Data) -> bool:
        result = self.store.add(data)
        self.store.sort()
        self.save_data()
        return result

    def delete_data(self, data: Data):
        result = self.store.delete(data)
        self.store.sort()
        self.save_data()
        return result

    def modify_data(self, data: Data) -> bool:
        result = self.store.modify(data)
        self.store.sort()
        self.save_data()
        return result

    def search(
        self,
        name: str | None = None,
        account: str | None = None,
        password: str | None = None,
        note: str | None = None,
    ) -> Store:
        return self.store.search(Data(name, account, password, note))

    def clean_data(self):
        """
        清空当前存储方式下的记录,但所有数据仍然保存在当前类中
        """
        self.tools = BaseTools.get_tools()
        self.tools.clear()

    def save_data(self):
        self.clean_data()
        self.tools.store = deepcopy(self.store)
        self.tools.save()
