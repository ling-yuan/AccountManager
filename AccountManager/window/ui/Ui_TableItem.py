from PyQt5.QtWidgets import QTableWidgetItem


class Ui_TableItem(QTableWidgetItem):

    def __init__(self, id: str | int, text: str):
        super().__init__(text)
        self._id = id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: str | int):
        self._id = id
