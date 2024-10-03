from copy import deepcopy
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QMessageBox,
    QFileDialog,
    QTableWidgetItem,
    QApplication,
)
from tools.Ui_mainWindow import Ui_MainWindow
from tools.Ui_systemTray import SystemTrayIcon
from tools.DBtools import MyDB


class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, app: QApplication, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.app = app
        self._bound()
        self.__initialization__()
        self.__init_systemTray(app)

    def _bound(self):
        """
        绑定事件
        """
        self.actiontest.triggered.connect(self.test)
        self.importtxt.triggered.connect(self.import_txt)
        self.importxls.triggered.connect(self.import_xls)
        self.exporttxt.triggered.connect(self.export_txt)
        self.exportxls.triggered.connect(self.export_xls)

        self.pushButtonmodify.clicked.connect(self.modify)
        self.pushButtondelete.clicked.connect(self.delete)
        self.pushButtonclear.clicked.connect(self.clear)
        self.pushButtonquery.clicked.connect(self.query)

        self.tableWidget.cellClicked.connect(self.cell_clicked)

    def __initialization__(self):
        # 测试菜单
        self.actiontest: QAction
        # 菜单
        self.importtxt: QAction
        self.importxls: QAction
        self.exporttxt: QAction
        self.exportxls: QAction
        # Button
        self.pushButtonmodify: QPushButton
        self.pushButtondelete: QPushButton
        self.pushButtonclear: QPushButton
        self.pushButtonquery: QPushButton
        # lineEdit
        self.lineEdituuid: QLineEdit
        self.lineEditname: QLineEdit
        self.lineEditremarks: QLineEdit
        self.lineEditaccount: QLineEdit
        self.lineEditpassword: QLineEdit
        # tableWidget
        self.tableWidget: QTableWidget
        # 记录当前数据库中的数据
        self.data: list = None
        # 数据库对象
        self.__init_db__()
        # 初始化数据库中数据加入tableWidget
        self._refresh_tableWidget(self._refresh_all_info())

    def __init_db__(self):
        self.db = MyDB()

    def __init_systemTray(self, app):
        """
        初始化系统托盘
        """
        self.tray = SystemTrayIcon(self)

    def _refresh_tableWidget(self, data: list = None):
        """
        初始化tableWidget
        """
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["名称", "账号", "密码", "备注"])
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                if j == 0:
                    continue
                t = str(value) if value else ""
                self.tableWidget.setItem(i, j - 1, QTableWidgetItem(t))

    def _choose_file(self, info: str, file_type_choose, filter: str):
        """
        选择文件
        """
        # 弹出警告框
        m = QMessageBox.warning(self, "警告", info, QMessageBox.Yes | QMessageBox.No)
        if m == QMessageBox.Yes:
            # 选择文件
            file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", filter)
            if file_name:
                flag = file_type_choose(file_name.rsplit(".", 1)[-1])
                if flag:
                    return file_name
                else:
                    QMessageBox.critical(self, "错误", "请选择对应文件", QMessageBox.Yes)
                    return False
        elif m == QMessageBox.No:
            return False
        else:
            return False
        return False

    def _choose_dir(self):
        """
        选择文件夹
        """
        # 选择文件夹
        dir_name = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if dir_name:
            return dir_name
        else:
            return False

    def _refresh_all_info(self, uuid: bool = True):
        """
        获取所有数据库表中的数据
        """
        self.data = self.db.fetch_all()
        if uuid:
            return deepcopy(self.data)
        else:
            return [i[1:] for i in deepcopy(self.data)]

    def _get_lineEdit_data(self):
        """
        获取输入框数据
        """
        uuid = self.lineEdituuid.text()
        name = self.lineEditname.text()
        account = self.lineEditaccount.text()
        password = self.lineEditpassword.text()
        remarks = self.lineEditremarks.text()
        return (uuid, name, account, password, remarks)

    def test(self):
        # 测试 弹出对话框
        s = self._choose_dir()
        print(s)

    def import_txt(self):
        """
        导入txt
        """
        file_name = self._choose_file(
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
                    t = i.split("\t")
                    t = [t.strip() for t in t]
                    tmp_info.append(tuple(t))
            self.db.clear_table()
            self.db.insert_many_data(tmp_info)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)
        finally:
            self._refresh_tableWidget(self._refresh_all_info())

    def import_xls(self):
        """
        导入xls
        """
        file_name = self._choose_file(
            '导入会覆盖之前保存的记录!\n\n每行数据从左至右顺序应为(名称,账号,密码,备注) \n"备注"一列可为空',
            lambda x: x in ["xls", "xlsx"],
            "Excel Files (*.xls *.xlsx);;All Files (*)",
        )
        if not file_name:
            return

        try:
            from numpy import nan
            import pandas as pd

            tmp_info = []

            data = pd.read_excel(file_name, dtype=str)
            for i in range(len(data)):
                t = [
                    str(data.loc[i, "名称"]).strip() if data.loc[i, "名称"] is not nan else "",
                    str(data.loc[i, "账号"]).strip() if data.loc[i, "账号"] is not nan else "",
                    str(data.loc[i, "密码"]).strip() if data.loc[i, "密码"] is not nan else "",
                    str(data.loc[i, "备注"]).strip() if data.loc[i, "备注"] is not nan else "",
                ]
                tmp_info.append(tuple(t))
            self.db.clear_table()
            self.db.insert_many_data(tmp_info)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)
        finally:
            self._refresh_tableWidget(self._refresh_all_info())

    def export_txt(self):
        """
        导出txt
        """
        dir: str = self._choose_dir()
        if not dir:
            return
        try:
            import os

            flag = ""
            file_name = dir + "/data{}.txt"
            while os.path.exists(file_name.format(flag)):
                flag = flag + 1 if flag else 1

            with open(file_name.format(flag), "w", encoding="utf-8") as f:
                tmp_data = self._refresh_all_info(False)
                for i in tmp_data:
                    f.write("\t".join(i) + "\n")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)

    def export_xls(self):
        """
        导出xls
        """
        dir = self._choose_dir()
        if not dir:
            return
        try:
            import os
            import pandas as pd

            flag = ""
            file_name = dir + "/data{}.xlsx"
            while os.path.exists(file_name.format(flag)):
                flag = flag + 1 if flag else 1

            tmp_data = self._refresh_all_info(False)
            data = pd.DataFrame(tmp_data, columns=["名称", "账号", "密码", "备注"])
            data.to_excel(file_name.format(flag), index=False)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e), QMessageBox.Yes)

    def modify(self):
        """
        修改或新增
        """
        data = self._get_lineEdit_data()
        if data[0]:
            self.db.update_data(data[0], data[1:])
        else:
            self.db.insert_data(data[1:])
        self._refresh_tableWidget(self._refresh_all_info())
        self.clear()

    def delete(self):
        """
        删除
        """
        t = self.tableWidget.selectedItems()
        rows = []
        for i in t:
            rows.append(i.row())
        rows = list(set(rows))
        uuid_list = [self.data[i][0] for i in rows]
        for i in uuid_list:
            self.db.delete_data(i)
        self._refresh_tableWidget(self._refresh_all_info())
        self.clear()

    def clear(self):
        """
        清空lineEdit
        """
        self.lineEdituuid.clear()
        self.lineEditname.clear()
        self.lineEditremarks.clear()
        self.lineEditaccount.clear()
        self.lineEditpassword.clear()
        self._refresh_tableWidget(self._refresh_all_info())

    def query(self):
        """
        查询并显示
        """
        data = self._get_lineEdit_data()
        ans = self.db.fetch(*data)
        all_info = self._refresh_all_info()
        for i in ans:
            if i in all_info:
                all_info.remove(i)
        self.data = [*ans, *all_info]
        self._refresh_tableWidget(self.data)
        
        l_ans = len(ans)
        for i in range(l_ans):
            self.tableWidget.selectRow(i)

    def cell_clicked(self, row, col):
        # 获取当前tablewidget中所有被选中的单元格
        t = self.tableWidget.selectedItems()
        rows = []
        for i in t:
            rows.append(i.row())
        rows = list(set(rows))
        if len(rows) != 1:
            return
        else:
            row = rows[0]
            self.lineEdituuid.setText(self.data[row][0])
            self.lineEditname.setText(self.data[row][1])
            self.lineEditaccount.setText(self.data[row][2])
            self.lineEditpassword.setText(self.data[row][3])
            self.lineEditremarks.setText(self.data[row][4])
