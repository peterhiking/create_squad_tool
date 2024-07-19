import os
import requests
import tkinter as tk  # 导入 Tkinter 库，用于创建 GUI 界面
from tkinter import messagebox
from tkinter import scrolledtext  # 导入 messagebox 库，用于显示消息框
from PIL import Image, ImageTk, ImageGrab  # 导入 PIL 库，用于处理图像
import socket  # 导入 socket 库，用于获取本机 IP 地址
import qrcode  # 导入 qrcode 库，用于生成二维码
import io  # 导入 io 库，用于处理字节流
from flask import Flask, request, render_template_string, redirect, url_for  # 导入 Flask 库，用于创建 Web 应用
import pyautogui  # 导入 pyautogui 库，用于模拟键盘输入
import time  # 导入 time 库，用于时间相关操作
import threading  # 导入 threading 库，用于多线程处理
import os
import clipboard
import requests
from io import BytesIO
import numpy as np
import concurrent.futures
import pyaudio
import json
import re
import sys
from tkinter import filedialog

import PyQt5
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

def check_local_txt_file(file_name):
    """
    检查指定文件名的txt文件是否存在
    """
    return os.path.isfile(file_name)

def fetch_urls_from_github(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 确保请求成功
        urls = {}
        for line in response.text.splitlines():
            parts = line.split('=', 1)  # 仅分割一次，确保只有两个部分
            if len(parts) == 2:
                key, value = parts
                urls[key.strip()] = value.strip()
        return urls, "成功获取URL配置文件"
    except requests.RequestException:
        return None, "获取URL配置文件失败"

def fetch_code_from_github(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 确保请求成功
        return response.text, "成功获取代码"
    except requests.RequestException:
        return None, "获取代码失败"

def execute_code(code):
    try:
        exec(code, globals())
        return "代码执行成功"
    except Exception as e:
        return f"代码执行失败: {e}"

if __name__ == "__main__":
    local_file_name = "urls.txt"  # 指定的本地txt文件名称
    
    if check_local_txt_file(local_file_name):
        with open(local_file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        urls = {line.split('=')[0].strip(): line.split('=')[1].strip() for line in lines if '=' in line}
        status = "成功读取本地URL配置文件"
    else:
        config_url = "https://gitee.com/petepetehiking/create_squad_tool/raw/master/urls.txt"  # 替换为实际的配置文件URL
        urls, status = fetch_urls_from_github(config_url)

    if urls:
        print(status)
        github_code_url = urls.get('github_url')
        print(github_code_url)
        if github_code_url:
            code, code_status = fetch_code_from_github(github_code_url)
            if code:
                print(code_status)
                exec_status = execute_code(code)
                print(exec_status)
            else:
                print(code_status)
        else:
            print("配置文件中没有找到github_url")
    else:
        print(status)
