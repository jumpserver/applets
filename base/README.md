# Applet base - applet基础类

## 阶段性封装进度

    - yml配置文件初始化
    - 入参校验：支持子类定义自己的校验schema
    - app基本的初始化
    - 增加上下文管理 强化对代理应用的管理 简化调用
    - 留有applet运行状态钩子：根据需要向上层调用方返回目前运行状态
    - 封装Exception：增加code等字段 方便上层调用方针对性处理异常或拦截触发修改运行状态
    - 更新了build.py打包脚本: 自动打包基类 子类引用方式不变（未经部署全流程测试 如遇问题请后续适时调整）


## 现有问题

    - 两个示例applet: mysql_workbench8_v2、dbeaver_v2在手头现有两台windows环境中测试 一台完美运行 一台可正常拉起应用但无法连接数据库分别有不同报错 未来得及定位问题


## 使用说明

    * 编写新的applet请参考mysql_workbench8_v2目录下的代码示例
    * applet子类需继承: from base import BaseApplication
    * build.py脚本打包时会自动打包base目录下的代码到applet目录中


> 备注：此为阶段性封装 希望有帮助 未尽事宜请再修缮
