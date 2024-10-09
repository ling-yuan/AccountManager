# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Code\Project\python\AccountManager\tools\ui\mainWindow\mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(721, 518)
        MainWindow.setMinimumSize(QtCore.QSize(721, 518))
        MainWindow.setMaximumSize(QtCore.QSize(721, 518))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./img/safe.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.labelname = QtWidgets.QLabel(self.centralwidget)
        self.labelname.setGeometry(QtCore.QRect(50, 20, 61, 30))
        self.labelname.setFocusPolicy(QtCore.Qt.NoFocus)
        self.labelname.setTextFormat(QtCore.Qt.AutoText)
        self.labelname.setAlignment(QtCore.Qt.AlignCenter)
        self.labelname.setObjectName("labelname")
        self.labelaccount = QtWidgets.QLabel(self.centralwidget)
        self.labelaccount.setGeometry(QtCore.QRect(370, 20, 61, 30))
        self.labelaccount.setAlignment(QtCore.Qt.AlignCenter)
        self.labelaccount.setObjectName("labelaccount")
        self.labelpassword = QtWidgets.QLabel(self.centralwidget)
        self.labelpassword.setGeometry(QtCore.QRect(370, 70, 61, 30))
        self.labelpassword.setAlignment(QtCore.Qt.AlignCenter)
        self.labelpassword.setObjectName("labelpassword")
        self.labelremarks = QtWidgets.QLabel(self.centralwidget)
        self.labelremarks.setGeometry(QtCore.QRect(50, 70, 61, 30))
        self.labelremarks.setAlignment(QtCore.Qt.AlignCenter)
        self.labelremarks.setObjectName("labelremarks")
        self.pushButtonclear = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonclear.setGeometry(QtCore.QRect(370, 130, 91, 31))
        self.pushButtonclear.setObjectName("pushButtonclear")
        self.pushButtonmodify = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonmodify.setGeometry(QtCore.QRect(90, 130, 91, 31))
        self.pushButtonmodify.setObjectName("pushButtonmodify")
        self.pushButtondelete = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtondelete.setGeometry(QtCore.QRect(230, 130, 91, 31))
        self.pushButtondelete.setObjectName("pushButtondelete")
        self.pushButtonquery = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonquery.setGeometry(QtCore.QRect(510, 130, 91, 31))
        self.pushButtonquery.setObjectName("pushButtonquery")
        self.lineEditname = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditname.setGeometry(QtCore.QRect(110, 20, 191, 31))
        self.lineEditname.setObjectName("lineEditname")
        self.lineEditaccount = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditaccount.setGeometry(QtCore.QRect(430, 20, 191, 31))
        self.lineEditaccount.setObjectName("lineEditaccount")
        self.lineEditpassword = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditpassword.setGeometry(QtCore.QRect(430, 70, 191, 31))
        self.lineEditpassword.setClearButtonEnabled(False)
        self.lineEditpassword.setObjectName("lineEditpassword")
        self.lineEditremarks = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditremarks.setGeometry(QtCore.QRect(110, 70, 191, 31))
        self.lineEditremarks.setObjectName("lineEditremarks")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(0, 180, 721, 311))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(167)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(50)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setDefaultSectionSize(30)
        self.lineEdituuid = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdituuid.setEnabled(False)
        self.lineEdituuid.setGeometry(QtCore.QRect(700, -20, 10, 10))
        self.lineEdituuid.setReadOnly(False)
        self.lineEdituuid.setClearButtonEnabled(False)
        self.lineEdituuid.setObjectName("lineEdituuid")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setGeometry(QtCore.QRect(0, -3, 721, 5))
        self.progressBar.setStyleSheet("QProgressBar { border : none; }")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 721, 26))
        self.menuBar.setObjectName("menuBar")
        self.menu = QtWidgets.QMenu(self.menuBar)
        self.menu.setObjectName("menu")
        self.submenu1 = QtWidgets.QMenu(self.menu)
        self.submenu1.setObjectName("submenu1")
        self.submenu2 = QtWidgets.QMenu(self.menu)
        self.submenu2.setObjectName("submenu2")
        self.menu_2 = QtWidgets.QMenu(self.menuBar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menuBar)
        self.importtxt = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("./img/txt.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.importtxt.setIcon(icon1)
        self.importtxt.setObjectName("importtxt")
        self.exporttxt = QtWidgets.QAction(MainWindow)
        self.exporttxt.setIcon(icon1)
        self.exporttxt.setObjectName("exporttxt")
        self.exportxls = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("./img/xls.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exportxls.setIcon(icon2)
        self.exportxls.setObjectName("exportxls")
        self.importxls = QtWidgets.QAction(MainWindow)
        self.importxls.setIcon(icon2)
        self.importxls.setObjectName("importxls")
        self.actiontest = QtWidgets.QAction(MainWindow)
        self.actiontest.setObjectName("actiontest")
        self.actionSetAutoOpen = QtWidgets.QAction(MainWindow)
        self.actionSetAutoOpen.setCheckable(True)
        self.actionSetAutoOpen.setChecked(False)
        self.actionSetAutoOpen.setObjectName("actionSetAutoOpen")
        self.actionRegister = QtWidgets.QAction(MainWindow)
        self.actionRegister.setObjectName("actionRegister")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.submenu1.addAction(self.importtxt)
        self.submenu1.addAction(self.importxls)
        self.submenu2.addAction(self.exporttxt)
        self.submenu2.addAction(self.exportxls)
        self.menu.addAction(self.submenu1.menuAction())
        self.menu.addAction(self.submenu2.menuAction())
        self.menu.addSeparator()
        self.menu_2.addAction(self.actionSetAutoOpen)
        self.menu_2.addAction(self.actionRegister)
        self.menu_2.addAction(self.actionExit)
        self.menuBar.addAction(self.menu.menuAction())
        self.menuBar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelname.setText(_translate("MainWindow", "名称"))
        self.labelaccount.setText(_translate("MainWindow", "账号"))
        self.labelpassword.setText(_translate("MainWindow", "密码"))
        self.labelremarks.setText(_translate("MainWindow", "备注"))
        self.pushButtonclear.setText(_translate("MainWindow", "清空"))
        self.pushButtonmodify.setText(_translate("MainWindow", "添加/修改"))
        self.pushButtondelete.setText(_translate("MainWindow", "删除"))
        self.pushButtonquery.setText(_translate("MainWindow", "查询"))
        self.tableWidget.setSortingEnabled(False)
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "名称"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "账号"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "密码"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "备注"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.submenu1.setTitle(_translate("MainWindow", "导入"))
        self.submenu2.setTitle(_translate("MainWindow", "导出"))
        self.menu_2.setTitle(_translate("MainWindow", "设置"))
        self.importtxt.setText(_translate("MainWindow", "txt"))
        self.exporttxt.setText(_translate("MainWindow", "txt"))
        self.exportxls.setText(_translate("MainWindow", "xls(x)"))
        self.importxls.setText(_translate("MainWindow", "xls(x)"))
        self.actiontest.setText(_translate("MainWindow", "test"))
        self.actionSetAutoOpen.setText(_translate("MainWindow", "开机自启动"))
        self.actionRegister.setText(_translate("MainWindow", "将显示界面选项注册至鼠标右键"))
        self.actionExit.setText(_translate("MainWindow", "退出"))
