from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
)

from . import Image_rc


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, MainWindow, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.mainWindow = MainWindow
        self.__init_gui__()
        self.__init_slot__()
        self.show()

    def __init_gui__(self):
        self.setIcon(QIcon(":/resource/resource/safe.png"))
        self.setToolTip("密码管理器")
        self.trayMenu = QMenu()
        self.trayMenu.addAction("显示", self.mainWindow.show)
        self.trayMenu.addAction("退出", self.mainWindow.app.quit)
        self.setContextMenu(self.trayMenu)

    def __init_slot__(self):
        # 绑定双击事件
        self.activated.connect(self.click_event)

    def click_event(self, event):
        # 鼠标左键点击事件
        if event == QSystemTrayIcon.Trigger:
            self.mainWindow.show()
        # 双击事件
        if event == QSystemTrayIcon.DoubleClick:
            self.mainWindow.show()
        # 鼠标中键点击事件
        elif event == QSystemTrayIcon.MiddleClick:
            self.mainWindow.app.quit()
