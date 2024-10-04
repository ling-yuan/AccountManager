import os
import shutil
from PyInstaller.__main__ import run

# 判断dist文件夹下是否有Account Manager文件夹
if os.path.exists("dist/Account Manager"):
    shutil.rmtree("dist/Account Manager")

# 打包
run(
    [
        "-D",
        "-w",
        "main.py",
        "-i./img/icon.ico",
        "-nAccount Manager",
    ]
)


# 判断dist/Account Manager下是否有img文件夹
if not os.path.exists("dist/Account Manager/img"):
    os.makedirs("dist/Account Manager/img")
else:
    shutil.rmtree("dist/Account Manager/img")

# 将img文件夹下所有png复制到dist/Account Manager下
for file in os.listdir("img"):
    if file.endswith(".png"):
        shutil.copy2("img/" + file, "dist/Account Manager/img/" + file)

# 判断dist/Account Manager下是否有info文件夹
if not os.path.exists("dist/Account Manager/info"):
    os.makedirs("dist/Account Manager/info")
else:
    shutil.rmtree("dist/Account Manager/info")

# 将info文件夹下所有json复制到dist/Account Manager下
for file in os.listdir("info"):
    if file.endswith(".json"):
        shutil.copy2("info/" + file, "dist/Account Manager/info/" + file)
