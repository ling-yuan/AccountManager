import os
import shutil
import subprocess
import sys

APP_NAME = "Account Manager"
APP_VERSION = "2.2.0"
FILE_VERSION = f"{APP_VERSION}.0"
COMPANY_NAME = "BaiShi"
COPYRIGHT = "Copyright (C) 2026"

# 清理之前的构建
for dir_name in ["build", "dist", ".nuitka-cache"]:
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
    f"--output-filename={APP_NAME}",  # 输出文件名
    f"--file-version={FILE_VERSION}",  # 文件版本
    f"--product-version={FILE_VERSION}",  # 产品版本
    f"--product-name={APP_NAME}",  # 产品名称
    f"--company-name={COMPANY_NAME}",  # 公司名称
    f"--file-description={APP_NAME} {APP_VERSION}",  # 文件描述
    f"--copyright={COPYRIGHT}",  # 版权信息
    "--plugin-enable=pyqt5",  # 启用PyQt5插件
    "--include-module=ctypes",  # 强制包含 ctypes，避免运行期硬导入失败
    "--include-module=_ctypes",  # 强制包含 _ctypes 扩展模块
    "--include-module=ctypes.wintypes",  # 强制包含 Windows ctypes 辅助模块
    "--onefile",  # 打包为单个文件
    "--assume-yes-for-downloads",  # 自动下载依赖组件
    "--remove-output",  # 覆盖旧输出
]

# 显式打包 libffi，规避某些环境下 _ctypes 动态库缺失
dll_dir = os.path.join(sys.base_prefix, "DLLs")
for dll_name in ["libffi-8.dll", "libffi-7.dll"]:
    dll_path = os.path.join(dll_dir, dll_name)
    if os.path.exists(dll_path):
        base_args.append(f"--include-data-files={dll_path}={dll_name}")
        print(f"包含动态库: {dll_name}")
        break

# 合并所有参数
nuitka_cmd = base_args + ["main.py"]

# 执行打包命令
print("开始使用Nuitka打包...")
print("打包命令:", " ".join(nuitka_cmd))

try:
    result = subprocess.run(nuitka_cmd, check=True)
    print("打包成功！")

    # Nuitka的实际输出路径是 dist/main.dist/Account Manager.exe
    output_file = os.path.join("dist", f"{APP_NAME}.exe")
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
