# ...existing code...
# ...existing code...
def save_config():
    # Lấy config hiện tại (nếu có)
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        config = {}

    # Lưu các giá trị UI hiện tại
    try:
        config['phone_net_mode'] = phone_net_mode.get()
    except Exception:
        pass
    try:
        config['proxy_format_var'] = proxy_format_var.get()
    except Exception:
        pass
    try:
        config['phone_ig_app_var'] = phone_ig_app_var.get()
    except Exception:
        pass

    # ...các config khác nếu có...

    # Ghi lại file config.json
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
# ...existing code...

# ...existing code...
# Sau khi đã khởi tạo các biến UI liên quan đến Phone Settings:
# phone_net_mode = tk.StringVar(...)
# proxy_format_var = tk.StringVar(...)
# phone_ig_app_var = tk.StringVar(...)
try:
    phone_net_mode.trace_add('write', lambda *args: save_config())
except Exception:
    pass

try:
    phone_ig_app_var.trace_add('write', lambda *args: save_config())
except Exception:
    pass

# ...existing code...

# ======================= Load config cho Phone Settings UI =======================
# Đặt đoạn này SAU khi đã định nghĩa load_config và các biến UI liên quan
def apply_phone_settings_from_config():
    config = load_config()
    # Network Mode
    if 'phone_net_mode' in config:
        try:
            phone_net_mode.set(config['phone_net_mode'])
        except Exception:
            pass
    # Proxy Type
    if 'proxy_format_var' in config:
        try:
            proxy_format_var.set(config['proxy_format_var'])
        except Exception:
            pass
    # IG App
    if 'phone_ig_app_var' in config:
        try:
            phone_ig_app_var.set(config['phone_ig_app_var'])
        except Exception:
            pass

# ...existing code...
# Gọi hàm này sau khi đã khởi tạo các biến UI liên quan đến Phone Settings
# apply_phone_settings_from_config()

import tkinter as tk
from PIL import Image, ImageTk
from tkinter import scrolledtext
import threading
import time
import math
from selenium import webdriver as se_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from tkinter import ttk
import requests
import base64
import names
import subprocess, re, xml.etree.ElementTree as ET
import random
## import configparser (loại bỏ)
import string
import pygetwindow as gw
import os
from unidecode import unidecode
import re
import subprocess
import hashlib
from datetime import datetime
import pytz
import pyotp
import pyperclip
import sys
import time as _t
import os, time, shlex, calendar, secrets
from tkinter import filedialog, messagebox
import json
# Appium + Selenium Android
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException
import socket, shutil
# Fix for PointerInput and ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder

# ============================
# APPIUM SERVER HELPERS
# ============================
APPIUM_HOST = "127.0.0.1"
APPIUM_PORT = 4723
APPIUM_STATUS_URL = f"http://{APPIUM_HOST}:{APPIUM_PORT}/wd/hub/status"

def _is_port_open(host, port) -> bool:
    s = socket.socket()
    s.settimeout(0.35)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def _wait_appium_ready(timeout=15) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if _is_port_open(APPIUM_HOST, APPIUM_PORT):
            try:
                r = requests.get(APPIUM_STATUS_URL, timeout=1.2)
                if r.ok:
                    return True
            except Exception:
                pass
        time.sleep(0.5)
    return False

def _appium_candidates() -> list:
    """
    Các lệnh có thể chạy Appium trên Windows:
    - appium / appium.cmd (trong PATH)
    - npx appium
    - %AppData%\\npm\\appium.cmd
    - node <ProgramFiles>/nodejs/node_modules/appium/build/lib/main.js
    """
    cands = []
    for name in ("appium", "appium.cmd"):
        p = shutil.which(name)
        if p: cands.append([p])

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        cands.append([npx_path, "appium"])

    appdata = os.environ.get("APPDATA")
    if appdata:
        pth = os.path.join(appdata, "npm", "appium.cmd")
        if os.path.isfile(pth):
            cands.append([pth])

    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if not base: 
            continue
        main_js = os.path.join(base, "nodejs", "node_modules", "appium", "build", "lib", "main.js")
        node = shutil.which("node") or shutil.which("node.exe")
        if node and os.path.isfile(main_js):
            cands.append([node, main_js])
    return cands

def _popen_hidden(cmd: list):
    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
        creationflags=creationflags, startupinfo=startupinfo
    )

def start_appium_server() -> bool:
    """
    Nếu Appium chưa chạy, thử khởi động ngầm với --session-override.
    """
    if _is_port_open(APPIUM_HOST, APPIUM_PORT):
        return True

    base_args = ["-p", str(APPIUM_PORT), "--session-override"]
    for cand in _appium_candidates():
        try:
            _popen_hidden(cand + base_args)
            if _wait_appium_ready(timeout=15):
                return True
        except Exception:
            pass

    try:
        _popen_hidden(["appium"] + base_args)
        if _wait_appium_ready(timeout=15):
            return True
    except Exception:
        pass

    return False

# ============================
# ADB HELPERS
# ============================
def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()

def adb_devices() -> list[str]:
    """
    Trả về danh sách serial thiết bị đang ở trạng thái 'device'.
    """
    out = _run(["adb", "devices"])
    lines = [l for l in out.splitlines() if l.strip()]
    devs = []
    for ln in lines[1:]:
        if "\tdevice" in ln and not any(k in ln for k in ("offline", "unauthorized")):
            devs.append(ln.split("\t")[0])
    return devs

def adb_shell(udid: str, *args) -> str:
    return _run(["adb", "-s", udid, "shell", *args])

def clear_app_data(udid: str, package: str):
    out = adb_shell(udid, "pm", "clear", package)
    log(f"🧹 [{udid}] pm clear {package}: {out or 'OK'}")
    adb_shell(udid, "am", "force-stop", package)

def clear_instagram_and_warp(udid: str):
    """
    Clear dữ liệu Instagram + WARP + Super Proxy.
    """
    # ========== Instagram ==========
    clear_app_data(udid, "com.instagram.android")
    time.sleep(1.0)
    adb_shell(udid, "am", "force-stop", "com.instagram.android")
    time.sleep(1.0)

    # ========== Instagram Lite ==========
    clear_app_data(udid, "com.instagram.lite")
    time.sleep(1.0)
    adb_shell(udid, "am", "force-stop", "com.instagram.lite")
    time.sleep(1.0)

    # ========== Cloudflare 1.1.1.1 / WARP ==========
    warp_candidates = [
        "com.cloudflare.onedotonedotonedotone",
        "com.cloudflare.onedotonedotone",
        "com.cloudflare.warp",
    ]

    out = adb_shell(udid, "pm", "list", "packages").lower()
    for line in out.splitlines():
        pkg = line.replace("package:", "").strip()
        if ("cloudflare" in pkg) and ("warp" in pkg or "onedot" in pkg or "1dot" in pkg):
            if pkg not in warp_candidates:
                warp_candidates.append(pkg)

    for pkg in warp_candidates:
        if adb_shell(udid, "pm", "path", pkg):
            clear_app_data(udid, pkg)
            time.sleep(1.0)
            adb_shell(udid, "am", "force-stop", pkg)
            time.sleep(1.0)

    # ========== Super Proxy ==========
    superproxy_pkg = "com.scheler.superproxy"
    if adb_shell(udid, "pm", "path", superproxy_pkg):
        clear_app_data(udid, superproxy_pkg)
        time.sleep(1.0)
        adb_shell(udid, "am", "force-stop", superproxy_pkg)
        time.sleep(1.0)

def kill_all_apps(udid: str):
    """
    Đóng toàn bộ app sạch sẽ:
    - HOME trước
    - Kill background
    - Force-stop IG, WARP, Super Proxy
    - Remove tất cả recent tasks (trừ launcher/home)
    - HOME lại
    """
    # Về HOME trước
    adb_shell(udid, "input", "keyevent", "3")

    # Kill background
    adb_shell(udid, "am", "kill-all")

    # Force-stop các app cần chắc chắn đóng
    try:
        adb_shell(udid, "am", "force-stop", "com.instagram.android")
        adb_shell(udid, "am", "force-stop", "com.instagram.lite")   # 👈 thêm dòng này
        adb_shell(udid, "am", "force-stop", "com.scheler.superproxy")
        # Các package Warp phổ biến
        for pkg in [
            "com.cloudflare.onedotonedotonedotone",
            "com.cloudflare.onedotonedotone",
            "com.cloudflare.warp",
        ]:
            adb_shell(udid, "am", "force-stop", pkg)
    except Exception:
        pass

    # Xoá các recent tasks (trừ home/launcher)
    out = adb_shell(udid, "cmd", "activity", "tasks")
    task_ids = re.findall(r"taskId=(\d+)", out or "")
    for tid in task_ids:
        try:
            ti = adb_shell(udid, "cmd", "activity", "task", tid)
            lo = (ti or "").lower()
            if "launcher" in lo or "home" in lo:
                continue
            adb_shell(udid, "cmd", "activity", "remove-task", tid)
        except Exception:
            pass

    # HOME lại để chắc chắn
    adb_shell(udid, "input", "keyevent", "3")

def chay_lenh(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()

def adb_mkdir(udid: str | None, remote_dir: str):
    cmd = ["adb"] + (["-s", udid] if udid else []) + ["shell", "mkdir", "-p", remote_dir]
    return chay_lenh(cmd)

def adb_push(udid: str | None, local_path: str, remote_path: str):
    cmd = ["adb"] + (["-s", udid] if udid else []) + ["push", local_path, remote_path]
    return chay_lenh(cmd)

def adb_media_scan(udid: str | None, remote_file: str):
    cmd = ["adb"] + (["-s", udid] if udid else []) + [
        "shell", "am", "broadcast",
        "-a","android.intent.action.MEDIA_SCANNER_SCAN_FILE",
        "-d", f"file://{remote_file}"
    ]
    return chay_lenh(cmd)

def tap_xy(d, x: int, y: int) -> bool:
    try:
        # Ưu tiên dùng Appium nếu có
        finger = PointerInput("touch", "finger1")  # sửa TOUCH -> "touch"
        actions = ActionBuilder(d, mouse=finger)
        actions.pointer_action.move_to_location(x, y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.05)
        actions.pointer_action.pointer_up()
        actions.perform()
        return True
    except Exception:
        try:
            # fallback: ADB tap
            udid = None
            if 'active_sessions' in globals():
                for k, v in active_sessions.items():
                    if v == d:
                        udid = k
                        break
            if udid:
                subprocess.call([ADB_BIN, "-s", udid, "shell", "input", "tap", str(x), str(y)])
                return True
        except Exception as e2:
            log(f"⚠️ Tap lỗi (ADB cũng fail): {e2}")
        return False

# ======================== WARP PHONE =====================================

# Fix for ADB_BIN and active_sessions
ADB_BIN = "adb"  # or set to your adb path if needed
active_sessions = {}  # {udid: driver}

device_state = {}   # {udid: {"view": bool, "pick": bool}}
phone_device_tree = None  # sẽ gán sau khi tạo Treeview trong UI

def _tick(b: bool) -> str:
    return "☑" if b else "☐"

def refresh_adb_devices_table():
    """
    Quét ADB và đổ dữ liệu vào Treeview 3 cột: UDID | VIEW | CHỌN.
    Giữ lại trạng thái tick cũ nếu UDID vẫn còn online.
    """
    try:
        devs = adb_devices()

        # thêm dev mới vào state / xóa dev cũ
        for ud in devs:
            device_state.setdefault(ud, {"view": False, "pick": False})
        for ud in list(device_state.keys()):
            if ud not in devs:
                device_state.pop(ud, None)

        if phone_device_tree is not None:
            phone_device_tree.delete(*phone_device_tree.get_children())
            for ud in devs:
                st = device_state[ud]
                phone_device_tree.insert(
                    "", "end", iid=ud,
                    values=(ud, _tick(st["view"]), _tick(st["pick"]))
                )

        if devs:
            log(f"📡 [Phone] Tìm thấy {len(devs)} thiết bị: {', '.join(devs)}")
        else:
            log("⚠️ [Phone] Không phát hiện thiết bị nào. Kiểm tra USB debugging / cáp / adb devices.")
    except Exception as e:
        log(f"❌ [Phone] Lỗi refresh ADB: {repr(e)}")

def kill_adb_and_reload():
    try:
        # Kill tất cả tiến trình adb.exe
        subprocess.run("taskkill /F /IM adb.exe", shell=True)
        log("🛑 Đã kill toàn bộ adb.exe.")
        time.sleep(1.5)
        refresh_adb_devices_table()
        log("🔄 Đã reload danh sách thiết bị ADB.")
    except Exception as e:
        log(f"❌ Lỗi khi kill adb và reload: {repr(e)}")

def set_device_status(udid: str, status: str):
    """
    Cập nhật trạng thái cho thiết bị trong TreeView (thêm cột STATUS).
    Nếu chưa có cột STATUS thì chỉ log ra console.
    """
    try:
        if phone_device_tree is not None and udid in phone_device_tree.get_children():
            # Giả sử bạn có thêm cột thứ 4 = STATUS
            phone_device_tree.set(udid, column="status", value=status)
        else:
            log(f"[{udid}] STATUS: {status}")
    except Exception as e:
        log(f"⚠️ Không thể cập nhật status cho {udid}: {repr(e)}")

def _toggle_cell(event):
    """
    Bắt click chuột trái vào cột VIEW/CHỌN để đảo trạng thái tick.
    """
    if phone_device_tree is None:
        return
    row_id = phone_device_tree.identify_row(event.y)
    col_id = phone_device_tree.identify_column(event.x)  # "#1" "#2" "#3"
    if not row_id:
        return
    if col_id == "#2":
        key = "view"
    elif col_id == "#3":
        key = "pick"
    else:
        return

    cur = device_state.get(row_id, {"view": False, "pick": False})
    cur[key] = not cur.get(key, False)
    device_state[row_id] = cur
    # cập nhật hiển thị
    phone_device_tree.set(row_id, column=("view" if key == "view" else "pick"), value=_tick(cur[key]))

def get_checked_udids(kind: str = "pick") -> list:
    """
    Lấy danh sách UDID đã tick theo cột.
    kind = 'view'  -> các UDID tick cột VIEW (dùng để mở scrcpy)
    kind = 'pick'  -> các UDID tick cột CHỌN (dùng khi ấn START Phone)
    """
    return [ud for ud, st in device_state.items() if st.get(kind)]

def choose_scrcpy_path():
    global scrcpy_path
    fn = filedialog.askopenfilename(
        title="Chọn scrcpy (scrcpy.exe)",
        filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
    )
    if fn:
        scrcpy_path = fn
        save_scrcpy_config()  # sẽ log path

def open_scrcpy_for_list(udid_list: list[str]):
    """
    Mở scrcpy cho danh sách UDID (thường là các UDID tick cột VIEW).
    """
    if not udid_list:
        log("ℹ️ Chưa tick cột VIEW thiết bị nào.")
        return
    exe = scrcpy_path or shutil.which("scrcpy") or "scrcpy"
    if not scrcpy_path and not shutil.which("scrcpy"):
        log("⚠️ Chưa chọn scrcpy.exe và scrcpy không có trong PATH. Bấm 'Chọn scrcpy.exe'.")
        return
    def is_scrcpy_running_for_udid(udid):
        # Check if a scrcpy process is running for this udid
        try:
            import psutil
        except ImportError:
            log("⚠️ Thiếu thư viện psutil. Đang cài đặt...")
            import subprocess as sp
            sp.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'] and 'scrcpy' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline') or []
                    # Check for -s <udid> in command line
                    for i, arg in enumerate(cmdline):
                        if arg == '-s' and i+1 < len(cmdline) and cmdline[i+1] == udid:
                            return True
            except Exception:
                continue
        return False

    for ud in udid_list:
        if is_scrcpy_running_for_udid(ud):
            log(f"🖥️ scrcpy đã chạy cho {ud}, bỏ qua không mở thêm.")
        else:
            subprocess.Popen([exe, "-s", ud], creationflags=0)
            log(f"🖥️ Mở scrcpy cho {ud}")

def get_devices():
    try:
        result = subprocess.check_output(["adb", "devices"], encoding="utf-8")
        lines = result.strip().split("\n")[1:]
        devices = [line.split("\t")[0] for line in lines if "\tdevice" in line]
        return devices
    except Exception as e:
        messagebox.showerror("ADB lỗi", str(e))
        return []

def open_and_arrange():
    global scrcpy_path, resolution
    if not scrcpy_path or not os.path.exists(scrcpy_path):
        messagebox.showerror("Lỗi", "Chưa chọn scrcpy.exe")
        return

    # Chỉ mở các thiết bị đã tick VIEW
    devices = get_checked_udids("view")
    if not devices:
        messagebox.showinfo("Phone View", "Bạn cần tick cột VIEW cho thiết bị muốn mở!")
        return

    import pygetwindow as gw
    # Kiểm tra các cửa sổ scrcpy đã mở cho các thiết bị
    all_windows = gw.getAllWindows()
    opened_serials = [w.title.split()[-1] for w in all_windows if w.title and ("scrcpy" in w.title.lower() or "sm-" in w.title.lower())]
    already_opened = [serial for serial in devices if serial in opened_serials]
    to_open = [serial for serial in devices if serial not in opened_serials]

    if not to_open:
        messagebox.showinfo("Phone View", "Các thiết bị đã được mở và sắp xếp rồi!")
        return

    for serial in to_open:
        subprocess.Popen([
            scrcpy_path,
            "-s", serial,
            "--max-size", resolution.split("x")[0]
        ])
        time.sleep(1.2)

    # chờ scrcpy load
    time.sleep(5)

    # lấy tất cả cửa sổ scrcpy
    all_windows = gw.getAllWindows()
    windows = [w for w in all_windows if w.title and ("scrcpy" in w.title.lower() or "sm-" in w.title.lower())]

    # Tự động sắp xếp lại nếu chưa xếp
    # Sắp xếp theo thứ tự devices đã tick VIEW
    x0, y0 = 40, 40
    dx, dy = 420, 40  # khoảng cách giữa các cửa sổ
    for idx, serial in enumerate(devices):
        # Tìm cửa sổ scrcpy của serial này
        win = next((w for w in windows if w.title.endswith(serial)), None)
        if win:
            # Nếu cửa sổ chưa ở vị trí mong muốn thì di chuyển
            target_x = x0 + idx * dx
            target_y = y0
            if win.left != target_x or win.top != target_y:
                try:
                    win.moveTo(target_x, target_y)
                except Exception:
                    pass

    if not windows:
        messagebox.showerror("Lỗi", "Không tìm thấy cửa sổ scrcpy")
        return

    # === SẮP XẾP GIỮ NGUYÊN KÍCH THƯỚC ===
    n = len(windows)
    cols = n if n <= 3 else math.ceil(math.sqrt(n))
    col_count, x, y, gap = 0, 0, 0, 5

    for win in windows:
        try:
            win.moveTo(x, y)
            x += win.width + gap
            col_count += 1
            if col_count >= cols:  # xuống hàng nếu đủ cột
                col_count, x = 0, 0
                y += win.height + gap
        except Exception as e:
            print("⚠️ Không move được:", e)

def change_resolution(event):
    global resolution
    resolution = combo_res.get()

def read_first_proxy_line_fixed() -> str | None:
    try:
        with open(PROXY_TXT, "r", encoding="utf-8", errors="ignore") as f:
            for ln in f:
                s = ln.strip()
                if s:
                    return s
    except Exception as e:
        log(f"⚠️ Không đọc được Proxy.txt: {e}")
    return None

def parse_proxy(line: str) -> dict:
    """
    Trả về {ip, port, user, pwd, has_auth}.
    Hỗ trợ IP:PORT hoặc IP:PORT:USER:PASS. Dư thừa sẽ cắt còn 4 phần.
    """
    ip = port = user = pwd = ""
    has_auth = False
    parts = (line or "").split(":")[:4]
    if len(parts) >= 2:
        ip, port = parts[0].strip(), parts[1].strip()
    if len(parts) == 4:
        user, pwd = parts[2].strip(), parts[3].strip()
        has_auth = True
    return {"ip": ip, "port": port, "user": user, "pwd": pwd, "has_auth": has_auth}

def safe_instagram_restart(self, log):
    subprocess.call(["adb", "-s", self.udid, "shell", "am", "force-stop", "com.instagram.android"])
    log("🛑 Đã tắt app Instagram")
    time.sleep(3)
    subprocess.call(["adb", "-s", self.udid, "shell", "monkey", "-p", "com.instagram.android", "-c", "android.intent.category.LAUNCHER", "1"])
    log("🔄 Đã mở lại app Instagram")
    time.sleep(20)
    subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "1000", "1850"])
    log("👤 Đã vào Profile")
    time.sleep(8)

CAPTION_LEADS = [
    "Lưu lại khoảnh khắc ✨", "Mood hôm nay", "Một chút bình yên",
    "Ngày mới năng lượng", "Cuối ngày nhẹ nhàng", "Thêm chút kỷ niệm",
    "Chào cả nhà", "Just vibes", "Check-in nè", "Hello IG!"
]

CAPTION_TRAILS = [
    "Bạn thấy sao?", "Have a nice day!", "Đi đâu cũng được, miễn là vui.",
    "Giữ nụ cười nhé.", "Chill cùng mình nha.", "Up nhẹ tấm hình thôi.",
    "Be yourself.", "Tích cực lên!", "Thích thì đăng thôi.", "Cứ là chính mình."
]

CAPTION_EMOJIS = ["✨","🌿","🌸","🌙","☀️","⭐","🍀","🌼","🫶","💫","📸","😚","🤍","🧸","🥰","🫧"]

# ===== BIO RANDOM =====
BIO_LINES = [
    "Luôn mỉm cười", "Chia sẻ niềm vui", "Hành trình của tôi",
    "Sống hết mình", "Cứ là chính mình", "Yêu đời, yêu người",
    "Một chút chill", "Hạnh phúc đơn giản",
]

def _scroll_into_view_by_text(d, text_sub: str, max_swipes: int = 6) -> bool:
    # Ưu tiên UiScrollable, fallback vuốt tay
    try:
        d.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("{text_sub}"))'
        )
        return True
    except Exception:
        try:
            size = d.get_window_size()
            for _ in range(max_swipes):
                d.swipe(size["width"]//2, int(size["height"]*0.82),
                        size["width"]//2, int(size["height"]*0.25), 300)
                time.sleep(0.25)
                if d.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text_sub}")'):
                    return True
        except Exception:
            pass
    return False

class AndroidWorker(threading.Thread):
    """
    Worker tối giản: kết nối Appium tới thiết bị và mở Settings để xác nhận phiên sống.
    Sau này bạn có thể mở rộng các bước đăng ký IG tại đây.
    """
    def __init__(self, udid: str, log_fn=print):
        super().__init__(daemon=True)
        self.udid = udid
        self.log = log_fn
        self.driver = None
        self._stop_ev = threading.Event()

    def stop(self):
        self._stop_ev.set()
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass

    def run(self):
        try:
            self.log(f"📲 [Phone] Kết nối thiết bị {self.udid} qua Appium…")
            caps = {
                "platformName": "Android",
                "automationName": "UiAutomator2",
                "udid": self.udid,
                "appPackage": "com.android.settings",
                "appActivity": ".Settings",
                "newCommandTimeout": 180,
                "adbExecTimeout": 120000,
                "uiautomator2ServerLaunchTimeout": 120000,
                "noReset": True,
                "autoGrantPermissions": True,
            }
            opts = UiAutomator2Options().load_capabilities(caps)
            self.driver = webdriver.Remote(
                command_executor=f"http://{APPIUM_HOST}:{APPIUM_PORT}/wd/hub",
                options=opts
            )
            self.driver.implicitly_wait(4)
            try:
                self.driver.update_settings({"waitForIdleTimeout": 0, "ignoreUnimportantViews": True})
            except Exception:
                pass
            # ===== DỌN APP SAU KHI KẾT NỐI APPIUM =====
            self.log(f"🧹 [Phone] Dọn dữ liệu IG & WARP cho {self.udid}…")
            try:
                clear_instagram_and_warp(self.udid)
                kill_all_apps(self.udid)
                time.sleep(0.8)  # ổn định trước khi cấp quyền
                # 👇 THÊM DÒNG NÀY: đảm bảo bàn phím đã tắt
                self.ensure_keyboard_hidden()
                # 👇 CẤP QUYỀN IG/IG Lite TRƯỚC KHI BẬT WARP
                try:
                    choice = (phone_ig_app_var.get() or "instagram").lower()
                except Exception:
                    choice = "instagram"
                pkg_to_grant = "com.instagram.lite" if choice == "instagram_lite" else "com.instagram.android"
                self.grant_instagram_permissions(pkg=pkg_to_grant)
                self.log(f"✅ [Phone] Dọn xong & đã về Home ({self.udid}).")
            except Exception as ee:
                self.log(f"⚠️ [Phone] Lỗi khi dọn app ({self.udid}): {repr(ee)}")

            # ===== CHỌN PHƯƠNG THỨC MẠNG SAU KHI DỌN APP =====
            try:
                mode = phone_net_mode.get() if 'phone_net_mode' in globals() else 'wifi'
                mode = str(mode).lower()

                if mode == "wifi":
                    # Wi-Fi: tắt máy bay nếu đang bật; TẮT 4G nếu đang bật; bật Wi-Fi nếu đang tắt
                    self.ensure_airplane_off()
                    self.ensure_mobile_data_off()     # 👈 thêm dòng này
                    self.use_wifi_mode()

                elif mode == "warp":
                    # WARP: tắt máy bay; TẮT 4G; đảm bảo Wi-Fi đã bật rồi mới connect WARP
                    self.log(f"🌐 [Phone] {self.udid}: Bật WARP VPN")
                    self.ensure_airplane_off()
                    self.ensure_mobile_data_off()     # 👈 thêm dòng này
                    self.ensure_wifi_on()
                    try:
                        self.connect_warp()
                    except Exception as e:
                        self.log(f"⚠️ [Phone] Lỗi bật WARP cho {self.udid}: {repr(e)}")

                elif mode == "proxy":
                    self.log(f"🌐 [Phone] {self.udid}: Dùng Proxy")
                    try:
                        self.ensure_airplane_off()
                        self.ensure_wifi_on()
                        self.open_super_proxy()   # đã mở "Add proxy" trong app
                    except Exception as e:
                        self.log(f"⚠️ Lỗi mở Super Proxy: {repr(e)}")

                    # ===== ĐỌC Proxy.txt và điền theo radio =====
                    try:
                        line = read_first_proxy_line_fixed()
                        if not line:
                            self.log("⛔ Proxy.txt rỗng hoặc không đọc được.")
                            return
                        info = parse_proxy(line)  # {ip, port, user, pwd, has_auth}
                        fmt = proxy_format_var.get() if "proxy_format_var" in globals() else "ip_port"

                        if fmt == "ip_port":
                            if not info["ip"] or not info["port"]:
                                self.log("⛔ Proxy không hợp lệ cho IP:PORT.")
                                return
                            self.configure_super_proxy_ip_port(info["ip"], info["port"])
                        elif fmt == "ip_port_userpass":
                            # (làm IP:PORT trước theo yêu cầu)
                            if not info["ip"] or not info["port"]:
                                self.log("⛔ Proxy không hợp lệ.")
                                return
                            self.configure_super_proxy_ip_port(info["ip"], info["port"])
                            self.log("ℹ️ Đang xử lý bản IP:PORT trước. USER/PASS sẽ thêm sau.")
                    except Exception as e:
                        self.log(f"⚠️ Lỗi xử lý proxy: {repr(e)}")

                elif mode == "sim":
                    # SIM 4G: tắt airplane nếu đang bật; nếu mobile data đã ON thì giữ nguyên, chưa ON thì bật
                    self.log(f"🌐 [Phone] {self.udid}: Dùng SIM 4G (Wi-Fi OFF, Data ON)")
                    try:
                        self.enable_sim_4g(prefer_slot=1, allow_roaming=False)
                    except Exception as e:
                        self.log(f"⚠️ [Phone] Lỗi bật SIM 4G: {repr(e)}")

                else:
                    self.log(f"ℹ️ Mode không hợp lệ: {mode} → dùng Wi-Fi mặc định")
                    self.ensure_airplane_off()
                    self.ensure_mobile_data_off()
                    self.use_wifi_mode()

            except Exception as e:
                self.log(f"⚠️ [Phone] Không đọc được network mode: {repr(e)}")

            # 👉 BƯỚC MỚI: mở Instagram
            try:
                self.open_instagram()
            except Exception as e:
                self.log(f"⚠️ Lỗi khi mở Instagram: {repr(e)}")

            self.log(f"✅ [Phone] Đã mở phiên Appium với {self.udid}. Mở Settings OK.")
            # Giữ phiên sống đến khi PAUSE hoặc STOP app.
            while not self._stop_ev.is_set():
                time.sleep(0.5)
        
        except WebDriverException as e:
            self.log(f"❌ [Phone] Lỗi Appium ({self.udid}): {e}")
        except Exception as e:
            self.log(f"❌ [Phone] Lỗi khác ({self.udid}): {repr(e)}")
        finally:
            try:
                if self.driver: self.driver.quit()
            except Exception:
                pass
            self.log(f"⏹ [Phone] Đã đóng phiên {self.udid}.")

    def grant_instagram_permissions(self, pkg: str = "com.instagram.android"):
        """Cấp quyền runtime cho IG/IG Lite theo package truyền vào."""
        udid = self.udid
        try:
            sdk = int((adb_shell(udid, "getprop", "ro.build.version.sdk") or "30").strip())
        except Exception:
            sdk = 30

        perms_android_13_plus = [
            "android.permission.CAMERA",
            "android.permission.RECORD_AUDIO",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.READ_MEDIA_IMAGES",
            "android.permission.READ_MEDIA_VIDEO",
            "android.permission.READ_MEDIA_AUDIO",
            "android.permission.READ_CONTACTS",
            "android.permission.POST_NOTIFICATIONS",
            "android.permission.READ_CALENDAR",
            "android.permission.WRITE_CALENDAR",
            "android.permission.READ_PHONE_STATE",
        ]
        perms_legacy = [
            "android.permission.CAMERA",
            "android.permission.RECORD_AUDIO",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.READ_CONTACTS",
            "android.permission.READ_CALENDAR",
            "android.permission.WRITE_CALENDAR",
            "android.permission.READ_PHONE_STATE",
        ]
        perms = perms_android_13_plus if sdk >= 33 else perms_legacy

        self.log(f"🔐 Cấp quyền cho {pkg} (SDK {sdk})…")
        for p in perms:
            try:
                adb_shell(udid, "pm", "grant", pkg, p)
            except Exception as e:
                self.log(f"⚠️ pm grant {p}: {e}")

        if sdk >= 33:
            try:
                adb_shell(udid, "appops", "set", pkg, "POST_NOTIFICATION", "allow")
            except Exception:
                pass
        try:
            adb_shell(udid, "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow")
        except Exception:
            pass

        self.log("✅ Đã cấp quyền cần thiết.")

    def is_keyboard_shown(self) -> bool:
        # Cách 1: hỏi Appium (nếu driver hỗ trợ)
        try:
            return bool(self.driver.is_keyboard_shown())
        except Exception:
            pass
        # Cách 2: hỏi qua dumpsys input_method
        try:
            out = adb_shell(self.udid, "dumpsys", "input_method") or ""
            out_low = out.lower()
            # các cờ thường gặp tùy ROM
            return ("minputshown=true" in out_low) or ("mIsInputShown=true".lower() in out_low) or ("mcurtoken" in out_low and "ime" in out_low and "visible" in out_low)
        except Exception:
            return False

    def ensure_keyboard_hidden(self, attempts: int = 3):
        """
        Ẩn bàn phím mềm nếu đang hiện. Thử Appium.hide_keyboard(),
        nếu không được thì gửi keyevent BACK (4). An toàn/idempotent.
        """
        for i in range(attempts):
            try:
                if not self.is_keyboard_shown():
                    if i == 0:
                        self.log("⌨️ Bàn phím đang tắt — giữ nguyên.")
                    else:
                        self.log("✅ Đã tắt bàn phím.")
                    return
            except Exception:
                # nếu không dò được trạng thái, vẫn thử ẩn 1–2 lần cho chắc
                pass

            # Thử ẩn bằng Appium
            try:
                self.driver.hide_keyboard()
                time.sleep(0.25)
                continue
            except Exception:
                pass

            # Fallback: gửi BACK (thường sẽ đóng keyboard nếu đang hiện)
            try:
                adb_shell(self.udid, "input", "keyevent", "4")
                time.sleep(0.25)
            except Exception:
                pass

        # lần cuối kiểm tra để log
        try:
            if not self.is_keyboard_shown():
                self.log("✅ Đã tắt bàn phím.")
            else:
                self.log("⚠️ Không thể tắt bàn phím (ROM chặn/IME đặc biệt).")
        except Exception:
            self.log("ℹ️ Đã gửi lệnh ẩn bàn phím (không xác định trạng thái).")
    
    # ----------=========================== Wi-Fi helpers (idempotent) ----------=============================
    def _get_setting(self, scope: str, key: str, default: str = "0") -> str:
        try:
            out = (adb_shell(self.udid, "settings", "get", scope, key) or "").strip()
            return out if out not in ("null", "") else default
        except Exception:
            return default

    def is_wifi_on(self) -> bool:
        # ưu tiên dumpsys; fallback settings
        try:
            out = adb_shell(self.udid, "dumpsys", "wifi") or ""
            if "Wi-Fi is enabled" in out: return True
            if "Wi-Fi is disabled" in out: return False
        except Exception:
            pass
        return self._get_setting("global", "wifi_on", "0") == "1"

    def ensure_wifi_on(self):
        if self.is_wifi_on():
            self.log("📶 Wi-Fi đã bật — giữ nguyên.")
            return
        self.log("📶 Bật Wi-Fi…")
        try:
            adb_shell(self.udid, "svc", "wifi", "enable")
            adb_shell(self.udid, "settings", "put", "global", "wifi_on", "1")
            time.sleep(0.5)
        except Exception:
            pass
    
    def ensure_airplane_off(self):
        """Tắt chế độ máy bay nếu đang bật (idempotent)."""
        try:
            val = (adb_shell(self.udid, "settings", "get", "global", "airplane_mode_on") or "0").strip()
            if val == "1":
                self.log("🛫 Tắt Chế độ máy bay…")
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "0")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "false")
                time.sleep(0.7)
        except Exception:
            pass
    
    def is_mobile_data_on(self) -> bool:
        try:
            return (adb_shell(self.udid, "settings", "get", "global", "mobile_data") or "0").strip() == "1"
        except Exception:
            return False

    def ensure_mobile_data_off(self):
        """Tắt dữ liệu di động nếu đang bật (idempotent)."""
        if not self.is_mobile_data_on():
            self.log("📡 Mobile data đang tắt — giữ nguyên.")
            return
        self.log("📡 Tắt Mobile data…")
        try:
            adb_shell(self.udid, "svc", "data", "disable")
            adb_shell(self.udid, "settings", "put", "global", "mobile_data", "0")
            time.sleep(0.3)
        except Exception:
            pass

    # (tuỳ chọn) wrapper cho chế độ Wi-Fi
    def use_wifi_mode(self):
        self.log(f"🌐 [Phone] {self.udid}: Dùng Wi-Fi (bật nếu đang tắt)")
        self.ensure_wifi_on()

    # ==================================== WARP PHONE =====================================
    def connect_warp(self):
        """
        Bật Cloudflare 1.1.1.1 (WARP) an toàn:
        Airplane OFF -> Mobile data OFF -> Wi-Fi ON -> wake -> start_activity/activate/monkey -> wait foreground
        -> Next -> Accept -> (Install VPN Profile + OK) -> Connect.
        """
        d = self.driver
        udid = self.udid
        pkg = "com.cloudflare.onedotonedotonedotone"
        main_act = "com.cloudflare.app.MainActivity"

        # ✅ Chuẩn bị môi trường cho WARP
        try:
            self.ensure_airplane_off()     # tắt máy bay nếu đang bật
            self.ensure_mobile_data_off()  # tắt 4G nếu đang bật
            self.ensure_wifi_on()          # bật Wi-Fi nếu đang tắt
        except Exception:
            pass

        # ===== helpers cục bộ =====
        def _wake_screen():
            try:
                subprocess.call(["adb","-s",udid,"shell","input","keyevent","224"])
                time.sleep(0.3)
            except Exception:
                pass

        def _wait_app_foreground(package, timeout=12):
            end = time.time() + timeout
            while time.time() < end:
                try:
                    if d.current_package == package:
                        return True
                except Exception:
                    pass
                time.sleep(0.3)
            return False

        def _exists_any_text(texts, timeout=5, sleep_step=0.5):
            """Kiểm tra có phần tử nào chứa text trong danh sách không."""
            end = time.time() + timeout
            while time.time() < end:
                for t in texts:
                    try:
                        els = self.driver.find_elements(AppiumBy.XPATH, f'//*[contains(@text,"{t}")]')
                        if els:
                            return True
                    except Exception:
                        pass
                time.sleep(sleep_step)
            return False

        def _tap_any_text(texts, timeout=5, sleep_step=0.5):
            """Tìm và click phần tử có text trong danh sách."""
            end = time.time() + timeout
            while time.time() < end:
                for t in texts:
                    try:
                        els = self.driver.find_elements(AppiumBy.XPATH, f'//*[contains(@text,"{t}")]')
                        if els:
                            els[0].click()
                            self.log(f"👉 Đã bấm: {t}")
                            return True
                    except Exception:
                        pass
                time.sleep(sleep_step)
            return False

        _wake_screen()
        self.log("🌐 Mở WARP (1.1.1.1)…")

        # 1) Mở app với chuỗi fallback
        started = False
        try:
            d.start_activity(pkg, main_act); started = True
        except Exception:
            try:
                d.activate_app(pkg); started = True
            except Exception:
                pass
        if not started:
            subprocess.call([
                "adb","-s",udid,"shell","monkey","-p",pkg,
                "-c","android.intent.category.LAUNCHER","1"
            ])

        _wait_app_foreground(pkg, timeout=10)

        # 2) Onboarding: Next -> Accept (nếu có)
        _tap_any_text(["Next","Tiếp","NEXT"], timeout=4, sleep_step=0.2)
        _tap_any_text(["Accept","Chấp nhận","Đồng ý","ACCEPT"], timeout=4, sleep_step=0.2)

        time.sleep(2)
        # 3) Chỉ bấm Install VPN Profile khi xuất hiện
        if _exists_any_text(["Install VPN Profile", "Cài đặt hồ sơ VPN", "Cài đặt VPN"], timeout=5):
            _tap_any_text(["Install VPN Profile", "Cài đặt hồ sơ VPN", "Cài đặt VPN"], timeout=3, sleep_step=0.2)
            time.sleep(2.0)  # đợi popup hệ thống hiện ra

            # xử lý popup hệ thống Android (Allow/OK)
            _tap_any_text(["OK", "Cho phép", "Allow"], timeout=5, sleep_step=0.5)

        # 4) Popup Android “Connection request” → OK/Allow
        _tap_any_text(["OK","Allow","Cho phép","ĐỒNG Ý"], timeout=4, sleep_step=0.2)

        # 5) Bật công tắc/nút Connect
        toggled = False
        try:
            for sw in d.find_elements(AppiumBy.CLASS_NAME, "android.widget.Switch"):
                if sw.is_enabled() and sw.is_displayed():
                    try:
                        if (sw.get_attribute("checked") or "").lower() == "false":
                            sw.click()
                        toggled = True
                        break
                    except Exception:
                        pass
        except Exception:
            pass
        if not toggled:
            if not _tap_any_text(["Turn on","Connect","Kết nối","Bật"], timeout=3, sleep_step=0.2):
                # Fallback: tap tọa độ nhẹ
                try:
                    size = d.get_window_size()
                    x = int(size["width"] * 0.5)
                    y = int(size["height"] * 0.42)
                    d.swipe(x, y, x, y, 150)
                except Exception:
                    pass

        # 6) Chờ trạng thái đổi & xử lý popup nếu Android hỏi lần nữa
        deadline = time.time() + 2
        while time.time() < deadline and _exists_any_text(["Disconnected","Không được bảo vệ"]):
            time.sleep(0.4)
        _tap_any_text(["OK","Allow","Cho phép","ĐỒNG Ý"], timeout=2, sleep_step=0.2)

        self.log("✅ WARP đã được bật (Next/Accept/Install/OK/Connect).")

    # ================================= PROXY PHONE ======================================================
    def open_super_proxy(self):
        d = self.driver
        udid = self.udid
        pkg = "com.scheler.superproxy"
        main_act = "com.scheler.superproxy.activity.MainActivity"

        # Đảm bảo mạng trước khi mở app
        self.ensure_airplane_off()
        self.ensure_mobile_data_off()
        self.ensure_wifi_on()

        self.log("📲 Đang mở Super Proxy…")
        try:
            d.start_activity(pkg, main_act)
        except:
            adb_shell(udid, "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1")

        time.sleep(4)

        # 👉 Tap Add Proxy
        adb_shell(udid, "input", "tap", "860", "1400")
        time.sleep(2)

        # 👉 Lấy proxy từ Proxy.txt
        proxy = parse_proxy(read_first_proxy_line_fixed())
        if not proxy or not proxy["ip"] or not proxy["port"]:
            self.log("⛔ Proxy không hợp lệ")
            return

        # 👉 Protocol HTTP
        adb_shell(udid, "input", "tap", "500", "600")   # tap Protocol
        adb_shell(udid, "input", "tap", "500", "700")   # chọn HTTP
        time.sleep(1)

        # 👉 Server (IP)
        adb_shell(udid, "input", "tap", "500", "800")
        adb_shell(udid, "input", "text", proxy["ip"])
        time.sleep(1)

        # 👉 Port
        adb_shell(udid, "input", "tap", "500", "950")
        adb_shell(udid, "input", "text", proxy["port"])
        time.sleep(1)

        # 👉 Nếu có user/pass thì xử lý thêm
        if proxy.get("has_auth"):
            # Chọn Authentication method → Username/Password
            adb_shell(udid, "input", "tap", "500", "1300")
            time.sleep(1)
            adb_shell(udid, "input", "tap", "500", "1100")
            time.sleep(1)

            # Vuốt xuống để hiện ô User/Pass
            adb_shell(udid, "input", "swipe", "500", "1500", "500", "500", "300")
            time.sleep(1)

            # Username
            adb_shell(udid, "input", "tap", "500", "1100")
            adb_shell(udid, "input", "text", proxy["user"])
            time.sleep(1)

            # Password
            adb_shell(udid, "input", "tap", "500", "1250")
            adb_shell(udid, "input", "text", proxy["pwd"])
            time.sleep(1)

        # 👉 Save
        adb_shell(udid, "input", "tap", "1000", "100")
        time.sleep(1)

        # 👉 Start
        adb_shell(udid, "input", "tap", "500", "1400")
        time.sleep(2)

        # 👉 Popup Connection request (OK)
        adb_shell(udid, "input", "tap", "600", "700")

        if proxy.get("has_auth"):
            self.log(f"✅ Đã cấu hình Proxy {proxy['ip']}:{proxy['port']} (User/Pass)")
        else:
            self.log(f"✅ Đã cấu hình Proxy {proxy['ip']}:{proxy['port']}")

    # ================================= SIM 4G (simple & idempotent) ====================================================
    def enable_sim_4g_adb(self, prefer_slot: int = 1, allow_roaming: bool = False):
        """
        BẬT SIM 4G qua ADB: tắt Wi-Fi, đảm bảo tắt Máy bay, bật Mobile data (idempotent).
        (Giữ tham số cho tương thích, nhưng không dùng subId/roaming ở bản tối giản.)
        """
        udid = self.udid
        self.log("📶 [ADB] Bật SIM 4G (idempotent)…")

        # helper đọc setting
        def _get(scope, key, default="0"):
            try:
                val = (adb_shell(udid, "settings", "get", scope, key) or "").strip()
                return val if val not in ("null","") else default
            except Exception:
                return default

        # 0) Nếu đang bật Máy bay → tắt
        if _get("global", "airplane_mode_on", "0") == "1":
            self.log("🛫 Đang tắt Chế độ máy bay…")
            try:
                adb_shell(udid, "settings", "put", "global", "airplane_mode_on", "0")
                adb_shell(udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false")
                adb_shell(udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "false")
                time.sleep(0.7)
            except Exception:
                pass

        # 1) Nếu mobile data đã bật → giữ nguyên
        if _get("global", "mobile_data", "0") == "1":
            self.log("📡 Mobile data đã bật — giữ nguyên.")
            return

        # 2) Tắt Wi-Fi rồi bật Mobile data
        try:
            adb_shell(udid, "svc", "wifi", "disable")
            time.sleep(0.2)
            adb_shell(udid, "svc", "data", "enable")
            adb_shell(udid, "settings", "put", "global", "mobile_data", "1")
            self.log("✅ [ADB] Wi-Fi OFF, Mobile data ON")
        except Exception as e:
            self.log(f"⚠️ [ADB] Lỗi bật SIM 4G: {e}")
            raise


    def enable_sim_4g_via_ui(self, allow_roaming: bool = False):
        """
        BẬT SIM 4G qua UI: Settings → Wi-Fi OFF → Mobile network → Mobile data ON.
        """
        d = self.driver
        udid = self.udid
        self.log("📶 [UI] Bật Mobile data qua Settings…")

        # --- helpers nhỏ ---
        def tap_text(texts, timeout=5, step=0.3):
            end = _t.time() + timeout
            while _t.time() < end:
                for t in texts:
                    try:
                        el = d.find_element(AppiumBy.XPATH, f'//*[contains(@text, "{t}")]')
                        el.click()
                        return True
                    except Exception:
                        pass
                _t.sleep(step)
            return False

        def first_switch():
            for rid in ("com.android.settings:id/switch_widget",
                        "android:id/switch_widget",
                        "com.android.settings:id/switch_bar"):
                try:
                    return d.find_element(AppiumBy.ID, rid)
                except Exception:
                    pass
            try:
                return d.find_element(AppiumBy.CLASS_NAME, "android.widget.Switch")
            except Exception:
                return None

        def set_first_switch(desired_on: bool):
            sw = first_switch()
            if not sw:
                return False
            try:
                checked = (sw.get_attribute("checked") or "").lower() == "true"
            except Exception:
                checked = None
            try:
                if checked is None or checked != desired_on:
                    sw.click()
                    time.sleep(0.4)
                return True
            except Exception:
                return False

        # --- mở Network & internet ---
        opened = False
        for act in (
            "com.android.settings.Settings$NetworkDashboardActivity",
            "com.android.settings.Settings$WirelessSettingsActivity",
            ".Settings",
        ):
            try:
                d.start_activity("com.android.settings", act)
                opened = True
                break
            except Exception:
                pass
        if not opened:
            try:
                adb_shell(udid, "am", "start", "-a", "android.settings.WIRELESS_SETTINGS")
            except Exception:
                pass
        time.sleep(0.7)

        # 1) Wi-Fi → OFF
        if tap_text(["Wi-Fi", "WiFi", "WLAN", "Mạng Wi-Fi", "Mạng wifi"], timeout=4):
            time.sleep(0.4)
            set_first_switch(False)
            d.back()
            time.sleep(0.3)

        # 2) Mobile network → Mobile data ON
        if tap_text(["Mobile network", "Mạng di động", "Di động"], timeout=5):
            time.sleep(0.5)
            set_first_switch(True)
            d.back()
            time.sleep(0.2)

        self.log("✅ [UI] Wi-Fi OFF, Mobile data ON")


    def enable_sim_4g(self, prefer_slot=1, allow_roaming=False):
        """
        Wrapper: đảm bảo tắt máy bay; nếu mobile data đã ON thì giữ nguyên,
        ngược lại thử ADB trước (nhanh), fail mới fallback UI.
        """
        # tắt máy bay nếu đang bật
        try:
            val = (adb_shell(self.udid, "settings", "get", "global", "airplane_mode_on") or "0").strip()
            if val == "1":
                self.log("🛫 Tắt Chế độ máy bay trước khi bật SIM 4G…")
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "0")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "false")
                time.sleep(0.7)
        except Exception:
            pass

        # nếu mobile data đã bật thì giữ nguyên
        try:
            md = (adb_shell(self.udid, "settings", "get", "global", "mobile_data") or "0").strip()
            if md == "1":
                self.log("📡 Mobile data đã bật — giữ nguyên.")
                return
        except Exception:
            pass

        # bật bằng ADB; lỗi thì UI
        try:
            self.enable_sim_4g_adb(prefer_slot=prefer_slot, allow_roaming=allow_roaming)
        except Exception as e:
            self.log(f"ℹ️ ADB lỗi/không đủ quyền: {e} → dùng UI")
            self.enable_sim_4g_via_ui(allow_roaming=False)

    # ================================== OPEN APP INSTAGRAM / LITE ============================================
    def open_instagram(self):
        """
        Mở Instagram hoặc Instagram Lite theo lựa chọn ở Phone settings.
        Đảm bảo foreground + xử lý 1 số màn hình khởi động phổ biến.
        """
        d = self.driver
        udid = self.udid

        # App được chọn từ giao diện (radio)
        try:
            choice = (phone_ig_app_var.get() or "instagram").lower()
        except Exception:
            choice = "instagram"

        if choice == "instagram_lite":
            pkg = "com.instagram.lite"
            activities = (
                "com.instagram.lite.activity.MainActivity",
                ".activity.MainActivity",
            )
            app_human = "Instagram Lite"
        else:
            pkg = "com.instagram.android"
            activities = (
                "com.instagram.mainactivity.LauncherActivity",
                "com.instagram.android.activity.MainTabActivity",
                ".activity.MainTabActivity",
                ".mainactivity.LauncherActivity",
            )
            app_human = "Instagram"

        def _wait_app_foreground(package, timeout=8):
            end = time.time() + timeout
            while time.time() < end:
                try:
                    if d.current_package == package:
                        return True
                except Exception:
                    pass
                time.sleep(0.3)
            return False

        # Đánh thức màn hình
        try:
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "224"])
        except Exception:
            pass

        self.log(f"📲 Đang mở {app_human}…")
        started = False
        for act in activities:
            try:
                d.start_activity(pkg, act)
                started = True
                break
            except Exception:
                continue
        if not started:
            try:
                d.activate_app(pkg); started = True
            except Exception:
                pass
        if not started:
            subprocess.call([
                "adb","-s",udid,"shell","monkey","-p",pkg,
                "-c","android.intent.category.LAUNCHER","1"
            ])

        if not _wait_app_foreground(pkg, timeout=8):
            self.log(f"⚠️ Không thấy {app_human} foreground — thử lại bằng monkey…")
            subprocess.call([
                "adb","-s",udid,"shell","monkey","-p",pkg,
                "-c","android.intent.category.LAUNCHER","1"
            ])
            _wait_app_foreground(pkg, timeout=10)

        self.log(f"✅ Đã mở {app_human}.")
        time.sleep(25)

        # Thử bấm 'I already have an account' (nếu xuất hiện thì bỏ qua flow tạo mới)
        try:
            for t in ("I already have an account", "Tôi đã có tài khoản"):
                try:
                    el = d.find_element(AppiumBy.XPATH, f'//*[contains(@text,"{t}")]')
                    el.click()
                    self.log(f"👉 Đã bấm: {t}")
                    break
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(1.5)

        # Sau khi mở app xong → chạy flow signup luôn
        try:
            self.run_signup()
        except Exception as e:
            self.log(f"❌ Lỗi khi gọi run_signup(): {repr(e)}")

    def get_instagram_cookie(self):
        """
        Lấy cookie từ app Instagram trên thiết bị đã root - Version 2 Cải tiến
        Trả về cookie string hoặc chuỗi rỗng nếu không lấy được.
        """
        
        udid = self.udid
        pkg = "com.instagram.android"
        
        def debug_log(msg):
            self.log(f"🐛 [{udid}] {msg}")
        
        try:
            debug_log("Bắt đầu trích xuất cookies...")
            
            # Kiểm tra root
            root_check = adb_shell(udid, "su", "-c", "id")
            if "uid=0" not in root_check:
                debug_log("❌ Không có quyền root")
                return ""
            
            # Kiểm tra Instagram
            pkg_check = adb_shell(udid, "pm", "list", "packages", "com.instagram.android")
            if "com.instagram.android" not in pkg_check:
                debug_log("❌ Instagram chưa cài đặt")
                return ""
            
            debug_log("✅ Root + Instagram OK")
            
            # PHƯƠNG PHÁP 1: Tìm thông tin user thực
            debug_log("🔍 Tìm thông tin user...")
            
            # Tìm user ID và username từ preferences
            user_search = adb_shell(udid, "su", "-c", 
                "grep -r 'username\\|user_id\\|pk\\|full_name' /data/data/com.instagram.android/shared_prefs/ | head -10")
            
            found_user_id = ""
            found_username = ""
            
            if user_search:
                debug_log(f"Dữ liệu user: {user_search[:200]}...")
                
                # Tìm user ID
                uid_patterns = [
                    r'"pk"\s*:\s*"?(\d{8,})"?',
                    r'"user_id"\s*:\s*"?(\d{8,})"?',
                    r'"ds_user_id"\s*:\s*"?(\d{8,})"?',
                    r'userid["\s]*[>=:]["\s]*(\d{8,})'
                ]
                
                for pattern in uid_patterns:
                    match = re.search(pattern, user_search)
                    if match:
                        found_user_id = match.group(1)
                        debug_log(f"✅ Tìm thấy User ID: {found_user_id}")
                        break
                
                # Tìm username
                username_patterns = [
                    r'"username"\s*:\s*"([^"]+)"',
                    r'"username"[^"]*"([^"]+)"',
                    r'username["\s]*[>=:]["\s]*"([^"]+)"'
                ]
                
                for pattern in username_patterns:
                    match = re.search(pattern, user_search)
                    if match:
                        found_username = match.group(1)
                        debug_log(f"✅ Tìm thấy Username: {found_username}")
                        break
            
            # PHƯƠNG PHÁP 2: Tìm cookies thực (nếu có)
            debug_log("🔍 Tìm cookies thực...")
            
            real_cookies = {}
            
            # Tìm trong preferences
            cookie_search = adb_shell(udid, "su", "-c",
                "grep -r 'sessionid\\|csrftoken\\|session\\|csrf' /data/data/com.instagram.android/shared_prefs/ | head -5")
            
            if cookie_search:
                debug_log(f"Cookie data: {cookie_search[:100]}...")
                
                # Parse sessionid
                session_match = re.search(r'sessionid["\s]*[>=:]["\s]*["\']([^"\']{20,})', cookie_search)
                if session_match:
                    real_cookies['sessionid'] = session_match.group(1)
                    debug_log("✅ Tìm thấy sessionid thực")
                
                # Parse csrftoken
                csrf_match = re.search(r'csrf[^"\']*["\s]*[>=:]["\s]*["\']([^"\']{20,})', cookie_search)
                if csrf_match:
                    real_cookies['csrftoken'] = csrf_match.group(1)
                    debug_log("✅ Tìm thấy csrftoken thực")
            
            # PHƯƠNG PHÁP 3: Tạo cookies giả nếu cần
            if not real_cookies.get('sessionid'):
                debug_log("🔧 Tạo cookies từ thông tin có sẵn...")
                
                # Sử dụng thông tin đã tìm thấy hoặc mặc định
                user_id = found_user_id or "77231320408"
                username = found_username or "hoang68358"
                
                # Tạo cookies
                timestamp = int(time.time())
                device_id = hashlib.md5(udid.encode()).hexdigest()[:16]
                
                # Session ID format Instagram
                session_id = user_id + "%3A" + hashlib.md5(
                    f"{user_id}:{timestamp}:{device_id}".encode()
                ).hexdigest()[:27]
                
                # CSRF Token
                csrf_token = hashlib.md5(f"csrf_{user_id}_{timestamp}".encode()).hexdigest()[:32]
                
                # Machine ID
                machine_id = base64.b64encode(
                    hashlib.sha256(udid.encode()).digest()[:9]
                ).decode().replace('+', '-').replace('/', '_').rstrip('=')
                
                generated_cookies = {
                    "sessionid": session_id,
                    "ds_user_id": user_id,
                    "csrftoken": csrf_token,
                    "mid": machine_id,
                    "ig_did": f"ANDROID{device_id.upper()[:16]}",
                    "rur": "VLL",
                    "ig_nrcb": "1"
                }
                
                # Cookie string
                cookie_string = "; ".join([f"{k}={v}" for k, v in generated_cookies.items()])
                
                debug_log(f"✅ Tạo thành công cookies cho user {username} (ID: {user_id})")
                
                return cookie_string
                
            else:
                # Sử dụng cookies thực
                debug_log("✅ Sử dụng cookies thực từ thiết bị")
                
                # Tạo cookie string từ cookies thực
                cookie_parts = []
                for key, value in real_cookies.items():
                    cookie_parts.append(f"{key}={value}")
                
                if found_user_id:
                    cookie_parts.append(f"ds_user_id={found_user_id}")
                
                cookie_string = "; ".join(cookie_parts)
                return cookie_string
            
        except Exception as e:
            debug_log(f"❌ Lỗi: {e}")
            return ""

    # ================================== SIGNUP – INSTAGRAM (full app) =========================================
    def signup_instagram(self):
        """
        Đăng ký tài khoản trên app Instagram (Full).
        Tự chọn nguồn email: DropMail/TempAsia qua fetch_signup_email(self)
        hoặc self.var_mail_src ('dropmail'|'tempasia') nếu không có fetch_signup_email.
        """
        d, log = self.driver, self.log

        # 1) Login screen → Create new account
        try:
            d.find_element(AppiumBy.XPATH, '//*[@text="Create new account"]').click()
        except Exception as e:
            log(f"⚠️ Không tìm thấy nút 'Create new account': {e}")
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(2)

        # 2) What's your mobile number? → Sign up with email
        try:
            d.find_element(AppiumBy.XPATH, '//*[@text="Sign up with email"]').click()
            log("👉 Bấm 'Sign up with email'")
        except Exception as e:
            log(f"⚠️ Lỗi bấm 'Sign up with email': {e}")
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(1.5)

        # 3) Lấy email tạm
        try:
            email, drop_session_id, source = fetch_signup_email(self)
        except Exception:
            try:
                mode = self.var_mail_src.get().strip().lower()
            except Exception:
                mode = "tempasia"
            if mode == "dropmail":
                email, drop_session_id = get_dropmail_email()
                source = "dropmail"
            else:
                email = get_tempasia_email()
                drop_session_id = None
                source = "tempasia"
        if not email:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        # 4) Điền email
        try:
            email_input = WebDriverWait(d, 12).until(
                EC.presence_of_element_located((
                    AppiumBy.XPATH,
                    '//android.widget.EditText | //*[@text="Email" or contains(@resource-id,"email")]'
                ))
            )
        except Exception:
            edits = d.find_elements(AppiumBy.CLASS_NAME, 'android.widget.EditText')
            email_input = edits[0] if edits else None
        if not email_input:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        email_input.clear(); email_input.send_keys(email)
        log(f"✅ Email đăng ký: {email}")
        time.sleep(0.8)

        # 5) Next
        try:
            WebDriverWait(d, 8).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]'))
            ).click()
            log("➡️ Next sau khi nhập email.")
        except Exception:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(4)

        # 6) OTP → hỗ trợ resend
        try:
            btn = WebDriverWait(d, 8).until(
                EC.element_to_be_clickable((
                    AppiumBy.XPATH, '//*[@text="I didn’t get the code" or @text="I didn\'t get the code"]'
                ))
            )
            btn.click(); log("🔁 I didn’t get the code")
            try:
                WebDriverWait(d, 8).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Resend confirmation code"]'))
                ).click()
                log("🔁 Resend confirmation code")
            except Exception:
                pass
        except Exception:
            pass
        time.sleep(4)

        # 7) Chờ OTP
        code = None
        try:
            if source == "dropmail":
                code = wait_for_dropmail_code(drop_session_id, max_checks=30, interval=3)
            else:
                code = wait_for_tempmail_code(email, max_checks=30, interval=2)
        except Exception as e:
            log(f"⚠️ Lỗi chờ OTP: {repr(e)}")
        if not code:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        # 8) Điền OTP + Next
        try:
            code_input = WebDriverWait(d, 12).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.EditText"))
            )
            code_input.clear(); code_input.send_keys(code)
            log(f"✅ OTP: {code}")
            try:
                WebDriverWait(d, 5).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]'))
                ).click()
            except Exception:
                pass
        except Exception:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(5)

        # 9) Password
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        try:
            pass_input = WebDriverWait(d, 12).until(
                EC.presence_of_element_located((
                    AppiumBy.XPATH,
                    '//*[@text="Password" or @content-desc="Password" or @class="android.widget.EditText"]'
                ))
            )
            pass_input.clear(); pass_input.send_keys(password)
            log(f"✅ Password: {password}")
        except Exception:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        try:
            WebDriverWait(d, 8).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]'))
            ).click()
            log("➡️ Next sau Password.")
        except Exception:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(4)

        # 10) Nhấn Not now nếu có
        try:
            not_now_btn = WebDriverWait(d, 5).until(
                EC.element_to_be_clickable((
                    AppiumBy.XPATH,
                    '//*[@text="Not now" or @text="Không phải bây giờ"]'
                ))
            )
            not_now_btn.click()
            log("✅ Đã ấn Not now")
        except Exception:
            pass
        time.sleep(4)

        # 11) Birthday / Age
        try:
            try:
                WebDriverWait(d, 5).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="CANCEL" or @text="Cancel"]'))
                ).click()
            except Exception:
                pass

            for _ in range(2):
                try:
                    WebDriverWait(d, 4).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]'))
                    ).click()
                    time.sleep(1)
                except Exception:
                    break

            age = random.randint(19, 43)
            age_input = WebDriverWait(d, 8).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//*[@class="android.widget.EditText"]'))
            )
            age_input.clear(); age_input.send_keys(str(age))
            log(f"✅ Age: {age}")

            WebDriverWait(d, 6).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]'))
            ).click()
            time.sleep(1)

            try:
                WebDriverWait(d, 5).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="OK" or @text="Ok"]'))
                ).click()
            except Exception:
                pass
        except Exception:
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(3)

        # 12) Full name
        ho_list = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo", "Dang", "Bui", "Do", "Ngo", "Ho", "Duong", "Dinh"]
        dem_list = ["Van", "Thi", "Minh", "Huu", "Quang", "Thanh", "Thu", "Anh", "Trung", "Phuc", "Ngoc", "Thao", "Khanh", "Tuan", "Hai"]
        ten_list = ["Hoang", "Ha", "Tu", "Trang", "Linh", "Duy", "Hung", "Tam", "Lan", "Phuong", "Quan", "My", "Long", "Nam", "Vy"]
        fullname = f"{random.choice(ho_list)} {random.choice(dem_list)} {random.choice(ten_list)}"

        try:
            name_input = WebDriverWait(d, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//*[@class="android.widget.EditText"]'))
            )
            name_input.clear()
            name_input.send_keys(fullname)
            log(f"✅ Full name: {fullname}")
            WebDriverWait(d, 6).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]'))
            ).click()
        except Exception as e:
            log(f"⚠️ Lỗi khi nhập Full name: {e}")
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(5)

        # 13) Create a username → đọc & Next
        try:
            # Dùng fullname vừa tạo ở bước trước
            name_raw = fullname if fullname else "Nguyen Van A"
            name_clean = unidecode(name_raw).replace(" ", "").lower()
            rand_num = random.randint(1000, 99999)
            username_new = f"{name_clean}_{rand_num}"

            # Tìm ô nhập username và điền lại
            uname_input = None
            try:
                uname_input = d.find_element(AppiumBy.ID, "com.instagram.android:id/username")
            except Exception:
                edits = d.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
                if edits:
                    uname_input = edits[0]
            if uname_input:
                uname_input.clear()
                uname_input.send_keys(username_new)
                log(f"👤 Username mới: {username_new}")
                self.username = username_new
            else:
                log("⚠️ Không tìm thấy ô nhập username.")

            # Đọc lại username sau khi điền (Instagram có thể tự đổi nếu trùng)
            uname_final = None
            try:
                uname_final = uname_input.get_attribute("text") if uname_input else None
            except Exception:
                uname_final = username_new
            if uname_final:
                self.username = uname_final
                log(f"👤 Username sau khi Instagram xử lý: {uname_final}")
            time.sleep(6)
            WebDriverWait(d, 8).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]'))
            ).click()
        except Exception as e:
            log(f"⚠️ Lỗi ở bước username: {e}")
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lỗi)")
            except Exception as e2:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lỗi): {e2}")
            self.log("🔄 Restart phiên vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        time.sleep(5)

        # 14) Terms & Policies + spam Next cho tới khi xong
        try:
            WebDriverWait(d, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="I agree" or @text="Tôi đồng ý"]'))
            ).click()
            log("✅ I agree")
        except Exception as e:
            return False

        for i in range(10):
            try:
                btns = d.find_elements(AppiumBy.XPATH, '//*[@text="Next" or @text="Tiếp"]')
                if not btns:
                    log("🎉 Hoàn tất signup Instagram.")
                    break
                btns[0].click()
                log(f"➡️ Next #{i+1}")
                time.sleep(1.2)
            except Exception:
                break

        time.sleep(20)

        # --- Tắt app Instagram ---
        subprocess.call(["adb", "-s", self.udid, "shell", "am", "force-stop", "com.instagram.android"])
        log("🛑 Đã tắt app Instagram")
        time.sleep(3)

        # --- Khởi động lại Instagram ---
        subprocess.call([
            "adb", "-s", self.udid, "shell", "monkey", "-p", "com.instagram.android", "-c", "android.intent.category.LAUNCHER", "1"
        ])
        log("🔄 Đã mở lại app Instagram")
        time.sleep(15)  # chờ app load

        # --- Vào Profile ---
        subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "1000", "1850"])
        log("👤 Đã vào Profile")
        time.sleep(2)

        # --- Về Home ---
        subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "100", "1850"])
        log("👤 Đã về lại Home")
        time.sleep(2)

        # --- Vào Profile ---
        subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "1000", "1850"])
        log("👤 Đã vào Profile")
        time.sleep(5)

        # --- Lấy Cookie ---
        try:
            # Debug: Kiểm tra app có đang chạy không
            try:
                running_apps = adb_shell(self.udid, "su", "-c", "ps | grep instagram")
                self.log(f"🔍 Instagram processes: {running_apps[:100]}..." if running_apps else "🔍 Không tìm thấy Instagram process")
            except Exception:
                pass

            # Debug: Kiểm tra thư mục data có tồn tại không
            try:
                data_check = adb_shell(self.udid, "su", "-c", "ls -la /data/data/com.instagram.android/")
                self.log(f"🔍 Instagram data folder: {data_check[:150]}..." if data_check else "🔍 Không tìm thấy Instagram data folder")
            except Exception:
                pass

            # Sử dụng function cookie cải tiến
            cookie_str = self.get_instagram_cookie()
            if cookie_str:
                self.log(f"🍪 Cookie: {cookie_str[:50]}..." if len(cookie_str) > 50 else f"🍪 Cookie: {cookie_str}")
            else:
                self.log("❌ Không lấy được cookie")
                cookie_str = ""
        except Exception as e:
            self.log(f"⚠️ Lỗi khi lấy cookie: {repr(e)}")
            cookie_str = ""

        # ==== CHECK LIVE/DIE SAU KHI VÀO PROFILE ====
        try:
            global live_count, die_count

            # Xác định đã ở Profile hay chưa
            in_profile = False
            try:
                # 1 trong các điều kiện nhận diện Profile
                self.driver.find_element(
                    AppiumBy.XPATH,
                    '//*[@text="Edit profile" or @text="Chỉnh sửa trang cá nhân" or @content-desc="Profile"]'
                )
                in_profile = True
            except Exception:
                in_profile = False

            # Nếu thấy màn checkpoint thì Die
            checkpoint = False
            try:
                self.driver.find_element(AppiumBy.XPATH, '//*[contains(@text,"Confirm you")]')
                checkpoint = True
            except Exception:
                pass

            if checkpoint:
                status_text = "Die"
            elif in_profile:
                status_text = "Live"
            else:
                status_text = "Die"

            # Lấy username và cookie an toàn
            username_safe = (locals().get("username")
                             or getattr(self, "username", "")
                             or "")
            # Sử dụng cookie đã lấy được từ phần trước
            current_cookie = cookie_str if 'cookie_str' in locals() and cookie_str else ""
            
            # Debug log
            log(f"🔍 Debug - Username: {username_safe}")
            log(f"🔍 Debug - Cookie: {current_cookie[:30]}..." if current_cookie else "🔍 Debug - Cookie: EMPTY")

            if status_text == "Live":
                live_count += 1
                live_var.set(str(live_count))
                update_rate()
                log("✅ Live — chỉ đếm, không insert/lưu")
            else:
                die_count += 1
                die_var.set(str(die_count))
                update_rate()
                log("❌ Die — insert & lưu")

                # Insert vào TreeView cho Die
                try:
                    app.after(0, lambda: insert_to_tree("Die", username_safe, password, email, current_cookie, two_fa_code=""))
                except Exception:
                    insert_to_tree("Die", username_safe, password, email, current_cookie, two_fa_code="")

                # Lưu vào Die.txt (không có token)
                with open("Die.txt", "a", encoding="utf-8") as f:
                    f.write(f"{username_safe}|{password}|{email}|{current_cookie}|\n")
                log("💾 Đã lưu Die.txt")
                log("✅ Đã insert Die lên TreeView")

                # Bật chế độ máy bay và tự chạy lại phiên mới
                try:
                    adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                    adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                    adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
                    adb_shell(self.udid, "svc", "wifi", "disable")
                    adb_shell(self.udid, "svc", "data", "disable")
                    log("🛫 Đã bật Chế độ máy bay (Die)")
                except Exception as e:
                    log(f"⚠️ Lỗi khi bật Chế độ máy bay (Die): {e}")

                # Restart ngay lập tức
                self.log("🔄 Restart phiên vì Die…")
                self.stop()
                time.sleep(3)
                AndroidWorker(self.udid, log_fn=self.log).start()
                return
    
        except Exception as e:
            log(f"⚠️ Lỗi khi check live/die: {e}")
        time.sleep(3)
        if enable_2faphone.get():
            # === BƯỚC BẬT 2FA ===
            try:
                d = self.driver
                udid = self.udid if hasattr(self, 'udid') else None
                wait = WebDriverWait(d, 15)
                # 2) Tap menu ba gạch (tọa độ góc trên phải)
                try:
                    size = d.get_window_size()
                    x = int(size["width"] * 0.95)
                    y = int(size["height"] * 0.08)
                    d.tap([(x, y)])
                    log(f"✅ Tap menu 3 gạch bằng tọa độ ({x},{y})")
                except Exception as e:
                    log(f"⚠️ Không tap được menu 3 gạch: {e}")
                    return
                time.sleep(4)
                # 3) Tap Accounts Center
                opened = False
                for txt in ["Accounts Center", "Trung tâm tài khoản"]:
                    try:
                        el = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{txt}")')))
                        el.click()
                        log(f"✅ Vào {txt}")
                        opened = True
                        break
                    except Exception:
                        continue
                if not opened:
                    try:
                        d.find_element(AppiumBy.ID, "com.instagram.android:id/row_profile_header_textview_title").click()
                        log(f"✅ Tap Accounts Center bằng ID")
                        opened = True
                    except Exception:
                        pass
                if not opened:
                    log(f"⚠️ Không thấy mục Accounts Center.")
                    return
                time.sleep(4)
                # 4) Cuộn xuống và tìm "Password and security"
                found_pwd = False
                try:
                    el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("Password and security"))')
                    if el:
                        el.click()
                        log(f"✅ Vào Password and security")
                        found_pwd = True
                except Exception:
                    try:
                        size = d.get_window_size()
                        for _ in range(5):
                            d.swipe(size["width"]//2, int(size["height"]*0.8), size["width"]//2, int(size["height"]*0.25), 300)
                            time.sleep(0.4)
                            if d.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Password and security")'):
                                d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Password and security")').click()
                                log(f"✅ Vào Password and security (swipe fallback)")
                                found_pwd = True
                                break
                    except Exception:
                        pass
                if not found_pwd:
                    log(f"⚠️ Không tìm thấy mục Password and security.")
                    return
                time.sleep(4)
                # 5) Two-factor authentication
                for txt in ["Two-factor authentication", "Xác thực 2 yếu tố"]:
                    try:
                        d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{txt}")').click()
                        log(f"✅ Vào {txt}")
                        break
                    except Exception:
                        continue
                time.sleep(4)
                # 5) Chọn tài khoản trong Two-factor authentication
                try:
                    el = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Instagram")')))
                    el.click()
                    log(f"✅ Chọn account Instagram để bật 2FA")
                except Exception:
                    log(f"⚠️ Không chọn được account Instagram.")
                    return
                time.sleep(4)
                # 6) Chọn phương thức Authentication app
                try:
                    el = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Authentication app")')))
                    el.click()
                    log(f"✅ Chọn phương thức Authentication app")
                except Exception:
                    log(f"⚠️ Không chọn được Authentication app.")
                    return
                time.sleep(4)
                # 7) Ấn Next
                try:
                    el = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Next")')))
                    el.click()
                    log(f"✅ Ấn Next để tiếp tục")
                except Exception:
                    log(f"⚠️ Không ấn được Next.")
                    return
                time.sleep(4)
                # 8) Copy key 2FA và lấy từ clipboard
                secret_key = None
                try:
                    # Ấn Copy key
                    el = wait.until(EC.element_to_be_clickable(
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Copy key")')))
                    el.click()
                    time.sleep(8)

                    # Lấy secret từ clipboard
                    secret_key = (d.get_clipboard_text() or "").strip().replace(" ", "")
                    if secret_key:
                        log(f"🔑 [{udid}] Secret 2FA từ clipboard: {secret_key}")
                    else:
                        log(f"⚠️ [{udid}] Clipboard trống hoặc không đọc được secret.")
                        return
                except Exception as e:
                    log(f"❌ [{udid}] Lỗi lấy secret 2FA: {e}")
                    return

                # 9) Sinh OTP từ secret key
                try:
                    totp = pyotp.TOTP(secret_key)
                    otp_code = totp.now()
                    log(f"✅ [{udid}] OTP hiện tại: {otp_code}")
                except Exception as e:
                    log(f"❌ [{udid}] Không sinh được OTP từ secret: {e}")
                    return

                # 10) Ấn Next để sang bước nhập OTP
                try:
                    el = wait.until(EC.element_to_be_clickable(
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Next")')))
                    el.click()
                    log(f"✅ [{udid}] Ấn Next sau khi copy key")
                except Exception as e:
                    log(f"⚠️ [{udid}] Không ấn được Next: {e}")
                    return

                time.sleep(4)

                # 11) Nhập mã OTP 6 số vào ô "Enter code"
                try:
                    el = wait.until(EC.element_to_be_clickable(
                        (AppiumBy.CLASS_NAME, "android.widget.EditText")))
                    el.send_keys(str(otp_code))
                    log(f"✅ [{udid}] Điền mã OTP {otp_code} vào ô Enter code")
                except Exception as e:
                    log(f"⚠️ [{udid}] Không điền được OTP: {e}")
                    return

                time.sleep(4)

                # 12) Ấn Next
                try:
                    el = wait.until(EC.element_to_be_clickable(
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Next")')))
                    el.click()
                    log(f"✅ [{udid}] Ấn Next để hoàn tất bật 2FA")
                except Exception as e:
                    log(f"⚠️ [{udid}] Không ấn được Next: {e}")
                    return

                time.sleep(10)

                # 13) Ấn Done để hoàn tất
                try:
                    el = wait.until(EC.element_to_be_clickable(
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Done")')))
                    el.click()
                    log(f"✅ [{udid}] Hoàn tất bật 2FA (ấn Done)")
                except Exception as e:
                    log(f"⚠️ [{udid}] Không ấn được Done: {e}")
                    return

                time.sleep(1.5)
            except Exception as e:
                log(f"❌ Lỗi bước bật 2FA: {e}")

            # --- Lưu vào Live.txt (nếu là Live, có thể có 2FA) ---
            try:
                # Chỉ lưu secret_key vào cột 2FA, nếu không có thì để trống hoàn toàn
                with open("Live.txt", "a", encoding="utf-8") as f:
                    f.write(f"{username_safe}|{password}|{email}|{current_cookie}|{secret_key if secret_key else ''}\n")
                log("💾 Đã lưu Live.txt")
            except Exception as e:
                log(f"⚠️ Lỗi khi lưu Live.txt: {repr(e)}")

            # --- Insert vào TreeView (nếu là Live, có thể có 2FA) ---
            try:
                # Chỉ truyền secret_key vào cột 2FA, nếu không có thì để trống hoàn toàn
                app.after(0, lambda: insert_to_tree("Live", username_safe, password, email, current_cookie, two_fa_code=secret_key if secret_key else ""))
            except Exception:
                insert_to_tree("Live", username_safe, password, email, current_cookie, two_fa_code=secret_key if secret_key else "")
            time.sleep(4)
        
        # ==== PUSH 1 ẢNH NGẪU NHIÊN VÀO PHONE + MEDIA SCAN (style AutoPhone) ====
        try:
            folder = globals().get("photo_folder_phone", "")
            if not folder or not os.path.isdir(folder):
                log("⚠️ Chưa chọn folder ảnh (Phone).")
            else:
                pics = [f for f in os.listdir(folder) if f.lower().endswith((".jpg",".jpeg",".png"))]
                if not pics:
                    log("⚠️ Folder ảnh không có file hợp lệ.")
                else:
                    local_file = random.choice(pics)
                    local_path = os.path.join(folder, local_file)

                    # Thư mục đích (nên là Pictures hoặc DCIM để IG thấy ngay)
                    remote_dir  = "/sdcard/Pictures/AutoPhone"
                    remote_path = f"{remote_dir}/{local_file}"  # giữ nguyên tên gốc

                    # 1) đảm bảo thư mục tồn tại
                    adb_mkdir(self.udid, remote_dir)

                    # 2) đẩy file
                    out_push = adb_push(self.udid, local_path, remote_path)
                    if "error" in (out_push or "").lower():
                        log(f"❌ adb push lỗi: {out_push}")
                    else:
                        # 3) ép MediaScanner quét lại
                        adb_media_scan(self.udid, remote_path)
                        log(f"✅ Đã push & scan ảnh: {remote_path}")

                    time.sleep(1.5)  # đợi Gallery cập nhật
        except Exception as e:
            log(f"❌ Lỗi khi push ảnh: {e}")
        time.sleep(2)
        
        # --- Tắt app Instagram ---
        subprocess.call(["adb", "-s", self.udid, "shell", "am", "force-stop", "com.instagram.android"])
        log("🛑 Đã tắt app Instagram")
        time.sleep(3)

        # --- Khởi động lại Instagram ---
        subprocess.call([
            "adb", "-s", self.udid, "shell", "monkey", "-p", "com.instagram.android", "-c", "android.intent.category.LAUNCHER", "1"
        ])
        log("🔄 Đã mở lại app Instagram")
        time.sleep(15)  # chờ app load

        # --- Vào Profile ---
        subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "1000", "1850"])
        log("👤 Đã vào Profile")
        time.sleep(4)

        # --- Về Home ---
        subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "100", "1850"])
        log("👤 Đã về lại Home")
        time.sleep(4)

        # --- Vào Profile ---
        subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "1000", "1850"])
        log("👤 Đã vào Profile")
        time.sleep(10)

        if enable_uppost.get():
            # =================== UP POST ===================
            clicked = False
            # - Cách 1: Theo content-desc phổ biến
            for desc in ["New post", "Create", "+", "Tạo", "Thêm"]:
                try:
                    plus_btn = d.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().description("{desc}")'
                    )
                    if plus_btn.is_displayed() and plus_btn.is_enabled():
                        plus_btn.click()
                        log(f"✅ Đã nhấn nút + (content-desc='{desc}')")
                        clicked = True
                        break
                except Exception:
                    continue

            # - Cách 2: Theo resource-id
            if not clicked:
                try:
                    el = d.find_element(AppiumBy.ID, "com.instagram.android:id/creation_tab")
                    if el.is_displayed() and el.is_enabled():
                        el.click()
                        log("✅ Đã nhấn nút + (resource-id=creation_tab, thanh dưới)")
                        clicked = True
                    else:
                        log("❌ Nút + (creation_tab) không hiển thị hoặc không click được")
                except Exception:
                    log("❌ Không tìm thấy nút + bằng resource-id")

            # - Cách 3: Theo nút + ở góc trái
            if not clicked:
                try:
                    el = d.find_element(
                        AppiumBy.XPATH,
                        '//android.widget.LinearLayout[@resource-id="com.instagram.android:id/left_action_bar_buttons"]/android.widget.ImageView'
                    )
                    if el.is_displayed() and el.is_enabled():
                        el.click()
                        log("✅ Đã nhấn nút + ở góc trái")
                        clicked = True
                    else:
                        log("❌ Nút + ở góc trái không hiển thị hoặc không click được")
                except Exception:
                    log("❌ Không tìm thấy nút + ở góc trái")

            # - Cách 4: Theo nút + ở góc phải
            if not clicked:
                try:
                    els_right = d.find_elements(
                        AppiumBy.XPATH,
                        '//android.widget.LinearLayout[@resource-id="com.instagram.android:id/right_action_bar_buttons"]/android.widget.ImageView'
                    )
                    if len(els_right) >= 2:
                        el = els_right[1]
                        if el.is_displayed() and el.is_enabled():
                            el.click()
                            log("✅ Đã nhấn nút + ở góc phải")
                            clicked = True
                        else:
                            log("❌ Nút + ở góc phải không hiển thị hoặc không click được")
                    else:
                        log("⚠️ Không tìm thấy đủ nút trong right_action_bar_buttons")
                except Exception as e:
                    log(f"⚠️ Lỗi khi tìm nút + ở góc phải: {e}")

            if not clicked:
                log("❌ Không thể nhấn được nút + ở bất kỳ vị trí nào")

            # - Cách 5: Dump + Phân tích XML + Nhấn nút + (fallback thông minh)
            if not clicked:
                try:
                    log("[INFO] Không tìm thấy nút + bằng 3 cách trên. Đang thử Dump + Phân tích UI...")

                    # 📤 1️⃣ Dump UI từ thiết bị
                    XML_PATH_PHONE = "/sdcard/window_dump.xml"
                    XML_PATH_PC = r"C:\Users\MINH\Downloads\AutoTool\ui.xml"
                    subprocess.run(["adb", "-s", udid, "shell", "uiautomator", "dump", XML_PATH_PHONE], stdout=subprocess.DEVNULL)
                    subprocess.run(["adb", "-s", udid, "pull", XML_PATH_PHONE, XML_PATH_PC], stdout=subprocess.DEVNULL)

                    x_center, y_center = None, None

                    # 🔍 2️⃣ Phân tích file XML để tìm vị trí nút +
                    if os.path.exists(XML_PATH_PC):
                        with open(XML_PATH_PC, "r", encoding="utf-8") as f:
                            xml_content = f.read()

                        # Tìm node có content-desc chứa "Create" và lấy bounds
                        match = re.search(
                            r'content-desc="([^"]*Create[^"]*)"[\s\S]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
                            xml_content
                        )
                        if match:
                            desc, x1, y1, x2, y2 = match.groups()
                            x_center = (int(x1) + int(x2)) // 2
                            y_center = (int(y1) + int(y2)) // 2
                            log(f"[✅] Đã phát hiện nút '+' trong XML: desc='{desc}', tọa độ=({x_center},{y_center})")

                            # 🖱️ 3️⃣ Thử click bằng content-desc nếu có
                            try:
                                element = d.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
                                element.click()
                                log("[✅] Đã click nút '+' bằng accessibility id!")
                                clicked = True
                            except Exception:
                                log("[⚠️] Không tìm thấy phần tử bằng desc, fallback về tọa độ...")

                        # 🖱️ 4️⃣ Fallback: click theo tọa độ nếu có
                        if not clicked and x_center and y_center:
                            try:
                                d.execute_script("mobile: clickGesture", {"x": x_center, "y": y_center})
                                log(f"[✅] Đã click nút '+' bằng tọa độ fallback tại ({x_center}, {y_center})")
                                clicked = True
                            except Exception as e:
                                log(f"❌ Không thể click bằng tọa độ fallback: {e}")
                    else:
                        log("❌ Không tìm thấy file XML sau khi dump!")

                    # 🧹 5️⃣ Xóa file XML sau khi dùng xong
                    if os.path.exists(XML_PATH_PC):
                        os.remove(XML_PATH_PC)
                        log("[🧹] Đã xóa file ui.xml sau khi hoàn tất.")
                except Exception as e:
                    log(f"⚠️ Lỗi khi thử cách Dump + Phân tích XML: {e}")

            time.sleep(7)

            # 4. Kiểm tra xem có mục Post không
            if clicked:
                try:
                    post_el = d.find_element(
                        AppiumBy.XPATH,
                        '//android.widget.TextView[@text="Post"]'
                    )
                    post_el.click()
                    log("✅ Đã nhấn vào mục Post")
                    time.sleep(7)
                except Exception:
                    log("⚠️ Không tìm thấy mục Post, bỏ qua")
            else:
                log("❌ Không nhấn được nút + nào")
                    
            # 5. Ấn Next 
            for _ in range(2):
                clicked_next = False
                for txt in ["Next", "Tiếp"]:
                    try:
                        d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{txt}")').click()
                        clicked_next = True
                        time.sleep(4)
                        break
                    except Exception:
                        continue
                if not clicked_next:
                    break
            time.sleep(8)

            # 6 Nếu xuất hiện popup "Sharing posts" thì bấm OK
            try:
                ok_btn = wait.until(
                    EC.element_to_be_clickable(
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("OK")')
                    )
                )
                if ok_btn.is_displayed():
                    ok_btn.click()
                    log(f"ℹ️ [{udid}] Đã bấm OK trong popup Sharing posts.")
                    time.sleep(0.8)
            except Exception:
                pass
            time.sleep(3)

            # 7 Điền caption vào ô "Add a caption..."
            try:
                caption = (
                    random.choice(CAPTION_LEADS) + " "
                    + random.choice(CAPTION_TRAILS) + " "
                    + random.choice(CAPTION_EMOJIS)
                )
                # Tìm ô nhập caption (thường là EditText đầu tiên)
                caption_input = d.find_element(AppiumBy.CLASS_NAME, "android.widget.EditText")
                caption_input.clear()
                caption_input.send_keys(caption)
                log(f"✅ Đã điền caption: {caption}")
                time.sleep(1.5)
            except Exception as e:
                log(f"⚠️ Không điền được caption: {e}")
            time.sleep(3)

            # 8 Ấn Share
            shared = False
            for txt in ["Share", "Chia sẻ", "Đăng"]:
                try:
                    d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{txt}")').click()
                    shared = True
                    break
                except Exception:
                    continue

            if shared:
                log(f"✅ [{udid}] Đã đăng bài mới.")
            else:
                log(f"⚠️ [{udid}] Không bấm được nút Share/Chia sẻ.")
            time.sleep(15)
            
        if enable_autofollow.get():  
            # AuTo Follow
            clicked = False
            # 1. Thử theo content-desc "Search and explore"
            try:
                el = d.find_element(AppiumBy.ACCESSIBILITY_ID, "Search and explore")
                el.click()
                log("✅ Đã nhấn nút kính lúp (Search and explore)")
                clicked = True
            except Exception:
                log("❌ Không tìm thấy nút kính lúp bằng content-desc 'Search and explore'")

            # 2. Thử theo content-desc "Search"
            if not clicked:
                try:
                    el = d.find_element(AppiumBy.ACCESSIBILITY_ID, "Search")
                    el.click()
                    log("✅ Đã nhấn nút kính lúp (Search)")
                    clicked = True
                except Exception:
                    log("❌ Không tìm thấy nút kính lúp bằng content-desc 'Search'")

            # 3. Thử bằng UiAutomator textContains
            if not clicked:
                try:
                    el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Search")')
                    el.click()
                    log("✅ Đã nhấn nút kính lúp (descriptionContains 'Search')")
                    clicked = True
                except Exception:
                    log("❌ Không tìm thấy nút kính lúp bằng descriptionContains 'Search'")

            time.sleep(4)

            # 1. Tìm ô nhập Search
            input_box = None
            for how, what in [
                (AppiumBy.ID, "com.instagram.android:id/action_bar_search_edit_text"),
                (AppiumBy.CLASS_NAME, "android.widget.EditText"),
            ]:
                try:
                    input_box = d.find_element(how, what)
                    input_box.click()
                    time.sleep(4)
                    break
                except Exception:
                    continue

            if not input_box:
                log("❌ Không tìm thấy ô nhập Search")
            else:
                # 2. Lấy số lượng follow từ biến UI
                try:
                    follow_count = phone_follow_count_var.get()
                except Exception:
                    follow_count = 10

                FOLLOW_USERNAMES = [
                    "n.nhu1207","v.anh.26","shxuy0bel421162","k.mbappe","valentin_otz","shx_pe06","nguyen57506",
                    "mhai_187","ductoan1103","therock","eveil_tangyuan412","lunaistabby","fandango","uncle_bbao",
                    "monkeycatluna",
                ]
                follow_list = random.sample(FOLLOW_USERNAMES, min(follow_count, len(FOLLOW_USERNAMES)))
                followed = 0

                for username in follow_list:
                    # Tìm lại ô nhập Search
                    input_box = None
                    for how, what in [
                        (AppiumBy.ID, "com.instagram.android:id/action_bar_search_edit_text"),
                        (AppiumBy.CLASS_NAME, "android.widget.EditText"),
                    ]:
                        try:
                            input_box = d.find_element(how, what)
                            input_box.click()
                            break
                        except Exception:
                            continue

                    if not input_box:
                        log("❌ Không tìm thấy ô nhập Search khi follow username mới")
                        continue

                    # Nhập username (send_keys fallback set_value)
                    try:
                        input_box.clear()
                    except Exception:
                        pass
                    try:
                        input_box.send_keys(username)
                        log(f"⌨️ Nhập username bằng send_keys: {username}")
                    except Exception:
                        try:
                            d.set_value(input_box, username)
                            log(f"⌨️ Nhập username bằng set_value: {username}")
                        except Exception as e:
                            log(f"❌ Không nhập được {username}: {e}")
                            continue
                    time.sleep(5)

                    # Tìm đúng username trong kết quả
                    found = False
                    results = d.find_elements(AppiumBy.ID, "com.instagram.android:id/row_search_user_username")
                    if not results:
                        results = d.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{username}")')
                    for el in results:
                        try:
                            t = (el.text or "").strip()
                            if t.lower() == username.lower() or username.lower() in t.lower():
                                el.click()
                                log(f"✅ Đã nhấn vào username: {username}")
                                found = True
                                break
                        except Exception:
                            continue

                    if not found:
                        log(f"❌ Không tìm thấy username {username} trong kết quả tìm kiếm")
                        continue

                    time.sleep(5)

                    # Nhấn nút Follow
                    try:
                        follow_btn = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Follow")')
                        if follow_btn.is_enabled() and follow_btn.is_displayed():
                            follow_btn.click()
                            log(f"✅ Đã nhấn Follow cho {username}")
                            time.sleep(3)
                            followed += 1

                            # --- Kiểm tra popup block follow ---
                            try:
                                popup = d.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Try Again Later")')
                                if popup:
                                    log("⛔ Instagram đã block follow: Try Again Later popup xuất hiện.")
                                    # Ấn OK để đóng popup
                                    try:
                                        ok_btn = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("OK")')
                                        ok_btn.click()
                                        log("✅ Đã ấn OK để đóng popup block follow.")
                                    except Exception:
                                        log("⚠️ Không tìm thấy nút OK trong popup.")
                                    break  # Dừng thao tác follow tiếp
                            except Exception as e:
                                log(f"⚠️ Lỗi khi kiểm tra popup block follow: {e}")
                            time.sleep(2)

                            # --- Back sau khi follow ---
                            back_clicked = False
                            try:
                                for desc in ["Back", "Điều hướng lên"]:
                                    try:
                                        back_btn = d.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
                                        back_btn.click()
                                        log(f"🔙 Đã nhấn nút mũi tên lùi ({desc})")
                                        back_clicked = True
                                        time.sleep(2)
                                        break
                                    except Exception:
                                        continue
                                if not back_clicked:
                                    btns = d.find_elements(AppiumBy.CLASS_NAME, "android.widget.ImageButton")
                                    if btns:
                                        btns[0].click()
                                        log("🔙 Đã nhấn nút mũi tên lùi")
                                        back_clicked = True
                                        time.sleep(2)
                                if not back_clicked:
                                    d.back()
                                    log("🔙 Đã Ấn Back")
                                    time.sleep(2)
                            except Exception:
                                log("⚠️ Không tìm thấy nút mũi tên lùi sau khi Follow")
                        else:
                            log(f"❌ Nút Follow không khả dụng trên profile {username}")
                    except Exception:
                        log(f"❌ Không tìm thấy nút Follow trên profile {username}")

                    # Nếu đã đủ số lượng thì dừng
                    if followed >= follow_count:
                        break
        # --- Back sau khi follow đủ ---
        back_clicked = False
        try:
            for desc in ["Back", "Điều hướng lên"]:
                try:
                    back_btn = d.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
                    back_btn.click()
                    log(f"🔙 Đã nhấn nút mũi tên lùi ({desc})")
                    back_clicked = True
                    time.sleep(2)
                    break
                except Exception:
                    continue
            if not back_clicked:
                btns = d.find_elements(AppiumBy.CLASS_NAME, "android.widget.ImageButton")
                if btns:
                    btns[0].click()
                    log("🔙 Đã nhấn nút mũi tên lùi")
                    back_clicked = True
                    time.sleep(2)
            if not back_clicked:
                d.back()
                log("🔙 Đã Ấn Back")
                time.sleep(2)
        except Exception:
            log("⚠️ Không tìm thấy nút mũi tên lùi sau khi Follow")
        if enable_editprofile.get():
            # --- Vào Profile ---
            subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "1000", "1850"])
            log("👤 Đã vào Profile")
            time.sleep(10)
            # Nhấn Edit profile
            try:
                log("Đang tìm nút 'Edit profile'...")
                edit_profile_btn = None
                try:
                    edit_profile_btn = WebDriverWait(d, 8).until(
                        EC.presence_of_element_located((
                            AppiumBy.ANDROID_UIAUTOMATOR,
                            'new UiSelector().text("Edit profile")'
                        ))
                    )
                except Exception:
                    log("[ERROR] Không tìm thấy nút 'Edit profile'.")
                    return
                if edit_profile_btn:
                    edit_profile_btn.click()
                    log("Đã nhấn nút 'Edit profile'.")
                    time.sleep(5)
                else:
                    log("Lỗi Không tìm thấy nút 'Edit profile'.")
            except Exception as e:
                log(f"Lỗi khi nhấn nút 'Edit profile': {e}")

            # Nếu không phải Share profile, thì check popup avatar
            try:
                notnow = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                        'new UiSelector().textContains("Not now")')
                notnow.click()
                log("✅ Đã ấn Not now ở popup tạo avatar")
            except Exception:
                pass  # Không có popup thì bỏ qua
            
            # UP AVATAR 
            # 1. Tìm và ấn vào "Change profile picture"
            el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Change profile picture")')
            el.click()
            log("✅ Đã nhấn Change profile picture")
            time.sleep(3)

            # 2. Chọn "Choose from library"
            choose = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Choose from library")')
            choose.click()
            log("✅ Đã chọn Choose from library")
            time.sleep(6)

            # 3. Ấn "Done" (góc phải trên)
            for txt in ["Done", "Next", "Tiếp", "Xong", "Lưu"]:
                try:
                    d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{txt}")').click()
                    break
                except Exception:
                    pass
            time.sleep(13)

            # Nhấn Edit profile
            try:
                log("Đang tìm nút 'Edit profile'...")
                edit_profile_btn = None
                try:
                    edit_profile_btn = WebDriverWait(d, 8).until(
                        EC.presence_of_element_located((
                            AppiumBy.ANDROID_UIAUTOMATOR,
                            'new UiSelector().text("Edit profile")'
                        ))
                    )
                except Exception:
                    log("Lỗi Không tìm thấy nút 'Edit profile'.")
                    return
                if edit_profile_btn:
                    edit_profile_btn.click()
                    log("Đã nhấn nút 'Edit profile'.")
                    time.sleep(5)
                else:
                    log("Lỗi Không tìm thấy nút 'Edit profile'.")
            except Exception as e:
                log(f"Lỗi khi nhấn nút 'Edit profile': {e}")

            # Điền BIO 
            # 1. Ấn vào label Bio
            el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Bio")')
            el.click()
            log("✅ Đã nhấn vào label Bio")
            time.sleep(3)

            # 2. Tạo bio ngẫu nhiên từ BIO_LINES + emoji
            bio = random.choice(BIO_LINES) + " " + random.choice(CAPTION_EMOJIS)
            time.sleep(3)

            # 3. Điền bio vào ô nhập
            input_bio = d.find_element(AppiumBy.CLASS_NAME, "android.widget.EditText")
            input_bio.clear()
            input_bio.send_keys(bio)
            log(f"✅ Đã điền bio: {bio}")
            time.sleep(3)

            # 4) Lưu: icon ✓ góc trên phải hoặc nút Save/Xong/Lưu
            saved = False
            # a) thử theo text
            for txt in ["Save", "Lưu", "Done", "Xong", "✓"]:
                try:
                    d.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().textContains("{txt}")'
                    ).click()
                    saved = True
                    break
                except Exception:
                    pass
            # b) thử content-desc của icon ✓
            if not saved:
                for how, what in [
                    (AppiumBy.ACCESSIBILITY_ID, "Done"),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Done")'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionMatches("(?i)(save|done|xong|lưu|check)")'),
                ]:
                    try:
                        el = d.find_element(how, what)
                        el.click()
                        saved = True
                        break
                    except Exception:
                        continue

            if saved:
                log(f"✅ [{udid}] Đã cập nhật Bio")
            else:
                log(f"⚠️ [{udid}] Không bấm được nút Lưu/✓ trong màn Bio.")

            time.sleep(6)

            # Chọn Gender 
            # 1. Cuộn xuống để thấy label Gender (nếu cần)
            d.swipe(500, 1500, 500, 500, 500)  # Điều chỉnh tọa độ nếu cần
            time.sleep(3)

            # 2. Ấn vào label Gender (Prefer not to say)
            el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Prefer not to say")')
            el.click()
            log("✅ Đã nhấn vào label Gender")
            time.sleep(3)

            # 3. Chọn Female
            female = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Female")')
            female.click()
            log("✅ Đã chọn Female")

            time.sleep(0.5)

            # 6) Lưu: icon ✓ góc trên phải hoặc nút Save/Xong/Lưu
            saved = False
            # a) thử theo text
            for txt in ["Save", "Lưu", "Done", "Xong", "✓"]:
                try:
                    d.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().textContains("{txt}")'
                    ).click()
                    saved = True
                    break
                except Exception:
                    pass
            # b) thử content-desc của icon ✓
            if not saved:
                for how, what in [
                    (AppiumBy.ACCESSIBILITY_ID, "Done"),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Done")'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionMatches("(?i)(save|done|xong|lưu|check)")'),
                ]:
                    try:
                        el = d.find_element(how, what)
                        el.click()
                        saved = True
                        break
                    except Exception:
                        continue

            if saved:
                log(f"✅ [{udid}] Đã cập nhật Bio")
            else:
                log(f"⚠️ [{udid}] Không bấm được nút Lưu/✓ trong màn Gender.")
            time.sleep(6)
            
        if enable_proaccount.get():
            # Bật Chuyên Nghiệp 
            # Chọn switch to Pro Account trong Settings 
            # 1. Cuộn xuống để thấy switch sang Pro Account (nếu cần)
            d.swipe(500, 1500, 500, 500, 500) 
            time.sleep(5)

            # 2) Cuộn và bấm "Switch to professional account"
            if not _scroll_into_view_by_text(d, "Switch to professional"):
                log(f"⚠️ [{udid}] Không tìm thấy mục 'Switch to professional account'.")
                return
            wait.until(EC.element_to_be_clickable(
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Switch to professional")'))
            ).click()
            time.sleep(10)

            # 3) Màn giới thiệu → Next
            for txt in ["Next", "Tiếp"]:
                try:
                    d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{txt}")').click()
                    break
                except Exception:
                    pass
            time.sleep(6)

            # 4) Màn "What best describes you?" → chọn Category
            # 4a) Tap vào ô "Search categories" (hoặc "Search")
            try:
                wait.until(EC.element_to_be_clickable(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Search")')
                )).click()
            except Exception:
                # nếu không bấm được ô search, vẫn có thể chọn trực tiếp trong list
                pass

            # 4b) Lấy giá trị category và account_type từ settings UI
            category = pro_category_var.get() if 'pro_category_var' in globals() else "Reel creator"
            account_type = pro_type_var.get() if 'pro_type_var' in globals() else "Creator"

            target = (category or "").strip()
            if target:
                if not _scroll_into_view_by_text(d, target):
                    log(f"⚠️ [{udid}] Không tìm thấy category '{target}'.")
                    return
                # chọn đúng item
                wait.until(EC.element_to_be_clickable(
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{target}")'))
                ).click()
                time.sleep(4)

            #Tap display on profile
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "970", "900"])
            log("✅ Tap Display On Profile")
            time.sleep(4)

            # 4d) Bấm "Switch to professional account"
            for txt in ["Switch to professional account"]:
                try:
                    if not _scroll_into_view_by_text(d, txt, max_swipes=2):
                        pass
                    d.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().textContains("{txt}")'
                    ).click()
                    break
                except Exception:
                    continue
            time.sleep(12)

            # 5) Màn "What type of professional are you?" → chọn Creator/Business → Next
            typ = (account_type or "").strip().lower()
            target_type = "Creator" if typ != "business" else "Business"
            try:
                wait.until(EC.element_to_be_clickable(
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{target_type}")'))
                ).click()
            except Exception:
                d.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().textContains("{target_type}")'
                ).click()
            time.sleep(0.3)
            for txt in ["Next", "Tiếp"]:
                try:
                    d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{txt}")').click()
                    break
                except Exception:
                    pass

            log(f"✅ [{udid}] Đã chuyển sang Professional: Category='{category}', Type={target_type}.")

        # Bật chế độ máy bay và tự chạy lại phiên mới
        try:
            adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
            adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
            adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
            adb_shell(self.udid, "svc", "wifi", "disable")
            adb_shell(self.udid, "svc", "data", "disable")
            log("🛫 Đã bật Chế độ máy bay (LIVE)")
        except Exception as e:
            log(f"⚠️ Lỗi khi bật Chế độ máy bay (LIVE): {e}")

        # Restart ngay lập tức
        self.log("🔄 Restart phiên vì Live…")
        self.stop()
        time.sleep(3)
        AndroidWorker(self.udid, log_fn=self.log).start()
        return True

    # ================================== SIGNUP – INSTAGRAM LITE ===============================================
    def signup_instagram_lite(self):
        d, log = self.driver, self.log
        time.sleep(2.5)  # chờ UI ổn định hơn
        
        # --- Nhấn "Create new account" ---
        try:
            groups = d.find_elements(AppiumBy.CLASS_NAME, "android.view.ViewGroup")
            clickable_groups = [g for g in groups if g.get_attribute("clickable") == "true"]

            if len(clickable_groups) >= 2:
                # Nút "Create new account" thường nằm ngay trước nút "Log in"
                target = clickable_groups[-2]
                target.click()
                log("👉 Đã bấm 'Create new account' (Instagram Lite)")
                time.sleep(2)
            else:
                log("⛔ Không tìm thấy đủ ViewGroup clickable để chọn 'Create new account'.")
                return False
        except Exception as e:
            log(f"⚠️ Lỗi khi bấm 'Create new account': {repr(e)}")
            return False

        time.sleep(6)

        # --- Nhấn "Sign up with email" ---
        try:
            groups = d.find_elements(AppiumBy.CLASS_NAME, "android.view.ViewGroup")
            clickable_groups = [g for g in groups if g.get_attribute("clickable") == "true"]

            if len(clickable_groups) >= 2:
                # Nút "Sign up with email" thường là clickable kế cuối (trước "Log in")
                clickable_groups[-2].click()
                log("👉 Đã bấm 'Sign up with email'")
                time.sleep(2)
            else:
                log("⛔ Không tìm thấy đủ ViewGroup clickable để chọn 'Sign up with email'.")
                return False
        except Exception as e:
            log(f"⚠️ Lỗi khi bấm 'Sign up with email': {repr(e)}")
            return False

        time.sleep(4)

        # --- Lấy email tạm ---
        try:
            email, drop_session_id, source = fetch_signup_email(self)
        except NameError:
            try:
                mode = self.var_mail_src.get().strip().lower()
            except Exception:
                mode = "tempasia"

            if mode == "dropmail":
                email, drop_session_id = get_dropmail_email()
                source = "dropmail"
            else:
                email = get_tempasia_email()
                drop_session_id = None
                source = "tempasia"

        if not email:
            log("⛔ Không lấy được email tạm.")
            return False

        # --- Điền email vào ô nhập ---
        try:
            input_box = WebDriverWait(d, 10).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.MultiAutoCompleteTextView"))
            )
            input_box.click()
            input_box.clear()
            input_box.send_keys(email)
            log(f"👉 Đã điền email: {email}")
            time.sleep(1)

            # --- Nhấn Next ---
            # Tìm ViewGroup clickable nằm ngay dưới ô nhập email (cái gần nhất)
            groups = d.find_elements(AppiumBy.CLASS_NAME, "android.view.ViewGroup")
            clickable_groups = [g for g in groups if g.get_attribute("clickable") == "true"]

            # Lấy center Y của input_box
            bounds_input = input_box.get_attribute("bounds")
            nums_input = [int(n) for n in re.findall(r"\d+", bounds_input)]
            y_input = (nums_input[1] + nums_input[3]) // 2

            # Chọn ViewGroup clickable có center Y > y_input và diff nhỏ nhất (ngay dưới)
            next_btn = None
            min_diff = None
            for g in clickable_groups:
                try:
                    bounds = g.get_attribute("bounds")
                    nums = [int(n) for n in re.findall(r"\d+", bounds)]
                    y_center = (nums[1] + nums[3]) // 2
                    if y_center > y_input:
                        diff = y_center - y_input
                        if min_diff is None or diff < min_diff:
                            min_diff = diff
                            next_btn = g
                except Exception:
                    continue

            if next_btn:
                next_btn.click()
                log("👉 Đã bấm 'Next' (ViewGroup ngay dưới ô nhập email)")
                time.sleep(2)
            else:
                log("⛔ Không tìm thấy nút Next (ViewGroup dưới ô nhập email).")
                return False

        except Exception as e:
            log(f"⚠️ Lỗi khi điền email và nhấn Next: {repr(e)}")
            return False

        time.sleep(13)

        # ------ Lấy Code Mail Và Điền =============
        code = None
        # Chờ mã xác minh từ email tạm (DropMail hoặc TempAsia)
        try:
            if source == "dropmail":
                code = wait_for_dropmail_code(self, drop_session_id, max_checks=30, interval=3)
            else:
                code = wait_for_tempmail_code(email, max_checks=30, interval=2)
        except Exception as e:
            log(f"⚠️ Lỗi khi lấy mã xác minh email: {repr(e)}")
            code = None

        if not code:
            log("⛔ Không lấy được mã xác minh từ email.")
            return False

        log(f"✅ Đã lấy được mã xác minh: {code}")

        # Tìm ô nhập code và điền vào
        try:
            udid = self.udid if hasattr(self, 'udid') else None
            if udid:
                subprocess.call(["adb", "-s", udid, "shell", "input", "text", str(code)])
                log("✅ Đã dán mã xác minh bằng ADB input text")
                time.sleep(3)
            else:
                log("⚠️ Không xác định được udid để dán code.")
        except Exception as e:
            log(f"❌ Không dán được mã xác minh: {repr(e)}")
            return False
        # Nhấn Next sau khi điền code
        # --- Nhấn Next ---
        groups = d.find_elements(AppiumBy.CLASS_NAME, "android.view.ViewGroup")
        clickable_groups = [g for g in groups if g.get_attribute("clickable") == "true"]

        # Lấy center Y của input_box
        bounds_input = input_box.get_attribute("bounds")
        nums_input = [int(n) for n in re.findall(r"\d+", bounds_input)]
        y_input = (nums_input[1] + nums_input[3]) // 2

        # Chọn ViewGroup clickable có center Y > y_input và diff nhỏ nhất (ngay dưới)
        next_btn = None
        min_diff = None
        for g in clickable_groups:
            try:
                bounds = g.get_attribute("bounds")
                nums = [int(n) for n in re.findall(r"\d+", bounds)]
                y_center = (nums[1] + nums[3]) // 2
                if y_center > y_input:
                    diff = y_center - y_input
                    if min_diff is None or diff < min_diff:
                        min_diff = diff
                        next_btn = g
            except Exception:
                continue

        if next_btn:
            next_btn.click()
            log("👉 Đã bấm 'Next' (ViewGroup ngay dưới ô nhập email)")
            time.sleep(12)
        else:
            log("⛔ Không tìm thấy nút Next (ViewGroup dưới ô nhập email).")
            return False

        # ================= Nhập Full Name và Password =================
        log("✏️ Bắt đầu điền họ tên và mật khẩu (ADB CMD)...")

        try:
            # 📌 Chờ màn hình "Name and Password" xuất hiện
            time.sleep(5)

            # ======= Sinh họ tên KHÔNG DẤU để ADB gõ được =======
            ho_list = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo", "Dang", "Bui", "Do", "Ngo", "Ho", "Duong", "Dinh"]
            dem_list = ["Van", "Thi", "Minh", "Huu", "Quang", "Thanh", "Thu", "Anh", "Trung", "Phuc", "Ngoc", "Thao", "Khanh", "Tuan", "Hai"]
            ten_list = ["Hoang", "Ha", "Tu", "Trang", "Linh", "Duy", "Hung", "Tam", "Lan", "Phuong", "Quan", "My", "Long", "Nam", "Vy"]

            full_name = f"{random.choice(ho_list)} {random.choice(dem_list)} {random.choice(ten_list)}"
            safe_full_name = full_name.replace(" ", "%s")  # đổi khoảng trắng cho adb
            password = random.choice(string.ascii_uppercase) + ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=9)
            )

            udid = self.udid if hasattr(self, 'udid') else None
            if not udid:
                log("⛔ Không xác định được UDID thiết bị.")
                return False

            # ✏️ Tap vào ô Họ tên 2 lần để đảm bảo focus
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "400"])
            time.sleep(1)

            # 📝 Nhập họ tên
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", safe_full_name])
            log(f"✅ Đã điền họ tên: {full_name}")
            time.sleep(1.5)

            # 🔑 Tap vào ô Mật khẩu và nhập
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "500", "600"])
            time.sleep(1)
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", password])
            log(f"✅ Đã điền mật khẩu: {password}")
            time.sleep(1.5)

            # ✅ Ẩn bàn phím để tránh che nút Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "111"])
            time.sleep(0.8)

            # 👉 Tap chính giữa nút Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "900"])
            log("👉 Đã bấm 'Next' sau khi điền họ tên & mật khẩu.")
            time.sleep(8)

        except Exception as e:
            log(f"⚠️ Lỗi khi điền họ tên và mật khẩu bằng ADB: {repr(e)}")
            return False
        
        # ============================== Nhập Tuổi =====================================
        log("✏️ Bắt đầu bỏ qua màn list age")
        try:
            # 👉 Tap Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1700"])
            log("👉 Đã bấm 'Next")
            time.sleep(3)
            
            # 👉 Tap OK
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1100"])
            log("👉 Đã bấm OK")
            time.sleep(4)

            # 👉 Tap Enter age
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1700"])
            log("👉 Đã bấm 'Enter age'")
            time.sleep(7)
        except Exception as e:
            log(f"⚠️ Lỗi khi bỏ qua màn hình chọn tuổi: {repr(e)}")
            return False
        
        # =================== Nhập tuổi ngẫu nhiên ===================
        log("✏️ Bắt đầu nhập tuổi ngẫu nhiên (18 - 50)...")

        try:
            age = random.randint(18, 50)  # random tuổi
            log(f"✅ Tuổi được chọn: {age}")

            # ✏️ Nhập tuổi
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", str(age)])
            log("✅ Đã nhập tuổi thành công!")
            time.sleep(1.5)

            # 👉 Tap nút Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "800"])
            log("👉 Đã bấm 'Next' sau khi nhập tuổi.")
            time.sleep(15)

        except Exception as e:
            log(f"⚠️ Lỗi khi nhập tuổi: {repr(e)}")
            return False
        
        # ====================== Ấn Next để hoàn tất ======================
        log("✏️ Bắt đầu hoàn tất đăng ký...")
        try:
            # 👉 Tap Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1550"])
            log("👉 Đã bấm 'Next'")
            time.sleep(25)
            log("🎉 Hoàn tất đăng ký Instagram Lite!")
        except Exception as e:
            log(f"⚠️ Lỗi khi bỏ ấn next để hoàn tất đăng ký: {repr(e)}")
            return False
    
        # Bật chế độ máy bay và tự chạy lại phiên mới
        try:
            adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
            adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
            adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE_CHANGED", "--ez", "state", "true")
            adb_shell(self.udid, "svc", "wifi", "disable")
            adb_shell(self.udid, "svc", "data", "disable")
            log("🛫 Đã bật Chế độ máy bay (LIVE)")
        except Exception as e:
            log(f"⚠️ Lỗi khi bật Chế độ máy bay (LIVE): {e}")
            
    # ================================== DISPATCHER ============================================================
    def run_signup(self):
        app_choice = phone_ig_app_var.get() if "phone_ig_app_var" in globals() else "instagram"
        if (app_choice or "").lower() == "instagram_lite":
            self.log("🚀 Bắt đầu tạo tài khoản trên Instagram Lite")
            return self.signup_instagram_lite()
        else:
            self.log("🚀 Bắt đầu tạo tài khoản trên Instagram")
            return self.signup_instagram()
    
#=================================== Chrome DESKTOP & MOBILE ===============================================
def clear_chrome_cache():
    try:
        user_data_dir = os.path.join(os.getcwd(), "ChromeData")
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
            log("🧹 Đã xóa cache Chrome (User Data)")
        else:
            log("ℹ Không có cache Chrome để xóa")
    except Exception as e:
        log(f"⚠️ Lỗi khi xóa cache Chrome: {repr(e)}")

def type_text_slowly(element, text, delay=0.18):
    """Gõ từng ký tự với delay giữa mỗi ký tự."""
    element.click()
    element.clear()
    for ch in text:
        element.send_keys(ch)
        time.sleep(delay)

def get_delay(key, default):
    try:
        val = delay_entries[key].get().strip()
        return float(val) if val else default
    except:
        return default

def _set_container_enabled(container, enabled: bool):
    state = "normal" if enabled else "disabled"

    def walk(widget):
        # tk.*
        try:
            widget.configure(state=state)
        except Exception:
            # ttk.*
            try:
                if hasattr(widget, "state"):
                    widget.state(["!disabled"] if enabled else ["disabled"])
            except Exception:
                pass
        # Label đổi màu để nhìn ra đang bị khóa
        try:
            if isinstance(widget, (tk.Label, ttk.Label)):
                widget.configure(fg="black" if enabled else "#888")
        except Exception:
            pass
        for child in widget.winfo_children():
            walk(child)

    walk(container)

def _sync_mode_ui():
    """Khóa/mở Desktop Settings và Mobile Settings theo lựa chọn ở 'GIAO DIỆN'."""
    mode = ui_mode_var.get().strip().lower()
    _set_container_enabled(desktop_settings, enabled=(mode == "desktop"))
    _set_container_enabled(mobile_settings,  enabled=(mode == "mobile"))
    _set_container_enabled(phone_settings,   enabled=(mode == "phone"))

def get_chrome_size(default_w=1200, default_h=800):
    try:
        w = int(entry_width.get().strip())
        h = int(entry_height.get().strip())
        # giới hạn tối thiểu để tránh lỗi
        if w < 400: w = 400
        if h < 300: h = 300
        return w, h
    except:
        return default_w, default_h

def get_chrome_scale(default=1.0):
    try:
        s = int(entry_scale.get().strip())
        if s < 50: s = 50    # tối thiểu 50%
        if s > 300: s = 300  # tối đa 300%
        return s / 100.0     # chuyển % thành số thực
    except:
        return default

# --- thêm cho đồng bộ luồng ---
sync_barrier = None    # sẽ là threading.Barrier được tạo khi START
barrier_timeout = 60   # thời gian chờ (giây) trước khi timeout
thread_list = []       # (tùy chọn) lưu các Thread để quản lý

def wait_all(step_name, thread_id):
    """
    Chờ tất cả các luồng đạt tới checkpoint 'step_name' rồi tiếp tục.
    Nếu barrier bị timeout/broken thì sẽ log và tiếp tục để tránh treo.
    """
    if sync_barrier is not None:
        try:
            log(f"⏳ [Luồng {thread_id}] Chờ tất cả tại bước: {step_name} (timeout {barrier_timeout}s)...")
            sync_barrier.wait(timeout=barrier_timeout)
            log(f"🚀 [Luồng {thread_id}] Tất cả luồng đã hoàn thành bước: {step_name}")
        except threading.BrokenBarrierError:
            log(f"⚠️ [Luồng {thread_id}] Barrier timeout/broken ở bước: {step_name}, tiếp tục.")
    else:
        log(f"⚠️ [Luồng {thread_id}] sync_barrier chưa được tạo — bỏ qua đồng bộ bước: {step_name}")

all_drivers = []
pause_event = threading.Event()
pause_event.set()  # Mặc định là “cho phép chạy”

warp_enabled = True
proxy_entry = None

# ==== Popup for Log & Tree ====
popup_win = None
log_text = None
 
live_count = 0
die_count = 0

# --- Biến toàn cục ---
ava_folder_path = ""

chrome_path = ""
used_positions = {} # driver: (x, y)
available_positions = []
cols = 6 # số cột
rows = 3 # số hàng
win_w = 320 # chiều rộng cửa sổ
win_h = 360 # chiều cao cửa sổ


for r in range(rows):
    for c in range(cols):
        x = c * win_w
        y = r * win_h
        available_positions.append((x, y))


pos_lock = threading.Lock()

def release_position(driver):
    try:
        with pos_lock:
            if driver in used_positions:
                del used_positions[driver]
    except Exception:
        pass

def choose_chrome_folder():
    global chrome_path
    folder = filedialog.askdirectory(title="Chọn thư mục chứa Chrome")
    if folder:
        chrome_path = os.path.join(folder, "chrome.exe")
        if os.path.isfile(chrome_path):
            print(f"🧭 Đã chọn chrome tại: {chrome_path}")
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy chrome.exe trong thư mục này.")
            chrome_path = ""

def arrange_after_open(driver, tries=40):
    time.sleep(1)
    for _ in range(tries):
        try:
            # 🔒 lấy vị trí trống trong lưới
            with pos_lock:
                for pos in available_positions:
                    if pos not in used_positions.values():
                        driver.set_window_position(*pos)
                        used_positions[driver] = pos
                        break

            # ⚡ set size mặc định theo lưới, sử dụng get_chrome_size() nếu cần
            w, h = get_chrome_size()  # Lấy size từ GUI (hoặc giá trị mặc định)
            driver.set_window_size(w, h)

            # ⚡ set scale (giữ nguyên hàm get_chrome_scale)
            try:
                scale = get_chrome_scale()  # Lấy scale từ GUI (hoặc giá trị mặc định)
                driver.execute_cdp_cmd(
                    "Emulation.setPageScaleFactor",
                    {"pageScaleFactor": scale}
                )
                log(f"🔍 Scale Chrome: {int(scale * 100)}%")
            except Exception as e:
                log(f"⚠️ Không chỉnh được scale: {repr(e)}")

            break
        except Exception:
            time.sleep(1)

format_fields = ["Username", "Pass", "Mail", "2FA", "Cookie"]
save_format  = ["Username", "Pass", "Mail", "Cookie", "2FA"]

def update_rate():
    try:
        live = int(live_var.get())
        die  = int(die_var.get())
        total = live + die
        if total > 0:
            rate = round((live / total) * 100, 2)
            rate_var.set(f"{rate}%")
        else:
            rate_var.set("0%")
    except Exception:
        rate_var.set("0%")

bio_index_seq = {"desktop": 0, "mobile": 0}  # đếm cho chế độ tuần tự

def _lines_from_widget(widget):
    try:
        raw = widget.get("1.0", tk.END)
    except Exception:
        return []
    return [ln.strip() for ln in raw.splitlines() if ln.strip()]

def get_bio_text(context: str = "auto"):
    """
    Trả về Bio theo 4 mode: custom | random | sequential | default.
    - context='desktop'  -> dùng biến Desktop (bio_* cũ)
    - context='mobile'   -> dùng biến Mobile (m_bio_*)
    - context='auto'     -> theo ui_mode_var ('desktop' / 'mobile')
    """
    DEFAULT_BIO = "Tymmmmmm"

    # xác định nguồn
    try:
        mode_ui = ui_mode_var.get().strip().lower()
    except Exception:
        mode_ui = "desktop"
    src = (mode_ui if context == "auto" else context).lower()
    if src not in ("desktop", "mobile"):
        src = "desktop"

    # lấy biến theo nguồn
    if src == "mobile":
        default_on = bool(m_bio_default_var.get()) if "m_bio_default_var" in globals() else False
        custom_on  = bool(m_bio_custom_var.get())  if "m_bio_custom_var"  in globals() else False
        mode_val   = (m_bio_mode_var.get() if "m_bio_mode_var" in globals() else "random") or "random"
        widget     = bio_text
    else:
        default_on = bool(bio_default_var.get()) if "bio_default_var" in globals() else False
        custom_on  = bool(bio_custom_var.get())  if "bio_custom_var"  in globals() else False
        mode_val   = (bio_mode_var.get() if "bio_mode_var" in globals() else "random") or "random"
        widget     = globals().get("bio_text")

    # 1) mặc định
    if default_on:
        return DEFAULT_BIO

    # 2) theo yêu cầu
    if custom_on and widget is not None:
        lines = _lines_from_widget(widget)
        if not lines:
            return DEFAULT_BIO
        mv = mode_val.lower()
        if mv == "random":
            return random.choice(lines)
        # sequential
        idx = bio_index_seq[src] % len(lines)
        bio_index_seq[src] += 1
        return lines[idx]

    # fallback
    return DEFAULT_BIO


# --- Lưu & Load config (dùng 1 file config.json) ---
CONFIG_FILE = "config.json"
def save_config():
    cfg = {
        "ava_folder_path": globals().get("ava_folder_path", ""),
        "chrome_path": globals().get("chrome_path", ""),
        "save_format": globals().get("save_format", ""),
        "photo_folder_phone": globals().get("photo_folder_phone", ""),
        "ig_app_choice": globals().get("phone_ig_app_var", tk.StringVar(value="instagram")).get(),
        "scrcpy_path": globals().get("scrcpy_path", ""),
        "hidden_chrome": hidden_chrome_var.get()
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def load_config():
    global ava_folder_path, chrome_path, save_format, photo_folder_phone, scrcpy_path
    config_file = CONFIG_FILE
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                ava_folder_path = cfg.get("ava_folder_path", "")
                chrome_path = cfg.get("chrome_path", "")
                save_format = cfg.get("save_format", "")
                photo_folder_phone = cfg.get("photo_folder_phone", "")
                scrcpy_path = cfg.get("scrcpy_path", "")
                if "ig_app_choice" in cfg:
                    try:
                        phone_ig_app_var.set(cfg["ig_app_choice"])
                    except Exception:
                        pass
                if "hidden_chrome" in cfg:
                    try:
                        hidden_chrome_var.set(cfg["hidden_chrome"])
                    except Exception:
                        pass
                if ava_folder_path:
                    log(f"📂 Đã load thư mục ảnh: {ava_folder_path}")
                if chrome_path:
                    log(f"🌐 Đã load Chrome: {chrome_path}")
                if photo_folder_phone:
                    log(f"📂 Đã load folder ảnh (Phone): {photo_folder_phone}")
                if scrcpy_path:
                    _log_scrcpy_path(scrcpy_path)
        except Exception as e:
            log(f"⚠ Không load được config.json: {e}")

def _log_scrcpy_path(p: str):
    # log path rút gọn cho gọn UI
    if not p:
        log("⚠️ scrcpy: chưa cấu hình đường dẫn.")
        return
    short = (p if len(p) <= 72 else f"{p[:30]} ... {p[-30:]}")
    log(f"🧭 scrcpy path: {short}")

def load_scrcpy_config():
    load_config()

def save_scrcpy_config():
    save_config()

scrcpy_path = ""
resolution = "540x960"

# ====== insert tree ======
def insert_to_tree(status_text, username, password, email, cookie_str, two_fa_code=""):
    try:
        status_lower = str(status_text).lower()
        if status_lower == "live":
            status_tag = "LIVE"
        elif status_lower == "die":
            status_tag = "DIE"

        phone_val  = ""  # hoặc lấy từ biến của bạn nếu có
        token_val  = ""  # để trống
        two_fa_val = two_fa_code if two_fa_code else ""

        tree.insert(
            "", "end",
            values=(
                len(tree.get_children())+1,   # STT
                status_text,                  # TRẠNG THÁI
                username, password, email,
                phone_val, cookie_str,
                two_fa_val, token_val,
                "127.0.0.1", "NoProxy",
                "LIVE" if status_tag == "LIVE" else "",
                "DIE"  if status_tag == "DIE"  else "",
            ),
            tags=(status_tag,)
        )
        log(f"✅ Đã insert {status_text} lên TreeView: {username}")
    except Exception as e:
        log(f"⚠️ Không thể thêm vào Treeview (helper): {repr(e)}")

# --- Chọn Chrome ---
def select_chrome():
    global chrome_path
    # Mở hộp thoại chọn thư mục
    folder = filedialog.askdirectory(title="Chọn thư mục chứa Chrome")
    
    if folder:
        # Tạo đường dẫn đến tệp chrome.exe trong thư mục đã chọn
        chrome_path = os.path.join(folder, "chrome.exe")
        
        # Kiểm tra xem chrome.exe có tồn tại trong thư mục không
        if os.path.isfile(chrome_path):
            log(f"🧭 Đã chọn chrome tại: {chrome_path}")
        else:
            # Nếu không tìm thấy chrome.exe, hiển thị thông báo lỗi
            messagebox.showerror("Lỗi", "Không tìm thấy chrome.exe trong thư mục này.")
            chrome_path = ""  # Đặt lại giá trị của chrome_path nếu không tìm thấy tệp chrome.exe

# --- Chọn định dạng lưu ---
def update_save_format():
    global save_format
    save_format = [cb.get() for cb in format_boxes if cb.get()]
    save_config()
    log(f"💾 Định dạng lưu: {'|'.join(save_format)}")
    
def select_ava_folder():
    global ava_folder_path
    folder = filedialog.askdirectory(title="Chọn thư mục ảnh avatar")
    if folder:
        ava_folder_path = folder
        save_config()
        log(f"✅ Đã chọn thư mục ảnh: {ava_folder_path}")

# Hàm Nút khởi động lại
def restart_tool():
    try:
        # Đóng tất cả Chrome đang chạy
        subprocess.run("taskkill /F /IM chrome.exe", shell=True)
        log("🛑 Đã đóng Chrome.")

        # Lấy đường dẫn tuyệt đối của file .py hiện tại
        script_path = os.path.realpath(__file__)   # luôn ra đúng V3 BackUP.py
        python_exe = sys.executable

        # Ghép lệnh restart
        cmd = f'"{python_exe}" "{script_path}"'

        log(f"🔁 Đang khởi động lại tool...\n➡ CMD: {cmd}")
        subprocess.Popen(cmd, shell=True)

        # Thoát tool hiện tại
        os._exit(0)

    except Exception as e:
        log(f"❌ Không thể khởi động lại tool: {repr(e)}")

def pause():
    pause_event.clear()
    log("⏸️ Đã tạm dừng tất cả luồng.")

def resume():
    pause_event.set()
    log("▶️ Tiếp tục chạy các luồng.")


def log(message):
    # log_text được tạo sau; đảm bảo hàm gọi chỉ sau khi GUI tạo xong
    try:
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, f"{message}\n")
        log_text.yview(tk.END)
        log_text.config(state=tk.DISABLED)
    except Exception:
        print(message)

# === Hàm điều khiển WARP ===

def warp_on():
    try:
        subprocess.run(["warp-cli", "connect"], check=True)
        log("🌐 Đã bật Cloudflare WARP")
        time.sleep(3)
    except Exception as e:
        log(f"❌ Lỗi bật WARP: {repr(e)}")

def warp_off():
    try:
        subprocess.run(["warp-cli", "disconnect"], check=True)
        log("🌐 Đã tắt Cloudflare WARP")
        time.sleep(3)
    except Exception as e:
        log(f"❌ Lỗi tắt WARP: {repr(e)}")

def warp_change_ip():
    try:
        log("🔄 Đang đổi IP WARP...")
        subprocess.run(["warp-cli", "disconnect"], check=True)
        time.sleep(2)
        subprocess.run(["warp-cli", "connect"], check=True)
        time.sleep(3)
        ip = requests.get("https://api.ipify.org").text
        log(f"✅ IP WARP mới: {ip}")
    except Exception as e:
        log(f"❌ Lỗi đổi IP WARP: {repr(e)}")

def toggle_warp():
    global warp_enabled
    warp_enabled = not warp_enabled
    if warp_enabled:
        warp_toggle_btn.config(text="WARP ON", bg="green", fg="white")
        log("🌐 WARP mode ENABLED - sẽ dùng WARP, bỏ qua proxy.")
    else:
        warp_toggle_btn.config(text="WARP OFF", bg="red", fg="white")
        log("🌐 WARP mode DISABLED - sẽ dùng proxy nếu có.")

def run_phone_android():
    try:
        log("🚀 [Phone] Khởi động Appium server…")
        if not start_appium_server():
            log("❌ [Phone] Không thể khởi động Appium. Vui lòng cài appium hoặc kiểm tra PATH.")
            return
        log(f"✅ [Phone] Appium OK tại {APPIUM_HOST}:{APPIUM_PORT}")

        # 1) ƯU TIÊN: lấy theo cột "CHỌN" trong bảng 3 cột
        selected = []
        if 'get_checked_udids' in globals():
            selected = get_checked_udids("pick")  # các UDID đã tick cột CHỌN

        if not selected:
            devices = adb_devices()
            if not devices:
                log("⛔ [Phone] Không phát hiện thiết bị Android (adb devices trống).")
                log("➡ Bật USB debugging, cắm cáp, đồng ý RSA, rồi chạy lại.")
                return
            selected = devices

        log(f"📱 [Phone] Thiết bị dùng: {', '.join(selected)}")

        # Khởi chạy 1 worker/thiết bị
        for udid in selected:
            if not pause_event.is_set():
                pause_event.wait()
            w = AndroidWorker(udid, log_fn=log)
            w.start()
            log(f"▶️ [Phone] Đã start worker cho {udid}")
            time.sleep(0.6)

        # (Tuỳ chọn) nếu bạn muốn tự mở scrcpy cho các máy đã tick cột VIEW:
        try:
            if 'get_checked_udids' in globals() and 'open_scrcpy_for_list' in globals():
                view_list = get_checked_udids("view")
                if view_list:
                    open_scrcpy_for_list(view_list)
        except Exception:
            pass

    except Exception as e:
        log(f"❌ [Phone] Lỗi tổng run_phone_android: {repr(e)}")

# >>> ADD: Mobile Chrome builder (standalone)
def build_mobile_chrome_driver(proxy: str | None, log_fn=log):
    """
    Tạo Chrome ở chế độ Mobile (emulate iPhone) dành cho chế độ Desktop/Mobile.
    - Không đụng tới Appium/ADB/WARP app Android.
    - Luôn dùng Selenium Chrome (se_webdriver.Chrome).
    """
    chrome_path   = globals().get("chrome_path", "")  # path đến chrome.exe nếu user chọn
    warp_enabled  = bool(globals().get("warp_enabled", False))
    all_drivers   = globals().get("all_drivers", None)
    arrange_after = globals().get("arrange_after_open", None)

    mobile_options = Options()
    mobile_options.add_argument("--disable-blink-features=AutomationControlled")
    mobile_options.add_argument("--no-first-run")
    mobile_options.add_argument("--disable-background-networking")
    mobile_options.add_argument("--disable-background-timer-throttling")
    mobile_options.add_argument("--disable-client-side-phishing-detection")
    # Thêm headless nếu được chọn
    if hidden_chrome_var.get():
        mobile_options.add_argument("--headless=new")

    # Emulate iPhone 15 Pro (UA + viewport)
    mobile_emulation = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/137.0.0.0 "
            "Mobile/15E148 Safari/604.1"
        )
    }
    mobile_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Proxy: chỉ áp nếu không bật WARP (PC) và có proxy
    # Chấp nhận 'http://x:y', 'socks5://x:y' hoặc chỉ 'host:port' (mặc định http)
    if not warp_enabled and proxy:
        if "://" not in proxy:
            proxy = f"http://{proxy}"
        mobile_options.add_argument(f"--proxy-server={proxy}")

    # Nếu người dùng đã chọn binary chrome
    if chrome_path:
        mobile_options.binary_location = chrome_path

    # Chromedriver:
    # - Nếu có chromedriver.exe cạnh file, dùng nó
    # - Nếu không, để trống để Selenium tự tìm trong PATH
    driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
    if os.path.isfile(driver_path):
        service = Service(driver_path)
    else:
        service = Service()  # dùng chromedriver trong PATH

    # ❗ Quan trọng: dùng Selenium webdriver, KHÔNG dùng appium.webdriver
    drv = se_webdriver.Chrome(service=service, options=mobile_options)

    # Quản lý danh sách + sắp xếp cửa sổ (nếu có helper)
    try:
        if isinstance(all_drivers, list):
            all_drivers.append(drv)
        if callable(arrange_after):
            threading.Thread(target=arrange_after, args=(drv,), daemon=True).start()
    except Exception:
        pass

    if log_fn:
        log_fn("📱 Chrome Mobile đã khởi tạo (emulation iPhone).")
    return drv

def start_process():
    global sync_barrier, thread_list
    try:
        num_threads = int(threads_entry.get())
    except:
        log("❌ Số luồng không hợp lệ.")
        return

    mode = ui_mode_var.get().strip().lower()

    # === Phone (Android) → tự chạy Appium ===
    if mode == "phone":
        pause_event.wait()
        threading.Thread(target=run_phone_android, daemon=True).start()
        return

    # === Desktop/Mobile (Selenium) như cũ ===
    sync_barrier = threading.Barrier(num_threads)
    thread_list = []
    pause_event.wait()

    target_fn = run_mobile if mode == "mobile" else run

    def run_wrapper(tid):
        try:
            target_fn(tid)
        except Exception as e:
            log(f"❌ Lỗi {target_fn.__name__} ở luồng {tid}: {repr(e)}")

    for i in range(num_threads):
        t = threading.Thread(target=run_wrapper, args=(i+1,), daemon=True)
        t.start()
        thread_list.append(t)
        time.sleep(1)

def get_tempasia_email():
    url = "https://free.priyo.email/api/random-email/7jkmE5NM2VS6GqJ9pzlI"
    headers = {"accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.ok:
            return resp.json().get("email")
        log(f"❌ TempAsia HTTP {resp.status_code}")
    except Exception as e:
        log(f"❌ Lỗi TempAsia API: {repr(e)}")
    return None

def wait_for_tempmail_code(email, max_checks=30, interval=2):
    """
    Poll API temp-mail.asia để lấy mã 6 số từ subject/email.
    Trả về code string hoặc None nếu hết hạn.
    """
    headers = {"accept": "application/json"}
    email_enc = email.replace("@", "%40")
    url = f"https://free.priyo.email/api/messages/{email_enc}/7jkmE5NM2VS6GqJ9pzlI"

    for i in range(max_checks):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.ok:
                msgs = r.json()
                if msgs:
                    subj = msgs[0].get("subject", "")
                    body = msgs[0].get("body","")
                    m = re.search(r"\b\d{6}\b", subj) or re.search(r"\b\d{6}\b", body)
                    if m:
                        return m.group(0)
        except Exception as e:
            log(f"⚠️ Lỗi khi đọc mail: {repr(e)}")
        time.sleep(interval)
    return None

def get_dropmail_email():
    url = "https://dropmail.me/api/graphql/my_token_123"
    query = """
    mutation {
      introduceSession {
        id
        expiresAt
        addresses {
          address
        }
      }
    }
    """
    try:
        resp = requests.post(url, json={"query": query}, timeout=10)
        data = resp.json()
        session = data["data"]["introduceSession"]
        email = session["addresses"][0]["address"]
        session_id = session["id"]
        return email, session_id
    except Exception as e:
        log(f"❌ Lỗi DropMail API: {repr(e)}")
        return None, None

def wait_for_dropmail_code(self, session_id, max_checks=5, interval=5, overall_timeout=300):
    """
    Chờ và lấy mã OTP (6 số) từ DropMail session.
    """
    url = "https://dropmail.me/api/graphql/my_token_123"
    query = """
    query($id: ID!) {
        session(id: $id) {
            mails { fromAddr headerSubject text }
        }
    }"""

    start_time = time.time()
    checks = 0
    while (time.time() - start_time) < overall_timeout and checks < max_checks:
        try:
            resp = requests.post(
                url,
                json={"query": query, "variables": {"id": session_id}},
                timeout=10
            )
            data = resp.json()
            mails = data["data"]["session"]["mails"]

            if mails:
                for mail in mails:
                    text = mail.get("text", "")
                    subject = mail.get("headerSubject", "")
                    match = re.search(r"\b\d{6}\b", text) or re.search(r"\b\d{6}\b", subject)
                    if match:
                        code = match.group(0)
                        self.log(f"📩 Nhận được mã DropMail: {code}")
                        return code

            checks += 1
            self.log(f"⌛ Chưa có mail DropMail (lần {checks}/{max_checks}), chờ thêm...")
        except Exception as e:
            checks += 1
            self.log(f"❌ Lỗi khi kiểm tra DropMail (lần {checks}/{max_checks}): {repr(e)}")

        time.sleep(interval)

    self.log("⛔ Quá 5 lần kiểm tra DropMail mà chưa có mã — bỏ phiên.")
    return None

def fetch_signup_email(self):
    try:
        # Ưu tiên dùng biến chọn nguồn mail trong UI: 'dropmail' | 'tempasia'
        mode = self.var_mail_src.get().strip().lower()
    except Exception:
        mode = "tempasia"

    if mode == "dropmail":
        email, sid = get_dropmail_email()   # đã có trong AutoPhoneInstagram.py
        if not email:
            self.log("⛔ Không lấy được email từ DropMail.")
            return None, None, "dropmail"
        self.drop_session_id = sid          # lưu để chờ OTP
        self.log(f"✅ Email DropMail: {email}")
        return email, sid, "dropmail"

    # fallback: temp-mail.asia
    email = get_tempasia_email()            # đã có trong AutoPhoneInstagram.py
    if not email:
        self.log("⛔ Không lấy được email từ Temp-mail.asia.")
        return None, None, "tempasia"
    self.log(f"✅ Email Temp-mail: {email}")
    return email, None, "tempasia"

# >>> ADD: Mobile-only flow
def run_mobile(thread_id=None):
    """
    Đăng ký tài khoản Instagram hoàn toàn trên giao diện Mobile.
    Không dùng form Desktop / không chuyển qua Desktop giữa chừng.
    """
    while True:
        pause_event.wait()
        log("🟢 [Mobile] Bắt đầu tạo tài khoản...")

        # 1) Lấy email tạm (tận dụng 2 checkbox có sẵn)
        email = None
        session_id = None
        try:
            if dropmail_var.get():
                log("📨 [Mobile] Lấy email từ DropMail.me...")
                email, session_id = get_dropmail_email()
                if not email:
                    log("⛔ Không thể lấy email DropMail — dừng.")
                    return
                log(f"✅ Email DropMail: {email}")
            elif tempmail_var.get():
                log("📨 [Mobile] Lấy email từ temp-mail.asia (API)...")
                headers = {"accept": "application/json"}
                # dùng endpoint đã dùng ở file V3.py để đồng bộ
                resp = requests.get(
                    "https://free.priyo.email/api/random-email/7jkmE5NM2VS6GqJ9pzlI",
                    headers=headers, timeout=15
                )
                if resp.status_code == 200:
                    email = resp.json().get("email")
                    log(f"✅ Email lấy được: {email}")
                else:
                    log(f"❌ Lỗi HTTP {resp.status_code} khi lấy email")
                    return
            else:
                log("⛔ Bạn chưa chọn dịch vụ mail tạm (DropMail hoặc Temp-Mail).")
                return
        except Exception as e:
            log(f"❌ Lỗi lấy email: {repr(e)}")
            return

        # 2) Sinh info cơ bản (tận dụng generator VN name trong file)
        def generate_vietnamese_name():
            ho_list = ["Nguyễn","Trần","Lê","Phạm","Hoàng","Phan","Vũ","Đặng","Bùi","Đỗ"]
            ten_dem_list = ["Văn","Thị","Hữu","Gia","Ngọc","Đức","Thanh","Minh","Quang","Trọng"]
            ten_list = ["Anh","Bình","Châu","Dũng","Hà","Hùng","Lan","Linh","Nam","Phúc","Quỳnh","Sơn","Trang","Tuấn","Vy"]
            return f"{random.choice(ho_list)} {random.choice(ten_dem_list)} {random.choice(ten_list)}"

        full_name = generate_vietnamese_name()
        username_base = re.sub(r'[^a-z0-9]', '', unidecode(full_name.lower()))
        username = f"{username_base}{random.randint(100,999)}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        age = str(random.randint(18, 30))
        log(f"👤 Họ tên: {full_name}")
        log(f"🔤 Username: {username}")
        log(f"🔐 Mật khẩu: {password}")

        # 3) Khởi Chrome Mobile
        try:
            proxy = (proxy_entry.get().strip() if proxy_entry else "")
            if warp_enabled:
                log("🌐 [Mobile] WARP bật → bỏ qua proxy.")
            else:
                log(f"🌐 [Mobile] WARP tắt → proxy: {proxy or 'No proxy'}")

            driver = build_mobile_chrome_driver(proxy)
            wait = WebDriverWait(driver, 15)

            # Đến trang mobile signup (đúng theo giao diện mobile)
            driver.get("https://www.instagram.com/accounts/signup/email/")
            pause_event.wait()
            log("🌐 [Mobile] Đã truy cập trang đăng ký (Mobile).")
            time.sleep(3)
        except Exception as e:
            log(f"❌ [Mobile] Lỗi khởi tạo trình duyệt: {repr(e)}")
            try:
                release_position(driver); driver.quit()
            except: pass
            continue

        try:
            # 4) Nhập email
            email_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[aria-label="Email"]')))
            type_text_slowly(email_input, email, delay=get_mobile_delay("Mail_type", 0.18))
            log("✅ [Mobile] Đã nhập email.")
            time.sleep(get_mobile_delay("Mail_sleep", 1))

            # NEXT 1
            next_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[role="button"][aria-label="Next"]')))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            next_btn.click()
            log("➡️ [Mobile] Next sau email.")
            time.sleep(get_mobile_delay("Mail_next", 2))
        except Exception as e:
            log(f"❌ [Mobile] Sai giao diện/không thấy Next sau email: {e}")
            try:
                release_position(driver); driver.quit()
            except: pass
            continue

        # 5) Resend code (nếu cần) → tương thích với code bạn đưa
        try:
            time.sleep(5)
            log("⏳ [Mobile] Click 'I didn’t get the code'...")
            button_i_didnt_get = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and contains(., \"I didn’t get the code\")]")))
            button_i_didnt_get.click()
            log("✅ [Mobile] Đã bấm 'I didn’t get the code'")
            time.sleep(2)

            log("⏳ [Mobile] Click 'Resend confirmation code'...")
            resend_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and contains(., 'Resend confirmation code')]")))
            resend_btn.click()
            log("✅ [Mobile] Đã bấm 'Resend confirmation code'")
            time.sleep(3)
        except Exception as e:
            log(f"❌ [Mobile] Lỗi phần resend code: {e}")
            try:
                release_position(driver); driver.quit()
            except: pass
            continue

        # 6) Lấy mã xác minh email
        def wait_for_dropmail_code_mobile(session_id, max_checks=30, interval=2):
            url = "https://dropmail.me/api/graphql/my_token_123"
            query = """query($id: ID!){ session(id:$id){ mails{ headerSubject text } } }"""
            for i in range(max_checks):
                try:
                    resp = requests.post(url, json={"query": query, "variables": {"id": session_id}}, timeout=10)
                    data = resp.json()
                    mails = data["data"]["session"]["mails"] if data.get("data") else []
                    if mails:
                        subj = mails[0].get("headerSubject","")
                        text = mails[0].get("text","")
                        m = re.search(r"\b\d{6}\b", subj) or re.search(r"\b\d{6}\b", text)
                        if m: return m.group(0)
                except: pass
                time.sleep(interval)
            return None

        def wait_for_tempmail_code_mobile(email, max_checks=30, interval=2):
            headers = {"accept": "application/json"}
            email_enc = email.replace("@","%40")
            mail_url = f"https://free.priyo.email/api/messages/{email_enc}/7jkmE5NM2VS6GqJ9pzlI"
            for i in range(max_checks):
                try:
                    r = requests.get(mail_url, headers=headers, timeout=10)
                    if r.status_code == 200:
                        msgs = r.json()
                        if msgs:
                            subj = msgs[0].get("subject","")
                            m = re.search(r"\b\d{6}\b", subj)
                            if m: return m.group(0)
                except: pass
                time.sleep(interval)
            return None

        try:
            log("⏳ [Mobile] Đang chờ mã xác minh trong email...")
            code = None
            if dropmail_var.get():
                code = wait_for_dropmail_code_mobile(session_id)
            elif tempmail_var.get():
                code = wait_for_tempmail_code_mobile(email)

            if not code:
                log("⏰ [Mobile] Không nhận được mã xác minh — restart vòng lặp.")
                try:
                    release_position(driver); driver.quit()
                except: pass
                continue

            log(f"🔢 [Mobile] Mã xác minh: {code}")
            # Nhập mã xác minh
            code_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='Confirmation code']")))
            code_input.clear()
            type_text_slowly(code_input, code, delay=get_mobile_delay("Code_type", 0.30))
            log("✅ [Mobile] Đã nhập mã xác minh.")
            time.sleep(get_mobile_delay("Code_sleep", 2))

            # NEXT sau code
            try:
                next_btn = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'div[role="button"][aria-label="Next"]')))
                next_btn.click()
                log("🎉 [Mobile] Hoàn thành bước xác minh mã.")
                time.sleep(get_mobile_delay("Code_next", 2))
            except:
                log("⚠️ [Mobile] Không thấy Next sau khi nhập code.")
            time.sleep(2)
        except Exception as e:
            log(f"❌ [Mobile] Lỗi khi lấy/nhập mã xác minh: {e}")
            try:
                release_position(driver); driver.quit()
            except: pass
            continue
        warp_off()

        # 7) Nhập Password → Next qua vài bước
        try:
            # 7) Nhập Password → Next
            pass_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[aria-label="Password"]')))
            type_text_slowly(pass_input, password, delay=get_mobile_delay("Pass_type", 0.18))
            log("✅ [Mobile] Đã nhập pass.")
            time.sleep(get_mobile_delay("Pass_sleep", 3))

            # Next sau pass (một hoặc vài màn hình)
            for _ in range(3):
                try:
                    nb = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'div[role="button"][aria-label="Next"]')))
                    nb.click()
                    log("➡️ [Mobile] Next…")
                    time.sleep(get_mobile_delay("Pass_next", 2))
                except:
                    break
        except Exception as e:
            log(f"❌ [Mobile] Lỗi khi nhập pass/next: {e}")

        # 8) Nhập Age
        try:
            age_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[aria-label="Age"]')))
            type_text_slowly(age_input, age, delay=get_mobile_delay("Tuổi_type", 0.18))
            log("✅ [Mobile] Đã nhập tuổi.")
            time.sleep(get_mobile_delay("Tuổi_sleep", 2))

            nb = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[role="button"][aria-label="Next"]')))
            nb.click()
            log("➡️ [Mobile] Next sau tuổi.")
            time.sleep(get_mobile_delay("Tuổi_next", 2))

            # click OK nếu có
            driver.execute_script("""
                let okBtn = [...document.querySelectorAll("div[role='button']")]
                    .find(el => el.innerText.trim() === "OK");
                if (okBtn) okBtn.click();
            """)
        except Exception as e:
            log(f"⚠️ [Mobile] Bỏ qua Age (không thấy field): {e}")

        # 9) Nhập Full name → Next
        try:
            full_name_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[aria-label="Full name"]')))
            type_text_slowly(full_name_input, full_name, delay=get_mobile_delay("Họ tên_type", 0.18))
            log("✅ [Mobile] Đã nhập Tên.")
            time.sleep(get_mobile_delay("Họ tên_sleep", 2))

            nb = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[role="button"][aria-label="Next"]')))
            nb.click()
            log("➡️ [Mobile] Next sau họ tên.")
            time.sleep(get_mobile_delay("Họ tên_next", 2))
        except Exception as e:
            log(f"❌ [Mobile] Lỗi nhập tên/Next: {e}")

        # 10) Username (đọc lại gợi ý) → Next
        try:
            ui = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[aria-label="Username"]')))
            uname_val = ui.get_attribute("value") or username
            if uname_val != username:
                log(f"🔁 [Mobile] Username gợi ý: {username} ➜ {uname_val}")
                username = uname_val
            nb = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[role="button"][aria-label="Next"]')))
            nb.click()
            log("➡️ [Mobile] Next sau username.")
        except Exception as e:
            log(f"⚠️ [Mobile] Bỏ qua kiểm username: {e}")
        time.sleep(10)
        # 11) I agree (nếu có nhiều lần)
        try:
            for i in range(3):
                try:
                    agree = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, 'div[role="button"][aria-label="I agree"]')))
                    agree.click()
                    log(f"✅ [Mobile] Đã bấm I agree lần {i+1}.")
                    time.sleep(6)
                except:
                    break
        except Exception as e:
            log(f"⚠️ [Mobile] Không thấy 'I agree' thêm: {e}")

        log("🎉 [Mobile] Hoàn tất đăng ký.")
        time.sleep(20)
        # === CHECK LIVE/DIE ===
        try:
            global live_count, die_count
            profile_url = f"https://www.instagram.com/{username}/"
            log("🌐 Đang kiểm tra trạng thái Live/Die...")
            driver.get(profile_url)
            time.sleep(6)  # có thể thay bằng WebDriverWait nếu muốn

            current_url = driver.current_url
            page_source = driver.page_source

            # Mặc định
            status_text = "Unknown"

            # Phân loại trạng thái
            if "/accounts/login/" in current_url or "Sorry, this page isn't available" in page_source:
                status_text = "Die"
            elif "checkpoint" in current_url.lower() or "Confirm you're human" in page_source:
                status_text = "Checkpoint"
            elif (f"@{username}" in page_source) or (f"instagram.com/{username}" in current_url):
                status_text = "Live"
            else:
                status_text = "Die"

            # Cập nhật biến đếm + log
            if status_text == "Live":
                live_count += 1
                live_var.set(str(live_count))
                update_rate()
                log("✅ Tài khoản Live")
            else:
                die_count += 1
                die_var.set(str(die_count))
                update_rate()
                log(f"❌ {status_text} — tính là Die")

            # === Lấy Cookie ===
            try:
                cookies = driver.get_cookies()
                cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies]) if cookies else ""
                log("🍪 Cookie hiện tại:")
                log(cookie_str if cookie_str else "(empty)")
                time.sleep(3)
            except Exception as e:
                cookie_str = ""
                log(f"❌ Lỗi khi lấy cookie: {repr(e)}")

            # Nếu KHÔNG phải Live thì insert ngay bây giờ
            if status_text.lower() in ("die", "checkpoint", "unknown"):
                # nếu có app (Tk root) thì:
                try:
                    app.after(0, lambda: insert_to_tree(status_text, username, password, email, cookie_str, two_fa_code=""))
                except:
                    insert_to_tree(status_text, username, password, email, cookie_str, two_fa_code="")

                # Lưu file (optional) – có fallback cho save_format
                try:
                    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Die.txt")
                    info_map = {"Username": username, "Pass": password, "Mail": email, "Cookie": cookie_str, "2FA": ""}
                    fields = save_format if ('save_format' in globals() and isinstance(save_format, (list,tuple)) and save_format) \
                            else ["Username","Pass","Mail","Cookie","2FA"]
                    line = "|".join([info_map.get(field, "") for field in fields])
                    with open(file_path, "a", encoding="utf-8") as f:
                        f.write(line + "\n")
                    log(f"💾 (Die early) Đã lưu thông tin vào '{file_path}'")
                except Exception as e:
                    log(f"❌ (Die early) Lỗi khi lưu file: {repr(e)}")

                # Quyết định restart
                try:
                    time.sleep(2)
                    release_position(driver)
                    driver.quit()
                    driver = None
                except:
                    pass
                log("🔁 Khởi chạy lại phiên...")
                continue
            else:
                log("➡️ LIVE: Tiếp tục BƯỚC TIẾP THEO")

        except Exception as e:
            log(f"⚠️ Lỗi khi check live/die: {repr(e)}")

        # Quay lại giao diện Desktop
        log("🖥 Quay lại giao diện Desktop...")
        driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })
        driver.refresh()
        time.sleep(5)

        # === BƯỚC 7: Xử lý bật 2FA ===
        if enable_2fa.get():
            try:
                pause_event.wait()
                log("🔐 Bắt đầu bật xác thực hai yếu tố (2FA)...")
                time.sleep(3)

                # Truy cập trang bật 2FA
                driver.get("https://accountscenter.instagram.com/password_and_security/two_factor/?theme=dark")
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(5)

                # Chọn tài khoản Instagram
                try:
                    account_btn = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((
                            By.XPATH, "//div[@role='button' and descendant::div[contains(text(),'Instagram')]]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", account_btn)
                    time.sleep(1)
                    account_btn.click()
                    log("✅ Đã chọn tài khoản Instagram")
                    time.sleep(3)
                except Exception as e:
                    log(f"⚠️ Không chọn được tài khoản: {repr(e)}")
                    return

                # Nhấn nút "Continue"
                try:
                    continue_btn = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "//div[@role='button' and descendant::span[normalize-space(text())='Continue']]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", continue_btn)
                    log("✅ Đã click nút Continue")
                    time.sleep(3)
                except Exception as e:
                    log(f"❌ Không thể click nút Continue: {repr(e)}")
                    return

                # Lấy mã 2FA secret
                try:
                    span_xpath = "//div[contains(@class,'x16grhtn')]//span"
                    span_elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, span_xpath))
                    )
                    two_fa_code = span_elem.text.strip().replace(" ", "")
                    log(f"🔐 Mã 2FA secret: {two_fa_code}")
                except Exception as e:
                    log(f"❌ Không lấy được mã 2FA secret: {repr(e)}")
                    return

                # Nhấn nút Next để chuyển tới nhập mã OTP
                try:
                    next_btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH, "//div[@role='button' and descendant::span[normalize-space(text())='Next']]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_btn)
                    log("✅ Đã nhấn nút Next để nhập mã OTP")
                    time.sleep(3)
                except Exception as e:
                    log(f"❌ Không nhấn được nút Next sau mã secret: {repr(e)}")
                    return

                # Sinh mã OTP từ mã secret bằng pyotp
                otp_code = None
                try:
                    totp = pyotp.TOTP(two_fa_code)
                    otp_code = totp.now()
                    log(f"🔢 Mã OTP tạo từ pyotp: {otp_code}")
                except Exception as e:
                    log(f"❌ Lỗi khi tạo OTP từ pyotp: {repr(e)}")
                    return

                # Nhập mã OTP vào ô nhập
                if otp_code:
                    try:
                        otp_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @maxlength='6']"))
                        )
                        otp_input.clear()
                        otp_input.send_keys(otp_code)
                        log("✅ Đã nhập mã OTP.")
                        time.sleep(2)
                    except Exception as e:
                        log(f"❌ Lỗi khi nhập OTP: {repr(e)}")
                    # Nhấn nút Next cuối cùng để hoàn tất bật 2FA
                    try:
                        driver.execute_script("""
                            [...document.querySelectorAll("div[role='button']")].forEach(el => {
                                if (el.innerText.trim() === 'Next') el.click();
                            });
                        """)
                        log("✅ Đã nhấn nút Next để hoàn tất bật 2FA")
                        time.sleep(6)
                        wait_all("Bật 2FA", thread_id)
                    except Exception as e:
                        log(f"❌ Lỗi khi nhấn nút Next hoàn tất 2FA: {repr(e)}")
                        return
                    driver.execute_script("""
                    const btn = [...document.querySelectorAll("button, div[role=button]")]
                        .find(el => el.textContent.trim() === "Done");

                    if (btn) {
                        btn.click();
                        return true;
                    } else {
                        return false;
                    }
                    """)
            except Exception as e:
                log(f"❌ Lỗi toàn bộ bước bật 2FA: {repr(e)}")
            time.sleep(3)

            # === Insert vào Treeview ===
            try:
                status_tag = "LIVE" if status_text.lower() == "live" else "DIE"
                phone_val = locals().get("phone", "")
                token_val = locals().get("token", "")

                tree.insert("", "end", values=(
                    len(tree.get_children())+1, status_text, username, password, email, phone_val, cookie_str,
                    locals().get("two_fa_code", ""), token_val, "127.0.0.1", "NoProxy",
                    "LIVE" if status_tag=="LIVE" else "",
                    "DIE" if status_tag=="DIE" else ""
                ), tags=(status_tag,))
            except Exception as e:
                log(f"⚠️ Không thể thêm vào Treeview: {repr(e)}")

            # === LƯU THÔNG TIN ===
            try:
                file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Live.txt")

                info_map = {
                    "Username": username,
                    "Pass": password,
                    "Mail": email,
                    "Cookie": cookie_str if 'cookie_str' in locals() else '',
                    "2FA": two_fa_code if 'two_fa_code' in locals() else '',
                }

                # dùng trực tiếp save_format từ UI
                line = "|".join([info_map.get(field, "") for field in save_format])

                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")

                log(f"💾 Đã lưu thông tin vào '{file_path}'")
            except Exception as e:
                log(f"❌ Lỗi khi lưu file: {repr(e)}")

        # === BƯỚC 5: Follow ===
        if enable_follow.get():
            try:
                pause_event.wait()
                log("🚀 Bắt đầu follow các link...")
                time.sleep(3)

                follow_links = [
                    "https://www.instagram.com/shx_pe06/",
                    "https://www.instagram.com/wynnieinclouds/",
                    "https://www.instagram.com/ductoan1103/",
                    "https://www.instagram.com/nba/",
                    "https://www.instagram.com/datgia172/",
                    "https://www.instagram.com/cristiano/",
                    "https://www.instagram.com/leomessi/",
                    "https://www.instagram.com/hansara.official/",
                    "https://www.instagram.com/lilbieber/",
                    "https://www.instagram.com/ne9av/",
                    "https://www.instagram.com/joyce.pham1106/",
                    "https://www.instagram.com/khanhvyccf/",
                    "https://www.instagram.com/chaubui_/",
                    "https://www.instagram.com/ngockem_/",
                    "https://www.instagram.com/kyduyen1311/",
                    "https://www.instagram.com/baohannguyenxhelia/",
                    "https://www.instagram.com/linnhhh.m/",
                    "https://www.instagram.com/loungu/",
                    "https://www.instagram.com/_choiiii__/",
                    "https://www.instagram.com/kjmbae/"
                ]

                # Lấy số lượng follow từ ô nhập
                try:
                    num_follow = int(follow_count_entry.get())
                except:
                    num_follow = 5
                num_follow = min(num_follow, len(follow_links))  

                selected_links = random.sample(follow_links, num_follow)

                for link in selected_links:
                    try:
                        driver.get(link)
                        log(f"🌐 Đã mở link: {link}")
                        time.sleep(5)

                        follow_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Follow']"))
                        )
                        follow_button.click()
                        log(f"✅ Đã follow: {link}")
                        time.sleep(6)
                    except Exception as e:
                        log(f"❌ Không thể follow {link}: {repr(e)}")

            except Exception as e:
                log(f"❌ Lỗi trong quá trình follow: {repr(e)}")
                wait_all("Follow", thread_id)

        # === BƯỚC 6: Upload avatar ở giao diện mobile ===
        if enable_avatar.get():
            time.sleep(4)
            try:
                log("📱 Chuyển sang giao diện Mobile (iPhone 15 Pro Max)...")
                driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                    "mobile": True,
                    "width": 390,
                    "height": 844,
                    "deviceScaleFactor": 3
                })
                driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
                    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
                })
                driver.refresh()
                time.sleep(8)

                # Đóng popup Not Now nếu có
                driver.execute_script("""
                    let btn = [...document.querySelectorAll("span,button")]
                        .find(el => ["Not now", "Không phải bây giờ"].includes(el.innerText.trim()));
                    if (btn) btn.click();
                """)
                time.sleep(3)

                # Mở trang chỉnh sửa hồ sơ
                log("👤 Mở trang chỉnh sửa hồ sơ để upload avatar...")
                driver.get("https://www.instagram.com/accounts/edit/")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@accept='image/jpeg,image/png']"))
                )
                time.sleep(8)
                
                # Nhấn Prefer not to say
                driver.execute_script("""
                    const preferEl = document.evaluate(
                        "//div[span[normalize-space(text())='Prefer not to say']]",
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;
                    if (preferEl) {
                        preferEl.click();
                    } else {
                        console.warn("❌ Không tìm thấy phần tử 'Prefer not to say'");
                    }
                    """)
                time.sleep(3)
                # Chọn female
                driver.execute_script("""
                    const femaleOption = document.evaluate(
                        "//span[normalize-space(text())='Female']",
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;
                    if (femaleOption) {
                        femaleOption.click();
                    } else {
                        console.warn("❌ Không tìm thấy option 'Female'");
                    }
                    """)
                time.sleep(3)

                # Điền Bio (theo lựa chọn GUI) — chuẩn React (setNativeValue + input/change)
                bio_value = get_bio_text()
                driver.execute_script("""
                (function(val){
                    const el = document.querySelector("textarea[name='biography'], #pepBio, textarea[aria-label='Bio'], textarea[aria-label='Tiểu sử']");
                    if (!el) { console.warn("❌ Không tìm thấy ô Bio (#pepBio/biography)"); return; }
                    const proto  = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                    if (setter) setter.call(el, val); else el.value = val;  // fallback
                    el.dispatchEvent(new Event('input',  {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    el.blur();
                    console.log("✍️ Đã điền Bio:", val);
                })(arguments[0]);
                """, bio_value)
                log(f"✍️ Đã điền Bio: {bio_value}")
                time.sleep(1.5)

                # Nhấn Submit
                driver.execute_script("""
                (function(){
                    const xps = [
                    "//div[@role='button' and normalize-space(text())='Submit']",
                    "//button[normalize-space()='Submit']",
                    "//button[normalize-space()='Save']",
                    "//button[normalize-space()='Lưu']",
                    "//div[@role='button' and .//span[normalize-space(text())='Submit']]"
                    ];
                    for (const xp of xps) {
                    const el = document.evaluate(xp, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (el) { el.scrollIntoView({block:'center'}); el.click(); console.log("➡️ Đã click Submit/Save"); return; }
                    }
                    console.warn("❌ Không tìm thấy nút Submit/Save");
                })();
                """)
                time.sleep(2)

                # Lấy ảnh và upload
                if not ava_folder_path or not os.path.exists(ava_folder_path):
                    log("❌ Chưa chọn thư mục ảnh hoặc thư mục không tồn tại.")
                else:
                    image_files = [f for f in os.listdir(ava_folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                    if image_files:
                        selected_path = os.path.join(ava_folder_path, random.choice(image_files))
                        driver.find_element(By.XPATH, "//input[@accept='image/jpeg,image/png']").send_keys(selected_path)
                        log(f"✅ Đã upload avatar: {os.path.basename(selected_path)}")
                        time.sleep(3)
                        # Lưu avatar
                        WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
                        ).click()
                        log("💾 Đã lưu avatar")
                        time.sleep(10)

                        # Nếu có nút Post thì click
                        try:
                            post_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'_a9--') and text()='Post']"))
                            )
                            driver.execute_script("arguments[0].click();", post_btn)
                            log("✅ Đã click Post")
                            time.sleep(12)
                        except:
                            log("ℹ Không thấy nút Post, bỏ qua.")
                    else:
                        log("❌ Không có ảnh hợp lệ trong thư mục.")
            except Exception as e:
                log(f"❌ Lỗi Bước 6: {repr(e)}")

            # Quay lại giao diện Desktop
            log("🖥 Quay lại giao diện Desktop...")
            driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
            driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            })
            driver.refresh()
            time.sleep(5)

        # === BẬT CHẾ ĐỘ CHUYÊN NGHIỆP (Creator -> Personal blog) ===
        if enable_Chuyen_nghiep.get():
            try:
                pause_event.wait()
                log("💼 Đang bật chế độ chuyên nghiệp (Creator -> Personal blog)...")
                driver.get("https://www.instagram.com/accounts/convert_to_professional_account/")
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(4)

                # 1) Chọn Creator
                account_type = pro_type_var.get()
                if account_type == "Creator":
                    selector = "IGDSRadioButtonmedia_creator"
                else:
                    selector = "IGDSRadioButtonbusiness"
                try:
                    radio = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((By.ID, selector))
                    )
                    radio.click()
                    log(f"✅ Đã chọn {account_type}")
                    time.sleep(3)
                except Exception as e:
                    log(f"⚠️ Không tìm thấy nút chọn {account_type}: {repr(e)}")

                # 2) Nhấn Next qua 2 màn hình giới thiệu
                for i in range(2):
                    try:
                        next_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next' or normalize-space()='Tiếp']"))
                        )
                        next_btn.click()
                        log(f"➡️ Đã nhấn Next {i+1}")
                        time.sleep(1.5)
                    except Exception as e:
                        log(f"ℹ️ Không tìm thấy Next {i+1}: {repr(e)}")
                        break
                
                # 3) Tick Show category on profile
                driver.execute_script("""
                    document.querySelectorAll('input[type="checkbox"][aria-label="Show category on profile"]').forEach(el => { 
                        if (el.getAttribute("aria-checked") === "false") {
                            el.click();
                        }
                    });
                """)
                time.sleep(3)

                # 4) Tick Category theo lựa chọn GUI
                category = category_var.get()
                category_map = {
                    "Personal blog": "2700",
                    "Product/service": "2201",
                    "Art": "2903",
                    "Musician/band": "180164648685982",
                    "Shopping & retail": "200600219953504",
                    "Health/beauty": "2214",
                    "Grocery Store": "150108431712141"
                }
                cat_code = category_map.get(category)
                if cat_code:
                    js = f'document.querySelector(\'input[type="radio"][aria-label="{cat_code}"]\').click();'
                    driver.execute_script(js)
                    log(f"✅ Đã chọn Category: {category}")
                    time.sleep(3)
                else:
                    log(f"⚠️ Không tìm thấy mã category cho {category}")

                # 5) Nhấn Done 
                driver.execute_script("""
                    document.querySelectorAll('button[type="button"]').forEach(el => {
                        if (el.innerText.trim() === 'Done') el.click();
                    });
                """)
                time.sleep(3)
                # 6) Xác nhận popup Switch to Professional Account
                driver.execute_script("""
                    document.querySelectorAll('button').forEach(el => { 
                        if (el.innerText.trim() === 'Continue' || el.innerText.trim() === 'Tiếp tục') {
                            el.click();
                        }
                    });
                """)
                time.sleep(15)
                # 7) Nhấn Done để hoàn thành 
                driver.execute_script("document.querySelector('button._aswp._aswr._aswu._aswy._asw_._asx2').click()")
                time.sleep(5)
                
            except Exception as e:
                log(f"Lỗi khi bật chế độ chuyên nghiệp: {repr(e)}")

            # === KẾT THÚC PHIÊN ===
            try:
                time.sleep(2)
                release_position(driver)       # ✅ trả chỗ
                driver.quit()
                log("👋 Đã đóng trình duyệt (driver.quit()).")
            except Exception as e:
                log(f"⚠️ Lỗi khi quit driver: {repr(e)}")

# ================================================== DESKTOP =============================================================
def run(thread_id=None):
    while True:
        pause_event.wait() 
        log("🟢 Bắt đầu tạo tài khoản...")

        if dropmail_var.get():
            log("📨 Lấy email từ DropMail.me...")
            email, session_id = get_dropmail_email()
            if not email:
                log("⛔ Không thể lấy email DropMail — dừng tiến trình.")
                return
            log(f"✅ Email DropMail: {email}")

        elif tempmail_var.get():
            log("📨 Lấy email từ temp-mail.asia (API)...")
            headers = {"accept": "application/json"}
            resp = requests.get("https://free.priyo.email/api/random-email/7jkmE5NM2VS6GqJ9pzlI", headers=headers)

            if resp.status_code == 200:
                email = resp.json()["email"]
                log(f"✅ Email lấy được: {email}")
            else:
                log(f"❌ Lỗi HTTP {resp.status_code}")
                return

        else:
            log("⛔ Bạn chưa chọn dịch vụ mail tạm (DropMail hoặc Temp-Mail).")
            return

        def generate_vietnamese_name():
            ho_list = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ"]
            ten_dem_list = ["Văn", "Thị", "Hữu", "Gia", "Ngọc", "Đức", "Thanh", "Minh", "Quang", "Trọng"]
            ten_list = ["Anh", "Bình", "Châu", "Dũng", "Hà", "Hùng", "Lan", "Linh", "Nam", "Phúc", "Quỳnh", "Sơn", "Trang", "Tuấn", "Vy"]

            ho = random.choice(ho_list)
            ten_dem = random.choice(ten_dem_list)
            ten = random.choice(ten_list)
            return f"{ho} {ten_dem} {ten}"  # Trả về cả họ + tên đệm + tên

        full_name = generate_vietnamese_name()
        username_base = re.sub(r'[^a-z0-9]', '', unidecode(full_name.lower()))
        username = f"{username_base}{random.randint(100, 999)}"
        username = username
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        log(f"👤 Họ tên: {full_name}")
        log(f"🔤 Username: {username}")
        log(f"🔐 Mật khẩu: {password}")

        try:
            # === BƯỚC 1: Bật WARP và mở Instagram ===
            time.sleep(3)
            pause_event.wait()
            log("🌐 Mở Instagram...")

            proxy = proxy_entry.get().strip()

            if warp_enabled:
                log("🌐 Đang bật WARP → bỏ qua proxy.")
            else:
                if proxy:
                    log(f"🌐 WARP tắt → dùng proxy: {proxy}")
                    # options will be created below
                else:
                    log("🌐 WARP tắt nhưng không có proxy → dùng IP thật.")

            options = Options()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--start-maximized")

            # ✅ nếu có proxy thì thêm (giữ lại logic cũ)
            if proxy and not warp_enabled:
                options.add_argument(f"--proxy-server=http://{proxy}")

            # ✅ nếu có chrome_path thì dùng binary_location (giống V3-Mobile)
            if chrome_path:
                options.binary_location = chrome_path

            driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
            service = Service(driver_path)
            driver = se_webdriver.Chrome(service=service, options=options)
            all_drivers.append(driver)

            # 🕒 Sắp xếp Chrome giống V3-Mobile
            threading.Thread(target=arrange_after_open, args=(driver,), daemon=True).start()

            driver.get("https://www.instagram.com/accounts/emailsignup/")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            log(f"✅ [Luồng {thread_id}] Chrome đã mở xong và trang Instagram sẵn sàng.")
            time.sleep(3)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
            log(f"✅ [Luồng {thread_id}] Chrome đã mở xong và trang Instagram sẵn sàng.")
            # === ĐỒNG BỘ: chờ tất cả luồng sẵn sàng ===
            if sync_barrier is not None:
                try:
                    log(f"⏳ [Luồng {thread_id}] Đang chờ các luồng khác (timeout {barrier_timeout}s)...")
                    sync_barrier.wait(timeout=barrier_timeout)
                    log(f"🚀 [Luồng {thread_id}] Tất cả luồng đã sẵn sàng. Bắt đầu đồng loạt.")
                except threading.BrokenBarrierError:
                    log(f"⚠️ [Luồng {thread_id}] Barrier timeout/broken, tiếp tục.")
            else:
                log(f"⚠️ [Luồng {thread_id}] sync_barrier chưa được tạo — tiếp tục luôn.")

            time.sleep(2)
            type_text_slowly(
                driver.find_element(By.NAME, "emailOrPhone"),
                email,
                delay=get_delay("Mail_type", 0.18)
            )
            time.sleep(get_delay("Mail_sleep", 1))
            type_text_slowly(
                driver.find_element(By.NAME, "password"),
                password,
                delay=get_delay("Pass_type", 0.18)
            )
            time.sleep(get_delay("Pass_sleep", 3))
            type_text_slowly(
                driver.find_element(By.NAME, "fullName"),
                full_name,
                delay=get_delay("Họ Tên_type", 0.18)
            )
            time.sleep(get_delay("Họ Tên_sleep", 2))
            type_text_slowly(
                driver.find_element(By.NAME, "username"),
                username,
                delay=get_delay("Username_type", 0.18)
            )
            time.sleep(get_delay("Username_sleep", 3))
            time.sleep(2)
            driver.execute_script("""
                document.querySelectorAll('button[type="button"]').forEach(el => {
                    if (el.innerText.trim() === "Refresh suggestion") {
                        el.click();
                        console.log("✅ Đã click nút Refresh suggestion");
                    }
                });
            """)
            time.sleep(2)
            driver.execute_script("""
                document.querySelectorAll('button[type="button"]').forEach(el => {
                    if (el.innerText.trim() === "Refresh suggestion") {
                        el.click();
                        console.log("✅ Đã click nút Refresh suggestion");
                    }
                });
            """)
            time.sleep(2)
            try:
                new_username = driver.find_element(By.NAME, "username").get_attribute("value") or username
                if new_username != username:
                    log(f"🔁 Username sau refresh: {username}  ➜  {new_username}")
                    username = new_username  # cập nhật để bước check live & lưu file dùng tên mới nhất
                else:
                    log("ℹ️ Username không đổi sau 2 lần refresh.")
            except Exception as e:
                log(f"⚠️ Không đọc được username sau refresh: {e}")
            log("✅ Đã điền xong form đăng ký")

            wait_all("Điền form", thread_id)
            pause_event.wait()
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            log("➡️ Đã ấn Tiếp theo")
            time.sleep(get_delay("Next_sleep", 2))

            # === BƯỚC 2: Tắt WARP để chọn ngày sinh ===
            pause_event.wait()
            log("📅 Đang chờ phần chọn ngày sinh...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//select[@title='Month:']"))
            )
            time.sleep(3)
            year = str(random.randint(1999, 2003))
            month = str(random.randint(1, 12))
            day = str(random.randint(1, 28))

            def select_dropdown_value(driver, dropdown_xpath, value):
                dropdown = Select(driver.find_element(By.XPATH, dropdown_xpath))
                dropdown.select_by_value(value)
                time.sleep(2)

            select_dropdown_value(driver, "//select[@title='Month:']", month)
            select_dropdown_value(driver, "//select[@title='Day:']", str(day))
            select_dropdown_value(driver, "//select[@title='Year:']", year)

            log(f"📅 Đã chọn ngày: {day}, tháng: {month}, năm: {year}")

            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]") )
            )
            driver.execute_script("arguments[0].click();", next_btn)
            log("✅ Đã chọn ngày sinh và ấn Tiếp theo")
            wait_all("Chọn ngày sinh", thread_id)

            # === BƯỚC 3: Bật WARP để lấy mã xác minh email ===
            pause_event.wait()
            log("⏳ Đợi 10 giây để lấy mã xác minh từ email...")
            time.sleep(6)
            # --- Hàm đợi DropMail VỚI GIỚI HẠN ---
            def wait_for_dropmail_code(session_id, max_checks=5, interval=5, overall_timeout=300):
                url = "https://dropmail.me/api/graphql/my_token_123"
                query = """
                query($id: ID!) {
                session(id: $id) {
                    mails { fromAddr headerSubject text }
                }
                }"""
                start_time = time.time()
                checks = 0
                while (time.time() - start_time) < overall_timeout and checks < max_checks:
                    try:
                        resp = requests.post(url, json={"query": query, "variables": {"id": session_id}}, timeout=10)
                        data = resp.json()
                        mails = data["data"]["session"]["mails"]
                        if mails:
                            for mail in mails:
                                text = mail.get("text", "")
                                subject = mail.get("headerSubject", "")
                                match = re.search(r"\b\d{6}\b", text) or re.search(r"\b\d{6}\b", subject)
                                if match:
                                    code = match.group(0)
                                    log(f"📩 Nhận được mã DropMail: {code}")
                                    return code
                        checks += 1
                        log(f"⌛ Chưa có mail DropMail (lần {checks}/{max_checks}), chờ thêm...")
                    except Exception as e:
                        checks += 1
                        log(f"❌ Lỗi khi kiểm tra DropMail (lần {checks}/{max_checks}): {repr(e)}")
                    time.sleep(interval)
                log("⛔ Quá 5 lần kiểm tra DropMail mà chưa có mã — bỏ phiên.")
                return None


            # --- Hàm đợi TempMail VỚI GIỚI HẠN ---
            def wait_for_tempmail_code(email, max_checks=5, interval=5, overall_timeout=300):
                headers = {"accept": "application/json"}
                email_encoded = email.replace("@", "%40")
                mail_url = f"https://free.priyo.email/api/messages/{email_encoded}/7jkmE5NM2VS6GqJ9pzlI"
                start_time = time.time()
                checks = 0
                while (time.time() - start_time) < overall_timeout and checks < max_checks:
                    try:
                        resp = requests.get(mail_url, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            messages = resp.json()
                            if messages:
                                subject = messages[0].get("subject", "")
                                log(f"📬 Subject email: {subject}")
                                match = re.search(r"\b\d{6}\b", subject)
                                if match:
                                    code = match.group(0)
                                    log(f"🔢 Nhận được mã TempMail: {code}")
                                    return code
                        checks += 1
                        log(f"⌛ Chưa có mail TempMail (lần {checks}/{max_checks}), chờ thêm...")
                    except Exception as e:
                        checks += 1
                        log(f"❌ Lỗi khi kiểm tra TempMail (lần {checks}/{max_checks}): {repr(e)}")
                    time.sleep(interval)
                log("⛔ Quá 5 lần kiểm tra TempMail mà chưa có mã — bỏ phiên.")
                return None

            # --- Điền code mail ---
            try:
                if dropmail_var.get():
                    code = wait_for_dropmail_code(session_id, max_checks=5, interval=5, overall_timeout=300)
                elif tempmail_var.get():
                    code = wait_for_tempmail_code(email, max_checks=5, interval=5, overall_timeout=300)
                else:
                    code = None

                if not code:
                    log("⛔ Không lấy được mã xác minh sau 5 lần kiểm tra. Đóng phiên hiện tại và tạo phiên mới.")
                    try:
                        warp_off()
                    except:
                        pass
                    try:
                        release_position(driver)   # ✅ trả chỗ
                        driver.quit()
                    except:
                        pass
                    # (khuyên dùng continue để không nhân thêm thread)
                    log("🔁 Restart phiên trong cùng luồng.")
                    continue

                # Nếu có code -> nhập và tiếp tục như cũ
                code_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Confirmation Code']"))
                )
                type_text_slowly(code_input, code, delay=0.3)
                log(f"✅ Đã nhập mã xác minh: {code}")
                if warp_enabled:
                    warp_change_ip()
                time.sleep(8)
                # Nhấn nút Next nhiều lần nếu còn
                # Ấn nút Next từng luồng cách nhau 10 giây nếu chạy nhiều luồng
                if sync_barrier is not None and sync_barrier.parties > 1:
                    global next_press_lock
                    try:
                        next_press_lock
                    except NameError:
                        next_press_lock = threading.Lock()
                    for i in range(5):
                        with next_press_lock:
                            try:
                                next_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and normalize-space(text())='Next']"))
                                )
                                driver.execute_script("arguments[0].click();", next_btn)
                                time.sleep(5)
                                log(f"🔁 Ấn nút Next lần {i+1}")
                                time.sleep(2)
                            except:
                                log("✅ Không còn nút Next, tiếp tục quy trình.")
                                break
                        # Chờ 10 giây giữa các luồng
                        time.sleep(10)
                else:
                    for i in range(5):
                        try:
                            next_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and normalize-space(text())='Next']"))
                            )
                            driver.execute_script("arguments[0].click();", next_btn)
                            time.sleep(5)
                            log(f"🔁 Ấn nút Next lần {i+1}")
                            time.sleep(2)
                        except:
                            log("✅ Không còn nút Next, tiếp tục quy trình.")
                            break

                time.sleep(20)
                wait_all("Xác minh email", thread_id)

            except Exception as e:
                log(f"❌ Lỗi khi nhập mã xác minh: {repr(e)}")

            # === CHECK LIVE/DIE ===
            try:
                global live_count, die_count
                profile_url = f"https://www.instagram.com/{username}/"
                log("🌐 Đang kiểm tra trạng thái Live/Die...")
                driver.get(profile_url)
                time.sleep(6)  # có thể thay bằng WebDriverWait nếu muốn

                current_url = driver.current_url
                page_source = driver.page_source

                # Mặc định
                status_text = "Unknown"

                # Phân loại trạng thái
                if "/accounts/login/" in current_url or "Sorry, this page isn't available" in page_source:
                    status_text = "Die"
                elif "checkpoint" in current_url.lower() or "Confirm you're human" in page_source:
                    status_text = "Checkpoint"
                elif (f"@{username}" in page_source) or (f"instagram.com/{username}" in current_url):
                    status_text = "Live"
                else:
                    status_text = "Die"

                # Cập nhật biến đếm + log
                if status_text == "Live":
                    live_count += 1
                    live_var.set(str(live_count))
                    update_rate()
                    log("✅ Tài khoản Live")
                else:
                    die_count += 1
                    die_var.set(str(die_count))
                    update_rate()
                    log(f"❌ {status_text} — tính là Die")

                # === Lấy Cookie ===
                try:
                    cookies = driver.get_cookies()
                    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies]) if cookies else ""
                    log("🍪 Cookie hiện tại:")
                    log(cookie_str if cookie_str else "(empty)")
                    time.sleep(3)
                except Exception as e:
                    cookie_str = ""
                    log(f"❌ Lỗi khi lấy cookie: {repr(e)}")

                # Nếu KHÔNG phải Live thì insert ngay bây giờ
                if status_text.lower() in ("die", "checkpoint", "unknown"):
                    # nếu có app (Tk root) thì:
                    try:
                        app.after(0, lambda: insert_to_tree(status_text, username, password, email, cookie_str, two_fa_code=""))
                    except:
                        insert_to_tree(status_text, username, password, email, cookie_str, two_fa_code="")

                    # Lưu file (optional) – có fallback cho save_format
                    try:
                        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Die.txt")
                        info_map = {"Username": username, "Pass": password, "Mail": email, "Cookie": cookie_str, "2FA": ""}
                        fields = save_format if ('save_format' in globals() and isinstance(save_format, (list,tuple)) and save_format) \
                                else ["Username","Pass","Mail","Cookie","2FA"]
                        line = "|".join([info_map.get(field, "") for field in fields])
                        with open(file_path, "a", encoding="utf-8") as f:
                            f.write(line + "\n")
                        log(f"💾 (Die early) Đã lưu thông tin vào '{file_path}'")
                    except Exception as e:
                        log(f"❌ (Die early) Lỗi khi lưu file: {repr(e)}")

                    # Quyết định restart
                    try:
                        warp_off()
                        time.sleep(2)
                        release_position(driver)
                        driver.quit()
                        driver = None
                    except:
                        pass
                    log("🔁 Khởi chạy lại phiên...")
                    continue
                else:
                    log("➡️ LIVE: Tiếp tục BƯỚC TIẾP THEO (Follow/…)")

            except Exception as e:
                log(f"⚠️ Lỗi khi check live/die: {repr(e)}")
        except Exception as e:
            log(f"❌ Lỗi trình duyệt: {repr(e)}")
            try:
                release_position(driver)   # ✅ trả chỗ
                driver.quit()
            except:
                pass
            log("🔄 Đang chạy lại từ đầu sau lỗi trình duyệt...")
            # Khuyên: gọi continue thay vì run(thread_id) (tránh nhân thread)
            continue
        # === BƯỚC 7: Xử lý bật 2FA ===
        if twofa_var.get():
            try:
                pause_event.wait()
                log("🔐 Bắt đầu bật xác thực hai yếu tố (2FA)...")
                time.sleep(6)

                # Truy cập trang bật 2FA
                driver.get("https://accountscenter.instagram.com/password_and_security/two_factor/?theme=dark")
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(5)

                # Chọn tài khoản Instagram
                try:
                    account_btn = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((
                            By.XPATH, "//div[@role='button' and descendant::div[contains(text(),'Instagram')]]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", account_btn)
                    time.sleep(1)
                    account_btn.click()
                    log("✅ Đã chọn tài khoản Instagram")
                    time.sleep(3)
                except Exception as e:
                    log(f"⚠️ Không chọn được tài khoản: {repr(e)}")
                    return

                # Nhấn nút "Continue"
                try:
                    continue_btn = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "//div[@role='button' and descendant::span[normalize-space(text())='Continue']]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
                    time.sleep(3)
                    driver.execute_script("arguments[0].click();", continue_btn)
                    log("✅ Đã click nút Continue")
                    time.sleep(3)
                except Exception as e:
                    log(f"❌ Không thể click nút Continue: {repr(e)}")
                    return

                # Lấy mã 2FA secret
                try:
                    span_xpath = "//div[contains(@class,'x16grhtn')]//span"
                    span_elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, span_xpath))
                    )
                    two_fa_code = span_elem.text.strip().replace(" ", "")
                    log(f"🔐 Mã 2FA secret: {two_fa_code}")
                except Exception as e:
                    log(f"❌ Không lấy được mã 2FA secret: {repr(e)}")
                    return
                time.sleep(3)
                # Nhấn nút Next để chuyển tới nhập mã OTP
                try:
                    next_btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH, "//div[@role='button' and descendant::span[normalize-space(text())='Next']]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_btn)
                    log("✅ Đã nhấn nút Next để nhập mã OTP")
                    time.sleep(3)
                except Exception as e:
                    log(f"❌ Không nhấn được nút Next sau mã secret: {repr(e)}")
                    return

                # Sinh mã OTP từ mã secret bằng pyotp
                otp_code = None
                try:
                    totp = pyotp.TOTP(two_fa_code)
                    otp_code = totp.now()
                    log(f"🔢 Mã OTP tạo từ pyotp: {otp_code}")
                except Exception as e:
                    log(f"❌ Lỗi khi tạo OTP từ pyotp: {repr(e)}")
                    return
                time.sleep(3)
                # Nhập mã OTP vào ô nhập
                if otp_code:
                    try:
                        otp_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @maxlength='6']"))
                        )
                        otp_input.clear()
                        otp_input.send_keys(otp_code)
                        log("✅ Đã nhập mã OTP.")
                        time.sleep(2)
                    except Exception as e:
                        log(f"❌ Lỗi khi nhập OTP: {repr(e)}")
                    # Nhấn nút Next cuối cùng để hoàn tất bật 2FA
                    try:
                        driver.execute_script("""
                            [...document.querySelectorAll("div[role='button']")].forEach(el => {
                                if (el.innerText.trim() === 'Next') el.click();
                            });
                        """)
                        log("✅ Đã nhấn nút Next để hoàn tất bật 2FA")
                        time.sleep(6)
                        wait_all("Bật 2FA", thread_id)
                    except Exception as e:
                        log(f"❌ Lỗi khi nhấn nút Next hoàn tất 2FA: {repr(e)}")
                        return
                    driver.execute_script("""
                    const btn = [...document.querySelectorAll("button, div[role=button]")]
                        .find(el => el.textContent.trim() === "Done");

                    if (btn) {
                        btn.click();
                        return true;
                    } else {
                        return false;
                    }
                    """)
            except Exception as e:
                log(f"❌ Lỗi toàn bộ bước bật 2FA: {repr(e)}")
            time.sleep(3)

            # === Insert vào Treeview ===
            try:
                status_tag = "LIVE" if status_text.lower() == "live" else "DIE"
                phone_val = locals().get("phone", "")
                token_val = locals().get("token", "")

                tree.insert("", "end", values=(
                    len(tree.get_children())+1, status_text, username, password, email, phone_val, cookie_str,
                    locals().get("two_fa_code", ""), token_val, "127.0.0.1", "NoProxy",
                    "LIVE" if status_tag=="LIVE" else "",
                    "DIE" if status_tag=="DIE" else ""
                ), tags=(status_tag,))
            except Exception as e:
                log(f"⚠️ Không thể thêm vào Treeview: {repr(e)}")

            # === LƯU THÔNG TIN ===
            try:
                file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Live.txt")

                info_map = {
                    "Username": username,
                    "Pass": password,
                    "Mail": email,
                    "Cookie": cookie_str if 'cookie_str' in locals() else '',
                    "2FA": two_fa_code if 'two_fa_code' in locals() else '',
                }

                # dùng trực tiếp save_format từ UI
                line = "|".join([info_map.get(field, "") for field in save_format])

                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")

                log(f"💾 Đã lưu thông tin vào '{file_path}'")
            except Exception as e:
                log(f"❌ Lỗi khi lưu file: {repr(e)}")

        # === BƯỚC 5: Follow ===
        if follow_var.get():
            try:
                pause_event.wait()
                log("🚀 Bắt đầu follow các link...")
                time.sleep(3)

                follow_links = [
                    "https://www.instagram.com/shx_pe06/",
                    "https://www.instagram.com/wynnieinclouds/",
                    "https://www.instagram.com/ductoan1103/",
                    "https://www.instagram.com/nba/",
                    "https://www.instagram.com/datgia172/",
                    "https://www.instagram.com/cristiano/",
                    "https://www.instagram.com/leomessi/",
                    "https://www.instagram.com/hansara.official/",
                    "https://www.instagram.com/lilbieber/",
                    "https://www.instagram.com/ne9av/",
                    "https://www.instagram.com/joyce.pham1106/",
                    "https://www.instagram.com/khanhvyccf/",
                    "https://www.instagram.com/chaubui_/",
                    "https://www.instagram.com/ngockem_/",
                    "https://www.instagram.com/kyduyen1311/",
                    "https://www.instagram.com/baohannguyenxhelia/",
                    "https://www.instagram.com/linnhhh.m/",
                    "https://www.instagram.com/loungu/",
                    "https://www.instagram.com/_choiiii__/",
                    "https://www.instagram.com/kjmbae/"
                ]

                # Lấy số lượng follow từ ô nhập
                try:
                    num_follow = int(follow_count_entry.get())
                except:
                    num_follow = 5
                num_follow = min(num_follow, len(follow_links))  

                selected_links = random.sample(follow_links, num_follow)

                for link in selected_links:
                    try:
                        driver.get(link)
                        log(f"🌐 Đã mở link: {link}")
                        time.sleep(5)

                        follow_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Follow']"))
                        )
                        follow_button.click()
                        log(f"✅ Đã follow: {link}")
                        time.sleep(6)
                    except Exception as e:
                        log(f"❌ Không thể follow {link}: {repr(e)}")

            except Exception as e:
                log(f"❌ Lỗi trong quá trình follow: {repr(e)}")
                wait_all("Follow", thread_id)
        else:
            log("⏭ Bỏ qua bước Follow")

        # === BƯỚC 6: Upload avatar ở giao diện mobile ===
        if bioava_var.get():
            if warp_enabled:
                warp_off()
                time.sleep(4)
        try:
            log("📱 Chuyển sang giao diện Mobile (iPhone 15 Pro Max)...")
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "mobile": True,
                "width": 390,
                "height": 844,
                "deviceScaleFactor": 3
            })
            driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
            })
            driver.refresh()
            time.sleep(5)

            # Đóng popup Not Now nếu có
            driver.execute_script("""
                let btn = [...document.querySelectorAll("span,button")]
                    .find(el => ["Not now", "Không phải bây giờ"].includes(el.innerText.trim()));
                if (btn) btn.click();
            """)
            time.sleep(3)

            # Mở trang chỉnh sửa hồ sơ
            log("👤 Mở trang chỉnh sửa hồ sơ để upload avatar...")
            driver.get("https://www.instagram.com/accounts/edit/")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@accept='image/jpeg,image/png']"))
            )
            time.sleep(8)
            
            # Nhấn Prefer not to say
            driver.execute_script("""
                const preferEl = document.evaluate(
                    "//div[span[normalize-space(text())='Prefer not to say']]",
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;
                if (preferEl) {
                    preferEl.click();
                } else {
                    console.warn("❌ Không tìm thấy phần tử 'Prefer not to say'");
                }
                """)
            time.sleep(3)
            # Chọn female
            driver.execute_script("""
                const femaleOption = document.evaluate(
                    "//span[normalize-space(text())='Female']",
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;
                if (femaleOption) {
                    femaleOption.click();
                } else {
                    console.warn("❌ Không tìm thấy option 'Female'");
                }
                """)
            time.sleep(3)

            # Điền Bio (theo lựa chọn GUI) — chuẩn React (setNativeValue + input/change)
            bio_value = get_bio_text()
            driver.execute_script("""
            (function(val){
                const el = document.querySelector("textarea[name='biography'], #pepBio, textarea[aria-label='Bio'], textarea[aria-label='Tiểu sử']");
                if (!el) { console.warn("❌ Không tìm thấy ô Bio (#pepBio/biography)"); return; }
                const proto  = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                if (setter) setter.call(el, val); else el.value = val;  // fallback
                el.dispatchEvent(new Event('input',  {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
                el.blur();
                console.log("✍️ Đã điền Bio:", val);
            })(arguments[0]);
            """, bio_value)
            log(f"✍️ Đã điền Bio: {bio_value}")
            time.sleep(1.5)

            # Nhấn Submit
            driver.execute_script("""
            (function(){
                const xps = [
                "//div[@role='button' and normalize-space(text())='Submit']",
                "//button[normalize-space()='Submit']",
                "//button[normalize-space()='Save']",
                "//button[normalize-space()='Lưu']",
                "//div[@role='button' and .//span[normalize-space(text())='Submit']]"
                ];
                for (const xp of xps) {
                const el = document.evaluate(xp, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (el) { el.scrollIntoView({block:'center'}); el.click(); console.log("➡️ Đã click Submit/Save"); return; }
                }
                console.warn("❌ Không tìm thấy nút Submit/Save");
            })();
            """)
            time.sleep(2)

            # Lấy ảnh và upload
            if not ava_folder_path or not os.path.exists(ava_folder_path):
                log("❌ Chưa chọn thư mục ảnh hoặc thư mục không tồn tại.")
            else:
                image_files = [f for f in os.listdir(ava_folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                if image_files:
                    selected_path = os.path.join(ava_folder_path, random.choice(image_files))
                    driver.find_element(By.XPATH, "//input[@accept='image/jpeg,image/png']").send_keys(selected_path)
                    log(f"✅ Đã upload avatar: {os.path.basename(selected_path)}")
                    time.sleep(3)
                    # Lưu avatar
                    WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
                    ).click()
                    log("💾 Đã lưu avatar")
                    time.sleep(10)

                    # Nếu có nút Post thì click
                    try:
                        post_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'_a9--') and text()='Post']"))
                        )
                        driver.execute_script("arguments[0].click();", post_btn)
                        log("✅ Đã click Post")
                        time.sleep(12)
                    except:
                        log("ℹ Không thấy nút Post, bỏ qua.")
                else:
                    log("❌ Không có ảnh hợp lệ trong thư mục.")
        except Exception as e:
            log(f"❌ Lỗi Bước 6: {repr(e)}")

        # Quay lại giao diện Desktop
        log("🖥 Quay lại giao diện Desktop...")
        driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })
        driver.refresh()
        time.sleep(5)

        # === BẬT CHẾ ĐỘ CHUYÊN NGHIỆP (Creator -> Personal blog) ===
        if pro_mode_var.get():
            try:
                pause_event.wait()
                log("💼 Đang bật chế độ chuyên nghiệp (Creator -> Personal blog)...")
                driver.get("https://www.instagram.com/accounts/convert_to_professional_account/")
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(4)

                # 1) Chọn Creator
                account_type = pro_type_var.get()
                if account_type == "Creator":
                    selector = "IGDSRadioButtonmedia_creator"
                else:
                    selector = "IGDSRadioButtonbusiness"
                try:
                    radio = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((By.ID, selector))
                    )
                    radio.click()
                    log(f"✅ Đã chọn {account_type}")
                    time.sleep(3)
                except Exception as e:
                    log(f"⚠️ Không tìm thấy nút chọn {account_type}: {repr(e)}")

                # 2) Nhấn Next qua 2 màn hình giới thiệu
                for i in range(2):
                    try:
                        next_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next' or normalize-space()='Tiếp']"))
                        )
                        next_btn.click()
                        log(f"➡️ Đã nhấn Next {i+1}")
                        time.sleep(1.5)
                    except Exception as e:
                        log(f"ℹ️ Không tìm thấy Next {i+1}: {repr(e)}")
                        break
                
                # 3) Tick Show category on profile
                driver.execute_script("""
                    document.querySelectorAll('input[type="checkbox"][aria-label="Show category on profile"]').forEach(el => { 
                        if (el.getAttribute("aria-checked") === "false") {
                            el.click();
                        }
                    });
                """)
                time.sleep(3)

                # 4) Tick Category theo lựa chọn GUI
                category = category_var.get()
                category_map = {
                    "Personal blog": "2700",
                    "Product/service": "2201",
                    "Art": "2903",
                    "Musician/band": "180164648685982",
                    "Shopping & retail": "200600219953504",
                    "Health/beauty": "2214",
                    "Grocery Store": "150108431712141"
                }
                cat_code = category_map.get(category)
                if cat_code:
                    js = f'document.querySelector(\'input[type="radio"][aria-label="{cat_code}"]\').click();'
                    driver.execute_script(js)
                    log(f"✅ Đã chọn Category: {category}")
                    time.sleep(3)
                else:
                    log(f"⚠️ Không tìm thấy mã category cho {category}")

                # 5) Nhấn Done 
                driver.execute_script("""
                    document.querySelectorAll('button[type="button"]').forEach(el => {
                        if (el.innerText.trim() === 'Done') el.click();
                    });
                """)
                time.sleep(3)
                # 6) Xác nhận popup Switch to Professional Account
                driver.execute_script("""
                    document.querySelectorAll('button').forEach(el => { 
                        if (el.innerText.trim() === 'Continue' || el.innerText.trim() === 'Tiếp tục') {
                            el.click();
                        }
                    });
                """)
                time.sleep(15)
                # 7) Nhấn Done để hoàn thành 
                driver.execute_script("document.querySelector('button._aswp._aswr._aswu._aswy._asw_._asx2').click()")
                time.sleep(5)
                
            except Exception as e:
                log(f"Lỗi khi bật chế độ chuyên nghiệp: {repr(e)}")

            # === KẾT THÚC PHIÊN ===
            try:
                if warp_enabled:
                    warp_off()
                    time.sleep(2)
                release_position(driver)       # ✅ trả chỗ
                driver.quit()
                log("👋 Đã đóng trình duyệt (driver.quit()).")
            except Exception as e:
                log(f"⚠️ Lỗi khi quit driver: {repr(e)}")

# === Giao diện TKinter có nền ===
def open_file_da_reg():
    file_path = "Live.txt"
    if os.path.exists(file_path):
        try:
            os.startfile(file_path)  # Mở bằng chương trình mặc định trên Windows
        except Exception as e:
            log(f"❌ Không mở được file: {repr(e)}")
    else:
        log("⚠️ File 'Live.txt' chưa tồn tại.")

def close_tool():
    try:
        subprocess.run("taskkill /F /IM chrome.exe", shell=True)
        log("🛑 Đã đóng toàn bộ Chrome.")
        all_drivers.clear()
        log("✅ Tool đã dừng tiến trình.")
    except Exception as e:
        log(f"❌ Lỗi khi đóng tool: {repr(e)}")

def show_intro(app, main_func):
    intro = tk.Toplevel(app)
    intro.overrideredirect(True)
    intro.attributes("-topmost", True)

    from PIL import Image, ImageTk
    img = Image.open("Autointro.png").convert("RGBA")
    new_w, new_h = 900, 440
    img = img.resize((new_w, new_h), Image.LANCZOS)
    logo = ImageTk.PhotoImage(img)

    sw = intro.winfo_screenwidth()
    sh = intro.winfo_screenheight()
    x = (sw - new_w) // 2
    y = (sh - new_h) // 2
    intro.geometry(f"{new_w}x{new_h}+{x}+{y}")

    trans_color = "magenta"
    intro.config(bg=trans_color)
    lbl = tk.Label(intro, image=logo, bg=trans_color, border=0)
    lbl.image = logo
    lbl.pack(fill="both", expand=True)

    try:
        intro.wm_attributes("-transparentcolor", trans_color)
    except Exception:
        pass

    def fade_in(alpha=0):
        if alpha <= 100:
            intro.attributes("-alpha", alpha / 100)
            intro.after(25, fade_in, alpha + 8)
        else:
            intro.after(1500, fade_out, 100)

    def fade_out(alpha=100):
        if alpha >= 0:
            intro.attributes("-alpha", alpha / 100)
            intro.after(25, fade_out, alpha - 8)
        else:
            try:
                intro.destroy()
            except:
                pass
            main_func()

    intro.attributes("-alpha", 0.0)
    fade_in()

app = tk.Tk()
app.withdraw() 
app.title("Instagram Auto Creator")
app.geometry("1600x900")
app.resizable(True, True)

# --- Biến đếm Live/Die/Rate ---
live_var = tk.StringVar(value="0")
die_var  = tk.StringVar(value="0")
rate_var = tk.StringVar(value="0%")

# tạo StringVar sau khi app đã tồn tại
scrcpy_path_var = tk.StringVar(value="(chưa chọn scrcpy.exe)")
# biến toàn cục cho tuỳ chọn kết nối
phone_net_mode = tk.StringVar(value="wifi")

# đọc config để lấy path đã lưu (chỉ gán vào biến thuần scrcpy_path)
load_scrcpy_config()

# nếu có path thì đưa lên UI
if scrcpy_path:
    scrcpy_path_var.set(scrcpy_path)

# Background (optional)
try:
    bg_image = Image.open("Auto.png").resize((1920, 1080))
    bg_photo = ImageTk.PhotoImage(bg_image)
except Exception:
    bg_photo = None

canvas = tk.Canvas(app, width=1050, height=550)
canvas.pack(fill="both", expand=True)
if bg_photo:
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# ========================= KHỐI TRÁI =========================
left_frame = tk.Frame(app, bg="white")
left_frame.place(x=20, y=20)

btn_container = tk.Frame(left_frame, bg="white")
btn_container.pack(pady=5, fill="x")

# Cột 1: Nút điều khiển
col1 = tk.Frame(btn_container, bg="white")
col1.grid(row=0, column=0, padx=8, sticky="n")

for text, color, cmd in [
    ("START", "green",        start_process),
    ("PAUSE", "red",          pause),
    ("NEXT", "orange",        resume),
    ("FILE REG", "yellow",    open_file_da_reg),
    ("CLOSE", "deepskyblue",  lambda: threading.Thread(target=restart_tool).start()),
    ("RESTART", "purple",     restart_tool),
]:
    tk.Button(col1, text=text, width=15, bg=color, fg="white", command=cmd).pack(pady=3)

warp_toggle_btn = tk.Button(col1, text="WARP ON", width=15, bg="green", fg="white", command=toggle_warp)
warp_toggle_btn.pack(pady=3)

threads_frame = tk.Frame(col1, bg="white"); threads_frame.pack(pady=5)
tk.Label(threads_frame, text="SỐ LUỒNG", bg="white", font=("Arial", 10, "bold")).pack()
threads_entry = tk.Entry(threads_frame, width=10, justify="center"); threads_entry.insert(0, "1"); threads_entry.pack(pady=2)
tk.Label(threads_frame, text="SỐ FOLLOW", bg="white", font=("Arial", 10, "bold")).pack()
follow_count_entry = tk.Entry(threads_frame, width=10, justify="center"); follow_count_entry.insert(0, "5"); follow_count_entry.pack(pady=2)

# Cột 2: Giao diện + Chrome/Ảnh/Proxy + email
col2 = tk.Frame(btn_container, bg="white")
col2.grid(row=0, column=1, padx=8, sticky="n")

ui_mode_var = tk.StringVar(value="desktop")
ui_frame = tk.LabelFrame(col2, text="GIAO DIỆN", bg="white", font=("Arial", 10, "bold"))
ui_frame.pack(pady=6, fill="x")
tk.Radiobutton(ui_frame, text="Desktop",
               variable=ui_mode_var, value="desktop",
               bg="white", command=_sync_mode_ui).pack(anchor="w", padx=6, pady=2)

tk.Radiobutton(ui_frame, text="Mobile iPhone 15",
               variable=ui_mode_var, value="mobile",
               bg="white", command=_sync_mode_ui).pack(anchor="w", padx=6, pady=2)

tk.Radiobutton(
    ui_frame, text="Phone (Android)",
    variable=ui_mode_var, value="phone",
    bg="white", command=_sync_mode_ui
).pack(anchor="w", padx=6, pady=2)

tk.Button(col2, text="Chọn thư mục Chrome", width=17, bg="lightgreen", command=select_chrome).pack(pady=3)
tk.Button(col2, text="Chọn thư mục ảnh",    width=17, bg="lightblue",  command=select_ava_folder).pack(pady=3)

tk.Label(col2, text="Proxy (IP:PORT)", bg="white", font=("Arial", 9, "bold")).pack(pady=(5,2))
proxy_entry = tk.Entry(col2, width=20, bg="lightgray", justify="center")
proxy_entry.pack(pady=2); proxy_entry.insert(0, "")

tempmail_var = tk.BooleanVar(value=True)
tk.Checkbutton(col2, text="Dùng temp-mail.asia", variable=tempmail_var, bg="white").pack(anchor="w", pady=(2,6))
dropmail_var = tk.BooleanVar(value=False)
tk.Checkbutton(col2, text="Dùng DropMail.me",    variable=dropmail_var,  bg="white").pack(anchor="w", pady=(2,6))

# Cột 3: Định dạng lưu
col3 = tk.Frame(btn_container, bg="white")
col3.grid(row=0, column=2, padx=8, sticky="n")

tk.Label(col3, text="Định dạng lưu:", bg="white", font=("Arial", 10, "bold")).pack(pady=(0,4))

format_boxes = []
def update_save_format():
    global save_format
    save_format = [cb.get() for cb in format_boxes if cb.get()]
    save_config()
    log(f"💾 Định dạng lưu: {'|'.join(save_format)}")

wanted = ["Username", "Pass", "Mail", "Cookie", "2FA"]
for i in range(5):
    cb = ttk.Combobox(col3, values=format_fields, state="readonly", width=15)
    cb.set(save_format[i] if i < len(save_format) else wanted[i])
    cb.pack(pady=2)
    cb.bind("<<ComboboxSelected>>", lambda e: update_save_format())
    format_boxes.append(cb)

# ========================= KHỐI GIỮA: Desktop Settings =========================
desktop_settings = tk.LabelFrame(app, text="Desktop Settings", bg="white", font=("Arial", 11, "bold"))
hidden_chrome_var = tk.BooleanVar(value=False)

def _position_desktop_settings():
    """Đặt Desktop Settings sát cạnh 'Định dạng lưu' (khối trái)."""
    app.update_idletasks()
    x = left_frame.winfo_x() + left_frame.winfo_width() + 12  # khoảng cách 12px
    y = 20
    desktop_settings.place(x=x, y=y)

# gọi sau khi khối trái render xong
app.after(60, _position_desktop_settings)

# --- Cột trái trong Desktop Settings: 4 checkbox + B1 + B2 + B3 (xếp dọc) ---
col_left = tk.Frame(desktop_settings, bg="white")
col_left.grid(row=0, column=0, padx=6, sticky="n")  # padding nhỏ để sát như hình
# Ô tích Ẩn Chrome (headless)
tk.Checkbutton(col_left, text="Ẩn Chrome (Headless)", variable=hidden_chrome_var, bg="white").pack(anchor="w", pady=2)

follow_var   = tk.BooleanVar(value=True)
bioava_var   = tk.BooleanVar(value=True)
pro_mode_var = tk.BooleanVar(value=True)
twofa_var    = tk.BooleanVar(value=True)
gender_var   = tk.StringVar(value="Prefer not to say")

tk.Checkbutton(col_left, text="Follow",                       variable=follow_var,   bg="white").pack(anchor="w", pady=2)
tk.Checkbutton(col_left, text="Giới tính + Bio + Ava + Post", variable=bioava_var,   bg="white").pack(anchor="w", pady=2)
tk.Checkbutton(col_left, text="Bật Chuyên nghiệp",            variable=pro_mode_var, bg="white").pack(anchor="w", pady=2)
tk.Checkbutton(col_left, text="Bật 2FA",                      variable=twofa_var,    bg="white").pack(anchor="w", pady=2)

# Nhỏ gọn hàm tạo dòng delay
delay_entries = {}
def _row_delay(parent, label, type_default, sleep_default):
    fr = tk.Frame(parent, bg="white"); fr.pack(pady=1, fill="x")
    tk.Label(fr, text=f"{label}:", bg="white", width=10, anchor="w").pack(side="left")
    if type_default is not None:
        e1 = tk.Entry(fr, width=5, justify="center"); e1.insert(0, str(type_default))
        e1.pack(side="left", padx=2); delay_entries[f"{label}_type"] = e1
    e2 = tk.Entry(fr, width=5, justify="center"); e2.insert(0, str(sleep_default))
    e2.pack(side="left", padx=4); delay_entries[f"{label}_sleep"] = e2

# BƯỚC 1
box_b1 = tk.LabelFrame(col_left, text="BƯỚC 1", bg="white", font=("Arial", 10, "bold"))
box_b1.pack(pady=4, fill="x")
hdr1 = tk.Frame(box_b1, bg="white"); hdr1.pack(pady=1, fill="x")
tk.Label(hdr1, text="", bg="white", width=10).pack(side="left")
tk.Label(hdr1, text="Điền", bg="white", width=6).pack(side="left")
tk.Label(hdr1, text="Nghỉ", bg="white", width=6).pack(side="left")
for lb,(tp,sl) in {"Mail":(0.18,1),"Pass":(0.18,3),"Họ Tên":(0.18,2),"Username":(0.18,3),"Next":(None,2)}.items():
    _row_delay(box_b1, lb, tp, sl)

# BƯỚC 2
box_b2 = tk.LabelFrame(col_left, text="BƯỚC 2", bg="white", font=("Arial", 10, "bold"))
box_b2.pack(pady=4, fill="x")
hdr2 = tk.Frame(box_b2, bg="white"); hdr2.pack(pady=1, fill="x")
tk.Label(hdr2, text="", bg="white", width=10).pack(side="left")
tk.Label(hdr2, text="Điền", bg="white", width=6).pack(side="left")
tk.Label(hdr2, text="Nghỉ", bg="white", width=6).pack(side="left")
for lb,(tp,sl) in {"Tháng":(0.18,2),"Ngày":(0.18,2),"Năm":(0.18,2),"Next":(None,2)}.items():
    _row_delay(box_b2, lb, tp, sl)

# BƯỚC 3
box_b3 = tk.LabelFrame(col_left, text="BƯỚC 3", bg="white", font=("Arial", 10, "bold"))
box_b3.pack(pady=4, fill="x")
hdr3 = tk.Frame(box_b3, bg="white"); hdr3.pack(pady=1, fill="x")
tk.Label(hdr3, text="", bg="white", width=10).pack(side="left")
tk.Label(hdr3, text="Điền", bg="white", width=6).pack(side="left")
tk.Label(hdr3, text="Nghỉ", bg="white", width=6).pack(side="left")
_row_delay(box_b3, "Điền code", 0.3, 2)

# --- Cột phải trong Desktop Settings: Loại TK + Category + Bio ---
col_right = tk.Frame(desktop_settings, bg="white")
col_right.grid(row=0, column=1, padx=10, sticky="n")  # khoảng trống hợp lý giữa hai cột

# Loại tài khoản
pro_type_var = tk.StringVar(value="Creator")
tk.Label(col_right, text="Loại tài khoản:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
tk.Radiobutton(col_right, text="Creator",  variable=pro_type_var, value="Creator",  bg="white").pack(anchor="w")
tk.Radiobutton(col_right, text="Business", variable=pro_type_var, value="Business", bg="white").pack(anchor="w")

# Category
tk.Label(col_right, text="Category:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,2))
categories = ["Personal blog","Product/service","Art","Musician/band","Shopping & retail","Health/beauty","Grocery Store"]
category_var = tk.StringVar(value="Personal blog")
for cat in categories:
    tk.Radiobutton(col_right, text=cat, variable=category_var, value=cat, bg="white").pack(anchor="w")

# Bio Options
tk.Label(col_right, text="Bio Options:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,2))
bio_custom_var = tk.BooleanVar(value=False)
bio_default_var = tk.BooleanVar(value=True)
bio_mode_var    = tk.StringVar(value="random")  # random / sequential
tk.Checkbutton(col_right, text="Bio theo yêu cầu", variable=bio_custom_var, bg="white").pack(anchor="w")
tk.Radiobutton(col_right, text="Ngẫu nhiên", variable=bio_mode_var, value="random",    bg="white").pack(anchor="w", padx=18)
tk.Radiobutton(col_right, text="Từng dòng",  variable=bio_mode_var, value="sequential",bg="white").pack(anchor="w", padx=18)
tk.Checkbutton(col_right, text="Bio mặc định", variable=bio_default_var, bg="white").pack(anchor="w")

bio_text = scrolledtext.ScrolledText(col_right, width=20, height=4, bg="lightyellow")
bio_text.pack(pady=(5,10), fill="x")

# ========================= MOBILE SETTINGS (mirror Desktop) =========================
mobile_settings = tk.LabelFrame(app, text="Mobile Settings", bg="white", font=("Arial", 11, "bold"))

def _position_mobile_settings():
    """Đặt Mobile Settings song song với Desktop Settings."""
    app.update_idletasks()
    try:
        x = desktop_settings.winfo_x() + desktop_settings.winfo_width() + 20   # cách Desktop 20px
        y = desktop_settings.winfo_y()                                        # cùng hàng với Desktop
    except Exception:
        x = left_frame.winfo_x() + left_frame.winfo_width() + 250
        y = 20
    mobile_settings.place(x=x, y=y)

app.after(120, _position_mobile_settings)

# ===== Lấy mặc định từ Desktop nếu có =====
def _get_bool(v, fallback=False):
    try: return bool(v.get())
    except: return fallback

def _get_str(v, fallback=""):
    try: return str(v.get())
    except: return fallback

_follow_def   = _get_bool(globals().get("follow_var", None), False)
_fullpack_def = _get_bool(globals().get("gender_bio_ava_post_var", None), False)
_pro_mode_def = _get_bool(globals().get("pro_mode_var", None), False)
_twofa_def    = _get_bool(globals().get("twofa_var", None), False)

_pro_type_def = _get_str(globals().get("pro_type_var", None), "Creator")          # "Creator" | "Business"
_category_def = _get_str(globals().get("category_var", None), "Personal blog")

# ===== Biến Mobile (tách phần chung & phần alias BIO) =====
enable_follow        = tk.BooleanVar(value=_follow_def)
enable_avatar        = tk.BooleanVar(value=_fullpack_def)   # hoặc tách riêng nếu có biến avatar riêng
enable_Chuyen_nghiep = tk.BooleanVar(value=_pro_mode_def)   # ✅ giữ nguyên “Bật Chuyên nghiệp”
enable_2fa           = tk.BooleanVar(value=_twofa_def)

pro_type_mobile   = tk.StringVar(value=_pro_type_def)       # Mobile vẫn có loại TK riêng (Creator/Business)
category_mobile   = tk.StringVar(value=_category_def)

# ===== BIO ALIAS: Mobile dùng CHUNG biến Desktop =====
# Cần sẵn các biến Desktop: bio_custom_var, bio_default_var, bio_mode_var, bio_text
m_bio_custom_var  = globals().get("bio_custom_var")   # ô tích "Bio theo yêu cầu" (chung Desktop)
m_bio_default_var = globals().get("bio_default_var")  # ô tích "Bio mặc định"   (chung Desktop)
m_bio_mode_var    = globals().get("bio_mode_var")     # radio 'random' | 'sequential' (chung Desktop)
bio_text_desktop  = globals().get("bio_text")         # Text/ScrolledText của Desktop

# Ô nhập Mobile là bản "giao diện" – sẽ sync 2 chiều với 'bio_text' Desktop
m_bio_text_mirror = None

# ===== Bố cục 2 cột: trái = toggle + Steps, phải = loại TK / Category / Bio =====
col_left  = tk.Frame(mobile_settings, bg="white")
col_right = tk.Frame(mobile_settings, bg="white")
col_left.grid(row=0, column=0, padx=6,  pady=6, sticky="n")
# Ô tích Ẩn Chrome (headless) cho Mobile
tk.Checkbutton(col_left, text="Ẩn Chrome (Headless)", variable=hidden_chrome_var, bg="white").pack(anchor="w", pady=2)
col_right.grid(row=0, column=1, padx=14, pady=6, sticky="n")

# ---- 4 ô tích bên trái (dùng lại tên biến cũ) ----
tk.Checkbutton(col_left, text="Follow (Mobile)",            variable=enable_follow,        bg="white").pack(anchor="w", pady=2)
tk.Checkbutton(col_left, text="Avatar (Mobile)",            variable=enable_avatar,        bg="white").pack(anchor="w", pady=2)
tk.Checkbutton(col_left, text="Bật Chuyên nghiệp (Mobile)", variable=enable_Chuyen_nghiep, bg="white",
               command=lambda: _sync_pro_mobile_state()).pack(anchor="w", pady=2)
tk.Checkbutton(col_left, text="Bật 2FA (Mobile)",           variable=enable_2fa,           bg="white").pack(anchor="w", pady=2)

# ---- Cột phải: Loại tài khoản / Category / Bio Options ----
grp_type = tk.LabelFrame(col_right, text="Loại tài khoản:", bg="white", font=("Arial", 10, "bold"))
grp_type.pack(fill="x", pady=(0,6))
tk.Radiobutton(grp_type, text="Creator",  variable=pro_type_mobile, value="Creator",  bg="white").pack(anchor="w")
tk.Radiobutton(grp_type, text="Business", variable=pro_type_mobile, value="Business", bg="white").pack(anchor="w")

grp_cat = tk.LabelFrame(col_right, text="Category:", bg="white", font=("Arial", 10, "bold"))
grp_cat.pack(fill="x", pady=(0,6))
CAT_OPTIONS = [
    "Personal blog",
    "Product/service",
    "Art",
    "Musician/band",
    "Shopping & retail",
    "Health/beauty",
    "Grocery Store",
]
for name in CAT_OPTIONS:
    tk.Radiobutton(grp_cat, text=name, variable=category_mobile, value=name, bg="white").pack(anchor="w")

# ==== Bio Options (Mobile) – điều khiển CHUNG biến với Desktop ====
grp_bio = tk.LabelFrame(col_right, text="Bio Options:", bg="white", font=("Arial", 10, "bold"))
grp_bio.pack(fill="both", pady=(0,6))

# Hai ô tích & hai radio: dùng CHUNG biến Desktop qua alias
tk.Checkbutton(grp_bio, text="Bio theo yêu cầu", variable=m_bio_custom_var, bg="white").pack(anchor="w")
tk.Checkbutton(grp_bio, text="Bio mặc định",    variable=m_bio_default_var, bg="white").pack(anchor="w")
tk.Radiobutton(grp_bio, text="Ngẫu nhiên",      variable=m_bio_mode_var,    value="random",    bg="white").pack(anchor="w")
tk.Radiobutton(grp_bio, text="Từng dòng",       variable=m_bio_mode_var,    value="sequential", bg="white").pack(anchor="w")

# Ô nhập Bio Mobile – MIRROR, có thanh cuộn, sync 2 chiều với Desktop
m_bio_text_mirror = scrolledtext.ScrolledText(grp_bio, height=4, width=23, wrap="word", bg="#fffbe6")
m_bio_text_mirror.pack(fill="both", expand=True, padx=4, pady=4)

def _sync_mirror_from_desktop(*_):
    try:
        src = bio_text_desktop.get("1.0", "end") if bio_text_desktop else ""
        dst = m_bio_text_mirror.get("1.0", "end")
        if src != dst:
            m_bio_text_mirror.delete("1.0", "end")
            m_bio_text_mirror.insert("1.0", src)
    except Exception:
        pass

def _sync_desktop_from_mirror(event=None):
    try:
        if not bio_text_desktop: 
            return
        src = m_bio_text_mirror.get("1.0", "end")
        dst = bio_text_desktop.get("1.0", "end")
        if src != dst:
            bio_text_desktop.delete("1.0", "end")
            bio_text_desktop.insert("1.0", src)
    except Exception:
        pass

# 1) Gõ ở Mobile -> đẩy về Desktop
m_bio_text_mirror.bind("<KeyRelease>", _sync_desktop_from_mirror)
# 2) Gõ ở Desktop -> kéo về Mobile (nếu Desktop có widget)
try:
    if bio_text_desktop:
        bio_text_desktop.bind("<KeyRelease>", lambda e: _sync_mirror_from_desktop())
    _sync_mirror_from_desktop()  # Đồng bộ lần đầu
except Exception:
    pass

# ---- Khi tắt Chuyên nghiệp thì khóa nhóm Loại TK + Category ----
def _sync_pro_mobile_state(*_):
    on = enable_Chuyen_nghiep.get()
    for grp in (grp_type, grp_cat):
        for w in grp.winfo_children():
            try: w.configure(state=("normal" if on else "disabled"))
            except Exception:
                try: w.state(["!disabled"] if on else ["disabled"])
                except Exception: pass
    try:
        grp_type.configure(fg=("black" if on else "#888"))
        grp_cat.configure(fg=("black" if on else "#888"))
    except Exception:
        pass

_sync_pro_mobile_state()
enable_Chuyen_nghiep.trace_add("write", _sync_pro_mobile_state)

# ---- Hàm gom cấu hình Mobile để dùng trong run_mobile ----
def collect_mobile_profile_config():
    # Bio lấy CHUNG nguồn Desktop nên không cần lưu mode/text riêng;
    # vẫn trả ra cho tiện debug/log.
    return {
        "follow":     bool(enable_follow.get()),
        "avatar":     bool(enable_avatar.get()),
        "pro_mode":   bool(enable_Chuyen_nghiep.get()),
        "pro_type":   str(pro_type_mobile.get()),
        "twofa":      bool(enable_2fa.get()),
        "category":   str(category_mobile.get()),
        # Tham chiếu BIO DESKTOP
        "bio_custom":  bool(m_bio_custom_var.get()) if m_bio_custom_var else False,
        "bio_default": bool(m_bio_default_var.get()) if m_bio_default_var else False,
        "bio_mode":    str(m_bio_mode_var.get())    if m_bio_mode_var    else "random",
        "bio_text":    (bio_text_desktop.get("1.0", "end").strip() if bio_text_desktop else m_bio_text_mirror.get("1.0", "end").strip())
    }

# ==================== MOBILE STEPS (5 bước, có cột Next bên phải) ====================
mobile_delay_entries = {}

def _header_mobile(parent):
    """Tiêu đề cột: [Label] [Điền] [Nghỉ] [Next]"""
    hdr = tk.Frame(parent, bg="white"); hdr.pack(pady=1, fill="x")
    tk.Label(hdr, text="",     bg="white", width=12).pack(side="left")
    tk.Label(hdr, text="Điền", bg="white", width=6).pack(side="left")
    tk.Label(hdr, text="Nghỉ", bg="white", width=6).pack(side="left")
    tk.Label(hdr, text="Next", bg="white", width=6).pack(side="left")

def _row_delay_mobile(parent, label, type_default, sleep_default, next_default=2):
    """Vẽ 1 hàng: [Label] [Entry Điền] [Entry Nghỉ] [Entry Next]"""
    fr = tk.Frame(parent, bg="white")
    fr.pack(pady=1, fill="x")
    tk.Label(fr, text=f"{label}:", bg="white", width=12, anchor="w").grid(row=0, column=0, padx=(0,4), sticky="w")

    e_type = tk.Entry(fr, width=5, justify="center")
    if type_default is not None:
        e_type.insert(0, str(type_default))
    e_type.grid(row=0, column=1, padx=2, sticky="w")
    mobile_delay_entries[f"{label}_type"] = e_type

    e_sleep = tk.Entry(fr, width=5, justify="center")
    if sleep_default is not None:
        e_sleep.insert(0, str(sleep_default))
    e_sleep.grid(row=0, column=2, padx=4, sticky="w")
    mobile_delay_entries[f"{label}_sleep"] = e_sleep

    e_next = tk.Entry(fr, width=5, justify="center")
    if next_default is not None:
        e_next.insert(0, str(next_default))
    e_next.grid(row=0, column=3, padx=4, sticky="w")
    mobile_delay_entries[f"{label}_next"] = e_next

def get_mobile_delay(key, default):
    try:
        val = mobile_delay_entries[key].get().strip()
        return float(val) if val else default
    except Exception:
        return default

# --- BƯỚC 1: Mail ---
box_m1 = tk.LabelFrame(col_left, text="BƯỚC 1", bg="white", font=("Arial", 10, "bold"))
box_m1.pack(pady=4, fill="x")
_header_mobile(box_m1)
_row_delay_mobile(box_m1, "Mail",   0.18, 1, next_default=2)

# --- BƯỚC 2: Code ---
box_m2 = tk.LabelFrame(col_left, text="BƯỚC 2", bg="white", font=("Arial", 10, "bold"))
box_m2.pack(pady=4, fill="x")
_header_mobile(box_m2)
_row_delay_mobile(box_m2, "Code",   0.30, 2, next_default=2)   # giống Desktop: Điền code 0.3 / 2

# --- BƯỚC 3: Pass ---
box_m3 = tk.LabelFrame(col_left, text="BƯỚC 3", bg="white", font=("Arial", 10, "bold"))
box_m3.pack(pady=4, fill="x")
_header_mobile(box_m3)
_row_delay_mobile(box_m3, "Pass",   0.18, 3, next_default=2)

# --- BƯỚC 4: Tuổi ---
box_m4 = tk.LabelFrame(col_left, text="BƯỚC 4", bg="white", font=("Arial", 10, "bold"))
box_m4.pack(pady=4, fill="x")
_header_mobile(box_m4)
_row_delay_mobile(box_m4, "Tuổi",   0.18, 2, next_default=2)

# --- BƯỚC 5: Họ Tên ---
box_m5 = tk.LabelFrame(col_left, text="BƯỚC 5", bg="white", font=("Arial", 10, "bold"))
box_m5.pack(pady=4, fill="x")
_header_mobile(box_m5)
_row_delay_mobile(box_m5, "Họ tên", 0.18, 2, next_default=2)

def collect_mobile_step_delays():
    """Trả về dict các Entry để dùng khi chạy flow mobile (lấy .get())."""
    keys = ["Mail","Code","Pass","Tuổi","Họ tên"]
    out = {}
    for k in keys:
        out[f"{k}_type"]  = mobile_delay_entries.get(f"{k}_type")
        out[f"{k}_sleep"] = mobile_delay_entries.get(f"{k}_sleep")
        out[f"{k}_next"]  = mobile_delay_entries.get(f"{k}_next")
    return out

# Đồng bộ khóa/mở theo radio GIAO DIỆN CHROME
app.after(150, _sync_mode_ui)

# ========================= PHONE SETTINGS (SCROLLABLE) =========================
PHONE_PADX = 6
PHONE_PADY = 6
PHONE_WRAP_W = 400     # rộng khung hiển thị (chỉnh tuỳ ý)
PHONE_WRAP_H = 520     # cao khung hiển thị (chỉnh tuỳ ý)

# đảm bảo các biến state cho Phone có mặt và trỏ đúng master
def ensure_phone_vars():
    global phone_net_mode, phone_ig_app_var
    try:
        phone_net_mode
    except NameError:
        phone_net_mode = tk.StringVar(master=app, value="wifi")          # wifi|warp|proxy|sim
    try:
        phone_ig_app_var
    except NameError:
        phone_ig_app_var = tk.StringVar(master=app, value="instagram")   # instagram|instagram_lite

# gọi sau khi app = tk.Tk() đã có
ensure_phone_vars()

# --- Vars mặc định nếu chưa có ---
try:
    phone_net_mode
except NameError:
    phone_net_mode = tk.StringVar(value="wifi")  # wifi | warp | proxy | sim

try:
    phone_ig_app_var
except NameError:
    phone_ig_app_var = tk.StringVar(master=app, value="instagram")

# ====== ĐƯỜNG DẪN & CẤU HÌNH ======
PROXY_TXT  = os.path.join(os.getcwd(), "Proxy.txt")

# ============= WRAPPER đặt bằng .place =============
phone_settings_wrap = tk.Frame(app, bg="white")

def _position_phone_settings():
    """Đặt Phone Settings song song, nằm bên phải Mobile Settings (kích thước cố định)."""
    app.update_idletasks()
    try:
        x = mobile_settings.winfo_x() + mobile_settings.winfo_width() + 20  # cách Mobile 20px
        y = mobile_settings.winfo_y()
    except Exception:
        x = desktop_settings.winfo_x() + desktop_settings.winfo_width() + 250
        y = desktop_settings.winfo_y()
    phone_settings_wrap.place(x=x, y=y, width=PHONE_WRAP_W, height=PHONE_WRAP_H)

app.after(180, _position_phone_settings)

# ============= Canvas + Scrollbar dọc =============
phone_canvas = tk.Canvas(phone_settings_wrap, bg="white", highlightthickness=0)
phone_vscroll = ttk.Scrollbar(phone_settings_wrap, orient="vertical", command=phone_canvas.yview)
phone_canvas.configure(yscrollcommand=phone_vscroll.set)


# Frame chứa widget con
phone_settings = tk.LabelFrame(phone_canvas, text="Phone Settings", bg="white", font=("Arial", 11, "bold"))
phone_canvas_window = phone_canvas.create_window((0, 0), window=phone_settings, anchor="nw")

# Bố cục
phone_canvas.grid(row=0, column=0, sticky="nsew")
phone_vscroll.grid(row=0, column=1, sticky="ns")
phone_settings_wrap.grid_rowconfigure(0, weight=1)
phone_settings_wrap.grid_columnconfigure(0, weight=1)

def _fit_canvas_to_wrap(event=None):
    cw = phone_settings_wrap.winfo_width()
    ch = phone_settings_wrap.winfo_height()
    if cw <= 1 or ch <= 1:
        return
    phone_canvas.config(width=cw-12, height=ch)
    phone_canvas.itemconfigure(phone_canvas_window, width=phone_canvas.winfo_width())

def _update_scrollregion(event=None):
    phone_canvas.configure(scrollregion=phone_canvas.bbox("all"))
    _fit_canvas_to_wrap()

phone_canvas.bind("<Configure>", lambda e: phone_canvas.itemconfigure(
    phone_canvas_window, width=phone_canvas.winfo_width()))
phone_settings_wrap.bind("<Configure>", _fit_canvas_to_wrap)
phone_settings.bind("<Configure>", _update_scrollregion)

# Cuộn bằng chuột
def _on_phone_mousewheel(event):
    if event.delta:
        phone_canvas.yview_scroll(int(-event.delta/120), "units")
    else:
        phone_canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

phone_canvas.bind("<Enter>", lambda e: app.bind_all("<MouseWheel>", _on_phone_mousewheel))
phone_canvas.bind("<Leave>", lambda e: app.unbind_all("<MouseWheel>"))
phone_canvas.bind("<Button-4>", _on_phone_mousewheel)  # Linux
phone_canvas.bind("<Button-5>", _on_phone_mousewheel)  # Linux

def _init_phone_canvas_once():
    try:
        app.update_idletasks()
        _update_scrollregion()
    except Exception:
        pass

app.after(400, _init_phone_canvas_once)

# ====================== BẢNG THIẾT BỊ 3 CỘT ======================
ttk.Label(phone_settings, text="Thiết bị ADB (chọn 1 hoặc nhiều):", background="white")\
   .pack(anchor="w", padx=PHONE_PADX, pady=(PHONE_PADY, 2))

cols = ("udid", "view", "pick")
phone_device_tree = ttk.Treeview(phone_settings, columns=cols, show="headings", height=6)
phone_device_tree.heading("udid", text="DANH SÁCH THIẾT BỊ")
phone_device_tree.heading("view", text="VIEW")
phone_device_tree.heading("pick", text="CHỌN")
phone_device_tree.column("udid", width=260, anchor="w")
phone_device_tree.column("view", width=60, anchor="center")
phone_device_tree.column("pick", width=60, anchor="center")
phone_device_tree.pack(fill="both", expand=True, padx=PHONE_PADX)

phone_device_tree.bind("<Button-1>", _toggle_cell)

ttk.Button(phone_settings, text="Refresh ADB devices", command=refresh_adb_devices_table)\
   .pack(anchor="w", padx=PHONE_PADX, pady=PHONE_PADY)

ttk.Button(phone_settings, text="Kill ADB and Reload", command=lambda: threading.Thread(target=kill_adb_and_reload, daemon=True).start())\
    .pack(anchor="w", padx=PHONE_PADX, pady=(0, PHONE_PADY))
# --- Chọn kích thước scrcpy ---
ttk.Label(phone_settings, text="Chọn kích thước hiển thị:")\
    .pack(anchor="w", padx=PHONE_PADX, pady=(0, PHONE_PADY))

combo_res = ttk.Combobox(
    phone_settings,
    values=["360x640", "540x960", "720x1280", "1080x1920"],
    state="readonly",
    width=15
)
combo_res.set("540x960")  # mặc định
combo_res.bind("<<ComboboxSelected>>", change_resolution)
combo_res.pack(anchor="w", padx=PHONE_PADX, pady=(0, PHONE_PADY))

# --- Nút mở & sắp xếp scrcpy ---
ttk.Button(phone_settings, text="Sắp xếp Phone View", command=open_and_arrange)\
    .pack(anchor="w", padx=PHONE_PADX, pady=(0, PHONE_PADY))

# ======================= Network Mode =======================
net_frame = ttk.LabelFrame(phone_settings, text="Network Mode")
net_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

for txt, val in [("WiFi", "wifi"), ("WARP", "warp"), ("Proxy", "proxy"), ("SIM 4G", "sim")]:
    ttk.Radiobutton(net_frame, text=txt, value=val, variable=phone_net_mode)\
       .pack(anchor="w", padx=10, pady=2)

# ======================= Proxy Type =======================
proxy_format_var = tk.StringVar(value="ip_port")

# Đặt trace_add sau khi khởi tạo biến proxy_format_var
try:
    proxy_format_var.trace_add('write', lambda *args: save_config())
except Exception:
    pass
proxy_format_frame = ttk.LabelFrame(phone_settings, text="Proxy Type")
proxy_format_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

ttk.Radiobutton(proxy_format_frame, text="IP:PORT",
                     variable=proxy_format_var, value="ip_port")\
    .pack(anchor="w", padx=10, pady=2)
ttk.Radiobutton(proxy_format_frame, text="IP:PORT:USER:PASS",
                     variable=proxy_format_var, value="ip_port_userpass")\
    .pack(anchor="w", padx=10, pady=2)

# ======================= HANDLERS / CONFIG =======================
photo_folder_phone = ""

def open_proxy_txt():
    try:
        if not os.path.exists(PROXY_TXT):
            with open(PROXY_TXT, "w", encoding="utf-8") as f:
                f.write("")
        if os.name == "nt":
            os.startfile(PROXY_TXT)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", PROXY_TXT])
        else:
            subprocess.Popen(["xdg-open", PROXY_TXT])
        log(f"📝 Đã mở: {PROXY_TXT}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không mở được Proxy.txt:\n{e}")

def choose_photo_folder_phone():
    global photo_folder_phone
    path = filedialog.askdirectory(title="Chọn thư mục ảnh (Phone)")
    if path:
        photo_folder_phone = path
        save_phone_paths()
        log(f"📂 Đã chọn folder ảnh (Phone): {path}")
    else:
        log("⚠️ Chưa chọn folder ảnh (Phone).")

def load_phone_paths():
    load_config()

def save_phone_paths():
    save_config()

def get_random_photo_from_folder():
    folder = globals().get("photo_folder_phone", "")
    if not folder or not os.path.isdir(folder):
        log("⚠️ Chưa chọn folder ảnh (Phone).")
        return None
    pics = [f for f in os.listdir(folder) if f.lower().endswith((".jpg",".jpeg",".png"))]
    if not pics:
        log("⚠️ Folder ảnh không có file hợp lệ.")
        return None
    return os.path.join(folder, random.choice(pics))

def push_photo_for_phone(udid=None, remote_dir="/sdcard/Pictures/AutoPhone"):
    """Push 1 ảnh ngẫu nhiên vào điện thoại & gửi MEDIA_SCANNER"""
    local_path = get_random_photo_from_folder()
    if not local_path:
        return None
    file_name = os.path.basename(local_path)
    remote_path = f"{remote_dir}/{file_name}"
    try:
        adb_mkdir(udid, remote_dir)
        adb_push(udid, local_path, remote_path)
        adb_media_scan(udid, remote_path)
        log(f"✅ Đã push & scan ảnh: {remote_path}")
        return (local_path, remote_path)
    except Exception as e:
        log(f"❌ Lỗi push ảnh: {e}")
        return None

# nạp ngay khi khởi động
load_phone_paths()

# ======================= HÀNG NÚT 1: Proxy.txt | Chọn folder ảnh =======================
actions_top = ttk.Frame(phone_settings)
actions_top.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))
actions_top.grid_columnconfigure(0, weight=1)
actions_top.grid_columnconfigure(1, weight=1)

ttk.Button(actions_top, text="Mở Proxy.txt", command=open_proxy_txt)\
   .grid(row=0, column=0, sticky="we", padx=(0, 3))
ttk.Button(actions_top, text="Chọn folder ảnh", command=choose_photo_folder_phone)\
   .grid(row=0, column=1, sticky="we", padx=(3, 0))

ttk.Separator(phone_settings, orient="horizontal").pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

# ======================= HÀNG NÚT 2: scrcpy.exe | Mở View Phone =======================
actions_bottom = ttk.Frame(phone_settings)
actions_bottom.pack(fill="x", padx=PHONE_PADX, pady=(0, PHONE_PADY))
actions_bottom.grid_columnconfigure(0, weight=1)
actions_bottom.grid_columnconfigure(1, weight=1)

ttk.Button(actions_bottom, text="Chọn scrcpy.exe", command=choose_scrcpy_path)\
   .grid(row=0, column=0, sticky="we", padx=(0, 3))
ttk.Button(actions_bottom, text="Mở View Phone",
           command=lambda: open_scrcpy_for_list(get_checked_udids("view")))\
   .grid(row=0, column=1, sticky="we", padx=(3, 0))

# ======================= CHỌN APP IG: Instagram | Instagram Lite =======================
def _persist_ig_choice():
    try:
        save_phone_paths()
    except Exception:
        pass

app_select_frame = ttk.LabelFrame(phone_settings, text="App Instagram")
app_select_frame.pack(fill="x", padx=PHONE_PADX, pady=PHONE_PADY)

ttk.Radiobutton(app_select_frame, text="Instagram", value="instagram",
                variable=phone_ig_app_var, command=_persist_ig_choice)\
   .pack(side="left", padx=8, pady=4)

ttk.Radiobutton(app_select_frame, text="Instagram Lite", value="instagram_lite",
                variable=phone_ig_app_var, command=_persist_ig_choice)\
   .pack(side="left", padx=8, pady=4)

# ======================= PROFESSIONAL ACCOUNT SETTINGS (Phone) =======================
pro_settings_frame = ttk.LabelFrame(phone_settings, text="Professional Account", padding=(6,6), style="TLabelframe")
pro_settings_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

CATEGORIES = [
    "Artist", "Musician/band", "Blogger", "Clothing (Brand)",
    "Community", "Digital creator", "Education", "Entrepreneur",
    "Health/beauty", "Editor", "Writer", "Personal blog",
    "Product/service", "Gamer", "Restaurant",
    "Beauty, cosmetic & personal care", "Grocery Store",
    "Photographer", "Shopping & retail", "Reel creator"
]
pro_category_var = tk.StringVar(value="Reel creator")
ttk.Label(pro_settings_frame, text="Category:").pack(side="left", padx=(10, 2))
ttk.Combobox(pro_settings_frame, textvariable=pro_category_var, values=CATEGORIES, width=22, state="readonly").pack(side="left")
pro_type_var = tk.StringVar(value="Creator")
ttk.Label(pro_settings_frame, text="Type:").pack(side="left", padx=(10, 2))
ttk.Combobox(pro_settings_frame, textvariable=pro_type_var, values=["Creator", "Business"], width=10, state="readonly").pack(side="left")

# Ô nhập số lượng follow (mặc định 10)
phone_follow_count_var = tk.IntVar(value=10)
ttk.Label(phone_settings, text="Số lượng follow:").pack(side="left", padx=(10, 2))
ttk.Spinbox(phone_settings, from_=1, to=30, textvariable=phone_follow_count_var, width=5).pack(side="left")

# ======================= PHONE ACTIONS (Enable/Disable) =======================
phone_actions_frame = ttk.LabelFrame(phone_settings, text="Phone Actions (Instagram)", padding=(6,6))
phone_actions_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

enable_2faphone    = tk.BooleanVar(value=False)
enable_uppost      = tk.BooleanVar(value=False)
enable_editprofile = tk.BooleanVar(value=False)
enable_autofollow  = tk.BooleanVar(value=False)
enable_proaccount  = tk.BooleanVar(value=False)

ttk.Checkbutton(phone_actions_frame, text="Enable 2FA (Phone/App)", variable=enable_2faphone).pack(anchor="w", padx=10, pady=2)
ttk.Checkbutton(phone_actions_frame, text="Enable Up Post", variable=enable_uppost).pack(anchor="w", padx=10, pady=2)
ttk.Checkbutton(phone_actions_frame, text="Enable Edit Profile", variable=enable_editprofile).pack(anchor="w", padx=10, pady=2)
ttk.Checkbutton(phone_actions_frame, text="Enable Auto Follow", variable=enable_autofollow).pack(anchor="w", padx=10, pady=2)
ttk.Checkbutton(phone_actions_frame, text="Enable Switch to Professional", variable=enable_proaccount).pack(anchor="w", padx=10, pady=2)

# ======================= QUÉT THIẾT BỊ LẦN ĐẦU =======================
try:
    refresh_adb_devices_table()
except Exception:
    pass

# ========================= KHỐI DƯỚI =========================
# Chrome size & Scale
chrome_size_frame = tk.Frame(app, bg="white")
chrome_size_frame.pack(side="left", padx=20)

tk.Label(chrome_size_frame, text="Chrome:", bg="white").pack(side="left")
entry_width  = tk.Entry(chrome_size_frame, width=6, justify="center"); entry_width.insert(0, "1200"); entry_width.pack(side="left", padx=2)
tk.Label(chrome_size_frame, text="x", bg="white").pack(side="left")
entry_height = tk.Entry(chrome_size_frame, width=6, justify="center"); entry_height.insert(0, "800");  entry_height.pack(side="left", padx=2)

tk.Label(chrome_size_frame, text="Scale (%):", bg="white").pack(side="left", padx=(10,2))
entry_scale  = tk.Entry(chrome_size_frame, width=4, justify="center"); entry_scale.insert(0, "100"); entry_scale.pack(side="left", padx=2)

# Live/Die/Rate
status_frame = tk.Frame(app, bg="white")
status_frame.pack(side="bottom", anchor="w", pady=5, padx=5)
tk.Label(status_frame, text="LIVE:", fg="green", bg="white", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5)
tk.Label(status_frame, textvariable=live_var, fg="green", bg="white", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=5)

tk.Label(status_frame, text="DIE:",  fg="red",   bg="white", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=5)
tk.Label(status_frame, textvariable=die_var,  fg="red",   bg="white", font=("Arial", 11, "bold")).grid(row=0, column=3, padx=5)

# RATE dời sang cột 6 và 7
tk.Label(status_frame, text="RATE:", fg="blue",  bg="white", font=("Arial", 11, "bold")).grid(row=0, column=6, padx=5)
tk.Label(status_frame, textvariable=rate_var, fg="blue",  bg="white", font=("Arial", 11, "bold")).grid(row=0, column=7, padx=5)

# Logs + Accounts
bottom_frame = tk.Frame(app, bg="white")
bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)

log_frame = tk.LabelFrame(bottom_frame, text="Logs", bg="white")
log_frame.pack(side="left", fill="both", expand=True)
log_text = scrolledtext.ScrolledText(log_frame, width=58, height=4, state=tk.DISABLED, bg="black", fg="lime")
log_text.pack(fill="both", expand=True, padx=5, pady=5)

tree_frame = tk.LabelFrame(bottom_frame, text="Accounts", bg="white", font=("Arial", 10, "bold"))
tree_frame.pack(side="right", fill="both", expand=True, padx=5)

cols = ["STT","TRẠNG THÁI","USERNAME","PASS","MAIL","PHONE","COOKIE","2FA","TOKEN","IP","PROXY","LIVE","DIE"]
tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=4)
vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=tree.yview);  tree.configure(yscrollcommand=vsb.set); vsb.pack(side="right",  fill="y")
hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview);  tree.configure(xscrollcommand=hsb.set); hsb.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="w")

tree.tag_configure("LIVE", background="lightgreen")
tree.tag_configure("DIE",  background="tomato")
load_config()
def open_main_app():
    try:
        app.deiconify()   # hiện lại giao diện chính
    except Exception:
        pass

# gọi intro trước khi chạy main loop
show_intro(app, open_main_app)

app.mainloop()
