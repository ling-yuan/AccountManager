import sys
from PyQt5.QtWidgets import QApplication
from tools.window import MyMainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    myWin = MyMainWindow(app=app)
    myWin.show()
    sys.exit(app.exec_())
