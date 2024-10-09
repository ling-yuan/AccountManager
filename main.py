import os
import sys
from tools.window import MyMainWindow
from tools.singleapplication import SingleApplication


if __name__ == "__main__":
    # 获取当前文件夹路径
    p = sys.argv[0].rsplit("\\", 1)[0]
    # 设置当前文件夹路径为工作目录
    os.chdir(p)

    app = SingleApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    if not app.is_running:
        myWin = MyMainWindow(app=app, file_path=sys.argv[0])
        # 启动参数中如果不指定是否打开窗口，则默认打开
        if "--no-window" not in sys.argv:
            myWin.show()
        app.main_window = myWin
        sys.exit(app.exec_())
    else:
        app.quit()
        sys.exit()
