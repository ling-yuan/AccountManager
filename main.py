import os
import sys
from AccountManager.window.main_window import MainWindow
from AccountManager.single_app import SingleApplication


if __name__ == "__main__":
    # 获取当前文件夹路径
    p = sys.argv[0].rsplit("\\", 1)[0]
    # 设置当前文件夹路径为工作目录
    os.chdir(p)

    app = SingleApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    if not app.is_running:
        myWin = MainWindow(app=app)
        # 启动参数中如果不指定是否打开窗口，则默认打开
        if "--no-window" not in sys.argv:
            myWin.show()
        app.main_window = myWin
        sys.exit(app.exec_())
    else:
        app.quit()
        sys.exit()
