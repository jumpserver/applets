# import sys
# import traceback

__all__ = ['ApiInputException', 'AppletException', 'ApiOutputException']


class BaseException(Exception):
    map = dict()

    def __init__(self, code, msg=None):
        if not code in self.code__msg:
            # logger.error(sys._getframe().f_back.f_code.co_name)
            raise Exception(f'输入的异常代码code: {code} \
                            不在约定范围内: {self.__class__.__name__} \
                                约定的code请参考: {self.code__msg}')
        self.code = code
        self.msg = msg or self.code__msg.get(code, '')


class ApiInputException(BaseException):
    code__msg = {101: '输入数据不合法', }


class ApiOutputException(BaseException):
    code__msg = {201: '输出无效', }


class AppletException(BaseException):
    code__msg = {401: '工作状态异常', }


class ConfigException(BaseException):
    code__msg = {501: '配置文件异常', }


if __name__ == '__main__':
    ape = AppletException()
    ape = AppletException(201)
    ape = ApiInputException(102, 'name is required')
    print(ape)
    print(ape.code)
    print(ape.msg)
    print(ape.__dict__)
