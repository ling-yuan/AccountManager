from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFileInfo, QCoreApplication, Qt
from PyQt5.QtNetwork import QLocalSocket, QLocalServer, QAbstractSocket


class SingleApplication(QApplication):
    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self.main_window = None
        self.local_server = None
        self.is_running = False
        # 取应用程序名作为LocalServer的名字，也可以自己取一个str，不要和别的软件重复
        self.server_name = QFileInfo(QCoreApplication.applicationFilePath()).fileName()
        print(self.server_name)
        self.init_local_connection()

    def init_local_connection(self):
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(500):
            self.is_running = True
        else:
            self.is_running = False
            self.local_server = QLocalServer()
            self.local_server.newConnection.connect(self.new_local_connection)
            # 监听，如果监听失败，可能是之前程序崩溃时残留进程服务导致的，移除残留进程
            if not self.local_server.listen(self.server_name):
                if self.local_server.serverError() == QAbstractSocket.AddressInUseError:
                    QLocalServer.removeServer(self.server_name)
                    self.local_server.listen(self.server_name)

    def new_local_connection(self):
        if self.main_window is not None:
            self.main_window.raise_()
            self.main_window.activateWindow()
            self.main_window.setWindowState((self.main_window.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
            self.main_window.show()
