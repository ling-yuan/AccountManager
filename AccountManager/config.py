import os
import sys
from PyQt5.QtCore import QSettings


def singleton(cls):
    """
    Decorator: Makes a class a singleton.
    :param cls: The class to be made a singleton.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Config:
    def __init__(self):
        self._settings = QSettings("BaiShi", "AccountManager")
        # 获取当前文件夹路径
        if getattr(sys, "frozen", False):
            # 如果是打包后的可执行文件
            if hasattr(sys, "_MEIPASS"):
                # PyInstaller的临时目录
                self._folder_path = sys._MEIPASS
            else:
                # Nuitka的目录
                self._folder_path = os.path.dirname(sys.executable)
        else:
            # 开发环境
            self._folder_path = sys.argv[0].rsplit("\\", 1)[0]
        self._default_config = {
            "auto_start": False,
            "use_systemtray": True,
            "auto_update": False,
            "data_save_type": "sqlite",
            "txt": {"path": "./"},
            "sqlite": {"path": "./"},
            "mysql": {
                "host": "127.0.0.1",
                "port": 3306,
                "username": "root",
                "password": "",
            },
            "mongodb": {
                "host": "127.0.0.1",
                "port": 27017,
                "username": "root",
                "password": "",
            },
            "webdav": {
                "protocol": "https",
                "host": "",
                "port": "443",
                "path": "dav",
                "account": "",
                "password": "",
            },
            "about": {
                "version": "2.3.0",
            },
        }

    @property
    def folder_path(self) -> str:
        return self._folder_path

    @property
    def auto_start(self) -> bool:
        return self._settings.value(
            "auto_start", self._default_config["auto_start"], type=bool
        )

    @auto_start.setter
    def auto_start(self, value: bool):
        self._settings.setValue("auto_start", value)

    @property
    def use_systemtray(self) -> bool:
        return self._settings.value(
            "use_systemtray", self._default_config["use_systemtray"], type=bool
        )

    @use_systemtray.setter
    def use_systemtray(self, value: bool):
        self._settings.setValue("use_systemtray", value)

    @property
    def auto_update(self) -> bool:
        return self._settings.value(
            "auto_update", self._default_config["auto_update"], type=bool
        )

    @auto_update.setter
    def auto_update(self, value: bool):
        self._settings.setValue("auto_update", value)

    @property
    def data_save_type(self) -> str:
        return self._settings.value(
            "data_save_type", self._default_config["data_save_type"], type=str
        )

    @data_save_type.setter
    def data_save_type(self, value: str):
        self._settings.setValue("data_save_type", value)

    @property
    def txt_path(self) -> str:
        return self._settings.value(
            "txt/path", self._default_config["txt"]["path"], type=str
        )

    @txt_path.setter
    def txt_path(self, value: str):
        self._settings.setValue("txt/path", value)

    @property
    def sqlite_path(self) -> str:
        return self._settings.value(
            "sqlite/path", self._default_config["sqlite"]["path"], type=str
        )

    @sqlite_path.setter
    def sqlite_path(self, value: str):
        self._settings.setValue("sqlite/path", value)

    @property
    def mysql_host(self) -> str:
        return self._settings.value(
            "mysql/host", self._default_config["mysql"]["host"], type=str
        )

    @mysql_host.setter
    def mysql_host(self, value: str):
        self._settings.setValue("mysql/host", value)

    @property
    def mysql_port(self) -> int:
        return self._settings.value(
            "mysql/port", self._default_config["mysql"]["port"], type=int
        )

    @mysql_port.setter
    def mysql_port(self, value: int):
        self._settings.setValue("mysql/port", value)

    @property
    def mysql_username(self) -> str:
        return self._settings.value(
            "mysql/username", self._default_config["mysql"]["username"], type=str
        )

    @mysql_username.setter
    def mysql_username(self, value: str):
        self._settings.setValue("mysql/username", value)

    @property
    def mysql_password(self) -> str:
        return self._settings.value(
            "mysql/password", self._default_config["mysql"]["password"], type=str
        )

    @mysql_password.setter
    def mysql_password(self, value: str):
        self._settings.setValue("mysql/password", value)

    @property
    def mongodb_host(self) -> str:
        return self._settings.value(
            "mongodb/host", self._default_config["mongodb"]["host"], type=str
        )

    @mongodb_host.setter
    def mongodb_host(self, value: str):
        self._settings.setValue("mongodb/host", value)

    @property
    def mongodb_port(self) -> int:
        return self._settings.value(
            "mongodb/port", self._default_config["mongodb"]["port"], type=int
        )

    @mongodb_port.setter
    def mongodb_port(self, value: int):
        self._settings.setValue("mongodb/port", value)

    @property
    def mongodb_username(self) -> str:
        return self._settings.value(
            "mongodb/username", self._default_config["mongodb"]["username"], type=str
        )

    @mongodb_username.setter
    def mongodb_username(self, value: str):
        self._settings.setValue("mongodb/username", value)

    @property
    def mongodb_password(self) -> str:
        return self._settings.value(
            "mongodb/password", self._default_config["mongodb"]["password"], type=str
        )

    @mongodb_password.setter
    def mongodb_password(self, value: str):
        self._settings.setValue("mongodb/password", value)

    @property
    def version(self) -> str:
        return self._settings.value(
            "about/version", self._default_config["about"]["version"], type=str
        )

    @property
    def webdav_protocol(self) -> str:
        return self._settings.value(
            "webdav/protocol", self._default_config["webdav"]["protocol"], type=str
        )

    @webdav_protocol.setter
    def webdav_protocol(self, value: str):
        self._settings.setValue("webdav/protocol", value)

    @property
    def webdav_host(self) -> str:
        return self._settings.value(
            "webdav/host", self._default_config["webdav"]["host"], type=str
        )

    @webdav_host.setter
    def webdav_host(self, value: str):
        self._settings.setValue("webdav/host", value)

    @property
    def webdav_port(self) -> str:
        return self._settings.value(
            "webdav/port", self._default_config["webdav"]["port"], type=str
        )

    @webdav_port.setter
    def webdav_port(self, value: str):
        self._settings.setValue("webdav/port", value)

    @property
    def webdav_path(self) -> str:
        return self._settings.value(
            "webdav/path", self._default_config["webdav"]["path"], type=str
        )

    @webdav_path.setter
    def webdav_path(self, value: str):
        self._settings.setValue("webdav/path", value)

    @property
    def webdav_account(self) -> str:
        return self._settings.value(
            "webdav/account", self._default_config["webdav"]["account"], type=str
        )

    @webdav_account.setter
    def webdav_account(self, value: str):
        self._settings.setValue("webdav/account", value)

    @property
    def webdav_password(self) -> str:
        return self._settings.value(
            "webdav/password", self._default_config["webdav"]["password"], type=str
        )

    @webdav_password.setter
    def webdav_password(self, value: str):
        self._settings.setValue("webdav/password", value)
