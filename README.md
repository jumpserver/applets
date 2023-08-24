# JumpServer Remote Applets DEMO

## 开发说明

Applet 是一个包含 python 脚本的目录：
```
├── app.py
├── build.yml
├── common.py
├── icon.png
├── main.py
├── manifest.yml
├── platform.yml
├── README.md
├── patch.yml
└── setup.yml
```

各文件介绍：
- app.py 是 applet 的主程序
- build.yml 是 applet 依赖的外部部署文件，比如安装包 msi、exe
- common.py 是 applet 的通用模块
- icon.png 是 applet 的图标
- main.py 是 applet 启动入口文件
- manifest.yml 是 applet 的元数据，导入到 JumpServer 中会使用
- platform.yml 是 applet 配套平台的设置，安装时自动创建该平台
- README.md 是 applet 的说明文档
- patch.yml 是 applet 的补丁文件，一些应用需要额外的初始化操作，比如激活、修改配置文件等可以先通过补丁文件 msi、exe 实现
- setup.yml 是描述 applet 如何在 发布机上部署安装的文件

### 入口 app.py

app.py 是 applet 的主程序，定义了 app 启用时的启动命令、参数、自动化操作等。比如需要处理账号密码的填写，页面按钮的点击等，可以在这里定义。

### 依赖 build.yml

build.yml 定义了 applet 依赖的外部部署文件，比如安装包 msi、exe。在构建应用时，会自动下载 build.yml 中定义的文件。

```
source_url: https://jms-pkg.oss-cn-beijing.aliyuncs.com/windows-pkgs/mysql-workbench-community-8.0.31-winx64.msi
source_md5: d3641c423f00f0aa6f258ff116778e1b
```

### 通用模块 common.py

common.py 是 applet 的通用模块，与 JumpServer 数据相关的抽象。

### 元数据 manifest.yml

manifest.yml 定义了 applet 的元数据，如名称、作者、版本、支持的协议。

```
name: mysql_workbench8 （required）
display_name: MySQL Workbench8
comment: A tool for working with MySQL, to execute SQL and design tables (required）
version: 0.1 (required）
exec_type: python (reserved，暂未使用)
author: Eric (required）
type: general (required）
update_policy: none (暂未使用)
tags: (required）
  - database
protocols: (required）
  - mysql
```

字段说明：
- name：名称最好是字母数字，不要包含特殊字符
- protocols：此 applet 脚本支持的协议
- tags：一些标签
- type: 主要是 general 或 web

### 安装条件 setup.yml

setup.yml 定义了 applet 程序的安装方式，如果定义了 build.yml，会自动下载 build.yml 中定义的文件然后重命名为 source 定义的名称。
```
type: msi # exe, zip, manual
source: mysql-workbench-community-8.0.31-winx64.msi
arguments:
  - /qn
  - /norestart
destination: C:\Program Files\MySQL\MySQL Workbench 8.0 CE
program: C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe
md5: d628190252133c06dad399657666974a

```
字段说明：
- type 是软件安装的方式
    - msi 安装软件
    - exe 安装软件
    - zip 解压安装方式
    - manual 手动安装方式
- source 是软件下载地址
- arguments msi 或者 exe 安装程序需要的参数，使用静默安装
- destination 程序安装目录地址
- program 具体的软件地址
- md5 是 program 软件的 md5 值，主要用于校验安装是否成功

如果选择 manual 的方式，source等保持为空，可不校验 MD5 值，需要手动登录 applet host 发布机上安装软件

### 脚本执行 main.py

main.py 是 python 脚本主程序。JumpServer 的 Remoteapp 程序 tinker 将通过调用 `python main.py $base64_json_data` 的方式执行。

base64_json_data 是 JSON 数据进行 base64 之后的字符串，包含资产、账号等认证信息。数据格式大致如下，依据 api 变化做相应调整：

```
{
  "app_name": "mysql_workbench8",
  "protocol": "mysql",
  "user": {
    "id": "2647CA35-5CAD-4DDF-8A88-6BD88F39BB30",
    "name": "Administrator",
    "username": "admin"
  },
  "asset": {
    "asset_id": "46EE5F50-F1C1-468C-97EE-560E3436754C",
    "asset_name": "test_mysql",
    "address": "192.168.1.1",
    "protocols": [
      {
        "id": 2,
        "name": "mysql",
        "port": 3306
      }
    ]
  },
  "account": {
    "account_id": "9D5585DE-5132-458C-AABE-89A83C112A83",
    "username": "root",
    "secret": "test"
  },
  "platform": {
    "charset": "UTF-8"
  }
}
```

base64_json_data 的具体获取可以[参考文档](https://bbs.fit2cloud.com/t/topic/339)

### 自定义平台和协议 platform.yml
可参考 [查看这个](https://github.com/jumpserver/applets/blob/master/mysql_workbench8/platform.yml)，这个文件不是必须的，需要配套平台或者自定义协议时需要

```
# 该文件是添加 applet 时，同步添加的 platform
# 该 platform 必须是 custom 类别，支持自定义协议 和 自定义字段
#
# 平台名称: 需要唯一，所以开发者取名时要多注意 
name: MySQLWorkbench
# 类别: 必须是 custom
category: custom
# 类型: 可以自定义
type: DB
# 备注: 平台备注
comment: 自定义 MySQLWorkbench
# 支持的协议: 这个很关键，这里支持自定义协议
protocols:
  - name: mysqlworkbench
    port: 0
    primary: true
# 自定义字段：设置这个后，添加资产时，需要填写，applet 开发时，会在 资产的 info 中体现
custom_fields:
  - name: db_name   # 字段名，存数据库时使用
    label: "{{ 'DB Name' | trans }}"    # 字段标签， 添加时，在页面上显示
    default: mysql  # 默认值
    type: str       # 类型，支持 str, int, bool, choice, text, list 类型，如果是 choice，需要有 choices 字段
    help_text: ”{{ 'Please select a database' | trans }}“   # 帮助说明内容
  
  - name: ip
    label: IP
    type: str
    default: 127.0.0.1

  - name: port
    label: "{{ 'Port' | trans }}"
    type: int
    default: 3306 

  - name: username
    label: "{{ 'Username' | trans }}"
    type: str
    default: root

  - name: password
    label: "{{ 'Password' | trans }}"
    type: str
  
i18n:
  DB Name:
    zh: 数据库
    ja: データベース
  Please select a database:
    zh: 请选择数据库
    ja: データベースを選択してください
  Port:
    zh: 端口
    ja: ポート
  Username:
    zh: 用户名
    ja: ユーザー名
  Password:
    zh: 密码
    ja: パスワード

```











