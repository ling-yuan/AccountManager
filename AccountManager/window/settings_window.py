from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal, Qt

from .ui import Image_rc
from ..tools.custom_thread import CustomThread
from .ui.Ui_SettingsWindow import Ui_SettingsForm
from ..config import Config
from ..tools.data_tools import *
from ..tools.data_tools import WebDAVTools, DataTool


class SettingsWindow(Ui_SettingsForm, QDialog):
    signal_tray = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setupUi(self)
        self.config = Config()
        self.running_threads = 0  # 跟踪正在运行的线程数
        self.__init_ui__()
        self.__init_slot__()

    def __init_ui__(self):
        """
        初始化界面UI
        """
        # 设置窗口标题
        self.setWindowTitle("设置")
        # 设置窗口图标
        self.setWindowIcon(QtGui.QIcon(":/resource/resource/icon.png"))
        # 设置窗口固定大小
        self.setFixedSize(self.width(), self.height())
        # 隐藏标题栏帮助按钮
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint) -----------------------------
        # 通用设置
        self.checkBox_auto_start.setChecked(self.config.auto_start)
        self.checkBox_use_systemtray.setChecked(self.config.use_systemtray)
        self.checkBox_auto_update.setChecked(self.config.auto_update)
        # 数据保存
        self.comboBox_save_type.setCurrentText(self.config.data_save_type)
        self.lineEdit_txt_save_path.setText(self.config.txt_path)
        self.lineEdit_sqlite_save_path.setText(self.config.sqlite_path)
        self.lineEdit_mysql_host.setText(self.config.mysql_host)
        self.spinBox_mysql_port.setValue(self.config.mysql_port)
        self.lineEdit_mysql_username.setText(self.config.mysql_username)
        self.lineEdit_mysql_password.setText(self.config.mysql_password)
        self.lineEdit_mongodb_host.setText(self.config.mongodb_host)
        self.spinBox_mongodb_port.setValue(self.config.mongodb_port)
        self.lineEdit_mongodb_username.setText(self.config.mongodb_username)
        self.lineEdit_mongodb_password.setText(self.config.mongodb_password)
        # 备份设置
        self.comboBox_protocol.setCurrentText(self.config.webdav_protocol)
        self.lineEdit_webdav_host.setText(self.config.webdav_host)
        self.lineEdit_webdav_port.setText(self.config.webdav_port)
        self.lineEdit_webdav_path.setText(self.config.webdav_path)
        self.lineEdit_webdav_account.setText(self.config.webdav_account)
        self.lineEdit_webdav_password.setText(self.config.webdav_password)
        self.lineEdit_webdav_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        # 关于
        self.label_version.setText(f"{self.config.version}")
        # 根据comboBox_save_type的值，修改stackedWidget的显示
        self.stackedWidget.setCurrentIndex(self.comboBox_save_type.currentIndex())
        # 隐藏关闭按钮旁边的帮助按钮
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

    def __disable_ui_for_thread__(self):
        """
        线程运行时禁用UI
        """
        self.pushButton_save.setEnabled(False)
        self.running_threads += 1

    def __enable_ui_after_thread__(self):
        """
        线程完成后恢复UI
        """
        self.running_threads -= 1
        if self.running_threads <= 0:
            self.running_threads = 0
            self.pushButton_save.setEnabled(True)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        重写关闭事件，防止线程运行时关闭窗口
        """
        try:
            if self.running_threads > 0:
                QtWidgets.QMessageBox.warning(self, "警告", "线程运行中，请稍候...")
                event.ignore()
            self.on_click_save()
            event.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "错误", f"保存配置失败：{str(e)}\n请检查配置后再关闭"
            )
            event.ignore()

    def __init_slot__(self):
        """
        初始化槽函数
        """
        # 数据保存
        ## 下拉菜单切换事件
        self.comboBox_save_type.currentIndexChanged.connect(
            self.stackedWidget.setCurrentIndex
        )
        ## txt
        self.pushButton_txt_select_path.clicked.connect(
            lambda: self.lineEdit_txt_save_path.setText(
                self.open_file_dialog() or self.lineEdit_txt_save_path.text()
            )
        )
        ## sqlite
        self.pushButton_sqlite_select_path.clicked.connect(
            lambda: self.lineEdit_sqlite_save_path.setText(
                self.open_file_dialog() or self.lineEdit_sqlite_save_path.text()
            )
        )
        self.pushButton_sqlite_test_connect.clicked.connect(
            self.on_click_test_sqlite_connection
        )
        ## mysql
        self.pushButton_mysql_test_connect.clicked.connect(
            self.on_click_test_mysql_connection
        )
        ## mongodb
        self.pushButton_mongodb_test_connect.clicked.connect(
            self.on_click_test_mongodb_connection
        )
        ## webdav
        self.pushButton_webdav_test_connect.clicked.connect(
            self.on_click_test_webdav_connection
        )
        self.pushButton_webdav_backup.clicked.connect(self.on_click_webdav_backup)
        self.pushButton_webdav_restore.clicked.connect(self.on_click_webdav_restore)
        # 保存
        self.pushButton_save.clicked.connect(self.on_click_save)

    # slots
    def on_click_test_sqlite_connection(self):
        """
        测试SQLite连接
        """
        self.__disable_ui_for_thread__()
        self.thread = CustomThread(
            SqliteTools.test_connection,
            "SQLite",
            self.lineEdit_sqlite_save_path.text(),
        )
        self.thread.signal_result.connect(self.on_thread_finished)
        self.thread.finished.connect(self.__enable_ui_after_thread__)
        self.thread.start()

    def on_click_test_mysql_connection(self):
        """
        测试MySQL连接
        """
        self.__disable_ui_for_thread__()
        self.thread = CustomThread(
            MysqlTools.test_connection,
            "MySQL",
            self.lineEdit_mysql_host.text(),
            self.lineEdit_mysql_username.text(),
            self.lineEdit_mysql_password.text(),
            self.spinBox_mysql_port.value(),
        )
        self.thread.signal_result.connect(self.on_thread_finished)
        self.thread.finished.connect(self.__enable_ui_after_thread__)
        self.thread.start()

    def on_click_test_mongodb_connection(self):
        """
        测试MongoDB连接
        """
        self.__disable_ui_for_thread__()
        self.thread = CustomThread(
            MongodbTools.test_connection,
            "MongoDB",
            self.lineEdit_mongodb_host.text(),
            self.lineEdit_mongodb_username.text(),
            self.lineEdit_mongodb_password.text(),
            self.spinBox_mongodb_port.value(),
        )
        self.thread.signal_result.connect(self.on_thread_finished)
        self.thread.finished.connect(self.__enable_ui_after_thread__)
        self.thread.start()

    def on_click_test_webdav_connection(self):
        """
        测试WebDAV连接
        """
        self.__disable_ui_for_thread__()
        self.thread = CustomThread(
            WebDAVTools.test_connection,
            "WebDAV",
            self.comboBox_protocol.currentText(),
            self.lineEdit_webdav_host.text(),
            self.lineEdit_webdav_port.text(),
            self.lineEdit_webdav_path.text(),
            self.lineEdit_webdav_account.text(),
            self.lineEdit_webdav_password.text(),
        )
        self.thread.signal_result.connect(self.on_thread_finished)
        self.thread.finished.connect(self.__enable_ui_after_thread__)
        self.thread.start()

    def on_click_webdav_backup(self):
        """
        执行WebDAV备份
        """
        # 先保存WebDAV配置
        self.config.webdav_protocol = self.comboBox_protocol.currentText()
        self.config.webdav_host = self.lineEdit_webdav_host.text()
        self.config.webdav_port = self.lineEdit_webdav_port.text()
        self.config.webdav_path = self.lineEdit_webdav_path.text()
        self.config.webdav_account = self.lineEdit_webdav_account.text()
        self.config.webdav_password = self.lineEdit_webdav_password.text()

        # 获取主窗口的数据工具实例（如果有parent）
        if self.parent() and hasattr(self.parent(), "tools"):
            data_tool = self.parent().tools
        else:
            data_tool = DataTool()

        # 在线程中执行备份
        self.__disable_ui_for_thread__()
        self.thread = CustomThread(
            self.__backup_data_thread__,
            "备份",
            data_tool,
        )
        self.thread.signal_result.connect(self.on_webdav_operation_finished)
        self.thread.finished.connect(self.__enable_ui_after_thread__)
        self.thread.start()

    def __backup_data_thread__(self, data_tool) -> bool:
        """
        备份数据线程执行函数
        """
        webdav_tools = WebDAVTools()
        return webdav_tools.backup_data(data_tool)

    def on_click_webdav_restore(self):
        """
        执行WebDAV恢复
        """
        # 确认对话框
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认恢复",
            "恢复数据将覆盖当前所有数据，是否继续？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )

        if reply == QtWidgets.QMessageBox.No:
            return

        # 先保存WebDAV配置
        self.config.webdav_protocol = self.comboBox_protocol.currentText()
        self.config.webdav_host = self.lineEdit_webdav_host.text()
        self.config.webdav_port = self.lineEdit_webdav_port.text()
        self.config.webdav_path = self.lineEdit_webdav_path.text()
        self.config.webdav_account = self.lineEdit_webdav_account.text()
        self.config.webdav_password = self.lineEdit_webdav_password.text()

        # 获取主窗口的数据工具实例（如果有parent）
        if self.parent() and hasattr(self.parent(), "tools"):
            data_tool = self.parent().tools
        else:
            data_tool = DataTool()

        # 在线程中执行恢复
        self.__disable_ui_for_thread__()
        self.thread = CustomThread(
            self.__restore_data_thread__,
            "恢复",
            data_tool,
        )
        self.thread.signal_result.connect(self.on_webdav_operation_finished)
        self.thread.finished.connect(self.__enable_ui_after_thread__)
        self.thread.start()

    def __restore_data_thread__(self, data_tool) -> bool:
        """
        恢复数据线程执行函数
        """
        webdav_tools = WebDAVTools()
        return webdav_tools.restore_data(data_tool)

    def on_click_save(self):
        """
        保存配置
        """
        # 通用
        if self.config.auto_start != self.checkBox_auto_start.isChecked():
            self.set_auto_open(self.checkBox_auto_start.isChecked())
        if self.config.use_systemtray != self.checkBox_use_systemtray.isChecked():
            self.signal_tray.emit(self.checkBox_use_systemtray.isChecked())
            self.config.use_systemtray = self.checkBox_use_systemtray.isChecked()
        self.config.auto_update = self.checkBox_auto_update.isChecked()
        # 数据
        dtype = self.comboBox_save_type.currentText()
        if dtype == "txt":
            result = TxtTools.test_connection(self.lineEdit_txt_save_path.text())
            if result:
                self.config.txt_path = self.lineEdit_txt_save_path.text()
        elif dtype == "sqlite":
            result = SqliteTools.test_connection(self.lineEdit_sqlite_save_path.text())
            if result:
                self.config.sqlite_path = self.lineEdit_sqlite_save_path.text()
        elif dtype == "mysql":
            result = MysqlTools.test_connection(
                self.lineEdit_mysql_host.text(),
                self.lineEdit_mysql_username.text(),
                self.lineEdit_mysql_password.text(),
                self.spinBox_mysql_port.value(),
            )
            if result:
                self.config.mysql_host = self.lineEdit_mysql_host.text()
                self.config.mysql_username = self.lineEdit_mysql_username.text()
                self.config.mysql_password = self.lineEdit_mysql_password.text()
                self.config.mysql_port = self.spinBox_mysql_port.value()
        elif dtype == "mongodb":
            result = MongodbTools.test_connection(
                self.lineEdit_mongodb_host.text(),
                self.lineEdit_mongodb_username.text(),
                self.lineEdit_mongodb_password.text(),
                self.spinBox_mongodb_port.value(),
            )
            if result:
                self.config.mongodb_host = self.lineEdit_mongodb_host.text()
                self.config.mongodb_username = self.lineEdit_mongodb_username.text()
                self.config.mongodb_password = self.lineEdit_mongodb_password.text()
                self.config.mongodb_port = self.spinBox_mongodb_port.value()
        if result:
            self.config.data_save_type = dtype
        else:
            self.show_message(result, dtype)
            return

        # 备份设置 - 始终保存WebDAV配置
        self.config.webdav_protocol = self.comboBox_protocol.currentText()
        self.config.webdav_host = self.lineEdit_webdav_host.text()
        self.config.webdav_port = self.lineEdit_webdav_port.text()
        self.config.webdav_path = self.lineEdit_webdav_path.text()
        self.config.webdav_account = self.lineEdit_webdav_account.text()
        self.config.webdav_password = self.lineEdit_webdav_password.text()

        # 关闭窗口
        self.close()

    def on_thread_finished(self, result: bool, con_type: str):
        """
        线程结束 - 处理连接测试结果
        """
        self.show_message(result, con_type)

    def on_webdav_operation_finished(self, result: bool, operation_type: str):
        """
        线程结束 - 处理WebDAV操作结果（备份/恢复）
        """
        if result:
            if operation_type == "备份":
                QtWidgets.QMessageBox.information(self, "成功", "数据备份成功！")
            elif operation_type == "恢复":
                QtWidgets.QMessageBox.information(
                    self, "成功", "数据恢复成功！\n请重启应用以查看恢复的数据"
                )
        else:
            QtWidgets.QMessageBox.critical(
                self, "失败", f"数据{operation_type}失败！\n请检查WebDAV配置和网络连接"
            )

    # utils
    def open_file_dialog(self) -> str | None:
        """
        打开文件夹选择对话框
        """
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择文件夹", self.config.folder_path
        )
        return folder_path if folder_path else None

    def get_config(self) -> dict:
        """
        获取配置
        """
        if self.config.data_save_type == "txt":
            return {
                "type": "txt",
                "config": {"path": self.config.txt_path},
            }
        elif self.config.data_save_type == "sqlite":
            return {
                "type": "sqlite",
                "config": {"path": self.config.sqlite_path},
            }
        elif self.config.data_save_type == "mysql":
            return {
                "type": "mysql",
                "config": {
                    "host": self.config.mysql_host,
                    "port": self.config.mysql_port,
                    "username": self.config.mysql_username,
                    "password": self.config.mysql_password,
                },
            }
        elif self.config.data_save_type == "mongodb":
            return {
                "type": "mongodb",
                "config": {
                    "host": self.config.mongodb_host,
                    "port": self.config.mongodb_port,
                    "username": self.config.mongodb_username,
                    "password": self.config.mongodb_password,
                },
            }
        else:
            return {}

    def show_message(self, result: bool, con_type: str):
        """
        显示消息框
        """
        if result:
            QtWidgets.QMessageBox.information(self, "成功", f"{con_type}连接成功！")
        else:
            QtWidgets.QMessageBox.critical(
                self, "失败", f"{con_type}连接失败！\n请重新检查配置"
            )

    def set_auto_open(self, checked: bool):
        """
        设置开机自启动
        """
        import winreg

        if checked:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.SetValueEx(
                key,
                "Account Manager",
                0,
                winreg.REG_SZ,
                self.config.folder_path + " --no-window",
            )
            winreg.CloseKey(key)
        else:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.DeleteValue(key, "Account Manager")
