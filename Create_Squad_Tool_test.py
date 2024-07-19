import tkinter as tk  # 导入 Tkinter 库，用于创建 GUI 界面
from tkinter import messagebox
from tkinter import scrolledtext  # 导入 messagebox 库，用于显示消息框
from PIL import Image, ImageTk, ImageGrab  # 导入 PIL 库，用于处理图像
import socket  # 导入 socket 库，用于获取本机 IP 地址
import qrcode  # 导入 qrcode 库，用于生成二维码
import io  # 导入 io 库，用于处理字节流
from flask import (
    Flask,
    request,
    render_template_string,
    redirect,
    url_for,
    jsonify
)  # 导入 Flask 库，用于创建 Web 应用
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
from tkinter import ttk

vehicle_data = None
html_content_1 = None
license_text = """
create_squad_tool - Version 7.0

Copyright (C) 2024 皮特

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


# 添加重定向 print 的类
class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see("end")

    def flush(self):
        pass


def fetch_urls_from_github(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 确保请求成功
        urls = {}
        for line in response.text.splitlines():
            parts = line.split("=", 1)  # 仅分割一次，确保只有两个部分
            if len(parts) == 2:
                key, value = parts
                urls[key] = value
        return urls, "成功获取URL配置文件"
    except requests.RequestException as e:
        print(f"Error in fetch_urls_from_github: {e}")
        return None, "获取URL配置文件失败"


# 获取 HTML 文件的函数
def fetch_html_from_github(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 确保请求成功
        return response.text, "成功获取HTML模板"
    except requests.RequestException as e:
        print(f"Error in fetch_html_from_github: {e}")
        return None, "获取HTML模板失败"


# 获取 JSON 文件的函数
def fetch_json_from_github(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 确保请求成功
        return response.json(), "成功获取JSON文件"
    except requests.RequestException as e:
        print(f"Error in fetch_json_from_github: {e}")
        return None, "获取JSON文件失败"


# 生成IP地址的二维码图像
def generate_qr_code(ip_address, port):
    try:
        invert_colors = is_night_mode()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(f"http://{ip_address}:{port}")
        qr.make(fit=True)
        if invert_colors:
            qr_img = qr.make_image(fill_color="white", back_color="black")  # 反转颜色
        else:
            qr_img = qr.make_image(fill_color="black", back_color="white")  # 默认颜色
        return qr_img
    except Exception as e:
        print(f"Error in generate_qr_code: {e}")
        return None


def get_dominant_color_and_image_url(bing_url, backup_url):
    try:
        response = requests.get(bing_url, timeout=5)
        response.raise_for_status()  # 确保请求成功

        # 检查返回的内容类型是否为图片
        if "image" in response.headers.get("Content-Type"):
            image_response = response
            copyright_info = "No copyright info available"
        else:
            data = response.json()
            image_url = "https://www.bing.com" + data['images'][0]['url']
            copyright_info = data['images'][0].get('copyright', 'No copyright info available')

            image_response = requests.get(image_url)
            image_response.raise_for_status()  # 确保图像请求成功

    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching Bing image in get_dominant_color_and_image_url: {e}, switching to backup image.")
        try:
            image_response = requests.get(backup_url)
            image_response.raise_for_status()  # 确保图像请求成功
            copyright_info = 'No copyright info available (using backup image)'
        except requests.RequestException as backup_e:
            print(f"Error fetching backup image in get_dominant_color_and_image_url: {backup_e}, returning default color and no image URL.")
            return "#9695d1", backup_url  # 返回默认颜色和备用URL

    try:
        img = Image.open(BytesIO(image_response.content))

        # 缩小图片以加快处理速度
        img = img.resize((50, 50))
        img = img.convert("RGB")

        # 将图片转换为numpy数组
        pixels = np.array(img)

        # 计算三分之一宽度的像素范围
        one_third_width = int(pixels.shape[1] // 3)

        # 选择左边三分之一的像素
        left_pixels = pixels[:, :one_third_width]

        # 重塑数组为一维，以便进行颜色分析
        left_pixels = left_pixels.reshape((left_pixels.shape[0] * left_pixels.shape[1], 3))

        # 使用numpy的unique函数来找到最常见的颜色
        unique, counts = np.unique(left_pixels, return_counts=True, axis=0)
        dominant = unique[counts.argmax()]

        dominant_color = "#{:02x}{:02x}{:02x}".format(dominant[0], dominant[1], dominant[2])
        print(f"Image URL: {image_response.url}")
        print(f"Copyright: {copyright_info}")
        print("dominant_color:", dominant_color)
        return dominant_color, image_response.url
    except Exception as e:
        print(f"Error processing image in get_dominant_color_and_image_url: {e}, returning default color.")
        return "#9695d1", backup_url  # 返回默认颜色和备用URL



# 创建Flask应用
app = Flask(__name__)  # 创建 Flask 应用实例

# Flask应用的路由
@app.route("/")  # 根路径
def index():
    global vehicle_data, html_content_1, bing_daily_image_url, backup_image_url
    dominant_color, background_url, copyright_info = get_dominant_color_and_image_url(bing_daily_image_url, backup_image_url)
    return render_template_string(html_content_1, color=dominant_color, background_url=background_url, vehicle_data=vehicle_data, copyright_info=copyright_info)



# 并发下载图片，选取最快响应的URL
def download_image(urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {
            executor.submit(requests.get, url, timeout=5): url for url in urls
        }

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                response = future.result()
                response.raise_for_status()  # 确保下载成功
                return Image.open(BytesIO(response.content))
            except Exception as exc:
                print(f"Error in download_image: {url} generated an exception: {exc}")
    return None


def set_icon(window, img):
    try:
        photo_img = ImageTk.PhotoImage(img)
        window.iconphoto(False, photo_img)
        return photo_img
    except Exception as e:
        print(f"Error in set_icon: {e}")


def play_sound(reverse=False):
    try:
        p = pyaudio.PyAudio()

        volume = 0.5  # range [0.0, 1.0]
        fs = 44100  # sampling rate, Hz, must be integer

        # Define a melody inspired by Xiaomi notification sounds
        notes = [784, 880, 988, 1047]  # G5, A5, B5, C6 frequencies in Hz
        durations = [0.2, 0.2, 0.2, 0.5]  # duration of each note in seconds

        melody = np.array([], dtype=np.float32)

        for f, d in zip(notes, durations):
            samples = (np.sin(2 * np.pi * np.arange(fs * d) * f / fs)).astype(
                np.float32
            )
            melody = np.concatenate(
                (melody, samples, np.zeros(int(fs * 0.1), dtype=np.float32))
            )  # Adding a short pause between notes

        if reverse:
            # If reverse is True, reverse the melody
            melody = np.flip(melody)

        # Open stream
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs, output=True)

        # Play melody
        stream.write(volume * melody)

        # Close the stream
        stream.stop_stream()
        stream.close()

        p.terminate()
    except Exception as e:
        print(f"Error in play_sound: {e}")


def extract_map_info(json_data):
    try:
        # 初始化三个集合（去重）
        map_names = set()
        gamemodes = set()
        layer_versions = set()
        translations_map_name = {}
        translations_gamemodes = {}

        # 遍历Maps数组并提取所需信息
        for map_data in json_data.get("Maps", []):
            map_name = map_data.get("mapName", "")
            gamemode = map_data.get("gamemode", "")
            version = map_data.get("layerVersion", "")

            map_names.add(map_name)
            gamemodes.add(gamemode)
            if not re.match(r"v0\d+", version):  # 忽略v01, v02等版本
                layer_versions.add(version)

            translations_map_name[map_name] = map_data.get("mapId", "")  # 获取中文翻译
            translations_gamemodes[gamemode] = map_data.get(
                "minimapTexture", ""
            )  # 获取中文翻译
        # 将集合转换为列表并排序
        map_names = sorted(list(map_names))
        gamemodes = sorted(list(gamemodes))

        # 自定义排序函数
        def custom_sort(version):
            match = re.search(r"\d+", version)
            if match:
                return (0, int(match.group()))
            else:
                return (1, version)

        layer_versions = sorted(list(layer_versions), key=custom_sort)

        # 返回包含中英文翻译的选项列表和翻译字典
        return (
            map_names,
            gamemodes,
            layer_versions,
            translations_map_name,
            translations_gamemodes,
        )
    except Exception as e:
        print(f"Error in extract_map_info: {e}")
        return [], [], [], {}, {}


# 生成HTML内容的函数
def generate_html(
    template,
    map_names,
    gamemodes,
    layer_versions,
    status,
    json,
    translations_map_name,
    translations_gamemodes,
):
    try:
        # 使用中英文翻译生成选项
        map_options = "".join(
            [
                f'<option value="{name}">{name} {translations_map_name.get(name, "")}</option>'
                for name in map_names
            ]
        )
        gamemode_options = "".join(
            [
                f'<option value="{mode}">{mode} {translations_gamemodes.get(mode, "")}</option>'
                for mode in gamemodes
            ]
        )
        layer_version_options = "".join(
            [
                f'<option value="{version}">{version}</option>'
                for version in layer_versions
            ]
        )

        return (
            template.replace("{map_options}", map_options)
            .replace("{gamemode_options}", gamemode_options)
            .replace("{layer_version_options}", layer_version_options)
            .replace("{status}", status)
            .replace("{squad_data}", json)
        )
    except Exception as e:
        print(f"Error in generate_html: {e}")
        return template


def get_ip_and_open_port():
    dns_servers = [
        "114.114.114.114",
        "223.5.5.5",
        "180.76.76.76",
        "119.29.29.29",
    ]  # 添加多个DNS服务器
    ip_addresses = []

    for dns in dns_servers:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((dns, 80))
            ip = s.getsockname()[0]
            ip_addresses.append(ip)
        except Exception as e:
            print(f"Failed to connect to DNS server {dns} in get_ip_and_open_port: {e}")
        finally:
            s.close()

    # 统计每个IP地址的出现次数
    ip_count = {}
    for ip in ip_addresses:
        if ip in ip_count:
            ip_count[ip] += 1
        else:
            ip_count[ip] = 1

    # 找出出现次数最多的IP地址
    for ip, count in ip_count.items():
        if count >= 2:  # 如果有两个或更多DNS服务器返回相同的IP地址
            selected_ip = ip
            break
    else:
        print("Error in get_ip_and_open_port: Failed to get local IP")
        return "获取本地IP失败", None

    # 查找可用端口
    def find_open_port(start_port=49152, end_port=65535):
        range_size = end_port - start_port + 1
        while True:
            random_bytes = os.urandom(2)
            random_port = start_port + int.from_bytes(random_bytes, byteorder='big') % range_size
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", random_port))
                    return random_port
                except OSError:
                    continue
        print("Error in get_ip_and_open_port: No available ports found")
        return None

    open_port = find_open_port()
    if open_port:
        return selected_ip, open_port
    else:
        return selected_ip, "没有找到可用端口"

def quit_program():
    try:
        os._exit(0)
    except Exception as e:
        print(f"Error in quit_program: {e}")


def copy_download_url_to_clipboard(download_url):
    try:
        clipboard.copy(download_url)  # 将链接复制到剪切板
        messagebox.showinfo("链接已复制", "下载链接已复制到剪切板。")
    except Exception as e:
        print(f"Error in copy_download_url_to_clipboard: {e}")


def calculate_average_brightness(image):
    """
    计算图像的平均亮度
    :param image: PIL图像对象
    :return: 平均亮度值
    """
    image_np = np.array(image.convert('L'))  # 转换为灰度图像
    average_brightness = np.mean(image_np)
    return average_brightness

def adjust_brightness(image, target_brightness=128):
    """
    调整图像亮度
    :param image: PIL图像对象
    :param target_brightness: 目标亮度值
    :return: 调整亮度后的图像
    """
    current_brightness = calculate_average_brightness(image)
    adjustment_factor = target_brightness / current_brightness
    image = image.point(lambda p: p * adjustment_factor)
    return image

def calculate_color_diversity(image, num_bins=32):
    """
    计算图像的颜色多样性
    :param image: PIL图像对象
    :param num_bins: 颜色直方图的bin数
    :return: 颜色多样性得分
    """
    image = adjust_brightness(image)  # 调整图像亮度
    image_np = np.array(image)
    if len(image_np.shape) == 3:
        image_np = image_np.reshape((-1, 3))
    else:
        image_np = image_np.reshape((-1, 1))
    
    hist, _ = np.histogramdd(image_np, bins=num_bins, range=((0, 256),) * image_np.shape[1])
    diversity = np.count_nonzero(hist) / np.prod(hist.shape)
    return diversity

def is_screen_black(threshold, check_duration, num_bins=32):
    """
    通过颜色多样性判断屏幕是否为黑屏
    :param threshold: 判断黑屏的颜色多样性阈值
    :param check_duration: 检查持续时间
    :param num_bins: 颜色直方图的bin数
    :return: 是否为黑屏 (True/False)
    """
    threshold = float(threshold)
    count = int(check_duration / 0.03)
    temp = 1
    consecutive_black_count = 0  # 连续黑屏计数
    try:
        start_time = time.time()
        while time.time() - start_time < check_duration:
            screen = ImageGrab.grab()
            diversity = calculate_color_diversity(screen, num_bins)
            print(f"第{temp}/{count}次检测，{diversity:.4f}，阈值{threshold}。")
            if diversity < threshold:  # 阈值越低，意味着颜色多样性越低
                consecutive_black_count += 1
                print(f"第{temp}/{count}次检测为黑屏，{diversity:.4f}，阈值{threshold}。")
                if consecutive_black_count >= 2:  # 连续检测三次为黑屏
                    return True
            else:
                consecutive_black_count = 0  # 重置连续黑屏计数
            time.sleep(0.01)  # 每0.1秒检查一次
            temp += 1
        return False
    except Exception as e:
        print(f"Error in is_screen_black: {e}")
        return False

def save_debug_info():
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(debug_text.get("1.0", tk.END))
    except Exception as e:
        print(f"Error in save_debug_info: {e}")

def is_night_mode():
    current_hour = time.localtime().tm_hour
    return 18 <= current_hour or current_hour < 6


# 创建Flask应用
app = Flask(__name__)  # 创建 Flask 应用实例


# Flask应用的路由
@app.route("/")  # 根路径
def index():
    global vehicle_data, html_content_1, bing_daily_image_url, backup_image_url, license_text
    try:
        dominant_color, background_url = get_dominant_color_and_image_url(
            bing_daily_image_url, backup_image_url
        )
        return render_template_string(
            html_content_1,
            color=dominant_color,
            background_url=background_url,
            vehicle_data=vehicle_data,
        )
    except Exception as e:
        print(f"Error in Flask index route: {e}")
        return "Error occurred while processing the request."


@app.route("/send_text", methods=["POST"])
def send_text():
    try:
        text = request.form["text"].strip()
        repeat_times = int(request.form["repeat_times"])
        key_press_order = request.form.get("key_press_order", "home")
        delay_time = float(request.form.get("delay_time", 0.1))

        def is_valid_input(input_text):
            if len(input_text) < 3:
                return False
            return True

        if not is_valid_input(text):
            return jsonify({"success": False, "message": "输入无效，文本长度需大于3个字符。"})

        print(f"队伍名称：{text}")

        clipboard.copy("CreateSquad " + text + " 1")
        if key_press_order == "home":
            first_key = "home"
            second_key = ""
        else:
            first_key = ""
            second_key = "home"

        play_sound(reverse=True)

        pyautogui.PAUSE = delay_time
        for i in range(repeat_times):
            pyautogui.press(first_key)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            print(f"第 {i+1} 次建队操作成功！")  # 修改为 print，避免中断循环

        play_sound(reverse=True)


        # 循环结束后返回最终成功的消息
        return jsonify({"success": True, "message": "操作成功！"})

    except Exception as e:
        # 如果发生异常，返回请求失败的消息
        error_message = f"请求失败：{str(e)}"
        return jsonify({"success": False, "message": error_message})


# 启动Flask应用的函数
def run_flask_app():
    try:
        app.run(
            host="0.0.0.0", threaded=True, port=open_port, use_reloader=False
        )  # 在指定主机和端口上运行 Flask 应用，启用多线程支持
    except Exception as e:
        print(f"Error in run_flask_app: {e}")


def main():
    global debug_text, license_text
    global dominant_color, html_content_1, vehicle_data, open_port, bing_daily_image_url, backup_image_url, threshold, check_duration
    url_config_url = "https://gitee.com/petepetehiking/create_squad_tool/raw/master/urls_test.txt"
    urls, url_status = fetch_urls_from_github(url_config_url)
    if not urls:
        print(url_status)
        return

    html_url = urls.get("html_template_url")
    json_url = urls.get("json_data_url")
    icon_urls = [urls.get("icon_url")]
    bing_daily_image_url = urls.get("bing_daily_image_url")
    backup_image_url = urls.get("backup_image_url")
    important_message = urls.get("important_message", "")
    latest_version = urls.get("latest_version", "未知")
    download_url = urls.get("download_url")

    threshold = urls.get("threshold", 0.01)
    check_duration = int(urls.get("check_duration", 60))

    window_width = int(urls.get("window_width", 600))
    window_height = int(urls.get("window_height", 600))
    print(window_width, window_height)
    ip_address, open_port = get_ip_and_open_port()
    
    qr_img = generate_qr_code(ip_address, open_port)

    root = tk.Tk()
    root.title("Squad快速建队工具V7")

    is_night = is_night_mode()
    bg_color = '#2e2e2e' if is_night else 'white'
    fg_color = 'white' if is_night else 'black'
    
    root.configure(bg=bg_color)

    img = download_image(icon_urls)
    if img:
        photo_img = set_icon(root, img)
    else:
        print("Failed to download any image for icon.")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_coordinate, y_coordinate))

    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(fill="both", expand=True)

    left_frame = tk.Frame(main_frame, padx=10, pady=10, bg=bg_color)
    left_frame.grid(row=0, column=0, sticky="nsew")

    right_frame = tk.Frame(main_frame, padx=10, pady=10, bg=bg_color)
    right_frame.grid(row=0, column=1, sticky="ns")

    main_frame.columnconfigure(0, weight=3)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    label_1 = tk.Label(
        left_frame,
        text="手机扫码自动打开浏览器",
        justify="left",
        anchor="center",
        font=("微软雅黑", 18),
        fg=fg_color,
        bg=bg_color,
        compound="bottom",
        padx=0,
        pady=5,
    )
    label_1.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    status_label = tk.Label(
        left_frame,
        text="正在获取远程HTML和JSON文件...",
        fg=fg_color,
        bg=bg_color,
        font=("微软雅黑", 10),
    )
    status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    img = ImageTk.PhotoImage(qr_img)
    panel = tk.Label(left_frame, image=img, bg=bg_color)
    panel.grid(row=2, column=0, columnspan=2, pady=(0, 10))

    label_2 = tk.Label(
        left_frame,
        text="本地IP地址：{}，端口：{}".format(ip_address, open_port),
        justify="left",
        anchor="center",
        font=("微软雅黑", 10),
        fg=fg_color,
        bg=bg_color,
        compound="bottom",
        padx=0,
        pady=0,
    )
    label_2.grid(row=3, column=0, columnspan=2, pady=(0, 10))

    if important_message:
        important_message_label = tk.Label(
            left_frame,
            text=important_message,
            justify="center",
            anchor="center",
            font=("微软雅黑", 12, "bold"),
            fg="red",
            bg=bg_color,
            padx=0,
            pady=5,
            wraplength=int(window_width * 0.4),
        )
        important_message_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))

    html_content_1, html_status = fetch_html_from_github(html_url)
    if not html_content_1:
        status_label.config(text=html_status)
        return

    json_data, json_status = fetch_json_from_github(json_url)
    if not json_data:
        status_label.config(text=f"{html_status}，{json_status}")
        return

    status_label.config(text=f"{html_status}，{json_status}")

    map_names, gamemodes, layer_versions, translations_map_name, translations_gamemodes = extract_map_info(json_data)
    vehicle_data = json.dumps(json_data, ensure_ascii=False, indent=2)
    html_content_1 = generate_html(html_content_1, map_names, gamemodes, layer_versions, json_status, vehicle_data, translations_map_name, translations_gamemodes)

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    debug_label = tk.Label(right_frame, text="调试信息", font=("微软雅黑", 12, "bold"), bg=bg_color, fg=fg_color)
    debug_label.pack(pady=(0, 5))

    debug_text = scrolledtext.ScrolledText(right_frame, height=20, width=40, state="disabled", wrap="word", bg=bg_color, fg=fg_color, insertbackground=fg_color)
    debug_text.pack(fill="y", expand=True)
    save_button = tk.Button(right_frame, text="保存调试信息", command=save_debug_info, bg=bg_color, fg=fg_color)
    save_button.pack(pady=(5, 0))

    sys.stdout = TextRedirector(debug_text)
    sys.stderr = TextRedirector(debug_text)

    root.protocol("WM_DELETE_WINDOW", quit_program)
    root.resizable(True, True)
    root.mainloop()

if __name__ == "__main__":
    main()
