from copy import deepcopy
import json
import os


class Config:

    def __init__(self):
        self._config_file_path = "./info/config.json"
        self._key_path = "./info/key.key"
        self._config: dict = self.config

    @property
    def config(self) -> dict:
        self._config = json.load(open(self._config_file_path, "r", encoding="utf-8"))
        # 判断key是否存在
        if os.path.exists(self._key_path):
            with open(self._key_path, "rb") as f:
                tmp_key = f.read()
                self._config["key"] = tmp_key
        else:
            self._config["key"] = b""
        return deepcopy(self._config)

    @property
    def db_path(self) -> str:
        return self._config.get("db_path", "")

    @db_path.setter
    def db_path(self, db_path: str):
        self._config["db_path"] = db_path
        self.save()

    @property
    def auto_start(self) -> bool:
        return self._config.get("auto_start", False)

    @auto_start.setter
    def auto_start(self, auto_start: bool):
        self._config["auto_start"] = auto_start
        self.save()

    @property
    def key(self) -> bytes:
        tmp_key: bytes = self._config.get("key", b"")
        return tmp_key

    @key.setter
    def key(self, key: bytes):
        self._config["key"] = key
        self.save()

    def save(self):
        tmp_config = deepcopy(self._config)
        with open(self._key_path, "wb") as f:
            f.write(tmp_config.pop("key"))
        with open(self._config_file_path, "w", encoding="utf-8") as f:
            json.dump(tmp_config, f, ensure_ascii=False, indent=4)
