import sys
from PyQt5.QtWidgets import QApplication
from tools.window import MyMainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    myWin = MyMainWindow(app=app)

    # 启动参数中如果不指定是否打开窗口，则默认打开
    if "--no-window" not in sys.argv:
        myWin.show()

    sys.exit(app.exec_())
