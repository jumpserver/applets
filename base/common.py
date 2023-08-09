import abc
import os
import sys
import time
import functools
import enum
import yaml
from urllib import parse

if sys.platform == 'win32':
    from pywinauto import Application
    from pywinauto.timings import TimeoutError
    import win32api
    import pywintypes

from base.config import CONFIG
from base.utils import Dict2Obj, check_pid_alive, block_input, unblock_input, \
    convert_base64_to_dict, logger
from base.utils.exceptions import ApiInputException, AppletException, ConfigException
from base.utils.schema import Schema, SchemaError


class _Status(enum.Enum):
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2
    ABNORMAL = 3


# 调用入口接口数据格式校验策略
kwargs_schema = {}


class CatchException(type):

    def __new__(cls, name, bases, attr__map):
        for m in attr__map:
            if hasattr(attr__map[m], '__call__'):
                attr__map[m] = cls.wrap(attr__map[m])
        return type.__new__(cls, name, bases, attr__map)

    @staticmethod
    def wrap(f):
        @functools.wraps(f)
        def func(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                print(f'{f.__qualname__}, {e}')
                # logger.exception(f'{f.__qualname__}, {e}')
                return 1, f.__qualname__, str(e)
                raise Exception(f'{f.__name__}, {e}')
        return func


class _Config(metaclass=CatchException):

    def __init__(self, *args, **kwargs):
        for file in CONFIG.CONFIG_FILES:
            ret = self.load_config(os.path.join(CONFIG.APPDIR, file))
            setattr(self, file.split('.')[0], ret)

    @classmethod
    def load_config(cls, file):
        try:
            return cls.load_yml(file)
        except FileNotFoundError as error:
            logger.exception(error)
            raise ConfigException(
                101, f'Config file not found "{file}": {error}') from error
        except Exception as error:
            logger.exception(error)
            raise ConfigException(
                101, f'Load config file "{file}" error: {error}') from error

    @staticmethod
    def load_yml(yml_file: str) -> dict:
        if not os.path.exists(yml_file):
            raise FileNotFoundError(f'Config file: {yml_file} not exist')
        with open(yml_file, 'r', encoding='utf8') as f:
            return yaml.safe_load(f)


class BaseApplication(abc.ABC):
    app: Application = None
    pid: int = None
    _status: _Status = _Status.STOPPED
    config: Dict2Obj = Dict2Obj({})
    kwargs_validator = None

    def __init__(self, *args, kwargs_str=None, **kwargs):
        if not isinstance(kwargs_str, str):
            raise ApiInputException(
                101, f'{self.__class__.__name__} init kwargs invalid')
        try:
            self.kwargs = convert_base64_to_dict(kwargs_str)
        except Exception as error:
            # logger.exception(error)
            raise ApiInputException(
                101, f'{self.__class__.__name__} init kwargs invalid: {error}') from error
        if kwargs_schema:
            self.kwargs_validator = Schema(kwargs_schema, ignore_extra_keys=True)
        self.config = _Config()
        self.app_image_name = self.config.setup.get('program').split('\\')[-1]
        self.app_name = self.config.setup.get('program').split('\\')[-1]
        self.__validate()
        self.__init_app()
        self.__start_app()

    status = property(lambda self: self._status)

    @status.setter
    def status(self, value):
        if value not in _Status:
            raise ValueError(f'Invalid value for status: {value}')
        if value == self._status:
            return
        """
        do something... 比如状态改变时发送状态信号供上层调用方感知
        """
        self._status = value

    def __validate(self):
        if self.kwargs_validator:
            try:
                self.kwargs_validator.validate(self.kwargs)
            except SchemaError as error:
                # logger.exception(error)
                raise ApiInputException(
                    101, f'{self.app_name} init kwargs invalid: {error}') from error

        self.kwargs = Dict2Obj(self.kwargs)
        self.user = self.kwargs.user
        self.asset = self.kwargs.asset

        for protocol in self.asset.protocols:
            if protocol.name == self.kwargs.protocol:
                self.protocol = protocol
                self.port = protocol.port
                break
        self.account = self.kwargs.account
        self.platform = self.kwargs.platform

        self.username = self.account.username
        self.account.secret = parse.quote(self.account.secret)
        self.password = parse.quote(self.account.secret)
        self.host = self.asset.address
        self.db = self.asset.spec_info.db_name

    def __init_app(self):
        self.app = Application(backend='uia')

    def __start_app(self):
        try:
            self.app.start(self.config.setup.get('program'))
        except pywintypes.error as error:
            logger.exception(error)
        if self.app.process:
            self.pid = self.app.process
            self.status = _Status.RUNNING
            # self.window = self.app.window(title=self.setup.get('title'),
            # auto_id=self.setup.get('auto_id'), control_type=self.setup.get('control_type'))

    def start(self):
        try:
            if not CONFIG.DEBUG:
                block_input()
            self.run()
            if not CONFIG.DEBUG:
                unblock_input()
            self.__heath_check()
        except TimeoutError as error:
            logger.exception(error)
            raise AppletException(
                401, f'{self.app_name} run error: {error}') from error
        except Exception as error:
            logger.exception(error)
            raise AppletException(
                401, f'{self.app_name} run error: {error}') from error
        else:
            logger.info(f'{self.app_name} run success')
            self.status = _Status.STOPPED

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError('run')

    @property
    def win_user_name(self):
        return win32api.GetUserName()

    def __enter__(self):
        if self.status != _Status.RUNNING:
            logger.info(f'{self.app_name} failed to start, status: {self.status}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.status == _Status.RUNNING:
            logger.info(f'{self.app_name} failed to stop, status: {self.status}')
            self.app.kill()

    def __del__(self):
        self.status = _Status.STOPPED
        # 清理前先关闭所代理的应用
        self.app.kill()

    def __heath_check(self):
        while True:
            time.sleep(5)
            ok = check_pid_alive(self.pid)
            logger.info(f'Heath check: {self.app_name}, status: {ok}')
            if not ok:
                self.status = _Status.STOPPED
                logger.info(
                    f'Heath check: {self.app_name} is stopped')
                break
            logger.info(f'Heath check: {self.app_name} is running')
        self.status = _Status.ABNORMAL


if __name__ == '__main__':
    pass
