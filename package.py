import os
import shutil
import subprocess
import sys

# 清理之前的构建
for dir_name in ["build", "dist"]:
    if os.path.exists(dir_name):
        print(f"清理 {dir_name} 目录...")
        shutil.rmtree(dir_name)

# 检查Nuitka是否已安装
try:
    import nuitka

    print("已安装 Nuitka")
except ImportError:
    print("正在安装 Nuitka...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka"])
    import nuitka

    print("已安装 Nuitka")


# 基本打包参数
base_args = [
    sys.executable,
    "-m",
    "nuitka",
    "--windows-console-mode=disable",  # 禁用控制台窗口
    "--windows-icon-from-ico=./AccountManager/window/resource/icon.ico",  # 图标
    "--output-dir=dist",  # 输出目录
    "--output-filename=Account Manager",  # 输出文件名
    "--file-version=2.1.0.0",  # 文件版本
    "--product-version=2.1.0.0",  # 产品版本
    "--product-name=Account Manager",  # 产品名称
    "--company-name=BaiShi",  # 公司名称
    "--file-description=Account Manager",  # 文件描述
    "--copyright=Copyright (C) 2025",  # 版权信息
    "--plugin-enable=pyqt5",  # 启用PyQt5插件
    "--onefile",  # 打包为单个文件
]

# 合并所有参数
nuitka_cmd = base_args + ["main.py"]

# 执行打包命令
print("开始使用Nuitka打包...")
print("打包命令:", " ".join(nuitka_cmd))

try:
    result = subprocess.run(nuitka_cmd, check=True)
    print("打包成功！")

    # Nuitka的实际输出路径是 dist/main.dist/Account Manager.exe
    output_file = os.path.join("dist", "Account Manager.exe")
    print(f"输出文件位于: {os.path.abspath(output_file)}")

    # 检查输出文件是否存在
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"文件大小: {file_size:.2f} MB")
    else:
        print("警告: 输出文件未找到")

except subprocess.CalledProcessError as e:
    print("打包失败！")
    print(f"错误代码: {e.returncode}")
    sys.exit(1)
except Exception as e:
    print("打包过程中发生异常:", str(e))
    sys.exit(1)
