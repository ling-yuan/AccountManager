import os
import json
import uuid
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QMessageBox,
    QFileDialog,
    QTableWidgetItem,
    QApplication,
    QTabWidget,
    QInputDialog,
    QMenu,
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
        self.tab_stores: dict[str, Store] = {}

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
        # 初始化分组标签页
        self.init_tab_widget()
        self.load_tab_groups()
        self.action_import_txt.setText("导入分组文件")
        self.action_export_txt.setText("导出分组文件")
        # 初始化输入框
        self.clear_data()
        self.show_log("数据加载完成", 5000)

    def __init_slots__(self):
        # 菜单栏
        self.action_import_txt.triggered.connect(self.on_click_import_txt)
        self.action_export_txt.triggered.connect(self.on_click_export_txt)
        self.action_webdav_backup.triggered.connect(
            self.settings_window.on_click_webdav_backup
        )
        self.action_webdav_restore.triggered.connect(
            self.settings_window.on_click_webdav_restore
        )
        self.action_settings.triggered.connect(self.on_click_settings)
        # 按钮
        self.pushButton_modify.clicked.connect(self.on_click_modify)
        self.pushButton_delete.clicked.connect(self.on_click_delete)
        self.pushButton_clear.clicked.connect(self.on_click_clear)
        self.pushButton_query.clicked.connect(self.on_click_query)
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

    def init_tab_widget(self):
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setStyleSheet("""
            QTabWidget::pane {
                border: 0px;
                border-radius: 6px;
                border-top: none;
                top: 0px;
            }
            QTabBar {
                qproperty-drawBase: 0;
            }
            QTabBar::tab {
                background: #edf1f5;
                color: #2c3e50;
                border: 1px solid #c8d1dc;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 6px 5px;
                margin-right: -1px;
                min-width: 72px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #1f6feb;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background: #e3e9f1;
            }
            """)

        table_index = self.verticalLayout.indexOf(self.tableWidget)
        self.verticalLayout.removeWidget(self.tableWidget)
        self.tabWidget.addTab(self.tableWidget, "分组1")
        self.verticalLayout.insertWidget(table_index, self.tabWidget)

        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.tabWidget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tabWidget.tabBarDoubleClicked.connect(self.on_tab_bar_double_clicked)

        tab_bar = self.tabWidget.tabBar()
        tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self.on_tab_context_menu)

        self._bind_table(self.tableWidget)
        self.tableWidget.setProperty("tab_key", self._new_tab_key())
        self.tab_stores[self.tableWidget.property("tab_key")] = Store()

    def _new_tab_key(self) -> str:
        return str(uuid.uuid4())

    def _bind_table(self, table: QTableWidget):
        table.itemSelectionChanged.connect(self.on_selection_changed)

    def _create_table_widget(self) -> QTableWidget:
        table = QTableWidget(self.centralwidget)
        table.setFont(self.tableWidget.font())
        table.setFocusPolicy(self.tableWidget.focusPolicy())
        table.setEditTriggers(self.tableWidget.editTriggers())
        table.setSelectionBehavior(self.tableWidget.selectionBehavior())
        table.setHorizontalScrollMode(self.tableWidget.horizontalScrollMode())
        table.setShowGrid(self.tableWidget.showGrid())
        table.setGridStyle(self.tableWidget.gridStyle())
        table.setCornerButtonEnabled(self.tableWidget.isCornerButtonEnabled())
        table.setColumnCount(self.tableWidget.columnCount())
        table.setRowCount(0)
        table.setSortingEnabled(self.tableWidget.isSortingEnabled())
        table.horizontalHeader().setDefaultSectionSize(
            self.tableWidget.horizontalHeader().defaultSectionSize()
        )
        table.horizontalHeader().setMinimumSectionSize(
            self.tableWidget.horizontalHeader().minimumSectionSize()
        )
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setDefaultSectionSize(
            self.tableWidget.verticalHeader().defaultSectionSize()
        )
        for i in range(self.tableWidget.columnCount()):
            header = self.tableWidget.horizontalHeaderItem(i)
            title = header.text() if header else ""
            table.setHorizontalHeaderItem(i, QTableWidgetItem(title))
        self._bind_table(table)
        return table

    def current_table(self) -> QTableWidget:
        widget = self.tabWidget.currentWidget()
        if isinstance(widget, QTableWidget):
            return widget
        return self.tableWidget

    def current_tab_key(self) -> str:
        table = self.current_table()
        return table.property("tab_key")

    def current_store(self) -> Store:
        key = self.current_tab_key()
        if key not in self.tab_stores:
            self.tab_stores[key] = Store()
        return self.tab_stores[key]

    def load_tab_groups(self):
        payload = self.tools.load_tab_groups()
        groups = payload.get("groups", []) if isinstance(payload, dict) else []
        if not groups:
            payload = self.tools.default_tab_groups_payload()
            self.apply_tab_groups_payload(payload, save=True)
            return
        self.apply_tab_groups_payload(payload, save=False)

    def apply_tab_groups_payload(self, payload: dict, save: bool = True):
        groups = payload.get("groups", []) if isinstance(payload, dict) else []
        self.tab_stores.clear()
        while self.tabWidget.count() > 1:
            w = self.tabWidget.widget(1)
            self.tabWidget.removeTab(1)
            w.deleteLater()

        first = True
        for group in groups:
            key = str(group.get("key") or self._new_tab_key())
            title = str(group.get("title") or "未命名分组")
            records = group.get("records", [])
            store = Store()
            for item in records:
                if not isinstance(item, dict):
                    continue
                store.add(
                    Data(
                        name=item.get("name", ""),
                        account=item.get("account", ""),
                        password=item.get("password", ""),
                        note=item.get("note", ""),
                        id=item.get("id"),
                    )
                )
            self.tab_stores[key] = store
            if first:
                first = False
                self.tableWidget.setProperty("tab_key", key)
                self.tabWidget.setTabText(0, title)
                self.refresh_table(self.tableWidget, store)
            else:
                self.add_tab(title=title, store=store, key=key, save=False)

        if self.tabWidget.count() == 0 or not groups:
            fallback_key = self.tableWidget.property("tab_key") or self._new_tab_key()
            self.tableWidget.setProperty("tab_key", fallback_key)
            self.tab_stores[fallback_key] = Store()
            self.tabWidget.setTabText(0, "分组1")
            self.refresh_table(self.tableWidget, self.tab_stores[fallback_key])

        self.tabWidget.setCurrentIndex(0)
        self.clear_data()
        if save:
            self.save_tab_groups()

    def build_tab_groups_payload(self) -> dict:
        groups = []
        for i in range(self.tabWidget.count()):
            table = self.tabWidget.widget(i)
            if not isinstance(table, QTableWidget):
                continue
            key = table.property("tab_key")
            title = self.tabWidget.tabText(i)
            store = self.tab_stores.get(key, Store())
            groups.append(
                {
                    "key": key,
                    "title": title,
                    "records": [data.to_dict() for data in store],
                }
            )
        return {"format": "account_manager_groups_v1", "groups": groups}

    def save_tab_groups(self):
        self.tools.save_tab_groups(self.build_tab_groups_payload())

    def sync_tabs_to_data_tool(self):
        self.tools.save_tab_groups(self.build_tab_groups_payload())

    def add_tab(
        self,
        title: str = "新分组",
        store: Store | None = None,
        key: str | None = None,
        save: bool = True,
    ):
        table = self._create_table_widget()
        tab_key = key or self._new_tab_key()
        table.setProperty("tab_key", tab_key)
        self.tab_stores[tab_key] = store if store else Store()
        self.refresh_table(table, self.tab_stores[tab_key])
        index = self.tabWidget.addTab(table, title)
        self.tabWidget.setCurrentIndex(index)
        if save:
            self.save_tab_groups()
        return index

    def rename_tab(self, index: int):
        if index < 0 or index >= self.tabWidget.count():
            return
        old_title = self.tabWidget.tabText(index)
        new_title, ok = QInputDialog.getText(
            self, "重命名分组", "请输入新的分组名：", text=old_title
        )
        if ok:
            new_title = new_title.strip()
            if not new_title:
                QMessageBox.warning(self, "提示", "分组名不能为空", QMessageBox.Yes)
                return
            self.tabWidget.setTabText(index, new_title)
            self.save_tab_groups()

    def on_tab_context_menu(self, pos):
        index = self.tabWidget.tabBar().tabAt(pos)
        if index >= 0:
            self.tabWidget.setCurrentIndex(index)

        menu = QMenu(self)
        action_add = menu.addAction("新增分组")
        action_rename = menu.addAction("重命名分组")
        action_delete = menu.addAction("删除分组")
        selected = menu.exec_(self.tabWidget.tabBar().mapToGlobal(pos))
        if selected == action_add:
            self.add_tab()
        elif selected == action_rename:
            self.rename_tab(self.tabWidget.currentIndex())
        elif selected == action_delete:
            self.on_tab_close_requested(self.tabWidget.currentIndex())

    def on_tab_changed(self, _index: int):
        self.clear_data()
        table = self.current_table()
        table.clearSelection()
        self.refresh_table(table)

    def on_tab_close_requested(self, index: int):
        if self.tabWidget.count() <= 1:
            QMessageBox.information(
                self, "提示", "至少需要保留一个分组", QMessageBox.Yes
            )
            return
        tab_title = self.tabWidget.tabText(index) if index >= 0 else ""
        reply = QMessageBox.question(
            self,
            "确认删除分组",
            f"确定要删除分组“{tab_title}”吗？\n\n该分组内的记录将一并删除，且无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        table = self.tabWidget.widget(index)
        if not isinstance(table, QTableWidget):
            return
        key = table.property("tab_key")
        self.tabWidget.removeTab(index)
        self.tab_stores.pop(key, None)
        table.deleteLater()
        self.clear_data()
        self.save_tab_groups()

    def on_tab_bar_double_clicked(self, index: int):
        if index >= 0:
            self.rename_tab(index)

    # slots
    def on_click_import_txt(self):
        file_name = self.choose_file(
            "导入会覆盖当前所有分组与记录，是否继续？\n\n请导入分组同步文件（.amg 或 .json）。",
            lambda x: x.lower() in ["amg", "json"],
            "Account Manager Group Files (*.amg *.json);;All Files (*)",
        )
        if not file_name:
            return

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                payload = json.load(f)

            groups = payload.get("groups", [])
            if not isinstance(groups, list):
                raise ValueError("文件格式错误：缺少 groups 列表")

            self.apply_tab_groups_payload(payload, save=True)
            self.show_log("导入成功", 5000)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)
        finally:
            self.refresh_table(self.current_table())

    def on_click_export_txt(self):
        dir: str = self.choose_dir()
        if not dir:
            return
        try:
            flag = ""
            file_name = dir + "/account_groups{}.amg"
            while os.path.exists(file_name.format(flag)):
                flag = flag + 1 if flag else 1

            with open(file_name.format(flag), "w", encoding="utf-8") as f:
                json.dump(
                    self.build_tab_groups_payload(), f, ensure_ascii=False, indent=2
                )
            self.show_log("导出成功", 5000)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)

    def on_click_settings(self):
        self.sync_tabs_to_data_tool()
        self.on_click_clear()
        self.settings_window.show()
        self.settings_window.exec()
        self.on_click_clear()
        self.save_tab_groups()

    def on_click_modify(self):
        data = self.get_data()
        store = self.current_store()
        if self.lineEdit_name.id:
            store.modify(data)
            self.show_log("修改成功", 5000)
        else:
            store.add(data)
            self.show_log("添加成功", 5000)
        store.sort()
        self.save_tab_groups()
        self.on_click_clear()

    def on_click_delete(self):
        selected_store = self.get_selected_data()
        current_store = self.current_store()
        for data in selected_store:
            current_store.delete(data)
        self.show_log(f"已删除{selected_store.length}条数据", 5000)
        self.save_tab_groups()
        self.on_click_clear()

    def on_click_clear(self):
        self.clear_data()
        table = self.current_table()
        table.clearSelection()
        self.refresh_table(table)

    def on_click_query(self):
        pattern = Data(
            name=self.lineEdit_name.text(),
            account=self.lineEdit_account.text(),
            password=self.lineEdit_password.text(),
            note=self.textEdit_note.toPlainText(),
        )
        store = self.current_store().search(pattern)
        table = self.current_table()
        table.clearSelection()
        self.show_log(f"查询到{store.length}条数据", 5000)
        self.refresh_table(table, store)

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

    def refresh_table(
        self, table: QTableWidget | None = None, store: Store | None = None
    ):
        table = table or self.current_table()
        if store is None:
            store = self.tab_stores.get(table.property("tab_key"), Store())
        # 填充表格时临时关闭排序，避免排序触发行移动导致数据错位
        sorting_enabled = table.isSortingEnabled()
        table.setSortingEnabled(False)
        # 暂时禁用自动调整以提高性能
        table.setUpdatesEnabled(False)
        # 清空表格
        table.clearContents()
        table.clearSelection()
        table.setRowCount(store.length)
        for i, data in enumerate(store):
            # 创建表格项
            name_item = Ui_TableItem(id=data.id, text=data.name)
            account_item = QTableWidgetItem(data.account)
            password_item = QTableWidgetItem(data.password)
            note_item = QTableWidgetItem(data.note)
            # 设置文本自动换行
            note_item.setData(Qt.ItemDataRole.DisplayRole, data.note)
            # 添加到表格
            table.setItem(i, 0, name_item)
            table.setItem(i, 1, account_item)
            table.setItem(i, 2, password_item)
            table.setItem(i, 3, note_item)
        # 重新启用更新并调整大小
        table.setUpdatesEnabled(True)
        table.resizeRowsToContents()  # 调整所有行高
        table.setSortingEnabled(sorting_enabled)

    def get_selected_data(self):
        table = self.current_table()
        t = table.selectedItems()
        rows = list(set([i.row() for i in t]))
        selected = []
        for row in rows:
            name_item = table.item(row, 0)
            account_item = table.item(row, 1)
            password_item = table.item(row, 2)
            note_item = table.item(row, 3)
            # 在刷新/排序切换瞬间，可能出现暂时空单元格，跳过避免崩溃
            if not all([name_item, account_item, password_item, note_item]):
                continue
            selected.append(
                Data(
                    id=name_item.id,
                    name=name_item.text(),
                    account=account_item.text(),
                    password=password_item.text(),
                    note=note_item.text(),
                )
            )
        store = Store(*selected)
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
                self.current_table().clearSelection()
                self.show_log("已清除选择", 2000)

        # 调用父类方法保持正常行为
        super().mousePressEvent(event)

    def closeEvent(self, event: QtGui.QMouseEvent):
        self.save_tab_groups()
        event.accept()
        if not self.config.use_systemtray:
            self.app.quit()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
