import os
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QMessageBox,
    QFileDialog,
    QTableWidgetItem,
    QApplication,
)
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from ..tools.data_tools import *
from .ui.Ui_MainWindow import Ui_MainWindow
from .ui.Ui_SystemTray import SystemTrayIcon
from .ui.Ui_TableItem import Ui_TableItem
from .settings_window import SettingsWindow
from ..config import Config
from ..tools.data_struct import Data, Store


class MainWindow(Ui_MainWindow, QMainWindow):

    def __init__(self, app: QApplication, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.app = app
        self.config = Config()
        self.__init_vars__()
        self.__init_ui__()
        self.__init_slots__()
        self.__init_keypress__()

    def __init_vars__(self):
        self.tray = None
        self.tools = DataTool()

    def __init_ui__(self):
        # 设置窗口固定大小
        self.setFixedSize(self.width(), self.height())
        # 初始化setting窗口
        self.settings_window = SettingsWindow(parent=self)
        self.settings_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        # 初始化任务栏图标
        self.use_system_tray(self.config.use_systemtray)
        # 表格设置
        header_font = QtGui.QFont()
        # header_font.setFamily("Maple Mono CN")
        header_font.setPointSize(9)
        horizontal_header = self.tableWidget.horizontalHeader()
        horizontal_header.setFont(header_font)
        self.tableWidget.setHorizontalHeader(horizontal_header)
        # 初始化输入框
        self.clear_data()
        # 初始化表格数据
        self.refresh_table()
        self.show_log("数据加载完成", 5000)

    def __init_slots__(self):
        # 菜单栏
        self.action_import_txt.triggered.connect(self.on_click_import_txt)
        self.action_export_txt.triggered.connect(self.on_click_export_txt)
        self.action_settings.triggered.connect(self.on_click_settings)
        # 按钮
        self.pushButton_modify.clicked.connect(self.on_click_modify)
        self.pushButton_delete.clicked.connect(self.on_click_delete)
        self.pushButton_clear.clicked.connect(self.on_click_clear)
        self.pushButton_query.clicked.connect(self.on_click_query)
        # 表格
        self.tableWidget.itemSelectionChanged.connect(self.on_selection_changed)
        # 信号
        self.settings_window.signal_tray.connect(self.use_system_tray)

    def __init_keypress__(self):
        # ctrl+s 保存/修改
        self.pushButton_modify.setShortcut("Ctrl+S")
        # ctrl+d 删除
        self.pushButton_delete.setShortcut("Ctrl+D")
        # ctrl+l 清空
        self.pushButton_clear.setShortcut("Ctrl+L")
        # ctrl+f 查询
        self.pushButton_query.setShortcut("Ctrl+F")

    # slots
    def on_click_import_txt(self):
        file_name = self.choose_file(
            "导入会覆盖之前保存的记录!\n\n每行数据从左至右顺序应为(名称,账号,密码,备注)\n数据之间用TAB分开",
            lambda x: x == "txt",
            "Text Files (*.txt);;All Files (*)",
        )
        if not file_name:
            return

        try:
            tmp_info = []
            try:
                f = open(file_name, "r", encoding="utf-8")
                tmp_data = f.readlines()
            except:
                f = open(file_name, "r", encoding="gbk")
                tmp_data = f.readlines()
            finally:
                f.close()
                for i in tmp_data:
                    # 避免使用嵌套列表推导式，改用普通循环
                    parts = i.split("\t")
                    cleaned_parts = []
                    for t in parts:
                        cleaned_part = t.strip().replace("\\n", "\n")
                        cleaned_parts.append(cleaned_part)
                    tmp_info.append(cleaned_parts)
            self.tools.store = Store()
            for info in tmp_info:
                self.tools.insert_data(Data(*info))
            self.show_log("导入成功", 5000)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)
        finally:
            self.refresh_table()

    def on_click_export_txt(self):
        dir: str = self.choose_dir()
        if not dir:
            return
        try:
            flag = ""
            file_name = dir + "/data{}.txt"
            while os.path.exists(file_name.format(flag)):
                flag = flag + 1 if flag else 1

            with open(file_name.format(flag), "w", encoding="utf-8") as f:
                for data in self.tools.store:
                    tmp = [str(item).replace("\n", "\\n") for item in data.to_list()]
                    f.write("\t".join(tmp) + "\n")
            self.show_log("导出成功", 5000)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)

    def on_click_settings(self):
        self.tools.clean_data()
        self.on_click_clear()
        self.settings_window.show()
        self.settings_window.exec()
        self.on_click_clear()
        self.tools.save_data()

    def on_click_modify(self):
        data = self.get_data()
        if self.lineEdit_name.id:
            self.tools.modify_data(data)
            self.show_log("修改成功", 5000)
        else:
            self.tools.insert_data(data)
            self.show_log("添加成功", 5000)
        self.on_click_clear()

    def on_click_delete(self):
        store = self.get_selected_data()
        for data in store:
            self.tools.delete_data(data)
        self.show_log(f"已删除{store.length}条数据", 5000)
        self.on_click_clear()

    def on_click_clear(self):
        self.clear_data()
        self.tableWidget.clearSelection()
        self.refresh_table()

    def on_click_query(self):
        store = self.tools.search(
            name=self.lineEdit_name.text(),
            account=self.lineEdit_account.text(),
            password=self.lineEdit_password.text(),
            note=self.textEdit_note.toPlainText(),
        )
        self.tableWidget.clearSelection()
        self.show_log(f"查询到{store.length}条数据", 5000)
        self.refresh_table(store)

    def on_selection_changed(self):
        store = self.get_selected_data()
        if store.length == 1:
            self.set_data(store[0])
        else:
            self.clear_data()
        if store.length != 0:
            self.show_log(f"已选择{store.length}条数据")

    # utils
    def choose_file(self, info: str, file_type_choose, filter: str):
        """
        选择文件
        """
        m = QMessageBox.warning(self, "警告", info, QMessageBox.Yes | QMessageBox.No)
        if m == QMessageBox.Yes:
            file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", filter)
            if file_name:
                flag = file_type_choose(file_name.rsplit(".", 1)[-1])
                if flag:
                    return file_name
                else:
                    QMessageBox.critical(
                        self, "错误", "请选择对应文件", QMessageBox.Yes
                    )
                    return False
        elif m == QMessageBox.No:
            return False
        else:
            return False
        return False

    def choose_dir(self):
        """
        选择文件夹
        """
        dir_name = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if dir_name:
            return dir_name
        else:
            return False

    def use_system_tray(self, enable: bool):
        """
        初始化系统托盘
        """
        if enable:
            self.tray = SystemTrayIcon(self)
            self.show_log("系统托盘已启用", 5000)
        else:
            # 如果存在任务栏图标，则删除
            if self.tray:
                self.tray.deleteLater()
                self.tray = None
                self.show_log("系统托盘已禁用", 5000)

    def show_log(self, msg: str, msecs: int = 0):
        """
        显示日志在状态栏
        """
        self.statusbar.clearMessage()
        self.statusbar.showMessage(msg, msecs)

    def refresh_table(self, store: Store | None = None):
        if not store:
            store = self.tools.store
        # 暂时禁用自动调整以提高性能
        self.tableWidget.setUpdatesEnabled(False)
        # 清空表格
        self.tableWidget.clearContents()
        self.tableWidget.clearSelection()
        self.tableWidget.setRowCount(store.length)
        for i, data in enumerate(store):
            # 创建表格项
            name_item = Ui_TableItem(id=data.id, text=data.name)
            account_item = QTableWidgetItem(data.account)
            password_item = QTableWidgetItem(data.password)
            note_item = QTableWidgetItem(data.note)
            # 设置文本自动换行
            note_item.setData(Qt.ItemDataRole.DisplayRole, data.note)
            # 添加到表格
            self.tableWidget.setItem(i, 0, name_item)
            self.tableWidget.setItem(i, 1, account_item)
            self.tableWidget.setItem(i, 2, password_item)
            self.tableWidget.setItem(i, 3, note_item)
        # 重新启用更新并调整大小
        self.tableWidget.setUpdatesEnabled(True)
        self.tableWidget.resizeRowsToContents()  # 调整所有行高

    def get_selected_data(self):
        t = self.tableWidget.selectedItems()
        rows = list(set([i.row() for i in t]))
        store = Store(
            *[
                Data(
                    id=self.tableWidget.item(row, 0).id,
                    name=self.tableWidget.item(row, 0).text(),
                    account=self.tableWidget.item(row, 1).text(),
                    password=self.tableWidget.item(row, 2).text(),
                    note=self.tableWidget.item(row, 3).text(),
                )
                for row in rows
            ]
        )
        return store

    def set_data(self, data: Data):
        self.lineEdit_name.id = data.id
        self.lineEdit_name.setText(data.name)
        self.lineEdit_account.setText(data.account)
        self.lineEdit_password.setText(data.password)
        self.textEdit_note.setText(data.note)

    def get_data(self) -> Data:
        return Data(
            id=self.lineEdit_name.id,
            name=self.lineEdit_name.text(),
            account=self.lineEdit_account.text(),
            password=self.lineEdit_password.text(),
            note=self.textEdit_note.toPlainText(),
        )

    def clear_data(self):
        self.lineEdit_name.id = None
        self.lineEdit_name.clear()
        self.lineEdit_account.clear()
        self.lineEdit_password.clear()
        self.textEdit_note.clear()

    # 其他事件
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """
        鼠标点击空白区域事件
        """
        # 检查点击位置是否在空白区域
        widget_at_pos = self.childAt(event.pos())

        if (
            widget_at_pos is None
            or widget_at_pos == self
            or not isinstance(widget_at_pos, QTableWidget)
        ):
            if event.button() == Qt.MouseButton.LeftButton:
                self.tableWidget.clearSelection()
                self.show_log("已清除选择", 2000)

        # 调用父类方法保持正常行为
        super().mousePressEvent(event)

    def closeEvent(self, event: QtGui.QMouseEvent):
        self.tools.save_data()
        event.accept()
        if not self.config.use_systemtray:
            self.app.quit()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
