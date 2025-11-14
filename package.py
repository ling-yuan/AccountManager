import os
import shutil
from PyInstaller.__main__ import run

# 判断dist文件夹下是否有Account Manager文件夹
if os.path.exists("dist/Account Manager"):
    shutil.rmtree("dist/Account Manager")

# 打包 并添加版本信息 file_version_info.txt
# pyinstaller -D -w main.py -i./img/icon.ico -nAccount Manager
run(
    [
        "-D",  # 多文件
        "-w",  # 无命令行窗口
        "main.py",  # 主文件
        "-i./AccountManager/window/resource/icon.ico",
        "-nAccount Manager",
        "--version-file=file_version_info.txt",
    ]
)
