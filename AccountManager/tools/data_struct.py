from copy import deepcopy
import uuid


class Data:
    def __init__(
        self, name: str, account: str, password: str, note: str, id: str | None = None
    ):
        self.name = name
        self.account = account
        self.password = password
        self.note = note
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

    def to_list(self) -> list:
        return [self.name, self.account, self.password, self.note]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "account": self.account,
            "password": self.password,
            "note": self.note,
        }

    def __str__(self):
        return f"({self.id})[{self.name}, {self.account}, {self.password}, {self.note}]"

    def __eq__(self, other):
        if not isinstance(other, Data):
            return NotImplemented
        if self.id == other.id:
            return True
        elif (
            self.name == other.name
            and self.account == other.account
            and self.password == other.password
            and self.note == other.note
        ):
            return True
        return False

    def satisfy(self, patern) -> bool:
        if not isinstance(patern, Data):
            return NotImplemented
        if patern.name is not None and patern.name.lower() not in self.name.lower():
            return False
        if (
            patern.account is not None
            and patern.account.lower() not in self.account.lower()
        ):
            return False
        if (
            patern.password is not None
            and patern.password.lower() not in self.password.lower()
        ):
            return False
        if patern.note is not None and patern.note.lower() not in self.note.lower():
            return False
        return True


class Store:
    def __init__(self, *datas: Data):
        self.data: list[Data] = []
        self.load_data(*datas)

    def __str__(self):
        return "\n".join(str(item) for item in self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    @property
    def length(self) -> int:
        return len(self.data)

    def load_data(self, *datas: Data):
        for data in datas:
            self.add(data)

    def add(self, data) -> bool:
        if isinstance(data, Data):
            self.data.append(deepcopy(data))
        else:
            return False
        return True

    def delete(self, data: Data) -> bool:
        for i, item in enumerate(self.data):
            if item == data:
                del self.data[i]
                return True
        return False

    def modify(self, data: Data) -> bool:
        for i, item in enumerate(self.data):
            if item == data:
                self.data[i] = data
                return True
        return False

    def search(self, pattern: Data) -> "Store":
        result = Store()
        for data in self.data:
            if data.satisfy(pattern):
                result.add(data)
        return result.sort()

    def sort(self, sort_type: str = "id") -> "Store":
        if sort_type == "account":
            self.data.sort(key=lambda x: x.account)
        elif sort_type == "password":
            self.data.sort(key=lambda x: x.password)
        elif sort_type == "note":
            self.data.sort(key=lambda x: x.note)
        else:
            self.data.sort(key=lambda x: x.name)
        return self

    def clear(self):
        """清空所有数据"""
        self.data.clear()
