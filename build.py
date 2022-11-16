# !/usr/bin/env python
# -*- coding: utf-8 -*-
import contextlib
import os
import zipfile
import os.path


@contextlib.contextmanager
def change_dir(path):
    old_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_path)


def zip_applet(applet_path, dst_dir):
    dir_path = os.path.dirname(applet_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(f'creat zip build folder: {dst_dir}')
    with change_dir(dir_path):
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


ignore_dirs = ['dist', 'node_modules', 'build', 'venv', '.git', '.idea', '.vscode',
               '__pycache__', 'demo', 'pip_packages']


def zip_all_applets(applets_path):
    os.getcwd()
    applets_dir = []
    for file in os.listdir(applets_path):
        applet_path = os.path.join(applets_path, file)
        if os.path.isdir(applet_path) and file not in ignore_dirs:
            applets_dir.append(applet_path)
    dist_dir = os.path.join(applets_path, 'build')
    for applet in applets_dir:
        zip_applet(applet, dist_dir)


def zip_pip_packages(project_path):
    pip_packages_path = os.path.join(project_path, 'pip_packages')
    if not os.path.exists(pip_packages_path):
        raise Exception('pip_packages not exist')
    dst_dir = os.path.join(project_path, 'build')
    with change_dir(project_path):
        applet_name = "pip_packages"
        zip_name = os.path.join(dst_dir, applet_name + '.zip')
        filelist = []
        for root, dirs, files in os.walk(applet_name):
            for name in files:
                filelist.append(os.path.join(root, name))
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
            for tar in filelist:
                arcname = tar[len(applet_name):]
                zf.write(tar, arcname)


root_path = os.path.dirname(os.path.abspath(__file__))
zip_all_applets(root_path)
zip_pip_packages(root_path)
