# 自定义线程类
from PyQt5.QtCore import QThread, pyqtSignal


class CustomThread(QThread):
    signal_result = pyqtSignal(bool, str)

    def __init__(self, func: callable, con_type: str, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.con_type = con_type

    def run(self):
        result = self.func(*self.args, **self.kwargs)
        self.signal_result.emit(result, self.con_type)
