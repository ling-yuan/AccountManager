import os
import sqlite3
import tempfile
from tools.config import Config
from tools.cryption import Cryption


class MyDB:
    def __init__(self):
        self.cryption = Cryption()
        self._init_config()
        self._init_table()

    def _init_config(self):
        """
        读取config.json文件，获取配置
        """
        self._config = Config()
        self._db_path = self._config.db_path
        self.tmp_db_path = ""

        if os.path.exists(self._db_path):
            # 解密, 写入临时文件
            data = self.cryption.dectypt_file(self._db_path)
            with tempfile.NamedTemporaryFile(delete=False) as tmp_db:
                tmp_db.write(data)
                self.tmp_db_path = tmp_db.name
        else:
            conn, cur = self._connect_db(self._db_path)
            conn.close()
            with open(self._db_path, "rb") as f:
                data = f.read()
            with tempfile.NamedTemporaryFile(delete=False) as tmp_db:
                tmp_db.write(data)
                self.tmp_db_path = tmp_db.name
            with open(self._db_path, "wb") as f:
                f.write(self.cryption.encrypt_file(self._db_path))

    def _connect_db(self, path: str):
        """
        连接数据库

        :return: 连接对象, 游标对象
        """
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        return conn, cur

    def _init_table(self):
        """
        初始化数据表
        """
        conn, cur = self._connect_db(self.tmp_db_path)
        create_info_table = """
            CREATE TABLE IF NOT EXISTS `information`(
               `uuid` CHAR(36) PRIMARY KEY,
               `name` VARCHAR(100) NOT NULL,
               `account` CHAR,
               `password` CHAR,
               `remark` TEXT
            );
            """
        cur.execute(create_info_table)
        conn.commit()
        conn.close()

    def _execute_sql(self, sql, args=None):
        """
        执行SQL

        :param sql: SQL语句
        :param args: 参数，默认为None
        :return: 执行结果
        """
        conn, cur = self._connect_db(self.tmp_db_path)
        rows = None
        if args == None:
            rows = cur.execute(sql)
        else:
            if isinstance(args, tuple):
                rows = cur.execute(sql, args)
            elif isinstance(args, list):
                rows = cur.executemany(sql, args)
            else:
                raise TypeError("args must be tuple or list")
        conn.commit()
        conn.close()
        self._save_db()
        return rows

    def _generate_uuid(self):
        """
        生成UUID

        :return: UUID
        """
        import uuid

        return str(uuid.uuid4())

    def fetch_all(self):
        """
        查询所有数据
        """
        sql = "SELECT * FROM information"
        conn, cur = self._connect_db(self.tmp_db_path)
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        return result

    def fetch(self, uuid: str = "", name: str = "", account: str = "", password: str = "", remark: str = ""):
        """
        查询单条数据

        :param uuid: uuid, defaults to ""
        :param name: 名称, defaults to ""
        :param account: 账号, defaults to ""
        :param password: 密码, defaults to ""
        :param remark: 备注, defaults to ""
        :return: 查询结果
        """
        sql = "SELECT * FROM information WHERE "
        data = []
        if uuid:
            sql += "uuid LIKE ? AND "
            data.append("%" + uuid + "%")
        if name:
            sql += "name LIKE ? AND "
            data.append("%" + name + "%")
        if account:
            sql += "account LIKE ? AND "
            data.append("%" + account + "%")
        if password:
            sql += "password LIKE ? AND "
            data.append("%" + password + "%")
        if remark:
            sql += "remark LIKE ? AND "
            data.append("%" + remark + "%")

        sql = sql.rstrip(" AND ")
        conn, cur = self._connect_db(self.tmp_db_path)
        cur.execute(sql, data)
        result = cur.fetchall()
        conn.close()
        return result

    def clear_table(self):
        """
        清空数据表
        """
        sql = "DELETE FROM information"
        self._execute_sql(sql)
        return True

    def insert_data(self, data: list | tuple):
        """
        插入数据

        :param data: 数据，格式为元组或列表
        :return: 执行结果
        """
        sql = "INSERT INTO information VALUES (?, ?, ?, ?, ?)"
        uuid = self._generate_uuid()
        return self._execute_sql(sql, (uuid, *data))

    def insert_many_data(self, data: list):
        """
        插入多条数据

        :param data: 数据，格式为列表
        :return: 执行结果
        """
        sql = "INSERT INTO information VALUES (?, ?, ?, ?, ?)"
        data = [(self._generate_uuid(), *d) for d in data]
        return self._execute_sql(sql, data)

    def update_data(self, uuid: str, data: list | tuple):
        """
        更新数据

        :param uuid: 数据的唯一标识符
        :param data: 数据，格式为元组或列表
        :return: 执行结果
        """
        sql = "UPDATE information SET name = ?, account = ?, password = ?, remark = ? WHERE uuid = ?"
        return self._execute_sql(sql, (*data, uuid))

    def delete_data(self, uuid: str):
        """
        删除数据

        :param uuid: 数据的唯一标识符
        :return: 执行结果
        """
        sql = "DELETE FROM information WHERE uuid = ?"
        return self._execute_sql(sql, (uuid,))

    def _save_db(self):
        # 将临时数据库加密
        with open(self._db_path, "wb") as f:
            f.write(self.cryption.encrypt_file(self.tmp_db_path))

    # 实例回收时，删除临时数据库
    def __del__(self):
        os.remove(self.tmp_db_path)

    def _get_db_bytes(self):
        return self.cryption.dectypt_file(self.tmp_db_path)
