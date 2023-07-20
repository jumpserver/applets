import time

from enum import Enum
from subprocess import CREATE_NO_WINDOW

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from common import Asset, User, Account, Step
from common import BaseApplication
from common import notify_err_message, block_input, unblock_input


class Command(Enum):
    TYPE = 'type'
    CLICK = 'click'


commands_func_maps = {
    Command.CLICK: lambda e, v: e.click(),
    Command.TYPE: lambda e, v: e.send_keys(v),
}


class StepAction:
    methods_map = {
        "ID": By.ID,
        "CLASS_NAME": By.CLASS_NAME,
        "XPATH": By.XPATH
    }

    def __init__(self, target='', value='', command=Command.TYPE, **kwargs):
        self.target = target
        self.value = value
        self.command = command

    def execute(self, driver: webdriver.Chrome) -> bool:
        wait = WebDriverWait(driver, 60)
        target_name, target_value = self.target.split("=", 1)
        by_name = self.methods_map.get(target_name.upper(), By.ID)
        ele = wait.until(EC.element_to_be_clickable((by_name, target_value)))
        if not ele:
            return False
        commands_func_maps[self.command](ele, self.value)
        return True


    @staticmethod
    def _execute_command_type(ele, value):
        ele.send_keys(value)


def execute_action(driver: webdriver.Chrome, step: StepAction) -> bool:
    try:
        return step.execute(driver)
    except Exception as e:
        print(e)
        notify_err_message(str(e))
        return False


class WebAPP(object):

    def __init__(
            self, app_name: str = '', user: User = None,
            asset: Asset = None, account: Account = None, **kwargs
    ):
        self.app_name = app_name
        self.user = user
        self.asset = asset
        self.account = account
        self._steps = self._get_steps()

    def _get_steps(self) -> list:
        steps = [
            Step({
                "step": 1,
                "value": self.account.username,
                "target": 'name=username',
                "command": Command.TYPE
            }),
            Step({
                "step": 2,
                "value": self.account.secret,
                "target": 'name=password',
                "command": Command.TYPE
            }),
            Step({
                "step": 3,
                "value": "",
                "target": 'xpath=//*[@id="login-form"]/div[5]/button',
                "command": Command.CLICK
            })
        ]
        return steps

    def execute(self, driver: webdriver.Chrome) -> bool:
        for step in self._steps:
            action = StepAction(target=step.target, value=step.value, command=step.command)
            ret = execute_action(driver, action)
            if not ret:
                unblock_input()
                notify_err_message(f"执行失败: target: {action.target} command: {action.command}")
                block_input()
                return False
        return True


class AppletApplication(BaseApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = None
        self.app = WebAPP(
            app_name=self.app_name, user=self.user, account=self.account, asset=self.asset
        )
        self._chrome_options = self.set_chrome_driver_options()

    @staticmethod
    def set_chrome_driver_options():
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # 禁用 扩展
        options.add_argument("--disable-extensions")
        # 忽略证书错误相关
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--allow-running-insecure-content')

        # 禁用开发者工具
        options.add_argument("--disable-dev-tools")
        # 禁用 密码管理器弹窗
        prefs = {"credentials_enable_service": False,
                 "profile.password_manager_enabled": False}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        return options

    def run(self):
        service = Service()
        #  driver 的 console 终端框不显示
        service.creationflags = CREATE_NO_WINDOW
        self.driver = webdriver.Chrome(options=self._chrome_options, service=service)
        self.driver.implicitly_wait(30)
        if '/ui' not in self.app.asset.address:
            if self.app.asset.address.endswith('/'):
              self.app.asset.address = self.app.asset.address + 'ui/'
            else:
              self.app.asset.address = self.app.asset.address + '/ui/'
        self.driver.get(self.app.asset.address)
        ok = self.app.execute(self.driver)
        if not ok:
            print("执行失败")
        self.driver.maximize_window()

    def wait(self):
        disconnected_msg = "Unable to evaluate script: disconnected: not connected to DevTools\n"
        closed_msg = "Unable to evaluate script: no such window: target window already closed"

        while True:
            time.sleep(5)
            logs = self.driver.get_log('driver')
            if len(logs) == 0:
                continue
            ret = logs[-1]
            if isinstance(ret, dict):
                message = ret.get('message', '')
                if disconnected_msg in message or closed_msg in message:
                    break
                print("ret: ", ret)
        self.close()

    def close(self):
        if self.driver:
            try:
                # quit 退出全部打开的窗口
                self.driver.quit()
            except Exception as e:
                print(e)
