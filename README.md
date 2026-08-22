# AccountManager
PyQt 账号密码管理软件。

## 功能
- 支持多分组管理（标签页）：可新增、重命名、删除分组
- 支持账号记录的`添加/修改/删除/搜索`
- 支持最小化到系统托盘
- 本地持久化存储使用 SQLite
- 支持分组数据导入导出（`.amg` / `.json`）
- 支持 WebDAV 备份与恢复（上传前自动加密）

## 说明
- 当前版本仅支持 SQLite 存储
- 导入会覆盖当前全部分组与记录，请先做好备份
- WebDAV 恢复成功后会立即刷新到界面，无需重启应用

## 截图

### 主界面
![截图1](https://github.com/ling-yuan/AccountManager/blob/main/img_readme/mainWindow.png)

### 设置
![截图2](https://github.com/ling-yuan/AccountManager/blob/main/img_readme/setting.png)

### 系统托盘
![截图3](https://github.com/ling-yuan/AccountManager/blob/main/img_readme/systemTray.png)
