import sys
import os
import os.path
import subprocess
from subprocess import CREATE_NO_WINDOW
import locale
import time
import json
import base64

from base.config import CONFIG

__all__ = ['Dict2Obj', 'block_input', 'unblock_input', 'decode_content', 'notify_err_message', 'check_pid_alive',
           'process_exists', 'get_manifest_data', 'read_app_manifest', 'convert_dict_to_base64',
           'convert_base64_to_dict', 'DictObj', 'User', 'Specific', 'Category', 'Protocol', 'Asset', 'LabelValue',
           'Account', 'Platform', 'Manifest']

_blockInput = None
_messageBox = None


class Dict2Obj(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self.__wrap(value))

    def __wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self.__wrap(v) for v in value])
        else:
            return Dict2Obj(value) if isinstance(value, dict) else value


if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    import win32ui

    # import win32con

    _messageBox = win32ui.MessageBox

    _blockInput = ctypes.windll.user32.BlockInput
    _blockInput.argtypes = [wintypes.BOOL]
    _blockInput.restype = wintypes.BOOL


def block_input():
    if _blockInput:
        _blockInput(True)


def unblock_input():
    if _blockInput:
        _blockInput(False)


def decode_content(content: bytes) -> str:
    for encoding_name in ['utf-8', 'gbk', 'gb2312']:
        try:
            return content.decode(encoding_name)
        except Exception as e:
            pass  # print(encoding_name, e)
    encoding_name = locale.getpreferredencoding()
    return content.decode(encoding_name)


def notify_err_message(msg):
    # logger.warning((msg, 'Error'))
    # from win32ui import Response
    # Response.Write("<script type=\"text/javascript\">alert(" + es.Message + ");</script> "); 
    if _messageBox:
        _messageBox(msg, 'Error')


def check_pid_alive(pid) -> bool:
    # tasklist  /fi "PID eq 508" /fo csv
    # '"映像名称","PID","会话名      ","会话#   ","内存使用 "\r\n"wininit.exe","508","Services","0","6,920 K"\r\n'
    try:
        csv_ret = subprocess.check_output(["tasklist", "/fi", f'PID eq {pid}', "/fo", "csv"],
                                          creationflags=CREATE_NO_WINDOW)
        content = decode_content(csv_ret)
        content_list = content.strip().split("\r\n")
        if len(content_list) != 2:
            time.sleep(2)
            return False
        ret_pid = content_list[1].split(",")[1].strip('"')
        return str(pid) == ret_pid
    except Exception as e:
        return False


def process_exists(process_name: str):
    # import psutil
    # target = process_name.lower()
    # for i in psutil.process_iter():
    #     if i.name().lower() == target:
    #         return True, i.name()
    # return False, ''
    call = 'TASKLIST', '/FI', 'ImageName eq %s' % process_name
    output = subprocess.check_output(call)
    output = decode_content(output)
    last_line = output.strip().split('\r\n')[-1]
    return process_name.lower() in last_line.lower(), last_line


class DictObj:
    def __init__(self, in_dict: dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
                setattr(self, key, DictObj(val) if isinstance(val, dict) else val)


class User(DictObj):
    id: str
    name: str
    username: str


class Specific(DictObj):
    # web
    autofill: str
    username_selector: str
    password_selector: str
    submit_selector: str
    script: list

    # database
    db_name: str


class Category(DictObj):
    value: str
    label: str


class Protocol(DictObj):
    id: str
    name: str
    port: int


class Asset(DictObj):
    id: str
    name: str
    address: str
    protocols: Protocol
    category: Category
    spec_info: Specific

    def get_protocol_port(self, protocol):
        for item in self.protocols:
            if item.name == protocol:
                return item.port
        return None


class LabelValue(DictObj):
    label: str
    value: str


class Account(DictObj):
    id: str
    name: str
    username: str
    secret: str
    secret_type: LabelValue


class Platform(DictObj):
    charset: str
    name: str
    charset: LabelValue
    type: LabelValue


class Manifest(DictObj):
    name: str
    version: str
    path: str
    exec_type: str
    connect_type: str
    protocols: str


def get_manifest_data() -> dict:
    current_dir = os.path.dirname(__file__)
    manifest_file = os.path.join(current_dir, 'manifest.json')
    try:
        with open(manifest_file, "r", encoding='utf8') as f:
            return json.load(f)
    except Exception as e:
        print(e)
    return {}


def read_app_manifest(app_dir) -> dict:
    main_json_file = os.path.join(app_dir, "manifest.json")
    if not os.path.exists(main_json_file):
        return {}
    with open(main_json_file, 'r', encoding='utf8') as f:
        return json.load(f)


def convert_dict_to_base64(data: dict) -> str:
    try:
        data = json.dumps(data)
        return base64.encodebytes(data.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(e)
    return ''


def convert_base64_to_dict(base64_str: str) -> dict:
    try:
        data_json = base64.decodebytes(base64_str.encode('utf-8')).decode('utf-8')
        return json.loads(data_json)
    except Exception as e:
        print(e)
    return {}
