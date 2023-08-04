# !/usr/bin/env python
# -*- coding: utf-8 -*-
import contextlib
import os
import shutil
import zipfile
import os.path
import yaml
import json

applets_index = []


@contextlib.contextmanager
def change_dir(path):
    old_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_path)


def read_applet_config(applet_path) -> dict:
    config_path = os.path.join(applet_path, 'manifest.yml')
    if not os.path.exists(config_path):
        raise Exception(f'{applet_path} not exist manifest.yml')
    with open(config_path, 'r', encoding='utf8') as f:
        return yaml.safe_load(f)


def zip_applet(applet_path, dst_dir):
    dir_path = os.path.dirname(applet_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(f'creat zip build folder: {dst_dir}')
    with change_dir(dir_path):

        app_config = read_applet_config(applet_path)
        if app_config.get("name"):
            applets_index.append(app_config)
        applet_name = os.path.basename(applet_path)
        zip_name = os.path.join(dst_dir, applet_name + '.zip')

        filelist = []
        if os.path.isfile(applet_path):
            filelist.append(applet_path)
        else:
            for root, dirs, files in os.walk(applet_name):
                for name in files:
                    filelist.append(os.path.join(root, name))
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
            for tar in filelist:
                zf.write(tar, tar)
        print(f'zip  {applet_name} applet to {zip_name} success')


ignore_dirs = [
    'dist', 'node_modules', 'build', 'venv', '.git', '.github', '.idea', '.vscode',
    '__pycache__', 'demo', 'pip_packages', 'utils', 'tests', 'log', 'base', 'tmp',
]


def zip_all_applets(project_path):
    applets_dir = []
    for file in os.listdir(project_path):
        applet_path = os.path.join(project_path, file)
        if not os.path.isdir(applet_path):
            continue
        if file.startswith(".") or file in ignore_dirs:
            continue
        applets_dir.append(applet_path)
    dist_dir = os.path.join(project_path, 'build')
    base_dir = os.path.join(project_path, 'base')
    for applet in applets_dir:
        shutil.copytree(base_dir, os.path.join(applet, 'base'), dirs_exist_ok=True)
        zip_applet(applet, dist_dir)
        shutil.rmtree(os.path.join(applet, 'base'))


def write_index_json(project_path):
    dst_dir = os.path.join(project_path, 'build')
    with change_dir(dst_dir):
        with open('index.json', 'w', encoding='utf8') as f:
            json.dump(applets_index, f, ensure_ascii=False, indent=4)


def run():
    root_path = os.path.dirname(os.path.abspath(__file__))
    zip_all_applets(root_path)
    write_index_json(root_path)


if __name__ == '__main__':
    run()
