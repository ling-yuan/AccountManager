import os
import sys
from PyQt5.QtWidgets import QApplication
from tools.window import MyMainWindow


if __name__ == "__main__":
    # 获取当前文件夹路径
    p = sys.argv[0].rsplit("\\", 1)[0]
    # 设置当前文件夹路径为工作目录
    os.chdir(p)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    myWin = MyMainWindow(app=app, file_path=sys.argv[0])

    # 启动参数中如果不指定是否打开窗口，则默认打开
    if "--no-window" not in sys.argv:
        myWin.show()

    sys.exit(app.exec_())
