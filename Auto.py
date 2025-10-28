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
import urllib.parse
from urllib.parse import urlparse
from selenium import webdriver as se_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from tkinter import ttk
import requests
import base64
import names
import subprocess, re, xml.etree.ElementTree as ET
import random
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
from tkinter import Toplevel, Text, Scrollbar
from appium.webdriver.common.appiumby import AppiumBy
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException
from tkinter import ttk, messagebox, filedialog, Text, Scrollbar, Toplevel
import socket, shutil
# Fix for PointerInput and ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder

# ==================================== PHONE ====================================
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

def is_device_rooted(udid: str) -> bool:
    """Kiểm tra nhanh thiết bị có root không (dùng su -c id hoặc which su)."""
    try:
        out = adb_shell(udid, "su", "-c", "id")
        if out and "uid=0" in out:
            return True
    except Exception:
        pass
    try:
        out2 = adb_shell(udid, "which", "su")
        if out2 and out2.strip():
            return True
    except Exception:
        pass
    return False

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

    # ========== Chrome ==========
    clear_app_data(udid, "com.android.chrome")
    time.sleep(1.0)
    adb_shell(udid, "am", "force-stop", "com.android.chrome")
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
    - Force-stop IG, WARP, Super Proxy, Chrome
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
        adb_shell(udid, "am", "force-stop", "com.instagram.lite")
        adb_shell(udid, "am", "force-stop", "com.android.chrome")  # Thêm dòng này
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
    Quét ADB và đổ dữ liệu vào Treeview 4 cột: UDID | VIEW | CHỌN | STATUS.
    Giữ lại trạng thái tick cũ nếu UDID vẫn còn online.
    """
    try:
        devs = adb_devices()

        # thêm dev mới vào state / xóa dev cũ
        for ud in devs:
            device_state.setdefault(ud, {"view": False, "pick": False, "status": "No root"})
        for ud in list(device_state.keys()):
            if ud not in devs:
                device_state.pop(ud, None)

        # Cập nhật trạng thái root (có thể chậm nếu nhiều device)
        for ud in devs:
            try:
                rooted = is_device_rooted(ud)
                device_state.setdefault(ud, {})
                device_state[ud]["status"] = "Rooted" if rooted else "No root"
            except Exception:
                device_state[ud]["status"] = "No root"

        # Cập nhật phone_device_tree (4 cột)
        if phone_device_tree is not None:
            phone_device_tree.delete(*phone_device_tree.get_children())
            for ud in devs:
                st = device_state.get(ud, {"view": False, "pick": False, "status": "No root"})
                phone_device_tree.insert(
                    "", "end", iid=ud,
                    values=(ud, _tick(st.get("view", False)), _tick(st.get("pick", False)), st.get("status", "No root"))
                )

        if devs:
            log(f"📡 Tìm thấy {len(devs)} thiết bị: {', '.join(devs)}")
        else:
            log("⚠️ Không phát hiện thiết bị nào. Kiểm tra USB debugging / cáp / adb devices.")
    except Exception as e:
        log(f"❌ Lỗi refresh ADB: {repr(e)}")

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

def delete_pictures_and_reboot():
    try:
        selected = get_checked_udids("pick") if "get_checked_udids" in globals() else []
        if not selected:
            messagebox.showinfo("ADB", "Chưa chọn thiết bị nào trong bảng.")
            return
        for udid in selected:
            subprocess.call([
                "adb", "-s", udid, "shell",
                "rm", "-rf", "/sdcard/DCIM/*", "/sdcard/Pictures/*"
            ])
            subprocess.call(["adb", "-s", udid, "reboot"])
        messagebox.showinfo("DELETE PIC", f"Đã xóa ảnh và reboot {len(selected)} thiết bị.")
    except Exception as e:
        messagebox.showerror("DELETE PIC", f"Lỗi: {repr(e)}")
        log(f"❌ Lỗi khi xóa ảnh và reboot: {repr(e)}")

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
    Hoạt động với phone_device_tree.
    """
    # Xác định tree nào được click
    tree = event.widget
    if tree is None:
        return
    
    row_id = tree.identify_row(event.y)
    col_id = tree.identify_column(event.x)  # "#1" "#2" "#3"
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
    
    # Cập nhật hiển thị trên tree
    col_name = "view" if key == "view" else "pick"
    if phone_device_tree is not None and row_id in phone_device_tree.get_children():
        phone_device_tree.set(row_id, column=col_name, value=_tick(cur[key]))

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

    devices = get_checked_udids("view")
    if not devices:
        messagebox.showinfo("Phone View", "Bạn cần tick cột VIEW cho thiết bị muốn mở!")
        return

    import pygetwindow as gw

    # Kiểm tra cửa sổ scrcpy đã mở
    all_windows = gw.getAllWindows()
    opened_serials = [w.title.split()[-1] for w in all_windows if w.title and ("scrcpy" in w.title.lower() or "sm-" in w.title.lower())]
    already_opened = [serial for serial in devices if serial in opened_serials]
    to_open = [serial for serial in devices if serial not in opened_serials]

    # Mở scrcpy cho thiết bị chưa mở
    for serial in to_open:
        subprocess.Popen([
            scrcpy_path,
            "-s", serial,
            "--max-size", resolution.split("x")[0]
        ])
        time.sleep(1.2)

    time.sleep(5)

    # Lấy cửa sổ scrcpy
    all_windows = gw.getAllWindows()
    windows = [w for w in all_windows if w.title and ("scrcpy" in w.title.lower() or "sm-" in w.title.lower())]

    if not windows:
        messagebox.showerror("Lỗi", "Không tìm thấy cửa sổ scrcpy")
        return

    # ✅ Resize toàn bộ về cùng kích thước (để không lệch khi xếp sát)
    standard_width = min(w.width for w in windows)
    standard_height = min(w.height for w in windows)
    for w in windows:
        try:
            w.resizeTo(standard_width, standard_height)
        except:
            pass

    # ✅ Xếp sát tuyệt đối (8 view / hàng)
    max_per_row = 8
    x, y = 0, 0
    col_count = 0

    for idx, win in enumerate(windows):
        try:
            if col_count == 0:
                x = 0
            else:
                # ⚡ dùng right để mép trái cửa sổ kế tiếp chạm mép phải cửa sổ trước
                prev_win = windows[idx - 1]
                x = prev_win.right

            win.moveTo(x, y)
            col_count += 1

            if col_count >= max_per_row:
                col_count = 0
                y += win.height
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
    "Ghi dấu hôm nay", "Khoảnh khắc nhỏ", "Một tấm cho nhớ",
    "Tâm trạng nhẹ tênh", "Bắt đầu thật vui", "Hôm nay ổn áp",
    "Chút nắng cuối ngày", "Đi đâu đó nè", "Vẫn là mình thôi",
    "Giữ vibe này", "Lạc vào cuối tuần", "Góc nhỏ thân quen",
    "Lâu lâu đăng cái", "Tranh thủ chụp vội", "Lên hình cái đã",
    "Chọn bình yên", "Chấm một cái", "Nhỏ mà xinh",
    "Chạm nhẹ cảm xúc", "Một ngày đẹp", "Hơi bị mê góc này",
    "Up cho có động lực", "Giữ ký ức lại", "Tích điện năng lượng",
    "Trời đẹp thì đăng", "Nhẹ như mây", "Thích là nhích",
    "Đi để trở về", "Một màu rất tôi"
]

CAPTION_TRAILS = [
    "Hẹn gặp ngày mai.", "Bạn đang làm gì đó?", "Thêm chút động lực nhé.",
    "Cùng chill không?", "Góp ý cho mình nha.", "Like nhẹ cũng vui.",
    "Lưu lại để nhớ.", "Bạn chọn tông nào?", "Up rồi đi ngủ.",
    "Không filter vẫn xinh.", "Tấm này được không?", "Gợi ý caption giúp mình?",
    "Gặp nhau ở đây nhé.", "Cuối tuần làm gì?", "Nhìn mà thấy thương.",
    "Giữ vibe này lâu lâu.", "Hôm nay chấm mấy điểm?", "Cà phê hay trà?",
    "Mỗi ngày một niềm vui.", "Giản dị cho ngày dài.", "Đi đâu cuối tuần?",
    "Thả tim lấy vía đẹp.", "Cảm ơn đã xem.", "Xem xong nhớ mỉm cười.",
    "Đang trên đường về.", "Gõ cửa bình yên.", "Bạn đã ăn chưa?",
    "Chốt đơn nụ cười.", "Mình ổn, bạn thì sao?"
]

CAPTION_EMOJIS = ["✨","🌿","🌸","🌙","☀️","⭐","🍀","🌼","🫶","💫",
                  "📸","😚","🤍","🧸","🥰","🫧","🌈","🌊","🏖️","🏙️","🌅","🌇","🌁","🌵","🍰","🍩","🍹","🍓",
                  "🧋","🎧","🎒","🎀","🕊️","💌","💎","🪴","📍","🧭","🪄","🎞️"
                  ]

# ===== BIO RANDOM =====
BIO_LINES = [
    "Luôn học điều mới", "Ngày mới năng lượng", "Từng bước vững vàng",
    "Sống có mục tiêu", "Chọn tử tế", "Tin vào bản thân",
    "Nhỏ nhưng có võ", "Điềm tĩnh mà đi", "Gọn gàng suy nghĩ",
    "Mỗi ngày một tốt hơn", "Giữ nhịp bình yên", "Bắt đầu lại cũng được",
    "Không ngừng tò mò", "Kiên trì là chìa khóa", "Tập trung vào điều tốt",
    "Chậm mà chắc", "Mỗi việc một lần", "Năng lượng tích cực",
    "Đủ rồi là hạnh phúc", "Giản dị để tự do", "Vững như kiềng ba chân",
    "Nghĩ ít làm nhiều", "Làm đúng việc", "Tỉnh táo và chân thành",
    "Cứ đi sẽ đến", "Vun trồng thói quen", "Giỏi lên từng ngày",
    "Thích nghi nhanh", "Đặt mình vào hiện tại", "Giữ lửa đam mê",
    "Bản lĩnh từ trải nghiệm", "Thử rồi mới biết", "Luôn chủ động",
    "Định vị lại bản thân", "Góp nhặt niềm vui", "Xây mỗi ngày một viên gạch",
    "Sống chậm hiểu sâu", "Học từ sai lầm", "Tự do trong khuôn khổ",
    "Giữ lời hứa", "Chọn việc quan trọng", "Đơn giản hóa phức tạp",
    "Kỷ luật là sức mạnh", "Thái độ quyết định", "Cảm ơn vì hôm nay",
    "Lòng biết ơn dẫn lối", "Khỏe trong tâm trí", "An trú hiện tại",
    "Không so sánh", "Tạo khác biệt nhỏ", "Nhận trách nhiệm",
    "Làm khó để dễ", "Tắt ồn mở tập trung", "Sáng tạo mỗi ngày",
    "Học hỏi từ mọi người", "Tôn trọng thời gian", "Hướng đến giá trị",
    "Sống có ích", "Truyền cảm hứng nhẹ nhàng", "Tư duy dài hạn",
    "Tối ưu hơn hoàn hảo", "Xây hệ thống cho mình", "Kiên nhẫn với tiến bộ",
    "Thu gọn cuộc sống", "Đặt câu hỏi hay", "Giữ chuẩn mực",
    "Làm ít mà chất", "Tự chủ cảm xúc", "Tự tin vừa đủ",
    "Giữ nhịp rèn luyện", "Ngủ sớm dậy sớm", "Ăn mừng bước nhỏ",
    "Không ngừng đọc", "Ghi chép để nhớ", "Chọn bạn mà chơi",
    "Tích lũy kỹ năng", "Nói thật làm thật", "Học đi đôi với làm",
    "Bắt đầu từ hôm nay", "Cải thiện 1% mỗi ngày", "Giữ lưng thẳng",
    "Biết dừng đúng lúc", "Nhường phần đúng", "Nói ít hiểu nhiều",
    "Cân bằng công việc sống", "Đặt sức khỏe lên trước", "Nhìn xa trông rộng",
    "Tạo giá trị trước", "Làm chủ thời gian rảnh", "Xây thói quen tốt",
    "Giản lược ưu tiên", "Rõ mục tiêu rõ việc", "Đầu tư cho bản thân",
    "Tìm cơ hội trong khó", "Tích cực nhưng thực tế", "Tập trung điều kiểm soát",
    "Đam mê có kỷ luật", "Đường dài mới biết", "Kiên định lộ trình"
]

def _scroll_into_view_by_text(d, text_sub: str, max_swipes: int = 6, swipe_delay: float = 0.7) -> bool:
    # Ưu tiên UiScrollable, fallback vuốt tay chậm hơn
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
                time.sleep(swipe_delay)  # tăng delay để vuốt chậm hơn
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
                self.ensure_keyboard_hidden()
                # 👇 CẤP QUYỀN app theo lựa chọn
                try:
                    choice = (phone_ig_app_var.get() or "instagram").lower()
                except Exception:
                    choice = "instagram"
                if choice == "instagram_lite":
                    pkg_to_grant = "com.instagram.lite"
                elif choice == "chrome":
                    pkg_to_grant = "com.android.chrome"
                else:
                    pkg_to_grant = "com.instagram.android"
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
                elif mode == "1.1.1.1":
                    # 1.1.1.1: tương tự WARP nhưng dùng hàm riêng connect_1_1_1_1()
                    self.log(f"🌐 [Phone] {self.udid}: Bật VPN 1.1.1.1")
                    try:
                        self.ensure_airplane_off()
                        self.ensure_mobile_data_off()
                        self.ensure_wifi_on()
                        self.connect_1_1_1_1()  # ✅ dùng hàm mới
                    except Exception as e:
                        self.log(f"⚠️ [Phone] Lỗi bật 1.1.1.1 cho {self.udid}: {repr(e)}")
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

        time.sleep(5)
        # 3) Chỉ bấm Install VPN Profile khi xuất hiện (check nhanh, nếu không có thì bỏ qua)
        if _exists_any_text(["Install VPN Profile", "Cài đặt hồ sơ VPN", "Cài đặt VPN"], timeout=1, sleep_step=0.12):
            _tap_any_text(["Install VPN Profile", "Cài đặt hồ sơ VPN", "Cài đặt VPN"], timeout=1, sleep_step=0.12)
            time.sleep(0.8)  # đợi popup hệ thống hiện ra (rút ngắn)
            # xử lý popup hệ thống Android (Allow/OK) — chỉ bấm nếu xuất hiện
            if _exists_any_text(["OK", "Cho phép", "Allow"], timeout=1, sleep_step=0.12):
                _tap_any_text(["OK", "Cho phép", "Allow"], timeout=1, sleep_step=0.12)

        # 4) Popup Android “Connection request” → OK/Allow (chỉ bấm nếu có)
        if _exists_any_text(["OK", "Allow", "Cho phép", "ĐỒNG Ý"], timeout=1, sleep_step=0.12):
            _tap_any_text(["OK", "Allow", "Cho phép", "ĐỒNG Ý"], timeout=1, sleep_step=0.12)

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
    def configure_super_proxy_ip_port(self, ip=None, port=None, user=None, pwd=None):
        """Giữ hàm này để tránh lỗi AttributeError từ luồng network mode 'proxy'."""
        try:
            if ip and port:
                if user and pwd:
                    self.log(f"⚙️ configure_super_proxy_ip_port: IP={ip}:{port} | USER={user} | PASS={pwd}")
                else:
                    self.log(f"⚙️ configure_super_proxy_ip_port: IP={ip}:{port} (no auth)")
            else:
                self.log("⚙️ configure_super_proxy_ip_port: Không có IP/PORT hợp lệ.")
        except Exception as e:
            self.log(f"⚠️ Lỗi trong configure_super_proxy_ip_port: {repr(e)}")

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

        time.sleep(10)

        # 👉 Tap Add Proxy
        adb_shell(udid, "input", "tap", "860", "1400")
        time.sleep(4)

        # 👉 Lấy proxy từ Proxy.txt
        proxy = parse_proxy(read_first_proxy_line_fixed())
        if not proxy or not proxy["ip"] or not proxy["port"]:
            self.log("⛔ Proxy không hợp lệ")
            return

        # Log chính xác cấu hình proxy
        if proxy.get("has_auth"):
            self.log(f"⚙️ Proxy nhận được:")
            self.log(f"   ├─ IP: {proxy['ip']}")
            self.log(f"   ├─ PORT: {proxy['port']}")
            self.log(f"   ├─ USER: {proxy['user']}")
            self.log(f"   └─ PASS: {proxy['pwd']}")
        else:
            self.log(f"⚙️ Proxy nhận được:")
            self.log(f"   ├─ IP: {proxy['ip']}")
            self.log(f"   └─ PORT: {proxy['port']}")

        # 👉 Protocol HTTP
        adb_shell(udid, "input", "tap", "500", "600")   # tap Protocol
        adb_shell(udid, "input", "tap", "500", "700")   # chọn HTTP
        time.sleep(3)

        # 👉 Server (IP)
        adb_shell(udid, "input", "tap", "500", "800")
        adb_shell(udid, "input", "text", proxy["ip"])
        time.sleep(3)

        # 👉 Port
        adb_shell(udid, "input", "tap", "500", "950")
        adb_shell(udid, "input", "text", proxy["port"])
        time.sleep(3)

        # 👉 Nếu có user/pass thì xử lý thêm
        if proxy.get("has_auth"):
            # Chọn Authentication method → Username/Password
            adb_shell(udid, "input", "tap", "500", "1300")
            time.sleep(3)
            adb_shell(udid, "input", "tap", "500", "1100")
            time.sleep(3)

            # Vuốt xuống để hiện ô User/Pass
            adb_shell(udid, "input", "swipe", "500", "1500", "500", "500", "300")
            time.sleep(6)

            # Username
            adb_shell(udid, "input", "tap", "500", "1100")
            adb_shell(udid, "input", "text", proxy["user"])
            time.sleep(3)

            # Password
            adb_shell(udid, "input", "tap", "500", "1250")
            adb_shell(udid, "input", "text", proxy["pwd"])
            time.sleep(3)

        # 👉 Save
        adb_shell(udid, "input", "tap", "1000", "100")
        time.sleep(3)

        # 👉 Start
        adb_shell(udid, "input", "tap", "500", "1400")
        time.sleep(4)

        # 👉 Popup Connection request (OK)
        adb_shell(udid, "input", "tap", "800", "1300")

        # 👉 Kết quả cuối
        if proxy.get("has_auth"):
            self.log(f"✅ Đã cấu hình Proxy {proxy['ip']}:{proxy['port']} "
                     f"(USER={proxy['user']} | PASS={proxy['pwd']})")
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

    # ================================== WARP ( 1.1.1.1 / DNS ) ============================================
    def connect_1_1_1_1(self):
        """
        Bật Cloudflare 1.1.1.1 (VPN) an toàn:
        Airplane OFF -> Mobile data OFF -> Wi-Fi ON -> wake -> start_activity/activate/monkey -> wait foreground
        -> Next -> Accept -> (Install VPN Profile + OK) -> Connect.
        """
        d = self.driver
        udid = self.udid
        pkg = "com.cloudflare.onedotonedotonedotone"
        main_act = "com.cloudflare.app.MainActivity"

        # ✅ Chuẩn bị môi trường cho 1.1.1.1
        try:
            self.ensure_airplane_off()
            self.ensure_mobile_data_off()
            self.ensure_wifi_on()
        except Exception:
            pass

        # ===== helpers cục bộ =====
        def _wake_screen():
            try:
                subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "224"])
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
        self.log("🌐 Mở ứng dụng 1.1.1.1 (Cloudflare)…")

        # 1) Mở app với chuỗi fallback
        started = False
        try:
            d.start_activity(pkg, main_act)
            started = True
        except Exception:
            try:
                d.activate_app(pkg)
                started = True
            except Exception:
                pass
        if not started:
            subprocess.call([
                "adb", "-s", udid, "shell", "monkey", "-p", pkg,
                "-c", "android.intent.category.LAUNCHER", "1"
            ])

        _wait_app_foreground(pkg, timeout=10)

        # 2) Onboarding: Next -> Accept (nếu có)
        _tap_any_text(["Next", "Tiếp", "NEXT"], timeout=4, sleep_step=0.2)
        _tap_any_text(["Accept", "Chấp nhận", "Đồng ý", "ACCEPT"], timeout=4, sleep_step=0.2)

        time.sleep(5)

        # 3) Cài VPN Profile nếu có
        if _exists_any_text(["Install VPN Profile", "Cài đặt hồ sơ VPN", "Cài đặt VPN"], timeout=1, sleep_step=0.12):
            _tap_any_text(["Install VPN Profile", "Cài đặt hồ sơ VPN", "Cài đặt VPN"], timeout=1, sleep_step=0.12)
            time.sleep(0.8)
            if _exists_any_text(["OK", "Cho phép", "Allow"], timeout=1, sleep_step=0.12):
                _tap_any_text(["OK", "Cho phép", "Allow"], timeout=1, sleep_step=0.12)

        # 4) Popup “Connection request” → OK/Allow (chỉ bấm nếu có)
        if _exists_any_text(["OK", "Allow", "Cho phép", "ĐỒNG Ý"], timeout=1, sleep_step=0.12):
            _tap_any_text(["OK", "Allow", "Cho phép", "ĐỒNG Ý"], timeout=1, sleep_step=0.12)
        
        # 5) Mở menu và chọn chế độ 1.1.1.1 (DNS only)
        try:
            self.log("⚙️ Đang chuyển sang chế độ 1.1.1.1 (DNS only)…")

            # Nhấn nút 3 gạch góc phải trên (Menu)
            if _tap_any_text(["☰", "Menu"], timeout=2, sleep_step=0.3) is False:
                # fallback: tap tọa độ góc phải trên nếu không có phần tử chứa text
                try:
                    size = d.get_window_size()
                    x = int(size["width"] * 0.93)
                    y = int(size["height"] * 0.08)
                    d.swipe(x, y, x, y, 100)
                except Exception:
                    pass

            # Chờ trang Settings hiện
            time.sleep(5)

            # Nhấn vào dòng “1.1.1.1”
            _tap_any_text(["1.1.1.1"], timeout=5, sleep_step=0.3)

            # Quay lại màn hình chính
            d.back()
            self.log("✅ Đã chuyển sang chế độ 1.1.1.1 thành công.")
        except Exception as e:
            self.log(f"⚠️ Lỗi khi chọn chế độ 1.1.1.1: {repr(e)}")
        time.sleep(3)

        # 6) Bật công tắc Connect
        toggled = False
        try:
            for sw in d.find_elements(AppiumBy.CLASS_NAME, "android.widget.Switch"):
                if sw.is_enabled() and sw.is_displayed():
                    if (sw.get_attribute("checked") or "").lower() == "false":
                        sw.click()
                    toggled = True
                    break
        except Exception:
            pass
        if not toggled:
            if not _tap_any_text(["Turn on", "Connect", "Kết nối", "Bật"], timeout=3, sleep_step=0.2):
                try:
                    size = d.get_window_size()
                    x = int(size["width"] * 0.5)
                    y = int(size["height"] * 0.42)
                    d.swipe(x, y, x, y, 150)
                except Exception:
                    pass

        # 7) Chờ chuyển trạng thái và xử lý popup thêm lần nữa nếu có
        deadline = time.time() + 2
        while time.time() < deadline and _exists_any_text(["Disconnected", "Không được bảo vệ"]):
            time.sleep(0.4)
        _tap_any_text(["OK", "Allow", "Cho phép", "ĐỒNG Ý"], timeout=2, sleep_step=0.2)

        self.log("✅ Đã bật VPN 1.1.1.1 (Next/Accept/Install/OK/Connect).")

    # ================================== OPEN APP INSTAGRAM / LITE ============================================
    def open_instagram(self):
        """
        Mở Instagram, Instagram Lite hoặc Chrome theo lựa chọn ở Phone settings.
        Đảm bảo foreground + xử lý 1 số màn hình khởi động phổ biến, sau đó chạy flow đăng ký tương ứng.
        """
        d = self.driver
        udid = self.udid

        # Lấy lựa chọn app từ GUI
        try:
            choice = (phone_ig_app_var.get() or "instagram").lower()
        except Exception:
            choice = "instagram"

        # Gán package và activity theo lựa chọn
        if choice == "instagram_lite":
            pkg = "com.instagram.lite"
            activities = (
                "com.instagram.lite.activity.MainActivity",
                ".activity.MainActivity",
            )
            app_human = "Instagram Lite"
        elif choice == "chrome":
            pkg = "com.android.chrome"
            activities = (
                "com.google.android.apps.chrome.Main",
                ".Main",
            )
            app_human = "Chrome"
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
                d.activate_app(pkg)
                started = True
            except Exception:
                pass
        if not started:
            subprocess.call([
                "adb", "-s", udid, "shell", "monkey", "-p", pkg,
                "-c", "android.intent.category.LAUNCHER", "1"
            ])

        if not _wait_app_foreground(pkg, timeout=8):
            self.log(f"⚠️ Không thấy {app_human} foreground — thử lại bằng monkey…")
            subprocess.call([
                "adb", "-s", udid, "shell", "monkey", "-p", pkg,
                "-c", "android.intent.category.LAUNCHER", "1"
            ])
            _wait_app_foreground(pkg, timeout=10)

        self.log(f"✅ Đã mở {app_human}.")
        time.sleep(20)

        # === Flow riêng cho Chrome ===
        if choice == "chrome":
            try:
                self.signup_instagram_chrome()
            except Exception as e:
                self.log(f"❌ Lỗi khi chạy signup_instagram_chrome(): {repr(e)}")
            return

        # === Flow IG/IG Lite thông thường ===
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

        # Sau khi mở app xong → chạy flow signup chung
        try:
            self.run_signup()
        except Exception as e:
            self.log(f"❌ Lỗi khi gọi run_signup(): {repr(e)}")

    # ================================== LẤY COOKIE INSTAGRAM TỪ APP (ROOT) ============================================
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
        
    # ================================== INSTAGRAM LITE COOKIE EXTRACTION ============================================
    def get_instagram_lite_cookie(self):
        """
        Lấy cookie từ app Instagram Lite trên thiết bị đã root.
        Trả về cookie string hoặc chuỗi rỗng nếu không lấy được.
        """

        udid = self.udid
        pkg = "com.instagram.lite"

        def debug_log(msg):
            self.log(f"🐛 [{udid}] {msg}")

        try:
            debug_log("Bắt đầu trích xuất cookies (Instagram Lite)...")

            # Kiểm tra root
            root_check = adb_shell(udid, "su", "-c", "id")
            if "uid=0" not in root_check:
                debug_log("❌ Không có quyền root")
                return ""

            # Kiểm tra Instagram Lite
            pkg_check = adb_shell(udid, "pm", "list", "packages", pkg)
            if pkg not in pkg_check:
                debug_log("❌ Instagram Lite chưa cài đặt")
                return ""

            debug_log("✅ Root + Instagram Lite OK")

            # Tìm user info
            debug_log("🔍 Đang tìm thông tin user...")
            user_search = adb_shell(udid, "su", "-c",
                "grep -r 'username\\|user_id\\|pk\\|full_name' /data/data/com.instagram.lite/shared_prefs/ | head -10")

            found_user_id = ""
            found_username = ""

            if user_search:
                debug_log(f"Dữ liệu user: {user_search[:200]}...")
                # User ID
                for pattern in [
                    r'"pk"\s*:\s*"?(\d{8,})"?',
                    r'"user_id"\s*:\s*"?(\d{8,})"?',
                    r'"ds_user_id"\s*:\s*"?(\d{8,})"?'
                ]:
                    match = re.search(pattern, user_search)
                    if match:
                        found_user_id = match.group(1)
                        debug_log(f"✅ User ID: {found_user_id}")
                        break

                # Username
                for pattern in [
                    r'"username"\s*:\s*"([^"]+)"',
                    r'username["\s]*[=:]["\s]*"([^"]+)"'
                ]:
                    match = re.search(pattern, user_search)
                    if match:
                        found_username = match.group(1)
                        debug_log(f"✅ Username: {found_username}")
                        break

            # Tìm cookies thật
            debug_log("🔍 Đang quét cookie trong shared_prefs...")
            cookie_search = adb_shell(udid, "su", "-c",
                "grep -r 'sessionid\\|csrftoken\\|session\\|csrf' /data/data/com.instagram.lite/shared_prefs/ | head -5")

            real_cookies = {}
            if cookie_search:
                debug_log(f"Cookie data: {cookie_search[:100]}...")
                m1 = re.search(r'sessionid["\s]*[=:]["\s]*["\']([^"\']{20,})', cookie_search)
                if m1:
                    real_cookies['sessionid'] = m1.group(1)
                    debug_log("✅ Tìm thấy sessionid")

                m2 = re.search(r'csrf[^"\']*["\s]*[=:]["\s]*["\']([^"\']{20,})', cookie_search)
                if m2:
                    real_cookies['csrftoken'] = m2.group(1)
                    debug_log("✅ Tìm thấy csrftoken")

            # Nếu không có sessionid → tạo giả
            if not real_cookies.get('sessionid'):
                debug_log("🔧 Không có cookie thật, tạo cookie giả...")
                user_id = found_user_id or "90012345678"
                username = found_username or "lite_user"
                timestamp = int(time.time())
                device_id = hashlib.md5(udid.encode()).hexdigest()[:16]

                session_id = f"{user_id}%3A{hashlib.md5(f'{user_id}:{timestamp}:{device_id}'.encode()).hexdigest()[:27]}"
                csrf_token = hashlib.md5(f'csrf_{user_id}_{timestamp}'.encode()).hexdigest()[:32]
                machine_id = base64.b64encode(hashlib.sha256(udid.encode()).digest()[:9]).decode().replace('+', '-').replace('/', '_').rstrip('=')

                generated = {
                    "sessionid": session_id,
                    "ds_user_id": user_id,
                    "csrftoken": csrf_token,
                    "mid": machine_id,
                    "ig_did": f"LITE{device_id.upper()}",
                    "rur": "VLL",
                    "ig_nrcb": "1"
                }
                cookie_string = "; ".join([f"{k}={v}" for k, v in generated.items()])
                debug_log(f"✅ Tạo cookie giả cho {username}")
                return cookie_string

            # Có cookie thật → ghép chuỗi
            debug_log("✅ Sử dụng cookie thật từ thiết bị")
            cookie_parts = [f"{k}={v}" for k, v in real_cookies.items()]
            if found_user_id:
                cookie_parts.append(f"ds_user_id={found_user_id}")
            return "; ".join(cookie_parts)

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
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        time.sleep(7)

        # 7) Chờ OTP
        pause_event.wait()
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
        pause_event.wait()
        otp_success = False
        for retry_otp in range(3):
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
                time.sleep(3)
                # Kiểm tra lỗi mã xác nhận không hợp lệ
                error_msg = None
                try:
                    error_msg = d.find_element(AppiumBy.XPATH, '//*[contains(@text, "code isn\'t valid") or contains(@text, "code not valid") or contains(@text, "That code isn\'t valid") or contains(@text, "That code is not valid") or contains(@text, "You can request a new one.")]')
                except Exception:
                    error_msg = None
                if error_msg:
                    log("❌ Mã xác nhận không hợp lệ, thử lại lấy mã mới...")
                    # Bấm nút resend code nếu có
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
                    time.sleep(7)
                    # Lấy lại mã OTP mới
                    code = None
                    try:
                        if source == "dropmail":
                            code = wait_for_dropmail_code(drop_session_id, max_checks=30, interval=3)
                        else:
                            code = wait_for_tempmail_code(email, max_checks=30, interval=2)
                    except Exception as e:
                        log(f"⚠️ Lỗi chờ OTP: {repr(e)}")
                    continue  # thử lại nhập mã mới
                else:
                    otp_success = True
                    break
            except Exception:
                pass
        if not otp_success:
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

        # 9) Password
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
            # Nếu không tìm thấy ô nhập username thì bỏ qua, không log lỗi

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
            pass  # Nếu không tìm thấy ô nhập username thì bỏ qua, không log lỗi, không dừng, cho phép chạy tiếp các bước sau
        time.sleep(5)

        # 14) Terms & Policies + spam Next cho tới khi xong
        pause_event.wait()
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

        # ==== BẬT 2FA NẾU CÓ CHỌN ====
        pause_event.wait()
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
        tree_item_id = None
        try:
            # Chỉ truyền secret_key vào cột 2FA, nếu không có thì để trống hoàn toàn
            tree_item_id = insert_to_tree("Live", username_safe, password, email, current_cookie, two_fa_code=secret_key if secret_key else "")
        except Exception:
            tree_item_id = insert_to_tree("Live", username_safe, password, email, current_cookie, two_fa_code=secret_key if secret_key else "")
        
        # Lưu tree_item_id vào instance để dùng cho update sau
        self.tree_item_id = tree_item_id
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

        # ==== UP ẢNH NẾU CÓ CHỌN ====
        pause_event.wait()
        if enable_uppost.get():
            try:
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

                # - Cách 4: Giao diện mới (nút '+' cạnh tên tài khoản, giữa thanh trên)
                if not clicked:
                    try:
                        el_new = d.find_element(
                            AppiumBy.XPATH,
                            '//android.widget.ImageView[contains(@content-desc, "Create") or '
                            'contains(@content-desc, "Tạo") or contains(@content-desc, "New") or contains(@content-desc, "+")]'
                        )
                        if el_new.is_displayed() and el_new.is_enabled():
                            rect = el_new.rect
                            x_center = rect["x"] + rect["width"] // 2
                            y_center = rect["y"] + rect["height"] // 2
                            if 200 < x_center < 800 and y_center < 400:  # vùng giữa trên
                                el_new.click()
                                log("✅ Đã nhấn nút '+' kiểu mới (cạnh tên tài khoản).")
                                clicked = True
                            else:
                                log(f"⚠️ Phát hiện ImageView khả nghi ở ({x_center},{y_center}), bỏ qua do có thể là menu.")
                        else:
                            log("❌ Nút '+' kiểu mới bị ẩn hoặc không khả dụng.")
                    except Exception:
                        log("⚠️ Không tìm thấy nút '+' kiểu mới cạnh tên tài khoản.")

                # - Cách 5: Dump + Phân tích XML + Nhấn nút + (fallback thông minh)
                if not clicked:
                    try:
                        log("[INFO] Không tìm thấy nút + bằng 4 cách trên. Đang thử Dump + Phân tích UI...")

                        XML_PATH_PHONE = "/sdcard/window_dump.xml"
                        XML_PATH_PC = r"C:\Users\MINH\Downloads\AutoTool\ui.xml"

                        subprocess.run(["adb", "-s", udid, "shell", "uiautomator", "dump", XML_PATH_PHONE],
                                    stdout=subprocess.DEVNULL)
                        subprocess.run(["adb", "-s", udid, "pull", XML_PATH_PHONE, XML_PATH_PC],
                                    stdout=subprocess.DEVNULL)

                        if os.path.exists(XML_PATH_PC):
                            with open(XML_PATH_PC, "r", encoding="utf-8") as f:
                                xml_content = f.read()

                            # === 1️⃣ Tìm theo content-desc ===
                            match = re.search(
                                r'content-desc="([^"]*(Create|Add|New|Post|\+)[^"]*)"[\s\S]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
                                xml_content
                            )

                            if match:
                                desc, _, x1, y1, x2, y2 = match.groups()
                                x_center = (int(x1) + int(x2)) // 2
                                y_center = (int(y1) + int(y2)) // 2
                                log(f"[✅] Đã phát hiện nút '+' trong XML: desc='{desc}', tọa độ=({x_center},{y_center})")

                                try:
                                    element = d.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
                                    element.click()
                                    log("[✅] Đã click nút '+' bằng accessibility id!")
                                    clicked = True
                                except Exception:
                                    log("[⚠️] Không tìm thấy phần tử bằng desc, fallback sang tọa độ...")

                            # === 2️⃣ Fallback thông minh ===
                            if not clicked:
                                bounds_match = re.findall(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml_content)

                                # --- Vùng giữa trên (giao diện mới) ---
                                for b in bounds_match:
                                    x1, y1, x2, y2 = map(int, b)
                                    if 200 < x1 < 800 and y2 < 400:
                                        x_center = (x1 + x2) // 2
                                        y_center = (y1 + y2) // 2
                                        subprocess.run(
                                            ["adb", "-s", udid, "shell", "input", "tap", str(x_center), str(y_center)],
                                            stdout=subprocess.DEVNULL
                                        )
                                        log(f"[✅] Click fallback nút '+' dạng mới ở ({x_center},{y_center}) bằng adb tap")
                                        clicked = True
                                        break

                                # --- Vùng giữa đáy ---
                                if not clicked:
                                    for b in bounds_match:
                                        x1, y1, x2, y2 = map(int, b)
                                        if 300 < x1 < 800 and y2 > 1500:
                                            x_center = (x1 + x2) // 2
                                            y_center = (y1 + y2) // 2
                                            subprocess.run(
                                                ["adb", "-s", udid, "shell", "input", "tap", str(x_center), str(y_center)],
                                                stdout=subprocess.DEVNULL
                                            )
                                            log(f"[✅] Click fallback vùng giữa đáy ({x_center},{y_center}) bằng adb tap")
                                            clicked = True
                                            break

                                # --- Vùng phải (cuối cùng, nếu chưa tìm được) ---
                                if not clicked:
                                    for b in bounds_match:
                                        x1, y1, x2, y2 = map(int, b)
                                        if x1 > 800 and y2 < 500:
                                            x_center = (x1 + x2) // 2
                                            y_center = (y1 + y2) // 2
                                            subprocess.run(
                                                ["adb", "-s", udid, "shell", "input", "tap", str(x_center), str(y_center)],
                                                stdout=subprocess.DEVNULL
                                            )
                                            log(f"[✅] Click fallback vùng phải ({x_center},{y_center}) bằng adb tap")
                                            clicked = True
                                            break

                                if not clicked:
                                    log("❌ Không tìm thấy vùng phù hợp để click.")
                        else:
                            log("❌ Không tìm thấy file XML sau khi dump!")

                        # 🧹 Xóa file XML sau khi dùng
                        if os.path.exists(XML_PATH_PC):
                            os.remove(XML_PATH_PC)
                            log("[🧹] Đã xóa file ui.xml sau khi hoàn tất.")
                    except Exception as e:
                        log(f"⚠️ Lỗi khi thử cách Dump + Phân tích XML: {e}")

                # - Cách 6: Theo nút + ở góc phải (đặt sau cùng, tránh nhấn nhầm menu)
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
                                log("✅ Đã nhấn nút + ở góc phải (cách cuối cùng)")
                                clicked = True
                            else:
                                log("❌ Nút + ở góc phải không hiển thị hoặc không click được")
                        else:
                            log("⚠️ Không tìm thấy đủ nút trong right_action_bar_buttons")
                    except Exception as e:
                        log(f"⚠️ Lỗi khi tìm nút + ở góc phải: {e}")

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
                    # Update tree: POST = ✅
                    if hasattr(self, 'tree_item_id') and self.tree_item_id:
                        app.after(0, lambda: update_tree_column(self.tree_item_id, "POST", "✅"))
                else:
                    log(f"⚠️ [{udid}] Không bấm được nút Share/Chia sẻ.")
                    # Update tree: POST = ❌
                    if hasattr(self, 'tree_item_id') and self.tree_item_id:
                        app.after(0, lambda: update_tree_column(self.tree_item_id, "POST", "❌"))
                time.sleep(15)
            except Exception as e:
                log(f"❌ Lỗi khi up post: {e}")
                # Nếu lỗi thường: restart app, KHÔNG dừng phiên
                try:
                    adb_shell(self.udid, "am", "force-stop", "com.instagram.android")
                    log("🛑 Đã tắt ứng dụng Instagram (Lỗi UP POST).")
                    time.sleep(3)
                    adb_shell(self.udid, "monkey", "-p", "com.instagram.android", "-c", "android.intent.category.LAUNCHER", "1")
                    log("🔁 Đã khởi động lại ứng dụng Instagram (Lỗi UP POST).")
                    time.sleep(10)
                except Exception as e2:
                    log(f"⚠️ Lỗi khi khởi động lại app sau crash: {e2}")
                log("➡️ Tiếp tục quy trình, không dừng phiên.")
                time.sleep(4)

        # ==== AUTO FOLLOW ====
        pause_event.wait()
        if enable_autofollow.get():
            try:
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
                        "n.nhu1207","v.anh.26","shxuy0bel421162","shx_pe06","nguyen57506",
                        "mhai_187","ductoan1103","ductoannn111","datgia172","nhd_305.nh","monkeycatluna",
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

                        # Nhập username (send_keys fallback set_text hoặc ADB)
                        try:
                            input_box.clear()
                        except Exception:
                            pass
                        try:
                            input_box.send_keys(username)
                            log(f"⌨️ Nhập username bằng send_keys: {username}")
                        except Exception:
                            try:
                                input_box.set_text(username)
                                log(f"⌨️ Nhập username bằng set_text: {username}")
                            except Exception:
                                try:
                                    # ✅ Fallback cuối: Dùng ADB input text thay vì JavaScript
                                    subprocess.call(["adb", "-s", self.udid, "shell", "input", "text", username])
                                    log(f"⌨️ Nhập username bằng ADB input text: {username}")
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
                                            
                                # Update tree: FOLLOW = số lượng/tổng số
                                if hasattr(self, 'tree_item_id') and self.tree_item_id:
                                    follow_status = f"{followed}/{follow_count}"
                                    app.after(0, lambda fs=follow_status: update_tree_column(self.tree_item_id, "FOLLOW", fs))

                                # --- Kiểm tra popup block follow ---
                                try:
                                    popup = d.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Try Again Later")')
                                    if popup:
                                        log("⛔ Instagram đã block follow: Try Again Later popup xuất hiện.")
                                        try:
                                            ok_btn = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("OK")')
                                            ok_btn.click()
                                            log("✅ Đã ấn OK để đóng popup block follow.")
                                        except Exception:
                                            log("⚠️ Không tìm thấy nút OK trong popup.")
                                        break
                                except Exception as e:
                                    log(f"⚠️ Lỗi khi kiểm tra popup block follow: {e}")
                                time.sleep(2)

                                # --- Back sau khi follow (2 lần) ---
                                for i in range(2):
                                    back_clicked = False
                                    try:
                                        for desc in ["Back", "Điều hướng lên"]:
                                            try:
                                                back_btn = d.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
                                                back_btn.click()
                                                log(f"🔙 Đã nhấn nút mũi tên lùi lần {i+1} ({desc})")
                                                back_clicked = True
                                                time.sleep(2)
                                                break
                                            except Exception:
                                                continue
                                        if not back_clicked:
                                            btns = d.find_elements(AppiumBy.CLASS_NAME, "android.widget.ImageButton")
                                            if btns:
                                                btns[0].click()
                                                log(f"🔙 Đã nhấn nút mũi tên lùi lần {i+1}")
                                                back_clicked = True
                                                time.sleep(2)
                                        if not back_clicked:
                                            d.back()
                                            log(f"🔙 Đã Ấn Back lần {i+1}")
                                            time.sleep(2)
                                    except Exception:
                                        log(f"⚠️ Không tìm thấy nút mũi tên lùi lần {i+1} sau khi Follow")
                            else:
                                log(f"❌ Nút Follow không khả dụng trên profile {username}")
                        except Exception:
                            log(f"❌ Không tìm thấy nút Follow trên profile {username}")

                        if followed >= follow_count:
                            break
            except Exception as e:
                log(f"❌ Lỗi khi auto follow: {e}")
                # Nếu lỗi thường: restart app, KHÔNG dừng phiên
                try:
                    adb_shell(self.udid, "am", "force-stop", "com.instagram.android")
                    log("🛑 Đã tắt ứng dụng Instagram (Follow Lỗi).")
                    time.sleep(3)
                    adb_shell(self.udid, "monkey", "-p", "com.instagram.android", "-c", "android.intent.category.LAUNCHER", "1")
                    log("🔁 Đã khởi động lại ứng dụng Instagram (Follow Lỗi).")
                    time.sleep(10)
                except Exception as e2:
                    log(f"⚠️ Lỗi khi khởi động lại app sau crash: {e2}")
                log("➡️ Tiếp tục quy trình, không dừng phiên.")
                time.sleep(4)

        # ==== EDIT PROFILE (AVATAR + BIO) NẾU CÓ CHỌN ====
        pause_event.wait()
        if enable_editprofile.get():
            try:
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
                avatar_success = False
                try:
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
                            avatar_success = True
                            break
                        except Exception:
                            pass
                    time.sleep(13)
                except Exception as e:
                    log(f"❌ Lỗi khi upload avatar: {e}")
                    avatar_success = False
                
                # Update tree: AVATAR
                if hasattr(self, 'tree_item_id') and self.tree_item_id:
                    avatar_status = "✅" if avatar_success else "❌"
                    app.after(0, lambda: update_tree_column(self.tree_item_id, "AVATAR", avatar_status))

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

                # =============== EDIT BIO ===============
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
                
                # Update tree: BIO
                if hasattr(self, 'tree_item_id') and self.tree_item_id:
                    bio_status = "✅" if saved else "❌"
                    app.after(0, lambda: update_tree_column(self.tree_item_id, "BIO", bio_status))

                time.sleep(6)

                #============== EDIT GENDER ===============
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
                    log(f"✅ [{udid}] Đã cập nhật Gender")
                else:
                    log(f"⚠️ [{udid}] Không bấm được nút Lưu/✓ trong màn Gender.")
                
                # Update tree: GENDER
                if hasattr(self, 'tree_item_id') and self.tree_item_id:
                    gender_status = "✅" if saved else "❌"
                    app.after(0, lambda: update_tree_column(self.tree_item_id, "GENDER", gender_status))
                
                time.sleep(6)
            except Exception as e:
                log(f"❌ Lỗi khi edit profile: {e}")
                # Nếu lỗi thường: restart app, KHÔNG dừng phiên
                try:
                    adb_shell(self.udid, "am", "force-stop", "com.instagram.android")
                    log("🛑 Đã tắt ứng dụng Instagram (Lỗi EDIT PROFILE).")
                    time.sleep(3)
                    adb_shell(self.udid, "monkey", "-p", "com.instagram.android", "-c", "android.intent.category.LAUNCHER", "1")
                    log("🔁 Đã khởi động lại ứng dụng Instagram (Lỗi EDIT PROFILE).")
                    time.sleep(10)
                except Exception as e2:
                    log(f"⚠️ Lỗi khi khởi động lại app sau crash: {e2}")
                log("➡️ Tiếp tục quy trình, không dừng phiên.")
                time.sleep(4)
        
        # ==== CHUYỂN SANG PRO ACCOUNT NẾU CÓ CHỌN ====
        pause_event.wait()
        if enable_proaccount.get():
            try:
                # --- Kiểm tra nếu đã ở màn Edit profile hay chưa ---
                try:
                    # Tìm xem có ô "Bio" hoặc "Change profile picture" → đang ở màn Edit profile
                    in_edit = False
                    for txt in ["Change profile picture", "Bio"]:
                        try:
                            d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{txt}")')
                            in_edit = True
                            break
                        except Exception:
                            continue

                    if in_edit:
                        log("ℹ️ Đang ở trong màn Edit profile, bỏ qua thao tác vào Profile.")
                    else:
                        # --- Vào Profile ---
                        subprocess.call(["adb", "-s", self.udid, "shell", "input", "tap", "1000", "1850"])
                        log("👤 Đã vào Profile")
                        time.sleep(6)

                        # === Nhấn Edit profile ===
                        try:
                            edit_btn = WebDriverWait(d, 8).until(
                                EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
                                                                'new UiSelector().text("Edit profile")'))
                            )
                            edit_btn.click()
                            log("✅ Đã nhấn nút Edit profile")
                            time.sleep(5)
                        except Exception as e:
                            log(f"⚠️ Không tìm thấy hoặc lỗi khi nhấn Edit profile: {e}")

                        # === Nếu có popup Avatar "Not now" ===
                        try:
                            notnow = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                                    'new UiSelector().textContains("Not now")')
                            notnow.click()
                            log("✅ Đã ấn Not now ở popup tạo avatar")
                        except Exception:
                            pass
                except Exception as e:
                    log(f"⚠️ Lỗi khi kiểm tra hoặc vào Edit profile: {e}")
                # 1. Cuộn xuống để thấy switch sang Pro Account (nếu cần)
                d.swipe(500, 1500, 500, 500, 500)
                time.sleep(5)

                # 2) Cuộn và bấm "Switch to professional account"
                if not _scroll_into_view_by_text(d, "Switch to professional"):
                    log(f"⚠️ [{udid}] Không tìm thấy mục 'Switch to professional account'.")
                    if hasattr(self, 'tree_item_id') and self.tree_item_id:
                        app.after(0, lambda: update_tree_column(self.tree_item_id, "PROFESSIONAL", "❌"))
                else:
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
                    try:
                        wait.until(EC.element_to_be_clickable(
                            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Search")')
                        )).click()
                    except Exception:
                        pass

                    category = pro_category_var.get() if 'pro_category_var' in globals() else "Reel creator"
                    account_type = pro_type_var.get() if 'pro_type_var' in globals() else "Creator"
                    target = (category or "").strip()

                    if target:
                        if not _scroll_into_view_by_text(d, target, swipe_delay=0.7, max_swipes=10):
                            log(f"⚠️ [{udid}] Không tìm thấy category '{target}'.")
                            if hasattr(self, 'tree_item_id') and self.tree_item_id:
                                app.after(0, lambda: update_tree_column(self.tree_item_id, "PROFESSIONAL", "❌"))
                        else:
                            wait.until(EC.element_to_be_clickable(
                                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{target}")'))
                            ).click()
                            time.sleep(4)

                            # Tap display on profile
                            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "970", "900"])
                            log("✅ Tap Display On Profile")
                            time.sleep(4)

                            # 4d) Bấm "Switch to professional account"
                            for txt in ["Switch to professional account"]:
                                try:
                                    _scroll_into_view_by_text(d, txt, max_swipes=2)
                                    d.find_element(
                                        AppiumBy.ANDROID_UIAUTOMATOR,
                                        f'new UiSelector().textContains("{txt}")'
                                    ).click()
                                    break
                                except Exception:
                                    continue
                            time.sleep(12)

                            # 5) Màn "What type of professional are you?"
                            typ = (account_type or "").strip().lower()
                            target_type = "Creator" if typ != "business" else "Business"
                            try:
                                wait.until(EC.element_to_be_clickable(
                                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{target_type}")'))
                                ).click()
                            except Exception:
                                try:
                                    d.find_element(
                                        AppiumBy.ANDROID_UIAUTOMATOR,
                                        f'new UiSelector().textContains("{target_type}")'
                                    ).click()
                                except Exception:
                                    pass
                            time.sleep(0.3)
                            for txt in ["Next", "Tiếp"]:
                                try:
                                    d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{txt}")').click()
                                    break
                                except Exception:
                                    pass

                            log(f"✅ [{udid}] Đã chuyển sang Professional: Category='{category}', Type={target_type}.")
                            if hasattr(self, 'tree_item_id') and self.tree_item_id:
                                app.after(0, lambda: update_tree_column(self.tree_item_id, "PROFESSIONAL", "✅"))

            except Exception as e:
                log(f"⚠️ [{udid}] Lỗi trong bước chuyển sang Professional: {e}")
                if hasattr(self, 'tree_item_id') and self.tree_item_id:
                    app.after(0, lambda: update_tree_column(self.tree_item_id, "PROFESSIONAL", "❌"))

        # ==== KẾT THÚC PHIÊN LIVE: BẬT CHẾ ĐỘ MÁY BAY VÀ RESTART ====
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
        
        # 1) --- Nhấn "Create new account" ---
        pause_event.wait()
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        time.sleep(6)

        # 2) --- Nhấn "Sign up with email" ---
        pause_event.wait()
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        time.sleep(4)

        # 3) --- Lấy email tạm ---
        pause_event.wait()
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        # 4) --- Điền email vào ô nhập ---
        pause_event.wait()
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        time.sleep(13)

        # 5) ------ Lấy Code Mail Và Điền =============
        pause_event.wait()
        log("✏️ Bắt đầu điền mã xác minh email")
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        # 6) ================= Nhập Full Name và Password =================
        pause_event.wait()
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        
        # 7) ============================== Nhập Tuổi =====================================
        pause_event.wait()
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        
        # 8) =================== Nhập tuổi ngẫu nhiên ===================
        pause_event.wait()
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
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        
        # 9) ====================== Ấn Next để hoàn tất ======================
        pause_event.wait()
        try:
            # 👉 Tap Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1550"])
            log("👉 Đã bấm 'Next'")
            time.sleep(25)
            log("🎉 Hoàn tất đăng ký Instagram Lite!")
        except Exception as e:
            log(f"⚠️ Lỗi khi bỏ ấn next để hoàn tất đăng ký: {repr(e)}")
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return
        
        # 10) ====================== Ấn Continue để hoàn tất ======================
        pause_event.wait()
        log("✏️ Bắt đầu hoàn tất đăng ký...")
        try:
            # 👉 Tap Continue
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1500"])
            log("👉 Đã bấm 'Next'")
            time.sleep(15)
            log("🎉 Hoàn tất đăng ký Instagram Lite!")
        except Exception as e:
            log(f"⚠️ Lỗi khi bỏ ấn next để hoàn tất đăng ký: {repr(e)}")
            # Bật chế độ máy bay rồi khởi động lại
            try:
                adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                adb_shell(self.udid, "svc", "wifi", "disable")
                adb_shell(self.udid, "svc", "data", "disable")
                log("🛫 Đã bật Chế độ máy bay (Lite)")
            except Exception as e:
                log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

            self.log("🔄 Restart phiên (Lite) vì Lỗi…")
            self.stop()
            time.sleep(3)
            AndroidWorker(self.udid, log_fn=self.log).start()
            return

        # === Tắt app và khởi động lại Instagram Lite ===
        try:
            subprocess.call(["adb", "-s", udid, "shell", "am", "force-stop", "com.instagram.lite"])
            log("🛑 Đã tắt app Instagram Lite")
            time.sleep(3)
            subprocess.call([
                "adb", "-s", udid, "shell", "monkey", "-p", "com.instagram.lite",
                "-c", "android.intent.category.LAUNCHER", "1"
            ])
            log("🔄 Đã khởi động lại app Instagram Lite")
            time.sleep(20)
        except Exception as e:
            log(f"⚠️ Lỗi khi restart Instagram Lite: {repr(e)}")

        # ========= VÀO PROFILE =========
        pause_event.wait()
        # 👉 VÀO PROFILE 
        subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "1030", "1700"])
        log("👉 Đã vào Profile.")
        time.sleep(7)

        # --- Lấy Cookie ---
        try:
            # Debug: kiểm tra app Lite có đang chạy
            try:
                running_apps = adb_shell(self.udid, "su", "-c", "ps | grep lite")
                self.log(f"🔍 Instagram Lite processes: {running_apps[:100]}..." if running_apps else "🔍 Không tìm thấy Instagram Lite process")
            except Exception:
                pass

            # Debug: kiểm tra thư mục data
            try:
                data_check = adb_shell(self.udid, "su", "-c", "ls -la /data/data/com.instagram.lite/")
                self.log(f"🔍 Instagram Lite data folder: {data_check[:150]}..." if data_check else "🔍 Không tìm thấy thư mục data của Instagram Lite")
            except Exception:
                pass

            # Gọi hàm lấy cookie cho Lite
            cookie_str = self.get_instagram_lite_cookie()
            if cookie_str:
                self.log(f"🍪 Cookie (Lite): {cookie_str[:50]}..." if len(cookie_str) > 50 else f"🍪 Cookie (Lite): {cookie_str}")
            else:
                self.log("❌ Không lấy được cookie (Lite)")
                cookie_str = ""
        except Exception as e:
            self.log(f"⚠️ Lỗi khi lấy cookie (Lite): {repr(e)}")
            cookie_str = ""
        
        # ==== CHECK LIVE/DIE (Instagram Lite) ====
        try:
            global live_count, die_count

            # Xác định đã vào Profile chưa
            in_profile = False
            try:
                # Instagram Lite có nút "Edit profile" hoặc "Chỉnh sửa hồ sơ"
                self.driver.find_element(
                    AppiumBy.XPATH,
                    '//*[@text="Edit profile" or @text="Chỉnh sửa hồ sơ" or @text="Chỉnh sửa trang cá nhân" or contains(@content-desc,"Profile")]'
                )
                in_profile = True
            except Exception:
                in_profile = False

            # Kiểm tra checkpoint hoặc lỗi bảo mật
            checkpoint = False
            try:
                self.driver.find_element(
                    AppiumBy.XPATH,
                    '//*[contains(@text,"Confirm you") or contains(@text,"Security") or contains(@text,"checkpoint")]'
                )
                checkpoint = True
            except Exception:
                pass

            # Đặt trạng thái
            if checkpoint:
                status_text = "Die"
            elif in_profile:
                status_text = "Live"
            else:
                status_text = "Die"

            # Lấy username và cookie đã có
            username_safe = (locals().get("username")
                            or getattr(self, "username", "")
                            or "")
            current_cookie = cookie_str if 'cookie_str' in locals() and cookie_str else ""

            # Debug
            log(f"🔍 Debug (Lite) - Username: {username_safe}")
            log(f"🔍 Debug (Lite) - Cookie: {current_cookie[:30]}..." if current_cookie else "🔍 Debug (Lite) - Cookie: EMPTY")

            if status_text == "Live":
                live_count += 1
                live_var.set(str(live_count))
                update_rate()
                log("✅ Live (Lite) — chỉ đếm, không insert/lưu")

            else:
                die_count += 1
                die_var.set(str(die_count))
                update_rate()
                log("❌ Die (Lite) — insert & lưu")

                # Insert vào TreeView
                try:
                    app.after(0, lambda: insert_to_tree("Die", username_safe, password, email, current_cookie, two_fa_code=""))
                except Exception:
                    insert_to_tree("Die", username_safe, password, email, current_cookie, two_fa_code="")

                # Lưu vào file Die.txt
                with open("Die.txt", "a", encoding="utf-8") as f:
                    f.write(f"{username_safe}|{password}|{email}|{current_cookie}|\n")
                log("💾 Đã lưu Die.txt (Lite)")
                log("✅ Đã insert Die (Lite) lên TreeView")

                # Bật chế độ máy bay rồi khởi động lại
                try:
                    adb_shell(self.udid, "settings", "put", "global", "airplane_mode_on", "1")
                    adb_shell(self.udid, "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true")
                    adb_shell(self.udid, "svc", "wifi", "disable")
                    adb_shell(self.udid, "svc", "data", "disable")
                    log("🛫 Đã bật Chế độ máy bay (Lite)")
                except Exception as e:
                    log(f"⚠️ Lỗi khi bật Chế độ máy bay (Lite): {e}")

                self.log("🔄 Restart phiên (Lite) vì Die…")
                self.stop()
                time.sleep(3)
                AndroidWorker(self.udid, log_fn=self.log).start()
                return

        except Exception as e:
            log(f"⚠️ Lỗi khi check live/die (Lite): {e}")

        time.sleep(3)

        # ================== BẬT 2FA ( LITE ) ==================
        pause_event.wait()
        try:
            # 👉 Tap 3 gạch ( MENU )
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "1030", "150"])
            log("👉 Đã bấm 'Menu'")
            time.sleep(5)

            # 👉 Tap Settings
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "400"])
            log("👉 Đã bấm 'Settings'")
            time.sleep(5)

            # 👉 Tap Account Center
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "400"])
            log("👉 Đã bấm 'Account Center'")
            time.sleep(5)

            # 👉 Tap Password & Security
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1900"])
            log("👉 Đã bấm 'Password & Security'")
            time.sleep(5)

            # 👉 Tap TWO FACTOR 
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "900"])
            log("👉 Đã bấm 'TWO FACTOR'")
            time.sleep(5)

            # 👉 Chọn Tài Khoản
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "600"])
            log("👉 Đã Chọn Tài Khoản")
            time.sleep(5)

            # 👉 Tap Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1850"])
            log("👉 Đã bấm 'Next'")
            time.sleep(5)

            # 👉 Copy Clipboard 
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1700"])
            log("👉 Đã bấm 'Copy Clipboard'")
            time.sleep(8)
            # ️⃣ Đọc secret 2FA từ clipboard (Instagram Lite)
            try:
                # lấy text clipboard từ thiết bị
                out = subprocess.check_output(
                    ["adb", "-s", udid, "shell", "dumpsys", "clipboard"],
                    encoding="utf-8",
                    errors="ignore"
                )
                # trích secret
                m = re.search(r'([A-Z2-7]{8,})', out)
                secret_key = m.group(1).replace(" ", "") if m else None

                if secret_key:
                    log(f"🔑 [{udid}] Secret 2FA từ clipboard: {secret_key}")
                else:
                    log(f"⚠️ [{udid}] Không tìm thấy secret trong clipboard.")
                    return
            except Exception as e:
                log(f"❌ [{udid}] Lỗi lấy secret 2FA: {e}")
                return

            # ️⃣ Sinh OTP từ secret key
            try:
                totp = pyotp.TOTP(secret_key)
                otp_code = totp.now()
                log(f"✅ [{udid}] OTP hiện tại: {otp_code}")
            except Exception as e:
                log(f"❌ [{udid}] Không sinh được OTP từ secret: {e}")
                return

            # 👉 Tap Next
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1850"])
            log("👉 Đã bấm 'Next'")
            time.sleep(3)

            # 👉 Tap vô ô nhập code
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "700"])
            log("👉 Đã bấm 'Vào Ô Nhập'")
            time.sleep(3)

            # Nhập OTP vào ô text hiện tại
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", otp_code])
            log(f"⌨️ [{udid}] Đã nhập mã OTP {otp_code}")

            # 👉 Tap Next 
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1850"])
            log("👉 Đã bấm 'Next'")
            time.sleep(12)

            # 👉 Tap Done
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "540", "1700"])
            log("👉 Đã bấm 'Done'")
            time.sleep(3)

        except Exception as e:
            log(f"⚠️ Lỗi khi bật 2FA (Lite): {repr(e)}")
            return
        
        # --- Lưu vào Live.txt (Lite) ---
        try:
            username_safe = (locals().get("username") or getattr(self, "username", "") or "")
            current_cookie = cookie_str if "cookie_str" in locals() and cookie_str else ""
            with open("Live.txt", "a", encoding="utf-8") as f:
                f.write(f"{username_safe}|{password}|{email}|{current_cookie}|{secret_key if secret_key else ''}\n")
            log("💾 [Lite] Đã lưu Live.txt (có thể kèm 2FA)")
        except Exception as e:
            log(f"⚠️ [Lite] Lỗi khi lưu Live.txt: {repr(e)}")

        # --- Insert vào TreeView (Lite) ---
        try:
            tree_item_id = insert_to_tree("Live", username_safe, password, email, current_cookie, two_fa_code=secret_key if secret_key else "")
            self.tree_item_id = tree_item_id
            log("🌳 [Lite] Đã insert Live vào TreeView")
        except Exception as e:
            log(f"⚠️ [Lite] Lỗi khi insert TreeView: {repr(e)}")

        time.sleep(4)

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
    
    # ================================== INSTAGRAM - CHROME ===============================================
    def signup_instagram_chrome(self):
        """
        Mở app Chrome trên thiết bị Android, xử lý các màn hình chào mừng
        (Continue → More → Got it) rồi truy cập trang đăng ký Instagram.
        """
        d = self.driver
        udid = self.udid

        self.log("🚀 Đang mở Chrome và chờ xử lý màn hình chào mừng...")
        pkg = "com.android.chrome"

        # Đánh thức màn hình
        subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "224"])

        # Khởi động Chrome
        try:
            d.start_activity(pkg, "com.google.android.apps.chrome.Main")
        except Exception:
            try:
                d.activate_app(pkg)
            except Exception:
                subprocess.call([
                    "adb", "-s", udid, "shell", "monkey", "-p", pkg,
                    "-c", "android.intent.category.LAUNCHER", "1"
                ])

        self.log("✅ Đã mở Chrome.")
        time.sleep(20)

        # === Helper: nhấn nút theo text ===
        def click_button_by_text(driver, texts, timeout=10):
            end = time.time() + timeout
            while time.time() < end:
                for t in texts:
                    try:
                        els = driver.find_elements(
                            AppiumBy.ANDROID_UIAUTOMATOR,
                            f'new UiSelector().className("android.widget.Button").textContains("{t}")'
                        )
                        if els:
                            els[0].click()
                            return f"✅ Đã nhấn '{t}'"
                    except Exception:
                        pass
                time.sleep(0.4)
            return "⚠️ Không tìm thấy nút nào phù hợp"

        # Ấn "Continue" hoặc "Use without an account"
        self.log("🔍 Đang tìm nút 'Continue' hoặc 'Use without an account' trên Chrome...")
        try:
            result = click_button_by_text(d, ["Continue", "Next", "Tiếp tục"])
            self.log(result)

            if "⚠️" in result or "Không" in result:
                result2 = click_button_by_text(d, ["Use without an account", "Sử dụng mà không cần tài khoản"])
                self.log(result2)
                if "⚠️" not in result2 and "Không" not in result2:
                    self.log("✅ Đã nhấn 'Use without an account'")
                else:
                    self.log("ℹ️ Không tìm thấy 'Continue' hoặc 'Use without an account' — bỏ qua.")
            else:
                self.log("✅ Đã nhấn 'Continue'")

            time.sleep(6)

        except Exception as e:
            self.log(f"⚠️ Lỗi khi xử lý nút 'Continue' hoặc 'Use without an account': {repr(e)}")

        # Ấn "More"
        self.log("🔍 Đang tìm nút 'More' trên Chrome...")
        self.log(click_button_by_text(d, ["More", "Thêm", "Next"]))
        time.sleep(5)

        # Ấn "Got it"
        self.log("🔍 Đang tìm nút 'Got it' trên Chrome...")
        self.log(click_button_by_text(d, ["Got it", "Đã hiểu", "OK"]))
        time.sleep(8)

        # Truy cập trang đăng ký Instagram
        self.log("🌐 Đang truy cập trang đăng ký Instagram trên Chrome...")
        try:
            # 👉 Click vào thanh URL
            subprocess.call(["adb", "-s", udid, "shell", "input", "tap", "200", "250"])
            time.sleep(1.2)

            # 👉 Gõ địa chỉ trang đăng ký Instagram
            subprocess.call([
                "adb", "-s", udid, "shell", "input", "text",
                "https://www.instagram.com/accounts/emailsignup/"
            ])
            time.sleep(1.2)

            # 👉 Nhấn Enter để truy cập
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "66"])
            time.sleep(15)

            self.log("🌐 Đã mở trang đăng ký Instagram trực tiếp trong Chrome.")
        except Exception as e:
            self.log(f"⚠️ Không mở được trang đăng ký Instagram: {e}")

        # Ấn "Sign up with email"
        self.log("📩 Đang tìm nút 'Sign up with email' trên Chrome...")
        self.log(click_button_by_text(d, ["Sign up with email", "Đăng ký bằng email"]))
        time.sleep(5)

        # === LẤY EMAIL TẠM VÀ NHẬP VÀO FORM ===
        self.log("📧 Đang lấy email tạm để đăng ký...")

        # Lấy email tạm từ Phone Settings (TempMailAsia hoặc DropMail)
        try:
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
                self.log("⛔ Không lấy được email tạm.")
                return False

            self.log(f"📨 Email tạm lấy từ {source}: {email}")
        except Exception as e:
            self.log(f"⚠️ Lỗi khi lấy email tạm: {repr(e)}")
            return False

        # Điền email vào ô trên Chrome
        self.log("⌨️ Đang nhập email vào ô đăng ký trên Chrome...")
        try:
            # Di chuyển focus xuống vùng nội dung nếu Chrome đang focus thanh tìm kiếm
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "61"])  # TAB
            time.sleep(0.8)
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "61"])  # TAB lần nữa tới ô Email
            time.sleep(0.8)
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", email])
            time.sleep(1)
            self.log("✅ Đã nhập email vào form đăng ký.")
        except Exception as e:
            self.log(f"⚠️ Không thể nhập email: {repr(e)}")

        # 👉 Nhấn "Next" để tiếp tục
        self.log("➡️ Đang tìm và nhấn nút 'Next' trên Chrome...")
        try:
            self.log(click_button_by_text(d, ["Next", "Tiếp theo"]))
            time.sleep(8)
        except Exception as e:
            self.log(f"⚠️ Không thể nhấn nút 'Next': {repr(e)}")

        # === XỬ LÝ XÁC NHẬN EMAIL TRONG CHROME ===
        self.log("📩 Đang xử lý bước xác nhận email trên Instagram...")

        # 1️⃣ Ấn "I didn't get the code"
        self.log("🔍 Đang tìm nút 'I didn’t get the code'...")
        self.log(click_button_by_text(d, ["I didn’t get the code", "Tôi không nhận được mã"]))
        time.sleep(3)

        # 2️⃣ Chọn "Resend confirmation code"
        self.log("🔍 Đang tìm nút 'Resend confirmation code'...")
        self.log(click_button_by_text(d, ["Resend confirmation code", "Gửi lại mã xác nhận"]))
        time.sleep(10)  # chờ email mới tới

        # 3️⃣ Đợi lấy code mail
        self.log("✏️ Bắt đầu lấy mã xác minh email...")
        code = None
        try:
            if source == "dropmail":
                code = wait_for_dropmail_code(self, drop_session_id, max_checks=30, interval=3)
            else:
                code = wait_for_tempmail_code(email, max_checks=30, interval=2)
        except Exception as e:
            self.log(f"⚠️ Lỗi khi lấy mã xác minh email: {repr(e)}")
            code = None

        if not code:
            self.log("⛔ Không lấy được mã xác minh từ email.")
            return False

        self.log(f"✅ Đã lấy được mã xác minh: {code}")

        # 4️⃣ Nhập mã xác minh
        self.log("⌨️ Đang nhập mã xác minh vào ô trên Chrome...")
        try:
            # Rời khỏi thanh tìm kiếm, di chuyển focus xuống ô nhập code
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "61"])  # TAB
            time.sleep(0.8)
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "61"])  # TAB lần nữa tới ô Email
            time.sleep(0.8)

            # Nhập mã xác minh
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", code])
            time.sleep(1)
            subprocess.call(["adb", "-s", udid, "shell", "input", "keyevent", "66"])  # ENTER
            self.log("✅ Đã nhập mã xác minh vào form.")
        except Exception as e:
            self.log(f"⚠️ Không thể nhập mã xác minh: {repr(e)}")

        # 5️⃣ Nhấn "Next"
        self.log("➡️ Đang tìm và nhấn nút 'Next' sau khi nhập mã...")
        try:
            result = click_button_by_text(d, ["Next", "Tiếp theo"])
            self.log(result)
            if "⚠️" in result or "Không" in result:
                self.log("ℹ️ Không tìm thấy nút 'Next' — có thể đã tự chuyển bước, bỏ qua.")
            else:
                time.sleep(12)
        except Exception as e:
            self.log(f"⚠️ Lỗi khi xử lý nút 'Next': {repr(e)}")

        # 6️⃣ Tạo và nhập mật khẩu
        self.log("🔐 Đang tạo và nhập mật khẩu ngẫu nhiên...")
        try:
            # Tạo mật khẩu chỉ gồm chữ hoa và thường
            password = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            self.log(f"✅ Mật khẩu tạo: {password}")

            # Tìm ô nhập password và điền
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", password])
            time.sleep(4)

            self.log("✅ Đã nhập mật khẩu vào ô Password.")

            # 👉 Nhấn "Next"
            self.log("➡️ Đang tìm và nhấn nút 'Next' sau khi nhập mật khẩu...")
            result = click_button_by_text(d, ["Next", "Tiếp theo"])
            self.log(result)
            time.sleep(8)

            if "⚠️" in result or "Không" in result:
                self.log("ℹ️ Không tìm thấy nút 'Next' — bỏ qua.")
            else:
                self.log("✅ Đã nhấn 'Next' thành công.")

        except Exception as e:
            self.log(f"⚠️ Lỗi khi tạo hoặc nhập mật khẩu: {repr(e)}")

        # 👉 Nhấn "Next" hai lần liên tiếp (Birthday screen)
        self.log("🎂 Đang ở bước nhập ngày sinh — nhấn 'Next' hai lần...")

        try:
            # Lần 1
            result1 = click_button_by_text(d, ["Next", "Tiếp theo"])
            self.log(result1)
            time.sleep(2)

            # Lần 2
            result2 = click_button_by_text(d, ["Next", "Tiếp theo"])
            self.log(result2)
            time.sleep(8)

        except Exception as e:
            self.log(f"⚠️ Lỗi khi nhấn 'Next' hai lần: {repr(e)}")

        # === BƯỚC NHẬP TUỔI VÀ NHẤN NEXT ===
        self.log("🎂 Đang nhập tuổi ngẫu nhiên và nhấn 'Next'...")

        age = random.randint(18, 50)

        try:
            # Nhập tuổi
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", str(age)])
            time.sleep(3)
            self.log(f"✅ Đã nhập tuổi: {age}")

            # Nhấn Next
            self.log("➡️ Đang nhấn 'Next' sau khi nhập tuổi...")
            self.log(click_button_by_text(d, ["Next", "Tiếp theo"]))
            time.sleep(6)

        except Exception as e:
            self.log(f"⚠️ Lỗi khi nhập tuổi và nhấn Next: {repr(e)}")

        # 6️⃣ Nếu xuất hiện popup xác nhận ngày sinh → nhấn OK
        self.log("📅 Kiểm tra popup xác nhận ngày sinh...")
        try:
            result = click_button_by_text(d, ["OK", "Đồng ý"])
            self.log(result)
            time.sleep(6)
        except Exception as e:
            self.log(f"⚠️ Không thấy popup 'OK' hoặc không thể nhấn: {repr(e)}")

        # === BƯỚC NHẬP HỌ TÊN VÀ NHẤN NEXT ===
        self.log("🧾 Đang tạo họ tên ngẫu nhiên và nhập vào...")

        # Danh sách họ, tên đệm, tên phổ biến Việt Nam
        ho = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Vu", "Vo", "Dang", "Bui", "Do"]
        ten_dem = ["Van", "Thi", "Ngoc", "Minh", "Duc", "Thanh", "Phuong", "Quoc", "Hong", "Anh"]
        ten = ["Toan", "Huy", "Linh", "Nam", "Trang", "An", "Nhi", "Tuan", "Thao", "Khanh"]

        fullname = f"{random.choice(ho)} {random.choice(ten_dem)} {random.choice(ten)}"
        self.log(f"📛 Họ tên được tạo: {fullname}")

        try:
            # Xử lý khoảng trắng để tránh lỗi adb
            safe_name = fullname.replace(" ", "\\ ")

            # Nhập tên
            subprocess.call(["adb", "-s", udid, "shell", "input", "text", safe_name])
            time.sleep(3)
            self.log("✅ Đã nhập họ tên vào form.")

            # Nhấn Next
            self.log("➡️ Đang nhấn 'Next' sau khi nhập tên...")
            result = click_button_by_text(d, ["Next", "Tiếp theo"])
            self.log(result)
            time.sleep(8)

        except Exception as e:
            self.log(f"⚠️ Lỗi khi nhập họ tên và nhấn Next: {repr(e)}")

        # === BƯỚC TẠO USERNAME TỪ FULLNAME ===
        self.log("👤 Đang ấn Next ở bước USERNAME...")

        try:
            # Nhấn Next
            self.log(click_button_by_text(d, ["Next", "Tiếp theo"]))
            time.sleep(8)
            self.log("✅ Đã ấn Next ở bước USERNAME.")
        except Exception as e:
            self.log(f"⚠️ Lỗi khi nhập username và nhấn Next: {repr(e)}")

        # === BƯỚC ĐỒNG Ý CHÍNH SÁCH ===
        self.log("📜 Đang tìm và nhấn 'I agree' để đồng ý điều khoản...")
        try:
            result = click_button_by_text(d, ["I agree", "Tôi đồng ý"])
            self.log(result)
            time.sleep(25)
        except Exception as e:
            self.log(f"⚠️ Lỗi khi nhấn 'I agree': {repr(e)}")

        return
    
    # ================================== DISPATCHER ============================================================
    def run_signup(self):
        app_choice = phone_ig_app_var.get() if "phone_ig_app_var" in globals() else "instagram"
        app_choice = (app_choice or "").lower()
        if app_choice == "instagram_lite":
            self.log("🚀 Bắt đầu tạo tài khoản trên Instagram Lite")
            return self.signup_instagram_lite()
        elif app_choice == "chrome":
            self.log("🚀 Đang mở Chrome và truy cập trang đăng ký Instagram")
            return self.signup_instagram_chrome()
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
    # delay_entries was removed, return default values
    return default

def get_mobile_delay(key, default):
    # mobile_delay_entries was removed, return default values
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

# --- Lấy kích thước và scale Chrome DESKTOP ---
def get_chrome_size(default_w=1200, default_h=800):
    """Lấy kích thước Chrome cho Desktop"""
    try:
        w = int(desktop_size_combo.get().split("x")[0])
        h = int(desktop_size_combo.get().split("x")[1])
        # giới hạn tối thiểu để tránh lỗi
        if w < 400: w = 400
        if h < 300: h = 300
        return w, h
    except:
        return default_w, default_h

def get_chrome_scale(default=1.0):
    """Lấy scale Chrome cho Desktop"""
    try:
        val = desktop_entry_scale.get().strip()
        if not val.isdigit():
            desktop_entry_scale.delete(0, tk.END)
            desktop_entry_scale.insert(0, "100")
            s = 100
        else:
            s = int(val)
        if s < 10: s = 10
        if s > 300: s = 300
        return s / 100.0
    except:
        return default

# --- Lấy kích thước và scale Chrome MOBILE ---
def get_chrome_size_mobile(default_w=375, default_h=667):
    """Lấy kích thước Chrome cho Mobile"""
    try:
        w = int(mobile_size_combo.get().split("x")[0])
        h = int(mobile_size_combo.get().split("x")[1])
        # giới hạn tối thiểu để tránh lỗi
        if w < 400: w = 400
        if h < 300: h = 300
        return w, h
    except:
        return default_w, default_h

def get_chrome_scale_mobile(default=1.0):
    """Lấy scale Chrome cho Mobile"""
    try:
        s = int(mobile_entry_scale.get().strip())
        if s < 10: s = 10    # tối thiểu 10%
        if s > 300: s = 300  # tối đa 300%
        return s / 100.0     # chuyển % thành số thực
    except:
        return default
    
# --- quản lý driver và tạm dừng luồng ---
all_drivers = []
pause_event = threading.Event()
pause_event.set()  # Mặc định là “cho phép chạy”
warp_enabled = True
proxy_entry = None

def is_warp_mode():
    """Kiểm tra xem có đang ở chế độ WARP (chỉ 'warp', KHÔNG phải 'warp-spin') không"""
    try:
        mode = ui_mode_var.get().strip().lower()
        if mode == "desktop":
            return network_mode_var.get() == "warp"
        elif mode == "mobile":
            return network_mode_mobile_var.get() == "warp"
        return False
    except:
        return False

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
    # Nếu user chọn ẩn Chrome (headless) thì không cần sắp xếp cửa sổ
    try:
        h = globals().get("hidden_chrome_var")
        if h and h.get():
            return
    except Exception:
        pass

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

# --- Lưu & Load config (dùng 1 file config.json duy nhất) ---
CONFIG_FILE = "config.json"
def save_config():
    """Lưu tất cả config vào một file config.json duy nhất"""
    cfg = {
        "ava_folder_path": globals().get("ava_folder_path", ""),
        "chrome_path": globals().get("chrome_path", ""),
        "save_format": globals().get("save_format", ""),
        "photo_folder_phone": globals().get("photo_folder_phone", ""),
        "ig_app_choice": globals().get("phone_ig_app_var", tk.StringVar(value="instagram")).get(),
        "scrcpy_path": globals().get("scrcpy_path", ""),
        "hidden_chrome": hidden_chrome_var.get(),
        "warp_controller_path": globals().get("warp_controller_path", ""),
        "warpxoay_path": globals().get("warpxoay_path", ""),
        "chrome_folder": globals().get("chrome_folder", ""),
        
        # Desktop Chrome Size
        "desktop_width": desktop_size_combo.get().split("x")[0] if 'desktop_entry_width' in globals() and desktop_size_combo else "1200",
        "desktop_height": desktop_size_combo.get().split("x")[1] if 'desktop_entry_height' in globals() and desktop_size_combo else "800",
        "desktop_scale": desktop_entry_scale.get() if 'desktop_entry_scale' in globals() and desktop_entry_scale else "100",
        
        # Mobile Chrome Size
        "mobile_width": entry_width_m.get() if 'entry_width_m' in globals() and entry_width_m else "400",
        "mobile_height": entry_height_m.get() if 'entry_height_m' in globals() and entry_height_m else "844",
        "mobile_scale": entry_scale_m.get() if 'entry_scale_m' in globals() and entry_scale_m else "100",
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def load_config():
    """Load tất cả config từ một file config.json duy nhất"""
    global ava_folder_path, chrome_path, save_format, photo_folder_phone, scrcpy_path
    global warp_controller_path, warpxoay_path, chrome_folder
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
                warp_controller_path = cfg.get("warp_controller_path", "")
                warpxoay_path = cfg.get("warpxoay_path", "")
                chrome_folder = cfg.get("chrome_folder", "")
                
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
                
                # Load Desktop Chrome Size
                if "desktop_width" in cfg and 'desktop_entry_width' in globals() and desktop_size_combo:
                    try:
                        desktop_size_combo.delete(0, tk.END)
                        desktop_size_combo.insert(0, f"{cfg['desktop_width']}x{cfg['desktop_height']}")
                    except Exception:
                        pass

                if "desktop_height" in cfg and 'desktop_entry_height' in globals() and desktop_size_combo:
                    try:
                        desktop_size_combo.delete(0, tk.END)
                        desktop_size_combo.insert(0, f"{cfg['desktop_width']}x{cfg['desktop_height']}")
                    except Exception:
                        pass
                
                if "desktop_scale" in cfg and 'desktop_entry_scale' in globals() and desktop_entry_scale:
                    try:
                        desktop_entry_scale.delete(0, tk.END)
                        desktop_entry_scale.insert(0, cfg["desktop_scale"])
                    except Exception:
                        pass
                
                # Load Mobile Chrome Size
                if "mobile_width" in cfg and 'entry_width_m' in globals() and entry_width_m:
                    try:
                        entry_width_m.delete(0, tk.END)
                        entry_width_m.insert(0, cfg["mobile_width"])
                    except Exception:
                        pass
                
                if "mobile_height" in cfg and 'entry_height_m' in globals() and entry_height_m:
                    try:
                        entry_height_m.delete(0, tk.END)
                        entry_height_m.insert(0, cfg["mobile_height"])
                    except Exception:
                        pass
                
                if "mobile_scale" in cfg and 'entry_scale_m' in globals() and entry_scale_m:
                    try:
                        entry_scale_m.delete(0, tk.END)
                        entry_scale_m.insert(0, cfg["mobile_scale"])
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
                if warp_controller_path:
                    log(f"🔧 Đã load WARP Controller: {warp_controller_path}")
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
resolution = "360x640"

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

        item_id = tree.insert(
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
                "",  # FOLLOW - sẽ update sau
                "",  # POST
                "",  # AVATAR
                "",  # GENDER
                "",  # BIO
                "",  # PROFESSIONAL
            ),
            tags=(status_tag,)
        )
        log(f"✅ Đã insert {status_text} lên TreeView: {username}")
        return item_id  # Trả về item_id để update sau
    except Exception as e:
        log(f"⚠️ Không thể thêm vào Treeview (helper): {repr(e)}")
        return None

def update_tree_column(item_id, column_name, value):
    """Update một cột cụ thể trong TreeView"""
    try:
        if not item_id:
            return
        cols = ["STT","TRẠNG THÁI","USERNAME","PASS","MAIL","PHONE","COOKIE","2FA","TOKEN","IP","PROXY","LIVE","DIE","FOLLOW","POST","AVATAR","GENDER","BIO","PROFESSIONAL"]
        col_index = cols.index(column_name)
        current_values = list(tree.item(item_id, "values"))
        current_values[col_index] = value
        tree.item(item_id, values=current_values)
        log(f"📝 Updated {column_name} = {value}")
    except Exception as e:
        log(f"⚠️ Lỗi khi update tree column {column_name}: {e}")

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
    """Hàm này vẫn giữ để tương thích với code cũ, nhưng giờ dùng RadioButton network_mode_var"""
    global warp_enabled
    warp_enabled = not warp_enabled
    if warp_enabled:
        log("🌐 WARP mode ENABLED - sẽ dùng WARP, bỏ qua proxy.")
        try:
            network_mode_var.set("warp")  # Tự động set RadioButton về WARP
        except:
            pass
    else:
        log("🌐 WARP mode DISABLED - sẽ dùng proxy nếu có.")
        try:
            network_mode_var.set("proxy")  # Tự động set RadioButton về PROXY
        except:
            pass

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
    try:
        if globals().get("hidden_chrome_var") and hidden_chrome_var.get():
            # Chrome hiện tại khuyến nghị dùng '--headless=new' nếu hỗ trợ
            try:
                mobile_options.add_argument("--headless=new")
            except Exception:
                mobile_options.add_argument("--headless")
            # một vài option bổ sung cho chạy headless ổn định trên Windows
            mobile_options.add_argument("--disable-gpu")
            mobile_options.add_argument("--disable-dev-shm-usage")
            mobile_options.add_argument("--no-sandbox")
            # có thể set window-size để tránh layout khác biệt trong headless
            mobile_options.add_argument("--window-size=390,844")
    except Exception:
        pass

    # Emulate iPhone 15 Pro (UA + viewport)
    # Lấy kích thước từ Mobile Settings
    try:
        mobile_width = int(entry_width_m.get()) if entry_width_m and entry_width_m.get() else 390
        mobile_height = int(entry_height_m.get()) if entry_height_m and entry_height_m.get() else 844
    except:
        mobile_width = 390
        mobile_height = 844
    
    mobile_emulation = {
        "deviceMetrics": {"width": mobile_width, "height": mobile_height, "pixelRatio": 3.0},
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
        # Chỉ chạy arrange_after nếu helper tồn tại và CHƯA bật headless
        try:
            is_hidden = globals().get("hidden_chrome_var") and hidden_chrome_var.get()
        except Exception:
            is_hidden = False
        if callable(arrange_after) and not is_hidden:
            threading.Thread(target=arrange_after, args=(drv,), daemon=True).start()
    except Exception:
        pass

    if log_fn:
        log_fn("📱 Chrome Mobile đã khởi tạo (emulation iPhone).")
    return drv

def start_process():
    global sync_barrier, thread_list
    # Mở một cửa sổ mới khi nhấn START
    try:
        win = tk.Toplevel(app)
        win.title("Quản Lý Reg - START")
        win.geometry("1700x650")
        
        # Ẩn cửa sổ chính khi mở cửa sổ mới
        app.withdraw()
        
        # Định nghĩa hàm xử lý khi đóng cửa sổ
        def on_closing():
            try:
                # Hiện lại cửa sổ chính
                app.deiconify()
                # Đóng cửa sổ mới
                win.destroy()
            except:
                pass
        
        # Gán sự kiện đóng cửa sổ
        win.protocol("WM_DELETE_WINDOW", on_closing)

        # Live/Die/Rate
        status_frame = tk.Frame(win, bg="white")
        status_frame.pack(side="bottom", anchor="w", pady=5, padx=5)
        rog_font = ("ROG Fonts STRIX SCAR", 13, "bold")
        tk.Label(status_frame, text="LIVE:", fg="green", bg="white", font=rog_font).grid(row=0, column=0, padx=5)
        tk.Label(status_frame, textvariable=live_var, fg="green", bg="white", font=rog_font).grid(row=0, column=1, padx=5)
        tk.Label(status_frame, text="DIE:",  fg="red",   bg="white", font=rog_font).grid(row=0, column=2, padx=5)
        tk.Label(status_frame, textvariable=die_var,  fg="red",   bg="white", font=rog_font).grid(row=0, column=3, padx=5)
        tk.Label(status_frame, text="RATE:", fg="blue",  bg="white", font=rog_font).grid(row=0, column=6, padx=5)
        tk.Label(status_frame, textvariable=rate_var, fg="blue",  bg="white", font=rog_font).grid(row=0, column=7, padx=5)

        # Accounts (Tree) nằm trên, Logs nằm dưới
        main_frame = tk.Frame(win, bg="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree_frame = tk.LabelFrame(main_frame, text="Accounts", bg="white", font=("Arial", 10, "bold"))
        tree_frame.pack(side="top", fill="both", expand=True, padx=5, pady=(0,5))

        cols = ["STT","TRẠNG THÁI","USERNAME","PASS","MAIL","PHONE","COOKIE","2FA","TOKEN","IP","PROXY","LIVE","DIE","FOLLOW","POST","AVATAR","GENDER","BIO","PROFESSIONAL"]
        global tree
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=tree.yview);  tree.configure(yscrollcommand=vsb.set); vsb.pack(side="right",  fill="y")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview);  tree.configure(xscrollcommand=hsb.set); hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        for col in cols:
            tree.heading(col, text=col, anchor="center")
            tree.column(col, width=120, anchor="center")

        tree.tag_configure("LIVE", background="lightgreen")
        tree.tag_configure("DIE",  background="tomato")

        log_frame = tk.LabelFrame(main_frame, text="Logs", bg="white")
        log_frame.pack(side="top", fill="x", padx=5, pady=(0,5))
        global log_text
        log_text = scrolledtext.ScrolledText(log_frame, width=58, height=12, state=tk.DISABLED, bg="black", fg="lime")
        log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Thêm nút PAUSE, NEXT và STOP nằm ngang nhau vào cửa sổ mới
        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(side="bottom", anchor="center", pady=10)
        
        def stop_all():
            """Dừng toàn bộ phiên và đóng cửa sổ ngay lập tức"""
            try:
                # Hiện lại cửa sổ chính
                app.deiconify()
                # Đóng cửa sổ NGAY LẬP TỨC
                win.destroy()
                
                # Chạy cleanup trong background thread để không block UI
                def cleanup():
                    try:
                        log("🛑 Đang dừng toàn bộ phiên...")
                        
                        # === Desktop/Mobile: Kill Chrome ===
                        try:
                            subprocess.Popen("taskkill /F /IM chrome.exe", shell=True, 
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        except:
                            pass
                        
                        # Dừng tất cả Chrome drivers
                        for drv in all_drivers:
                            try:
                                drv.quit()
                            except:
                                pass
                        all_drivers.clear()
                        
                        # === Phone: Dừng Android/Appium ===
                        # Dừng Instagram app trên tất cả thiết bị
                        try:
                            devices = adb_devices() if 'adb_devices' in globals() else []
                            for udid in devices:
                                try:
                                    subprocess.Popen(["adb", "-s", udid, "shell", "am", "force-stop", "com.instagram.android"],
                                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    subprocess.Popen(["adb", "-s", udid, "shell", "am", "force-stop", "com.instagram.lite"],
                                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                except:
                                    pass
                            log("📱 Đã dừng Instagram trên các thiết bị Android.")
                        except:
                            pass
                        
                        # Kill Appium server
                        try:
                            subprocess.Popen("taskkill /F /IM node.exe /FI \"WINDOWTITLE eq *appium*\"", shell=True,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            log("🛑 Đã dừng Appium server.")
                        except:
                            pass
                        
                        # Dừng tất cả threads
                        for t in thread_list:
                            try:
                                if hasattr(t, '_stop'):
                                    t._stop()
                            except:
                                pass
                        
                        log("✅ Đã dừng toàn bộ phiên.")
                        
                        # Đợi một chút để cleanup hoàn tất
                        time.sleep(1)
                        
                        # Khởi động lại tool
                        log("🔁 Đang khởi động lại tool...")
                        restart_tool()
                        
                    except Exception as e:
                        log(f"⚠️ Lỗi khi cleanup: {e}")
                
                # Chạy cleanup trong thread riêng
                threading.Thread(target=cleanup, daemon=True).start()
                
            except Exception as e:
                log(f"⚠️ Lỗi khi dừng phiên: {e}")
                try:
                    win.destroy()
                except:
                    pass
        
        pause_btn = tk.Button(btn_frame, text="PAUSE", width=15, bg="red", fg="white", font=rog_font, command=pause)
        next_btn = tk.Button(btn_frame, text="NEXT", width=15, bg="orange", fg="white", font=rog_font, command=resume)
        stop_btn = tk.Button(btn_frame, text="STOP", width=15, bg="darkred", fg="white", font=rog_font, command=stop_all)
        pause_btn.pack(side="left", padx=5)
        next_btn.pack(side="left", padx=5)
        stop_btn.pack(side="left", padx=5)
    except Exception as e:
        log(f"❌ Lỗi khi mở cửa sổ mới: {e}")


    mode = ui_mode_var.get().strip().lower()
    if mode == "phone":
        # Phone mode does not use thread count
        pause_event.wait()
        threading.Thread(target=run_phone_android, daemon=True).start()
        return

    # Only validate thread count for Desktop/Mobile
    try:
        if mode == "desktop":
            num_threads = int(desktop_threads_entry.get())
        elif mode == "mobile":
            num_threads = int(mobile_threads_entry.get())
        else:
            num_threads = int(threads_entry.get())
    except:
        log("❌ Số luồng không hợp lệ.")
        return

    # === Desktop/Mobile (Selenium) ===
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

# ============== Email temp-mail.asia ==============
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

# ============== Email DropMail.me ==============
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
        driver = None  # Always start with a fresh driver
        pause_event.wait()
        log("🟢 [Mobile] Bắt đầu tạo tài khoản...")

        # 1) Lấy email tạm (tận dụng 2 checkbox có sẵn)
        email = None
        session_id = None
        scale = get_chrome_scale_mobile()
        try:
            if mail_var.get() == "drop":
                log("📨 [Mobile] Lấy email từ DropMail.me...")
                email, session_id = get_dropmail_email()
                if not email:
                    log("⛔ Không thể lấy email DropMail — dừng.")
                    return
                log(f"✅ Email DropMail: {email}")
            elif mail_var.get() == "temp":
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
        pause_event.wait()
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
        pause_event.wait()
        try:
            proxy = (proxy_entry.get().strip() if proxy_entry else "")
            if is_warp_mode():
                log("🌐 [Mobile] WARP bật → bỏ qua proxy.")
            else:
                log(f"🌐 [Mobile] WARP tắt → proxy: {proxy or 'No proxy'}")

                # Tạo Chrome Mobile riêng biệt, không dùng chung với desktop
                chrome_path   = globals().get("chrome_path", "")
                warp_enabled  = bool(globals().get("warp_enabled", False))
                all_drivers   = globals().get("all_drivers", None)
                arrange_after = globals().get("arrange_after_open", None)

                mobile_options = Options()
                mobile_options.add_argument("--disable-blink-features=AutomationControlled")
                mobile_options.add_argument("--no-first-run")
                mobile_options.add_argument("--disable-background-networking")
                mobile_options.add_argument("--disable-background-timer-throttling")
                mobile_options.add_argument("--disable-client-side-phishing-detection")

                # Thêm headless nếu được chọn (riêng biệt cho mobile)
                try:
                    if globals().get("hidden_chrome_var") and hidden_chrome_var.get():
                        try:
                            mobile_options.add_argument("--headless=new")
                        except Exception:
                            mobile_options.add_argument("--headless")
                        mobile_options.add_argument("--disable-gpu")
                        mobile_options.add_argument("--disable-dev-shm-usage")
                        mobile_options.add_argument("--no-sandbox")
                        mobile_options.add_argument("--window-size=390,844")
                        log("ℹ️ [Mobile] Chạy Chrome ở chế độ Ẩn (headless).")
                except Exception:
                    pass

                # Emulate iPhone 15 Pro (UA + viewport)
                try:
                    mobile_width = int(entry_width_m.get()) if entry_width_m and entry_width_m.get() else 390
                    mobile_height = int(entry_height_m.get()) if entry_height_m and entry_height_m.get() else 844
                except:
                    mobile_width = 390
                    mobile_height = 844
                mobile_emulation = {
                    "deviceMetrics": {"width": mobile_width, "height": mobile_height, "pixelRatio": 3.0},
                    "userAgent": (
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/137.0.0.0 "
                        "Mobile/15E148 Safari/604.1"
                    )
                }
                mobile_options.add_experimental_option("mobileEmulation", mobile_emulation)

                # Proxy: chỉ áp nếu không bật WARP (PC) và có proxy
                if not warp_enabled and proxy:
                    if "://" not in proxy:
                        proxy = f"http://{proxy}"
                    mobile_options.add_argument(f"--proxy-server={proxy}")

                # Nếu người dùng đã chọn binary chrome
                if chrome_path:
                    mobile_options.binary_location = chrome_path

                # Chromedriver:
                driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
                if os.path.isfile(driver_path):
                    service = Service(driver_path)
                else:
                    service = Service()  # dùng chromedriver trong PATH

                driver = se_webdriver.Chrome(service=service, options=mobile_options)
                wait = WebDriverWait(driver, 15)

                # Đến trang mobile signup (đúng theo giao diện mobile)
                driver.get("https://www.instagram.com/accounts/signup/email/")
                pause_event.wait()
                log("🌐 [Mobile] Đã truy cập trang đăng ký (Mobile).")
                time.sleep(3)
        except Exception as e:
            log(f"❌ [Mobile] Lỗi khởi tạo trình duyệt: {repr(e)}")
            try:
                release_position(driver)
                driver.quit()
            except: pass
            driver = None
            continue
        
        # 4) Điền form đăng ký (email, tên đầy đủ, username, password, birthday)
        pause_event.wait()
        try:
            # Nhập email
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
                release_position(driver)
                driver.quit()
            except: pass
            driver = None
            continue

        # 5) Resend code (nếu cần) → tương thích với code bạn đưa
        pause_event.wait()
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
                release_position(driver)
                driver.quit()
            except: pass
            driver = None
            continue

        # 6) Lấy mã xác minh email
        pause_event.wait()
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
            if mail_var.get() == "drop":
                code = wait_for_dropmail_code_mobile(session_id)
            elif mail_var.get() == "temp":
                code = wait_for_tempmail_code_mobile(email)

            if not code:
                log("⏰ [Mobile] Không nhận được mã xác minh — restart vòng lặp.")
                try:
                    release_position(driver)
                    driver.quit()
                except: pass
                driver = None
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
                release_position(driver)
                driver.quit()
            except: pass
            driver = None
            continue

        # 7) Nhập Password → Next qua vài bước
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        pause_event.wait()
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
        if is_warp_mode():
                warp_change_ip()
                time.sleep(8)
        pause_event.wait()
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
        time.sleep(23)
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
                    app.after(0, lambda: insert_to_tree("Die", username, password, email, cookie_str, two_fa_code=""))
                except Exception:
                    insert_to_tree("Die", username, password, email, cookie_str, two_fa_code="")

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
                except:
                    pass
                driver = None
                log("🔁 Khởi chạy lại phiên...")
                continue
            else:
                log("➡️ LIVE: Tiếp tục BƯỚC TIẾP THEO")

        except Exception as e:
            log(f"⚠️ Lỗi khi check live/die: {repr(e)}")
        
        # === BƯỚC 7: Xử lý bật 2FA ===
        pause_event.wait()
        if enable_2fa.get():
            try:
                if is_warp_mode():
                    warp_off()
                    time.sleep(2)
                log("🔐 Bắt đầu bật xác thực hai yếu tố (2FA)...")
                time.sleep(3)

                # Truy cập trang bật 2FA
                driver.get("https://accountscenter.instagram.com/password_and_security/two_factor/?theme=dark")
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(8)
                driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")

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
                        time.sleep(12)
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
        tree_item_id = None
        try:
            status_tag = "LIVE" if status_text.lower() == "live" else "DIE"
            phone_val = locals().get("phone", "")
            token_val = locals().get("token", "")

            tree_item_id = insert_to_tree(status_text, username, password, email, cookie_str, locals().get("two_fa_code", ""))
            log(f"✅ [Mobile] Đã thêm vào TreeView với ID: {tree_item_id}")
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

        # Quay lại giao diện Desktop
        log("🖥 Quay lại giao diện Desktop...")
        driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })
        driver.refresh()
        time.sleep(10)

        # === BƯỚC 5: Follow ===
        pause_event.wait()
        if enable_follow.get():
            followed_count = 0
            try:
                log("🚀 [Mobile] Bắt đầu follow các link...")
                
                # Quay về trang chính Instagram
                log("🏠 [Mobile] Quay về trang chính Instagram...")
                driver.get("https://www.instagram.com/")
                time.sleep(8)
                
                # Xử lý popup "Save Login" nếu có
                try:
                    log("🔍 [Mobile] Kiểm tra popup 'Save Login'...")
                    not_now_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Not now']"))
                    )
                    not_now_btn.click()
                    log("✅ [Mobile] Đã nhấn 'Not now' popup Save Login")
                    time.sleep(2)
                except:
                    log("ℹ️ [Mobile] Không thấy popup Save Login hoặc đã đóng")
                
                time.sleep(2)

                follow_links = [
                    "https://www.instagram.com/shx_pe06/",
                    "https://www.instagram.com/shxuy0bel421162._/",
                    "https://www.instagram.com/ductoan1103/",
                    "https://www.instagram.com/v.anh.26/",
                    "https://www.instagram.com/datgia172/",
                    "https://www.instagram.com/mhai_187/",
                    "https://www.instagram.com/valentin_otz/",
                    "https://www.instagram.com/ductoannn111/",
                    "https://www.instagram.com/nhd_305.nh/",
                    "https://www.instagram.com/ngockem_/",
                ]

                # Lấy số lượng follow từ ô nhập Mobile
                try:
                    num_follow = int(mobile_follow_count_entry.get())
                except:
                    num_follow = 5
                num_follow = min(num_follow, len(follow_links))  

                selected_links = random.sample(follow_links, num_follow)

                for link in selected_links:
                    try:
                        driver.get(link)
                        log(f"🌐 [Mobile] Đã mở link: {link}")
                        time.sleep(7)
                        driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")

                        follow_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Follow']"))
                        )
                        follow_button.click()
                        followed_count += 1
                        log(f"✅ [Mobile] Đã follow: {link}")
                        
                        # Update FOLLOW column
                        if tree_item_id:
                            follow_status = f"{followed_count}/{num_follow}"
                            app.after(0, lambda s=follow_status: update_tree_column(tree_item_id, "FOLLOW", s))
                            log(f"📊 [Mobile] Cập nhật FOLLOW: {follow_status}")
                        
                        time.sleep(6)
                    except Exception as e:
                        log(f"❌ [Mobile] Không thể follow {link}: {repr(e)}")

            except Exception as e:
                log(f"❌ Lỗi trong quá trình follow: {repr(e)}")

        # === BƯỚC 6: Upload avatar ở giao diện mobile ===
        pause_event.wait()
        if enable_avatar.get():
            time.sleep(4)
            avatar_success = False
            gender_saved = False
            bio_saved = False
            post_shared = False
            try:
                log("📱 [Mobile] Chuyển sang giao diện Mobile (iPhone 15 Pro Max)...")
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
                log("👤 [Mobile] Mở trang chỉnh sửa hồ sơ để upload avatar...")
                driver.get("https://www.instagram.com/accounts/edit/")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@accept='image/jpeg,image/png']"))
                )
                time.sleep(8)
                driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")

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
                try:
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
                    gender_saved = True
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "GENDER", "✅"))
                        log("✅ [Mobile] Đã chọn Gender: Female")
                except Exception as e:
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "GENDER", "❌"))
                    log(f"❌ [Mobile] Lỗi chọn Gender: {repr(e)}")

                # Điền Bio (theo lựa chọn GUI) — chuẩn React (setNativeValue + input/change)
                try:
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
                    """)
                    log(f"✍️ [Mobile] Đã điền Bio")
                    time.sleep(1.5)
                    bio_saved = True
                except Exception as e:
                    log(f"❌ [Mobile] Lỗi điền Bio: {repr(e)}")

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
                
                # Update BIO column
                if tree_item_id:
                    if bio_saved:
                        app.after(0, lambda: update_tree_column(tree_item_id, "BIO", "✅"))
                        log("✅ [Mobile] Bio đã lưu thành công")
                    else:
                        app.after(0, lambda: update_tree_column(tree_item_id, "BIO", "❌"))
                        log("❌ [Mobile] Bio lưu thất bại")

                # Lấy ảnh và upload
                try:
                    if not ava_folder_path or not os.path.exists(ava_folder_path):
                        log("❌ [Mobile] Chưa chọn thư mục ảnh hoặc thư mục không tồn tại.")
                        if tree_item_id:
                            app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
                    else:
                        image_files = [f for f in os.listdir(ava_folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                        if image_files:
                            selected_path = os.path.join(ava_folder_path, random.choice(image_files))
                            driver.find_element(By.XPATH, "//input[@accept='image/jpeg,image/png']").send_keys(selected_path)
                            log(f"✅ [Mobile] Đã upload avatar: {os.path.basename(selected_path)}")
                            time.sleep(3)
                            
                            # Lưu avatar
                            WebDriverWait(driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
                            ).click()
                            log("💾 [Mobile] Đã lưu avatar")
                            avatar_success = True
                            if tree_item_id:
                                app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "✅"))
                            time.sleep(10)

                            # Nếu có nút Post thì click
                            try:
                                post_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'_a9--') and text()='Post']"))
                                )
                                driver.execute_script("arguments[0].click();", post_btn)
                                log("✅ [Mobile] Đã click Post")
                                post_shared = True
                                if tree_item_id:
                                    app.after(0, lambda: update_tree_column(tree_item_id, "POST", "✅"))
                                time.sleep(12)
                            except:
                                log("ℹ [Mobile] Không thấy nút Post, bỏ qua.")
                                if tree_item_id:
                                    app.after(0, lambda: update_tree_column(tree_item_id, "POST", "❌"))
                        else:
                            log("❌ [Mobile] Không có ảnh hợp lệ trong thư mục.")
                            if tree_item_id:
                                app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
                except Exception as e:
                    log(f"❌ [Mobile] Lỗi upload avatar: {repr(e)}")
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
                        
            except Exception as e:
                log(f"❌ [Mobile] Lỗi Bước 6: {repr(e)}")
                if tree_item_id:
                    if not gender_saved:
                        app.after(0, lambda: update_tree_column(tree_item_id, "GENDER", "❌"))
                    if not bio_saved:
                        app.after(0, lambda: update_tree_column(tree_item_id, "BIO", "❌"))
                    if not avatar_success:
                        app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
                    if not post_shared:
                        app.after(0, lambda: update_tree_column(tree_item_id, "POST", "❌"))

            # Quay lại giao diện Desktop
            log("🖥 Quay lại giao diện Desktop...")
            driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
            driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            })
            driver.refresh()
            time.sleep(10)

        # === BẬT CHẾ ĐỘ CHUYÊN NGHIỆP (Creator -> Personal blog) ===
        pause_event.wait()
        if enable_Chuyen_nghiep.get():
            professional_success = False
            try:
                log("💼 [Mobile] Đang bật chế độ chuyên nghiệp (Creator -> Personal blog)...")
                driver.get("https://www.instagram.com/accounts/convert_to_professional_account/")
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(8)
                driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")

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
                    log(f"✅ [Mobile] Đã chọn {account_type}")
                    time.sleep(3)
                except Exception as e:
                    log(f"⚠️ [Mobile] Không tìm thấy nút chọn {account_type}: {repr(e)}")
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "❌"))
                    raise

                # 2) Nhấn Next qua 2 màn hình giới thiệu
                for i in range(2):
                    try:
                        next_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next' or normalize-space()='Tiếp']"))
                        )
                        next_btn.click()
                        log(f"➡️ [Mobile] Đã nhấn Next {i+1}")
                        time.sleep(1.5)
                    except Exception as e:
                        log(f"ℹ️ [Mobile] Không tìm thấy Next {i+1}: {repr(e)}")
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
                    log(f"✅ [Mobile] Đã chọn Category: {category}")
                    time.sleep(3)
                else:
                    log(f"⚠️ [Mobile] Không tìm thấy mã category cho {category}")
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "❌"))
                    raise Exception(f"Category not found: {category}")

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
                
                professional_success = True
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "✅"))
                log("✅ [Mobile] Đã bật chế độ chuyên nghiệp thành công")
                
            except Exception as e:
                log(f"❌ [Mobile] Lỗi khi bật chế độ chuyên nghiệp: {repr(e)}")
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "❌"))

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
        driver = None  # Always start with a fresh driver
        pause_event.wait() 
        log("🟢 Bắt đầu tạo tài khoản...")

        if mail_var.get() == "drop":
            log("📨 Lấy email từ DropMail.me...")
            email, session_id = get_dropmail_email()
            if not email:
                log("⛔ Không thể lấy email DropMail — dừng tiến trình.")
                return
            log(f"✅ Email DropMail: {email}")

        elif mail_var.get() == "temp":
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

        # === BƯỚC 1: Bật WARP và mở Instagram ===
        time.sleep(3)
        pause_event.wait()
        log("🌐 Mở Instagram...")

        proxy = proxy_entry.get().strip()

        if is_warp_mode():
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
        # Lấy scale và kích thước từ settings
        scale = get_chrome_scale()
        try:
            w, h = get_chrome_size()
        except Exception:
            w, h = 1200, 800
        # Nếu scale khác 1, nhân kích thước lên
        if scale != 1.0:
            w = int(w * scale)
            h = int(h * scale)
        options.add_argument(f"--window-size={w},{h}")

        # Nếu user bật Ẩn Chrome -> chạy headless và set một số flag/size
        is_headless = False
        try:
            if globals().get("hidden_chrome_var") and hidden_chrome_var.get():
                try:
                    options.add_argument("--headless=new")
                except Exception:
                    options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--no-sandbox")
                try:
                    w, h = get_chrome_size()
                    options.add_argument(f"--window-size={w},{h}")
                except Exception:
                    options.add_argument("--window-size=1200,800")
                log("ℹ️ Chạy Chrome ở chế độ Ẩn (headless).")
                is_headless = True
        except Exception:
            is_headless = False

        # ✅ nếu có proxy thì thêm (giữ lại logic cũ)
        if proxy and not is_warp_mode():
            options.add_argument(f"--proxy-server=http://{proxy}")

        # ✅ nếu có chrome_path thì dùng binary_location (giống V3-Mobile)
        if chrome_path:
            options.binary_location = chrome_path

        driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        service = Service(driver_path)
        driver = se_webdriver.Chrome(service=service, options=options)
        all_drivers.append(driver)

        # 🕒 Sắp xếp Chrome giống V3-Mobile (chỉ khi không headless)
        try:
            if not is_headless:
                threading.Thread(target=arrange_after_open, args=(driver,), daemon=True).start()
        except Exception:
            pass

        driver.get("https://www.instagram.com/accounts/emailsignup/")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
        except Exception as e:
            log(f"❌ Lỗi khi mở trang signup (wait emailOrPhone): {repr(e)} — đóng phiên và restart...")
            try:
                if is_warp_mode():
                    warp_off()
            except:
                pass
            try:
                release_position(driver)
            except:
                pass
            try:
                driver.quit()
            except:
                pass
            driver = None
            continue

        # Áp dụng scale từ settings sau khi mở trang
        driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")
        time.sleep(3)
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
        except Exception as e:
            log(f"❌ Lỗi sau khi apply scale (wait emailOrPhone): {repr(e)} — đóng phiên và restart...")
            try:
                if is_warp_mode():
                    warp_off()
            except:
                pass
            try:
                release_position(driver)
            except:
                pass
            try:
                driver.quit()
            except:
                pass
            driver = None
            continue
        log(f"✅ [Luồng {thread_id}] Chrome đã mở xong và trang Instagram sẵn sàng.")
        try:
            # =========== Điền Thông tin USER-PASS-MAIL-FULLNAME (DESKTOP) ==============
            time.sleep(2)
            type_text_slowly(
                driver.find_element(By.NAME, "emailOrPhone"),
                email,
                delay=get_delay("Mail_type", 0.18)
            )
            log("✍️ Đã nhập email vào form đăng ký")
            time.sleep(get_delay("Mail_sleep", 1))
            type_text_slowly(
                driver.find_element(By.NAME, "password"),
                password,
                delay=get_delay("Pass_type", 0.18)
            )
            log("✍️ Đã nhập mật khẩu vào form đăng ký")
            time.sleep(get_delay("Pass_sleep", 3))
            type_text_slowly(
                driver.find_element(By.NAME, "fullName"),
                full_name,
                delay=get_delay("Họ Tên_type", 0.18)
            )
            log(f"✍️ Đã nhập họ tên vào form đăng ký: {full_name}")
            time.sleep(get_delay("Họ Tên_sleep", 2))

            # --- Xóa hết username cũ ---
            log("🧹 Đang xóa username cũ khỏi form đăng ký...")
            username_elem = driver.find_element(By.NAME, "username")
            username_elem.click()
            time.sleep(0.2)
            username_elem.send_keys(Keys.CONTROL, "a")
            time.sleep(0.1)
            username_elem.send_keys(Keys.DELETE)
            time.sleep(0.2)

            # --- Tạo lại username từ họ tên, random vị trí dấu '_' và '.' và số cuối ---
            log(f"🔄 Đang tạo lại username từ họ tên: {full_name}")
            def make_username(full_name):
                # Loại bỏ ký tự đặc biệt, chuyển về không dấu, thường
                base = re.sub(r'[^a-z0-9 ]', '', unidecode(full_name.lower()))
                parts = base.split()
                if len(parts) < 2:
                    parts.append('user')
                # Ghép các phần lại, random dấu giữa các phần
                username_core = parts[0]
                for p in parts[1:]:
                    sep = random.choice(['_', '.', ''])
                    username_core += sep + p
                # Thêm số random cuối cùng
                username_core += '_' + str(random.randint(1000, 99999))
                return username_core

            username_new = make_username(full_name)
            log(f"🔤 Username mới tạo: {username_new}")

            # --- Nhập username mới ---
            log(f"✍️ Đang nhập username mới vào form đăng ký: {username_new}")
            type_text_slowly(
                username_elem,
                username_new,
                delay=get_delay("Username_type", 0.18)
            )

            time.sleep(get_delay("Username_sleep", 3))
            time.sleep(4)

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

            log("➡️ Đang nhấn nút Tiếp theo để gửi form đăng ký...")
            pause_event.wait()
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            log("➡️ Đã ấn Tiếp theo")
            time.sleep(get_delay("Next_sleep", 2))
            
            # Chỉ áp dụng khi chọn mạng WARP
            if network_mode_var.get() == "warp":
                success = False
                for attempt in range(2):  # thử tối đa 2 lần (lần 2 sau khi đổi IP)
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//select[@title='Month:']"))
                        )
                        log("✅ Đã chuyển sang màn chọn ngày sinh.")
                        success = True
                        break
                    except Exception as e:
                        if attempt == 0:
                            log(f"❌ Không chuyển sang màn chọn ngày sinh sau khi Next. Đang đổi IP WARP và thử lại...")
                            if is_warp_mode():
                                warp_change_ip()
                                log("🌐 Đã đổi IP WARP, chờ 10 giây...")
                                time.sleep(10)
                            try:
                                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                                log("➡️ Đã thử lại ấn Tiếp theo sau khi đổi IP WARP")
                                time.sleep(get_delay("Next_sleep", 2))
                                time.sleep(4)
                            except Exception as e2:
                                log(f"❌ Lỗi khi thử lại ấn Tiếp theo: {repr(e2)}")
                        else:
                            log(f"❌ Vẫn không chuyển được sang màn ngày sinh sau khi đổi IP WARP: {repr(e)}")
                if not success:
                    log("🔁 Đóng phiên và restart lại từ đầu...")
                    try:
                        if is_warp_mode():
                            warp_off()
                        time.sleep(2)
                        release_position(driver)
                        driver.quit()
                    except:
                        pass
                    continue  # Restart phiên trong cùng luồng

            # === BƯỚC 2: chọn ngày sinh ===
            pause_event.wait()
            if is_warp_mode():
                log("🌐 Đang tắt WARP trước khi chọn ngày sinh...")
                warp_off()
                time.sleep(3)
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

            # === KIỂM TRA: Có chuyển sang màn điền code không? ===
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Confirmation Code']"))
                )
                log("✅ Đã chuyển sang màn điền mã xác minh.")
            except Exception as e:
                log(f"❌ Không chuyển sang màn điền code sau khi chọn ngày sinh. Lỗi: {repr(e)}")
                log("🔁 Đóng phiên và restart lại từ đầu...")
                try:
                    if is_warp_mode():
                        warp_off()
                    time.sleep(2)
                    release_position(driver)
                    driver.quit()
                except:
                    pass
                driver = None
                continue  # Restart phiên trong cùng luồng

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
                if mail_var.get() == "drop":
                    code = wait_for_dropmail_code(session_id)
                elif mail_var.get() == "temp":
                    code = wait_for_tempmail_code(email)
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
                    driver = None
                    # (khuyên dùng continue để không nhân thêm thread)
                    log("🔁 Restart phiên trong cùng luồng.")
                    continue

                # Nếu có code -> nhập và tiếp tục như cũ
                code_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Confirmation Code']"))
                )
                type_text_slowly(code_input, code, delay=0.3)
                log(f"✅ Đã nhập mã xác minh: {code}")
                if is_warp_mode():
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
                        time.sleep(18)
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
                        app.after(0, lambda: insert_to_tree("Die", username, password, email, cookie_str, two_fa_code=""))
                    except Exception:
                        insert_to_tree("Die", username, password, email, cookie_str, two_fa_code="")

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
                    except:
                        pass
                    driver = None
                    log("🔁 Khởi chạy lại phiên...")
                    continue
                else:
                    log("➡️ LIVE: Tiếp tục BƯỚC TIẾP THEO (Follow/…)")

            except Exception as e:
                log(f"⚠️ Lỗi khi check live/die: {repr(e)}")
        except Exception as e:
            log(f"❌ Lỗi trình duyệt: {repr(e)}")
            try:
                if is_warp_mode():
                    warp_off()
                release_position(driver)  # ✅ trả chỗ
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
                warp_off()
                log("🔐 Bắt đầu bật xác thực hai yếu tố (2FA)...")
                time.sleep(6)

                # Truy cập trang bật 2FA
                driver.get("https://accountscenter.instagram.com/password_and_security/two_factor/?theme=dark")
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(8)
                driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")
                
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
                        time.sleep(12)
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
        tree_item_id = None
        try:
            status_tag = "LIVE" if status_text.lower() == "live" else "DIE"
            phone_val = locals().get("phone", "")
            token_val = locals().get("token", "")

            tree_item_id = insert_to_tree(status_text, username, password, email, cookie_str, locals().get("two_fa_code", ""))
            log(f"✅ [Desktop] Đã thêm vào TreeView với ID: {tree_item_id}")
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
            if is_warp_mode():
                warp_change_ip()
                time.sleep(8)
            followed_count = 0
            try:
                pause_event.wait()
                log("🚀 [Desktop] Bắt đầu follow các link...")
                time.sleep(3)

                follow_links = [
                    "https://www.instagram.com/shx_pe06/",
                    "https://www.instagram.com/shxuy0bel421162._/",
                    "https://www.instagram.com/ductoan1103/",
                    "https://www.instagram.com/v.anh.26/",
                    "https://www.instagram.com/datgia172/",
                    "https://www.instagram.com/mhai_187/",
                    "https://www.instagram.com/valentin_otz/",
                    "https://www.instagram.com/ductoannn111/",
                    "https://www.instagram.com/nhd_305.nh/",
                    "https://www.instagram.com/ngockem_/",
                ]

                # Lấy số lượng follow từ ô nhập Desktop
                try:
                    num_follow = int(desktop_follow_count_entry.get())
                except:
                    num_follow = 5
                num_follow = min(num_follow, len(follow_links))  

                selected_links = random.sample(follow_links, num_follow)

                for link in selected_links:
                    try:
                        driver.get(link)
                        log(f"🌐 [Desktop] Đã mở link: {link}")
                        time.sleep(6)
                        driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")
                        # Check checkpoint or die after each follow
                        current_url = driver.current_url
                        page_source = driver.page_source
                        checkpoint_detected = False
                        if "checkpoint" in current_url.lower() or "Confirm you're human" in page_source or "/accounts/login/" in current_url or "Sorry, this page isn't available" in page_source:
                            checkpoint_detected = True

                        if checkpoint_detected:
                            log("❌ [Desktop] Phát hiện checkpoint hoặc Die trong quá trình follow!")
                            # Update TreeView: LIVE -> DIE
                            if tree_item_id:
                                app.after(0, lambda: update_tree_column(tree_item_id, "STATUS", "DIE"))
                                app.after(0, lambda: update_tree_column(tree_item_id, "FOLLOW", "❌"))
                            # Chuyển file Live.txt sang Die.txt
                            try:
                                live_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Live.txt")
                                die_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Die.txt")
                                with open(live_path, "r", encoding="utf-8") as f:
                                    lines = f.readlines()
                                new_lines = []
                                moved_line = None
                                for line in lines:
                                    if username in line and moved_line is None:
                                        moved_line = line
                                    else:
                                        new_lines.append(line)
                                if moved_line:
                                    with open(live_path, "w", encoding="utf-8") as f:
                                        f.writelines(new_lines)
                                    with open(die_path, "a", encoding="utf-8") as f:
                                        f.write(moved_line)
                                    log(f"🔄 Đã chuyển tài khoản từ Live.txt sang Die.txt: {username}")
                            except Exception as e:
                                log(f"❌ Lỗi chuyển file Live->Die: {repr(e)}")
                            # Báo đỏ
                            log("🔴 Tài khoản đã bị checkpoint/DIE. Restart lại phiên...")
                            try:
                                warp_off()
                                time.sleep(2)
                                release_position(driver)
                                driver.quit()
                            except:
                                pass
                            driver = None
                            continue  # Restart lại phiên

                        follow_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Follow']"))
                        )
                        follow_button.click()
                        followed_count += 1
                        log(f"✅ [Desktop] Đã follow: {link}")
                        # Update FOLLOW column
                        if tree_item_id:
                            follow_status = f"{followed_count}/{num_follow}"
                            app.after(0, lambda s=follow_status: update_tree_column(tree_item_id, "FOLLOW", s))
                            log(f"📊 [Desktop] Cập nhật FOLLOW: {follow_status}")
                        time.sleep(6)
                    except Exception as e:
                        log(f"❌ [Desktop] Không thể follow {link}: {repr(e)}")

            except Exception as e:
                log(f"❌ Lỗi trong quá trình follow: {repr(e)}")
        else:
            log("⏭ Bỏ qua bước Follow")

        # === BƯỚC 6: Upload avatar ở giao diện mobile ===
        if bioava_var.get():
            if is_warp_mode():
                warp_off()
                time.sleep(4)
        
        avatar_success = False
        gender_saved = False
        bio_saved = False
        post_shared = False
        try:
            log("📱 [Desktop] Chuyển sang giao diện Mobile (iPhone 15 Pro Max)...")
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
            driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")

            # Đóng popup Not Now nếu có
            driver.execute_script("""
                let btn = [...document.querySelectorAll("span,button")]
                    .find(el => ["Not now", "Không phải bây giờ"].includes(el.innerText.trim()));
                if (btn) btn.click();
            """)
            time.sleep(3)

            # Mở trang chỉnh sửa hồ sơ
            log("👤 [Desktop] Mở trang chỉnh sửa hồ sơ để upload avatar...")
            driver.get("https://www.instagram.com/accounts/edit/")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@accept='image/jpeg,image/png']"))
            )
            time.sleep(8)

            # ==== CHECKPOINT CHECK 1 ====
            current_url = driver.current_url
            page_source = driver.page_source
            checkpoint_detected = False
            if "checkpoint" in current_url.lower() or "Confirm you're human" in page_source or "/accounts/login/" in current_url or "Sorry, this page isn't available" in page_source:
                checkpoint_detected = True
            if checkpoint_detected:
                log("❌ [Desktop] Phát hiện checkpoint hoặc Die khi mở trang chỉnh sửa hồ sơ!")
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "STATUS", "DIE"))
                try:
                    live_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Live.txt")
                    die_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Die.txt")
                    with open(live_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    new_lines = []
                    moved_line = None
                    for line in lines:
                        if username in line and moved_line is None:
                            moved_line = line
                        else:
                            new_lines.append(line)
                    if moved_line:
                        with open(live_path, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                        with open(die_path, "a", encoding="utf-8") as f:
                            f.write(moved_line)
                        log(f"🔄 Đã chuyển tài khoản từ Live.txt sang Die.txt: {username}")
                except Exception as e:
                    log(f"❌ Lỗi chuyển file Live->Die: {repr(e)}")
                log("🔴 Tài khoản checkpoint/DIE. Restart lại phiên...")
                try:
                    warp_off()
                    time.sleep(2)
                    release_position(driver)
                    driver.quit()
                except:
                    pass
                driver = None
                return  # dừng bước 6

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
            try:
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
                gender_saved = True
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "GENDER", "✅"))
                    log("✅ [Desktop] Đã chọn Gender: Female")
            except Exception as e:
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "GENDER", "❌"))
                log(f"❌ [Desktop] Lỗi chọn Gender: {repr(e)}")

            # Điền Bio
            try:
                driver.execute_script("""
                (function(val){
                    const el = document.querySelector("textarea[name='biography'], #pepBio, textarea[aria-label='Bio'], textarea[aria-label='Tiểu sử']");
                    if (!el) { console.warn("❌ Không tìm thấy ô Bio (#pepBio/biography)"); return; }
                    const proto  = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                    if (setter) setter.call(el, val); else el.value = val;
                    el.dispatchEvent(new Event('input',  {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    el.blur();
                    console.log("✍️ Đã điền Bio:", val);
                })(arguments[0]);
                """)
                log(f"✍️ [Desktop] Đã điền Bio")
                time.sleep(1.5)
                bio_saved = True
            except Exception as e:
                log(f"❌ [Desktop] Lỗi điền Bio: {repr(e)}")

            # ==== CHECKPOINT CHECK 2 ====
            current_url = driver.current_url
            page_source = driver.page_source
            checkpoint_detected = False
            if "checkpoint" in current_url.lower() or "Confirm you're human" in page_source or "/accounts/login/" in current_url or "Sorry, this page isn't available" in page_source:
                checkpoint_detected = True
            if checkpoint_detected:
                log("❌ [Desktop] Phát hiện checkpoint hoặc Die sau khi điền Bio!")
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "STATUS", "DIE"))
                    app.after(0, lambda: update_tree_column(tree_item_id, "BIO", "❌"))
                try:
                    live_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Live.txt")
                    die_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Die.txt")
                    with open(live_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    new_lines = []
                    moved_line = None
                    for line in lines:
                        if username in line and moved_line is None:
                            moved_line = line
                        else:
                            new_lines.append(line)
                    if moved_line:
                        with open(live_path, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                        with open(die_path, "a", encoding="utf-8") as f:
                            f.write(moved_line)
                        log(f"🔄 Đã chuyển tài khoản từ Live.txt sang Die.txt: {username}")
                except Exception as e:
                    log(f"❌ Lỗi chuyển file Live->Die: {repr(e)}")
                log("🔴 Tài khoản checkpoint/DIE. Restart lại phiên...")
                try:
                    warp_off()
                    time.sleep(2)
                    release_position(driver)
                    driver.quit()
                except:
                    pass
                driver = None
                return

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
            
            # Update BIO column
            if tree_item_id:
                if bio_saved:
                    app.after(0, lambda: update_tree_column(tree_item_id, "BIO", "✅"))
                    log("✅ [Desktop] Bio đã lưu thành công")
                else:
                    app.after(0, lambda: update_tree_column(tree_item_id, "BIO", "❌"))
                    log("❌ [Desktop] Bio lưu thất bại")

            # Lấy ảnh và upload
            try:
                if not ava_folder_path or not os.path.exists(ava_folder_path):
                    log("❌ [Desktop] Chưa chọn thư mục ảnh hoặc thư mục không tồn tại.")
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
                else:
                    image_files = [f for f in os.listdir(ava_folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                    if image_files:
                        selected_path = os.path.join(ava_folder_path, random.choice(image_files))
                        driver.find_element(By.XPATH, "//input[@accept='image/jpeg,image/png']").send_keys(selected_path)
                        log(f"✅ [Desktop] Đã upload avatar: {os.path.basename(selected_path)}")
                        time.sleep(3)
                        
                        # Lưu avatar
                        WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
                        ).click()
                        log("💾 [Desktop] Đã lưu avatar")
                        avatar_success = True
                        if tree_item_id:
                            app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "✅"))
                        time.sleep(12)

                        # Nếu có nút Post thì click
                        try:
                            post_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'_a9--') and text()='Post']"))
                            )
                            driver.execute_script("arguments[0].click();", post_btn)
                            log("✅ [Desktop] Đã click Post")
                            post_shared = True
                            if tree_item_id:
                                app.after(0, lambda: update_tree_column(tree_item_id, "POST", "✅"))
                            time.sleep(12)
                        except:
                            log("ℹ [Desktop] Không thấy nút Post, bỏ qua.")
                            if tree_item_id:
                                app.after(0, lambda: update_tree_column(tree_item_id, "POST", "❌"))
                    else:
                        log("❌ [Desktop] Không có ảnh hợp lệ trong thư mục.")
                        if tree_item_id:
                            app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
            except Exception as e:
                log(f"❌ [Desktop] Lỗi upload avatar: {repr(e)}")
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))

            # ==== CHECKPOINT CHECK 3 ====
            current_url = driver.current_url
            page_source = driver.page_source
            checkpoint_detected = False
            if "checkpoint" in current_url.lower() or "Confirm you're human" in page_source or "/accounts/login/" in current_url or "Sorry, this page isn't available" in page_source:
                checkpoint_detected = True
            if checkpoint_detected:
                log("❌ [Desktop] Phát hiện checkpoint hoặc Die sau khi upload avatar!")
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "STATUS", "DIE"))
                    app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
                try:
                    live_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Live.txt")
                    die_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Die.txt")
                    with open(live_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    new_lines = []
                    moved_line = None
                    for line in lines:
                        if username in line and moved_line is None:
                            moved_line = line
                        else:
                            new_lines.append(line)
                    if moved_line:
                        with open(live_path, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                        with open(die_path, "a", encoding="utf-8") as f:
                            f.write(moved_line)
                        log(f"🔄 Đã chuyển tài khoản từ Live.txt sang Die.txt: {username}")
                except Exception as e:
                    log(f"❌ Lỗi chuyển file Live->Die: {repr(e)}")
                log("🔴 Tài khoản checkpoint/DIE. Restart lại phiên...")
                try:
                    warp_off()
                    time.sleep(2)
                    release_position(driver)
                    driver.quit()
                    driver = None
                except:
                    pass
                return
                    
        except Exception as e:
            log(f"❌ [Desktop] Lỗi Bước 6: {repr(e)}")
            if tree_item_id:
                if not gender_saved:
                    app.after(0, lambda: update_tree_column(tree_item_id, "GENDER", "❌"))
                if not bio_saved:
                    app.after(0, lambda: update_tree_column(tree_item_id, "BIO", "❌"))
                if not avatar_success:
                    app.after(0, lambda: update_tree_column(tree_item_id, "AVATAR", "❌"))
                if not post_shared:
                    app.after(0, lambda: update_tree_column(tree_item_id, "POST", "❌"))

        # Quay lại giao diện Desktop
        log("🖥 Quay lại giao diện Desktop...")
        driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })
        driver.refresh()
        time.sleep(10)

        # === BẬT CHẾ ĐỘ CHUYÊN NGHIỆP (Creator -> Personal blog) ===
        if pro_mode_var.get():
            professional_success = False
            try:
                pause_event.wait()
                log("💼 [Desktop] Đang bật chế độ chuyên nghiệp (Creator -> Personal blog)...")
                driver.get("https://www.instagram.com/accounts/convert_to_professional_account/")
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(10)
                driver.execute_script(f"document.body.style.zoom='{int(scale*100)}%'")
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
                    log(f"✅ [Desktop] Đã chọn {account_type}")
                    time.sleep(3)
                except Exception as e:
                    log(f"⚠️ [Desktop] Không tìm thấy nút chọn {account_type}: {repr(e)}")
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "❌"))
                    raise

                # 2) Nhấn Next qua 2 màn hình giới thiệu
                for i in range(2):
                    try:
                        next_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next' or normalize-space()='Tiếp']"))
                        )
                        next_btn.click()
                        log(f"➡️ [Desktop] Đã nhấn Next {i+1}")
                        time.sleep(1.5)
                    except Exception as e:
                        log(f"ℹ️ [Desktop] Không tìm thấy Next {i+1}: {repr(e)}")
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
                    log(f"✅ [Desktop] Đã chọn Category: {category}")
                    time.sleep(3)
                else:
                    log(f"⚠️ [Desktop] Không tìm thấy mã category cho {category}")
                    if tree_item_id:
                        app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "❌"))
                    raise Exception(f"Category not found: {category}")

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
                
                professional_success = True
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "✅"))
                log("✅ [Desktop] Đã bật chế độ chuyên nghiệp thành công")
                
            except Exception as e:
                log(f"❌ [Desktop] Lỗi khi bật chế độ chuyên nghiệp: {repr(e)}")
                if tree_item_id:
                    app.after(0, lambda: update_tree_column(tree_item_id, "PROFESSIONAL", "❌"))

            # === KẾT THÚC PHIÊN ===
            try:
                if is_warp_mode():
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
# --- Center window on screen ---
window_width = 1366
window_height = 830
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = int((screen_width - window_width) / 2)
y = int((screen_height - window_height) / 2)
app.geometry(f"{window_width}x{window_height}+{x}+{y}")
app.resizable(True, True)

# --- Biến đếm Live/Die/Rate ---
live_var = tk.StringVar(value="0")
die_var  = tk.StringVar(value="0")
rate_var = tk.StringVar(value="0%")

# tạo StringVar sau khi app đã tồn tại
scrcpy_path_var = tk.StringVar(value="(chưa chọn scrcpy.exe)")

# ===== WARP CONTROLLER MANAGEMENT =====
warp_controller_process = None
warp_controller_path = ""

def select_warp_controller():
    """Chọn đường dẫn đến WARP Controller"""
    global warp_controller_path
    path = filedialog.askopenfilename(
        title="Chọn file WARP Controller (warp_controller.py hoặc .exe)",
        filetypes=[("Python files", "*.py"), ("Executable", "*.exe"), ("All files", "*.*")]
    )
    if path:
        warp_controller_path = path
        save_warp_controller_path(path)
        log(f"✅ Đã chọn WARP Controller: {path}")
        return path
    return warp_controller_path

def save_warp_controller_path(path):
    """Lưu đường dẫn WARP Controller vào config.json"""
    global warp_controller_path
    warp_controller_path = path
    save_config()

def load_warp_controller_path():
    """Load đường dẫn WARP Controller từ config.json"""
    return globals().get("warp_controller_path", "")

def open_warp_controller():
    """Mở WARP Controller nếu chưa mở"""
    global warp_controller_process, warp_controller_path
    
    # Kiểm tra xem đã mở chưa
    if warp_controller_process is not None:
        try:
            # Kiểm tra process còn chạy không
            if warp_controller_process.poll() is None:
                log("⚠️ WARP Controller đã đang chạy!")
                return True
        except:
            pass
    
    # Nếu chưa có path, thử load từ config
    if not warp_controller_path:
        warp_controller_path = load_warp_controller_path()
    
    # Nếu vẫn không có path, yêu cầu chọn
    if not warp_controller_path or not os.path.exists(warp_controller_path):
        messagebox.showwarning("Chưa chọn WARP Controller", 
                             "Vui lòng chọn đường dẫn đến WARP Controller!")
        select_warp_controller()
        if not warp_controller_path or not os.path.exists(warp_controller_path):
            return False
    
    # Mở WARP Controller
    try:
        if warp_controller_path.endswith('.py'):
            # Chạy file Python
            warp_controller_process = subprocess.Popen(['python', warp_controller_path])
        else:
            # Chạy file exe
            warp_controller_process = subprocess.Popen([warp_controller_path])
        
        log(f"✅ Đã mở WARP Controller: {warp_controller_path}")
        return True
    except Exception as e:
        log(f"❌ Lỗi khi mở WARP Controller: {e}")
        messagebox.showerror("Lỗi", f"Không thể mở WARP Controller:\n{e}")
        return False

# Load path khi khởi động
warp_controller_path = load_warp_controller_path()

# biến toàn cục cho tuỳ chọn kết nối
phone_net_mode = tk.StringVar(value="wifi")

# đọc config để lấy path đã lưu (chỉ gán vào biến thuần scrcpy_path)
load_scrcpy_config()

# nếu có path thì đưa lên UI
if scrcpy_path:
    scrcpy_path_var.set(scrcpy_path)

# Background (optional) - đã bỏ load ảnh nền
canvas = tk.Canvas(app, width=1050, height=550, bg="white")
canvas.pack(fill="both", expand=True)

# ========================= TAB SYSTEM =========================
current_tab = tk.StringVar(value="INSTAGRAM")

# ===== THANH TRÊN ĐEN - Hiển thị tên tab hiện tại =====
top_bar = tk.Frame(app, bg="black", height=50)
top_bar.place(x=0, y=0, relwidth=1, height=50)

tab_title_label = tk.Label(top_bar, textvariable=current_tab, bg="black", fg="white", 
                           font=("ROG Fonts STRIX SCAR", 20, "bold"))
tab_title_label.pack(expand=True)

# ===== THANH TRÁI ĐEN - Menu chuyển tab =====
left_menu = tk.Frame(app, bg="black", width=150)
left_menu.place(x=0, y=50, width=150, relheight=1)

menu_font = ("ROG Fonts STRIX SCAR", 11, "bold")

def switch_tab(tab_name):
    """Chuyển tab và cập nhật nội dung"""
    current_tab.set(tab_name)
    
    # Ẩn tất cả các tab content
    instagram_content.place_forget()
    checklive_content.place_forget()
    history_content.place_forget()
    guide_content.place_forget()
    utilities_content.place_forget()
    menu_content.place_forget()
    
    # Hiện tab được chọn
    if tab_name == "INSTAGRAM":
        instagram_content.place(x=150, y=50, relwidth=1, width=-150, relheight=1, height=-50)
    elif tab_name == "CHECK LIVE":
        checklive_content.place(x=150, y=50, relwidth=1, width=-150, relheight=1, height=-50)
    elif tab_name == "HISTORY":
        history_content.place(x=150, y=50, relwidth=1, width=-150, relheight=1, height=-50)
    elif tab_name == "GUIDE":
        guide_content.place(x=150, y=50, relwidth=1, width=-150, relheight=1, height=-50)
    elif tab_name == "UTILITIES":
        utilities_content.place(x=150, y=50, relwidth=1, width=-150, relheight=1, height=-50)
    elif tab_name == "MENU":
        menu_content.place(x=150, y=50, relwidth=1, width=-150, relheight=1, height=-50)

# Frame chứa các nút chính ở trên
buttons_container = tk.Frame(left_menu, bg="black")
buttons_container.place(relx=0.5, rely=0.35, anchor="center")

# 5 nút menu chính với khoảng cách nhỏ hơn
tk.Button(buttons_container, text="INSTAGRAM", bg="black", fg="white", font=menu_font,
          command=lambda: switch_tab("INSTAGRAM"), bd=0, activebackground="#333", 
          activeforeground="white", width=15, height=2).pack(pady=5, padx=10)

tk.Button(buttons_container, text="CHECK LIVE", bg="black", fg="white", font=menu_font,
          command=lambda: switch_tab("CHECK LIVE"), bd=0, activebackground="#333", 
          activeforeground="white", width=15, height=2).pack(pady=5, padx=10)

tk.Button(buttons_container, text="HISTORY", bg="black", fg="white", font=menu_font,
          command=lambda: switch_tab("HISTORY"), bd=0, activebackground="#333", 
          activeforeground="white", width=15, height=2).pack(pady=5, padx=10)

tk.Button(buttons_container, text="GUIDE", bg="black", fg="white", font=menu_font,
          command=lambda: switch_tab("GUIDE"), bd=0, activebackground="#333", 
          activeforeground="white", width=15, height=2).pack(pady=5, padx=10)

tk.Button(buttons_container, text="UTILITIES", bg="black", fg="white", font=menu_font,
          command=lambda: switch_tab("UTILITIES"), bd=0, activebackground="#333", 
          activeforeground="white", width=15, height=2).pack(pady=5, padx=10)

# Nút MENU ở dưới cùng (position cố định)
menu_button = tk.Button(left_menu, text="MENU", bg="#1a1a1a", fg="white", 
                        font=("ROG Fonts STRIX SCAR", 12, "bold"),
                        command=lambda: switch_tab("MENU"), bd=0, activebackground="#333", 
                        activeforeground="white", width=13, height=2)
menu_button.place(relx=0.5, rely=0.92, anchor="center")

# ========================= TAB CONTENTS =========================

# ===== TAB 1: INSTAGRAM (Nội dung chính hiện tại) =====
instagram_content = tk.Frame(app, bg="white", width=900, height=500)
instagram_content.place(relx=0.5, rely=0.5, anchor="center")

center_frame = tk.Frame(instagram_content, bg="white")
center_frame.place(relx=0.5, y=0, anchor="n")

# ========================= KHỐI TRÁI (bây giờ nằm trong instagram_content) =========================
left_frame = tk.Frame(center_frame, bg="white")
left_frame.pack()

rog_font = ("ROG Fonts STRIX SCAR", 13, "bold")

# ========================= SAVE STATE MANAGEMENT =========================
is_saved = False
settings_hash = None

def calculate_settings_hash():
    """Tính hash của tất cả settings hiện tại"""
    mode = ui_mode_var.get().strip().lower()
    
    settings_str = f"{mode}|"
    
    if mode == "desktop":
        settings_str += f"{save_format}|{desktop_threads_entry.get()}|{desktop_follow_count_entry.get()}|{proxy_entry.get()}|"
        settings_str += f"{mail_var.get()}|{follow_var.get()}|{bioava_var.get()}|{pro_mode_var.get()}|{twofa_var.get()}|"
        settings_str += f"{category_var.get()}|{pro_type_var.get()}|{network_mode_var.get()}"
    elif mode == "mobile":
        settings_str += f"{save_format}|{mobile_threads_entry.get()}|{mobile_follow_count_entry.get()}|{proxy_mobile_entry.get() if proxy_mobile_entry else ''}|"
        settings_str += f"{mail_mobile_var.get()}|{enable_follow.get()}|{enable_avatar.get()}|"
        settings_str += f"{enable_Chuyen_nghiep.get()}|{enable_2fa.get()}|{network_mode_mobile_var.get()}"
    elif mode == "phone":
        settings_str += f"{save_format_phone}|{proxy_phone_entry.get()}|{phone_follow_count_var.get()}|"
        settings_str += f"{phone_net_mode.get()}|{proxy_format_var.get()}|{phone_ig_app_var.get()}|"
        settings_str += f"{mail_phone_var.get()}|{enable_2faphone.get()}|{enable_uppost.get()}|"
        settings_str += f"{enable_editprofile.get()}|{enable_autofollow.get()}|{enable_proaccount.get()}|"
        settings_str += f"{pro_category_var.get()}|{pro_type_var.get()}"
    
    return hashlib.md5(settings_str.encode()).hexdigest()

def save_settings():
    """Lưu settings và cập nhật trạng thái"""
    global is_saved, settings_hash
    
    mode = ui_mode_var.get().strip().lower()
    mode_name = {"desktop": "DESKTOP", "mobile": "MOBILE", "phone": "PHONE"}.get(mode, mode.upper())
    
    try:
        save_config()
        settings_hash = calculate_settings_hash()
        is_saved = True
        
        # Kiểm tra nếu chọn WARP-SPIN thì mở WARP Controller
        if mode == "desktop" and network_mode_var.get() == "warp-spin":
            open_warp_controller()
        elif mode == "mobile" and network_mode_mobile_var.get() == "warp-spin":
            open_warp_controller()
        
        messagebox.showinfo("Lưu thành công", f"✅ Đã lưu cài đặt giao diện {mode_name}!")
        log(f"💾 Đã lưu settings giao diện {mode_name}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"❌ Không thể lưu: {e}")
        log(f"❌ Lỗi khi lưu settings: {e}")

def check_settings_changed():
    """Kiểm tra xem settings có thay đổi sau khi save không"""
    if not is_saved:
        return True
    current_hash = calculate_settings_hash()
    return current_hash != settings_hash

# ===== HÀNG 1: RESTART | START | FILE REG =====
row1 = tk.Frame(left_frame, bg="white")
row1.pack(pady=(8,4), anchor="center")

def safe_start_process():
    """Wrapper cho start_process với kiểm tra save"""
    global is_saved
    
    if not is_saved:
        messagebox.showwarning("Chưa lưu", "⚠️ Bạn chưa lưu cài đặt!\nVui lòng nhấn SAVE trước khi START.")
        log("⚠️ Chưa lưu cài đặt. Vui lòng nhấn SAVE trước.")
        return
    
    if check_settings_changed():
        messagebox.showwarning("Cài đặt đã thay đổi", "⚠️ Cài đặt đã thay đổi sau lần SAVE cuối!\nVui lòng SAVE lại trước khi START.")
        log("⚠️ Cài đặt đã thay đổi. Vui lòng SAVE lại.")
        return
    
    # Nếu đã save và không thay đổi, cho phép start
    start_process()

btn_restart = tk.Button(row1, text="RESTART", width=18, height=1, bg="black", fg="white", font=rog_font, command=restart_tool)
btn_start = tk.Button(row1, text="START", width=18, height=1, bg="black", fg="white", font=rog_font, command=safe_start_process)
btn_file_reg = tk.Button(row1, text="FILE REG", width=18, height=1, bg="black", fg="white", font=rog_font, command=open_file_da_reg)

btn_restart.pack(side="left", padx=4)
btn_start.pack(side="left", padx=4, anchor="center")
btn_file_reg.pack(side="left", padx=4)

# ===== HÀNG 2: CHOOSE AVATAR | SAVE | CHOOSE CHROME =====
row2 = tk.Frame(left_frame, bg="white")
row2.pack(pady=4, anchor="center")

tk.Button(row2, text="CHOOSE AVATAR", width=18, height=1, bg="black", fg="white", font=rog_font, 
          command=select_ava_folder).pack(side="left", padx=4)
tk.Button(row2, text="SAVE", width=18, height=1, bg="black", fg="white", font=rog_font, 
          command=save_settings).pack(side="left", padx=4)
tk.Button(row2, text="CHOOSE CHROME", width=18, height=1, bg="black", fg="white", font=rog_font, 
          command=select_chrome).pack(side="left", padx=4)

# ===== HÀNG 3: Đã xóa WARP ON (chuyển xuống Desktop Settings) =====
row3 = tk.Frame(left_frame, bg="white")
row3.pack(pady=3, fill="x")

# ===== KHUNG GIAO DIỆN =====
ui_mode_var = tk.StringVar(value="desktop")

def set_ui_mode(mode):
    global is_saved
    ui_mode_var.set(mode)
    # Khi đổi giao diện, đánh dấu là chưa save
    is_saved = False
    # update_settings_visibility() sẽ tự động được gọi qua trace_add

giao_dien_frame = tk.LabelFrame(left_frame, text="GIAO DIỆN", bg="white", 
                                 font=("ROG Fonts STRIX SCAR", 11, "bold"), bd=2, relief="solid")
giao_dien_frame.pack(pady=(10,8), fill="x", padx=5)

# 3 nút giao diện xếp ngang
btn_container = tk.Frame(giao_dien_frame, bg="white")
btn_container.pack(pady=2, padx=8, anchor="center")

tk.Button(btn_container, text="DESKTOP", width=18, height=1, bg="black", fg="white", font=rog_font,
          command=lambda: set_ui_mode("desktop")).pack(side="left", padx=5)
tk.Button(btn_container, text="MOBILE", width=18, height=1, bg="black", fg="white", font=rog_font,
          command=lambda: set_ui_mode("mobile")).pack(side="left", padx=5)
tk.Button(btn_container, text="PHONE", width=18, height=1, bg="black", fg="white", font=rog_font,
          command=lambda: set_ui_mode("phone")).pack(side="left", padx=5)

# ===== AVATAR FOLDER SELECTION (fix indentation and undefined references) =====
def save_ava_folder_to_config(folder):
    """Lưu đường dẫn thư mục avatar vào config.json"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        config = {}
    config["ava_folder_path"] = folder
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_ava_folder_from_config():

# Khi khởi động, load lại từ config.json:
    """Đọc đường dẫn thư mục avatar từ config.json"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("ava_folder_path", "")
    except Exception:
        return ""
ava_folder_path = load_ava_folder_from_config()

# ========================= KHỐI GIỮA: Desktop Settings =========================
desktop_settings = tk.LabelFrame(instagram_content, text="Desktop Settings", bg="white", font=("ROG Fonts STRIX SCAR", 11, "bold"))
hidden_chrome_var = tk.BooleanVar(value=False)

def _position_desktop_settings():
    """Đặt Desktop Settings ở vị trí cố định giữa giao diện."""
    instagram_content.update_idletasks()
    desktop_settings.place(relx=0.5, y=250, anchor="n")

# app.after(60, _position_desktop_settings)  # ẨN khi mở app

# ========================= BỐ CỤC DESKTOP SETTINGS =========================
rog_font_small = ("ROG Fonts STRIX SCAR", 9, "bold")
rog_font_tiny = ("ROG Fonts STRIX SCAR", 8, "bold")

# HÀNG 1: Định dạng lưu
row_format = tk.Frame(desktop_settings, bg="white")
row_format.pack(fill="x", padx=6, pady=(4,2))

tk.Label(row_format, text="Định dạng lưu:", bg="white", font=rog_font_small).pack(side="left", padx=(0,4))
format_fields = ["Username","Pass","Mail","Cookie","2FA","Proxy","UID"]
save_format = []
format_boxes = []

def update_save_format(*_):
    global save_format
    save_format = [cb.get() for cb in format_boxes if cb.get()]
    try:
        save_config()
        log(f"💾 Định dạng lưu: {'|'.join(save_format)}")
    except Exception:
        pass

wanted = ["Username","Pass","Mail","Cookie","2FA"]
for i in range(5):
    cb = ttk.Combobox(row_format, values=format_fields, state="readonly", width=9)
    cb.set(save_format[i] if i < len(save_format) else wanted[i])
    cb.pack(side="left", padx=2)
    cb.bind("<<ComboboxSelected>>", update_save_format)
    format_boxes.append(cb)

# HÀNG 2: SỐ LUỒNG + SỐ FOLLOW + Proxy
row_threads = tk.Frame(desktop_settings, bg="white")
row_threads.pack(fill="x", padx=6, pady=2)

tk.Label(row_threads, text="NUMBER THREAD", bg="white", font=rog_font_small).pack(side="left", padx=(0,2))
desktop_threads_entry = tk.Entry(row_threads, width=6, justify="center")
desktop_threads_entry.insert(0, "1")
desktop_threads_entry.pack(side="left", padx=2)

tk.Label(row_threads, text="FOLLOW COUNT", bg="white", font=rog_font_small).pack(side="left", padx=(10,2))
desktop_follow_count_entry = tk.Entry(row_threads, width=6, justify="center")
desktop_follow_count_entry.insert(0, "5")
desktop_follow_count_entry.pack(side="left", padx=2)

tk.Label(row_threads, text="Proxy (IP:PORT)", bg="white", font=rog_font_small).pack(side="left", padx=(10,2))
proxy_entry = tk.Entry(row_threads, width=18, bg="lightgray", justify="center")
proxy_entry.insert(0, "")
proxy_entry.pack(side="left", padx=2)

# HÀNG 3: MAIL
row_mail = tk.Frame(desktop_settings, bg="white")
row_mail.pack(fill="x", padx=6, pady=2)

tk.Label(row_mail, text="MAIL:", bg="white", font=rog_font_small).pack(side="left", padx=(0,6))
mail_var = tk.StringVar(value="temp")
tk.Radiobutton(row_mail, text="temp-mail.asia", variable=mail_var, value="temp", bg="white").pack(side="left", padx=4)
tk.Radiobutton(row_mail, text="DropMail.me", variable=mail_var, value="drop", bg="white").pack(side="left", padx=4)

# HÀNG 4: JOB (Checkboxes)
row_job = tk.Frame(desktop_settings, bg="white")
row_job.pack(fill="x", padx=6, pady=2)

tk.Label(row_job, text="JOB:", bg="white", font=rog_font_small).pack(side="left", padx=(0,6))
follow_var = tk.BooleanVar(value=True)
bioava_var = tk.BooleanVar(value=True)
pro_mode_var = tk.BooleanVar(value=True)
twofa_var = tk.BooleanVar(value=True)

tk.Checkbutton(row_job, text="Follow", variable=follow_var, bg="white").pack(side="left", padx=4)
tk.Checkbutton(row_job, text="Giới tính + Bio + Ava + Post", variable=bioava_var, bg="white").pack(side="left", padx=4)
tk.Checkbutton(row_job, text="Bật Chuyên nghiệp", variable=pro_mode_var, bg="white").pack(side="left", padx=4)
tk.Checkbutton(row_job, text="Bật 2FA", variable=twofa_var, bg="white").pack(side="left", padx=4)

# HÀNG 5: PROFESSIONAL + CATEGORY + BIO
row_pro = tk.Frame(desktop_settings, bg="white")
row_pro.pack(fill="x", padx=6, pady=4)

# PROFESSIONAL
col_pro = tk.Frame(row_pro, bg="white")
col_pro.pack(side="left", padx=(0,10))
tk.Label(col_pro, text="PROFESSIONAL:", bg="white", font=rog_font_small).pack(anchor="w")

grp_cat = tk.Frame(col_pro, bg="white")
grp_cat.pack(anchor="w", pady=2)
tk.Label(grp_cat, text="Category:", bg="white", font=rog_font_tiny).grid(row=0, column=0, sticky="w", padx=(0,4))

category_var = tk.StringVar(value="Personal blog")
categories = ["Personal blog", "Art", "Shopping & retail", "Grocery Store",
              "Product/service", "Musician/band", "Health/beauty"]

row_idx = 0
col_idx = 1
for i, cat in enumerate(categories):
    tk.Radiobutton(grp_cat, text=cat, variable=category_var, value=cat, bg="white").grid(row=row_idx, column=col_idx, sticky="w", padx=2)
    col_idx += 1
    if col_idx > 3:  # 3 cột
        col_idx = 1
        row_idx += 1

grp_type = tk.Frame(col_pro, bg="white")
grp_type.pack(anchor="w", pady=(4,0))
tk.Label(grp_type, text="Loại tài khoản:", bg="white", font=rog_font_tiny).pack(side="left", padx=(0,4))
pro_type_var = tk.StringVar(value="Creator")
tk.Radiobutton(grp_type, text="Creator", variable=pro_type_var, value="Creator", bg="white").pack(side="left", padx=4)
tk.Radiobutton(grp_type, text="Business", variable=pro_type_var, value="Business", bg="white").pack(side="left", padx=4)

# === CHROME SETTINGS ===
col_chrome = tk.Frame(row_pro, bg="white")
col_chrome.pack(side="left")
tk.Label(col_chrome, text="CHROME SETTINGS:", bg="white", font=rog_font_small).pack(anchor="w")

chrome_size_frame = tk.LabelFrame(col_chrome, text="Chrome Size", bg="white", font=rog_font_tiny, bd=1)
chrome_size_frame.pack(fill="x", pady=2)

# === Danh sách kích thước có sẵn (từ nhỏ đến lớn) ===
size_list = [
    "100x100",
    "150x150",
    "200x200",
    "240x320",
    "320x480",
    "400x400",
    "480x800",
    "640x360",
    "800x600",
    "1024x768",
    "1280x720",
    "1366x768",
    "1440x900",
    "1600x900",
    "1680x1050",
    "1920x1080"
]

row_wh = tk.Frame(chrome_size_frame, bg="white")
row_wh.pack(anchor="w", pady=1)

tk.Label(row_wh, text="Chrome Window Size:", bg="white").pack(side="left", padx=2)
desktop_size_combo = ttk.Combobox(row_wh, values=size_list, width=12, state="readonly", justify="center")
desktop_size_combo.set("320x480")  # mặc định
desktop_size_combo.pack(side="left", padx=2)

row_scale = tk.Frame(chrome_size_frame, bg="white")
row_scale.pack(anchor="w", pady=1)
tk.Label(row_scale, text="Scale(%):", bg="white").pack(side="left", padx=2)
desktop_entry_scale = tk.Entry(row_scale, width=6, justify="center")
desktop_entry_scale.insert(0, "100")
desktop_entry_scale.pack(side="left", padx=2)

tk.Checkbutton(col_chrome, text="Ẩn Chrome (Headless)", variable=hidden_chrome_var, bg="white").pack(anchor="w", pady=2)

# HÀNG 7: NETWORK MODE (RadioButton: WIFI | WARP | WARP-SPIN | PROXY)
row_network = tk.Frame(desktop_settings, bg="white")
row_network.pack(fill="x", padx=6, pady=(4,6))

tk.Label(row_network, text="WIFI:", bg="white", font=rog_font_small).pack(side="left", padx=(0,6))

# Biến lưu chế độ mạng (mặc định là wifi)
network_mode_var = tk.StringVar(value="wifi")

tk.Radiobutton(row_network, text="WIFI", variable=network_mode_var, value="wifi", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=4)
tk.Radiobutton(row_network, text="WARP", variable=network_mode_var, value="warp", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=4)
tk.Radiobutton(row_network, text="WARP-SPIN", variable=network_mode_var, value="warp-spin", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=4)
tk.Radiobutton(row_network, text="PROXY", variable=network_mode_var, value="proxy", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=4)

# Nút chọn WARP Controller
tk.Button(row_network, text="📁 WARP Controller", bg="black", fg="white", 
          font=("ROG Fonts STRIX SCAR", 8, "bold"), command=select_warp_controller,
          width=18).pack(side="left", padx=10)

# ========================= MOBILE SETTINGS (mirror Desktop) =========================
mobile_settings = tk.LabelFrame(instagram_content, text="Mobile Settings", bg="white", font=("ROG Fonts STRIX SCAR", 11, "bold"))

def _position_mobile_settings():
    """Đặt Mobile Settings ở vị trí cố định giữa giao diện (giống Desktop)."""
    instagram_content.update_idletasks()
    mobile_settings.place(relx=0.5, y=250, anchor="n")

# app.after(120, _position_mobile_settings)  # ẨN khi mở app

# ===== Lấy mặc định từ Desktop nếu có =====
def _get_bool(v, fallback=False):
    try: return bool(v.get())
    except: return fallback

def _get_str(v, fallback=""):
    try: return str(v.get())
    except: return fallback

_follow_def   = _get_bool(globals().get("follow_var", None), True)
_fullpack_def = _get_bool(globals().get("gender_bio_ava_post_var", None), True)
_pro_mode_def = _get_bool(globals().get("pro_mode_var", None), True)
_twofa_def    = _get_bool(globals().get("twofa_var", None), True)
_pro_type_def = _get_str(globals().get("pro_type_var", None), "Creator")
_category_def = _get_str(globals().get("category_var", None), "Personal blog")

# ===== Biến Mobile =====
enable_follow        = tk.BooleanVar(value=_follow_def)
enable_avatar        = tk.BooleanVar(value=_fullpack_def)
enable_Chuyen_nghiep = tk.BooleanVar(value=_pro_mode_def)
enable_2fa           = tk.BooleanVar(value=_twofa_def)

pro_type_mobile = tk.StringVar(value=_pro_type_def)
category_mobile = tk.StringVar(value=_category_def)

# Mobile format boxes (separate from Desktop)
mobile_format_boxes = []
mail_mobile_var = tk.StringVar(value="temp")
proxy_mobile_entry = None
threads_entry = None
mobile_follow_count_entry = None
entry_width_m = None
entry_height_m = None
entry_scale_m = None

# HÀNG 1: Định dạng lưu (5 comboboxes ngang)
row_format_mobile = tk.Frame(mobile_settings, bg="white")
row_format_mobile.pack(fill="x", padx=6, pady=(4,2))

tk.Label(row_format_mobile, text="Định dạng lưu:", bg="white", font=rog_font_small).pack(side="left", padx=(0,6))

def update_mobile_save_format():
    global save_format
    save_format = [cb.get() for cb in mobile_format_boxes if cb.get()]
    save_config()
    log(f"💾 [Mobile] Định dạng lưu: {'|'.join(save_format)}")

wanted = ["Username", "Pass", "Mail", "Cookie", "2FA"]
for i in range(5):
    cb = ttk.Combobox(row_format_mobile, values=format_fields, state="readonly", width=10)
    cb.set(save_format[i] if i < len(save_format) else wanted[i])
    cb.pack(side="left", padx=2)
    cb.bind("<<ComboboxSelected>>", lambda e: update_mobile_save_format())
    mobile_format_boxes.append(cb)

# HÀNG 2: SỐ LUỒNG + SỐ FOLLOW + Proxy
row_counts_mobile = tk.Frame(mobile_settings, bg="white")
row_counts_mobile.pack(fill="x", padx=6, pady=2)

tk.Label(row_counts_mobile, text="NUMBER THREAD", bg="white", font=rog_font_small).pack(side="left", padx=(0,4))
mobile_threads_entry = tk.Entry(row_counts_mobile, width=6, justify="center", font=rog_font_tiny)
mobile_threads_entry.insert(0, "1")
mobile_threads_entry.pack(side="left", padx=(0,10))

tk.Label(row_counts_mobile, text="FOLLOW COUNT", bg="white", font=rog_font_small).pack(side="left", padx=(0,4))
mobile_follow_count_entry = tk.Entry(row_counts_mobile, width=6, justify="center", font=rog_font_tiny)
mobile_follow_count_entry.insert(0, "5")
mobile_follow_count_entry.pack(side="left", padx=(0,10))

tk.Label(row_counts_mobile, text="Proxy (IP:PORT)", bg="white", font=rog_font_small).pack(side="left", padx=(0,4))
proxy_mobile_entry = tk.Entry(row_counts_mobile, width=20, bg="lightgray", justify="center", font=rog_font_tiny)
proxy_mobile_entry.pack(side="left")

# HÀNG 3: MAIL SERVICE
row_mail_mobile = tk.Frame(mobile_settings, bg="white")
row_mail_mobile.pack(fill="x", padx=6, pady=2)

tk.Label(row_mail_mobile, text="MAIL:", bg="white", font=rog_font_small).pack(side="left", padx=(0,6))
tk.Radiobutton(row_mail_mobile, text="temp-mail.asia", variable=mail_mobile_var, value="temp", 
               bg="white").pack(side="left", padx=6)
tk.Radiobutton(row_mail_mobile, text="DropMail.me", variable=mail_mobile_var, value="drop", 
               bg="white").pack(side="left", padx=6)

# HÀNG 4: JOB CHECKBOXES
row_job_mobile = tk.Frame(mobile_settings, bg="white")
row_job_mobile.pack(fill="x", padx=6, pady=2)

tk.Label(row_job_mobile, text="JOB:", bg="white", font=rog_font_small).pack(side="left", padx=(0,6))
tk.Checkbutton(row_job_mobile, text="Follow (Mobile)", variable=enable_follow, bg="white").pack(side="left", padx=6)
tk.Checkbutton(row_job_mobile, text="Avatar (Mobile)", variable=enable_avatar, bg="white").pack(side="left", padx=6)
tk.Checkbutton(row_job_mobile, text="Bật Chuyên nghiệp (Mobile)", variable=enable_Chuyen_nghiep, bg="white",
               command=lambda: _sync_pro_mobile_state()).pack(side="left", padx=6)
tk.Checkbutton(row_job_mobile, text="Bật 2FA (Mobile)", variable=enable_2fa, bg="white").pack(side="left", padx=6)

# HÀNG 5: 3 COLUMNS (PROFESSIONAL | BIO | CHROME SETTINGS)
row_3cols_mobile = tk.Frame(mobile_settings, bg="white")
row_3cols_mobile.pack(fill="x", padx=6, pady=4)

# COL 1: PROFESSIONAL
col_pro_mobile = tk.LabelFrame(row_3cols_mobile, text="PROFESSIONAL:", bg="white", font=rog_font_tiny, 
                               relief="solid", borderwidth=1)
col_pro_mobile.pack(side="left", padx=(0,4), fill="both", expand=True)

# Category Grid
tk.Label(col_pro_mobile, text="Category:", bg="white", font=rog_font_tiny).pack(anchor="w", padx=4, pady=(2,0))
cat_grid_mobile = tk.Frame(col_pro_mobile, bg="white")
cat_grid_mobile.pack(fill="x", padx=4, pady=2)

CAT_OPTIONS = [
    "Personal blog", "Product/service", "Art", "Musician/band",
    "Shopping & retail", "Health/beauty", "Grocery Store"
]
for i, cat_name in enumerate(CAT_OPTIONS):
    row_idx = i // 2
    col_idx = i % 2
    tk.Radiobutton(cat_grid_mobile, text=cat_name, variable=category_mobile, value=cat_name, 
                   bg="white").grid(row=row_idx, column=col_idx, sticky="w", padx=2, pady=1)

# Account Type
tk.Label(col_pro_mobile, text="Loại tài khoản:", bg="white").pack(anchor="w", padx=4, pady=(4,0))
acc_type_frame_mobile = tk.Frame(col_pro_mobile, bg="white")
acc_type_frame_mobile.pack(anchor="w", padx=4, pady=2)
tk.Radiobutton(acc_type_frame_mobile, text="Creator", variable=pro_type_mobile, value="Creator", 
               bg="white").pack(anchor="w")
tk.Radiobutton(acc_type_frame_mobile, text="Business", variable=pro_type_mobile, value="Business", 
               bg="white").pack(anchor="w")

# COL 3: CHROME SETTINGS (MOBILE)
col_chrome_mobile = tk.LabelFrame(row_3cols_mobile, text="CHROME SETTINGS:", bg="white",
                                  font=rog_font_tiny, relief="solid", borderwidth=1)
col_chrome_mobile.pack(side="left", fill="both", expand=True)

# --- Chrome Size (Mobile) ---
chrome_size_frame = tk.LabelFrame(col_chrome_mobile, text="Chrome Size", bg="white", font=rog_font_tiny)
chrome_size_frame.pack(fill="x", padx=4, pady=4)

# === Danh sách kích thước có sẵn (từ nhỏ đến lớn, giống desktop) ===
mobile_size_list = [
    "100x100",
    "150x150",
    "200x200",
    "240x320",
    "320x480",
    "400x400",
    "480x800",
    "640x360",
    "800x600",
    "1024x768",
    "1280x720",
    "1366x768",
    "1440x900",
    "1600x900",
    "1680x1050",
    "1920x1080"
]

row_wh_m = tk.Frame(chrome_size_frame, bg="white")
row_wh_m.pack(anchor="w", pady=2)

tk.Label(row_wh_m, text="Chrome Window Size:", bg="white", font=rog_font_tiny).pack(side="left", padx=2)
mobile_size_combo = ttk.Combobox(row_wh_m, values=mobile_size_list, width=12, state="readonly", justify="center")
mobile_size_combo.set("375x667")  # mặc định giống iPhone 8
mobile_size_combo.pack(side="left", padx=2)

# --- Chrome Scale ---
row_scale_m = tk.Frame(chrome_size_frame, bg="white")
row_scale_m.pack(anchor="w", pady=2)

tk.Label(row_scale_m, text="Scale(%):", bg="white", font=rog_font_tiny).pack(side="left", padx=2)
mobile_entry_scale = tk.Entry(row_scale_m, width=6, justify="center")
mobile_entry_scale.insert(0, "100")
mobile_entry_scale.pack(side="left", padx=2)

hidden_chrome_mobile_var = tk.BooleanVar(value=False)
tk.Checkbutton(col_chrome_mobile, text="Ẩn Chrome (Headless)", variable=hidden_chrome_mobile_var, 
               bg="white").pack(anchor="w", pady=2, padx=4)

# ---- Khi bật/tắt chuyên nghiệp ----
def _sync_pro_mobile_state(*_):
    on = enable_Chuyen_nghiep.get()
    try:
        state_val = "normal" if on else "disabled"
        # Update Professional section widgets
        for w in col_pro_mobile.winfo_children():
            if isinstance(w, (tk.Label, tk.LabelFrame)):
                continue
            elif isinstance(w, tk.Frame):
                for child in w.winfo_children():
                    try: 
                        child.configure(state=state_val)
                    except: 
                        pass
            else:
                try:
                    w.configure(state=state_val)
                except:
                    pass
        col_pro_mobile.configure(fg=("black" if on else "#888"))
    except Exception:
        pass

_sync_pro_mobile_state()
enable_Chuyen_nghiep.trace_add("write", _sync_pro_mobile_state)

# ---- Gom cấu hình Mobile ----
def collect_mobile_profile_config():
    return {
        "follow": bool(enable_follow.get()),
        "avatar": bool(enable_avatar.get()),
        "pro_mode": bool(enable_Chuyen_nghiep.get()),
        "pro_type": str(pro_type_mobile.get()),
        "twofa": bool(enable_2fa.get()),
        "category": str(category_mobile.get()),
    }

# HÀNG 7: NETWORK MODE (RadioButton: WIFI | WARP | WARP-SPIN | PROXY)
row_network_mobile = tk.Frame(mobile_settings, bg="white")
row_network_mobile.pack(fill="x", padx=6, pady=(4,6))

tk.Label(row_network_mobile, text="WIFI:", bg="white", font=rog_font_small).pack(side="left", padx=(0,6))

# Biến lưu chế độ mạng Mobile (mặc định là wifi)
network_mode_mobile_var = tk.StringVar(value="wifi")

tk.Radiobutton(row_network_mobile, text="WIFI", variable=network_mode_mobile_var, value="wifi", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=6)
tk.Radiobutton(row_network_mobile, text="WARP", variable=network_mode_mobile_var, value="warp", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=6)
tk.Radiobutton(row_network_mobile, text="WARP-SPIN", variable=network_mode_mobile_var, value="warp-spin", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=6)
tk.Radiobutton(row_network_mobile, text="PROXY", variable=network_mode_mobile_var, value="proxy", bg="white", 
               font=rog_font_tiny).pack(side="left", padx=6)

# Nút chọn WARP Controller
tk.Button(row_network_mobile, text="📁 WARP Controller", bg="black", fg="white", 
          font=("ROG Fonts STRIX SCAR", 8, "bold"), command=select_warp_controller,
          width=18).pack(side="left", padx=10)

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

# ============= WRAPPER đặt bằng .place (KHÔNG CÓ SCROLLBAR) =============
phone_settings = tk.LabelFrame(instagram_content, text="Phone Settings", bg="white", font=("ROG Fonts STRIX SCAR", 11, "bold"))

def _position_phone_settings():
    """Đặt Phone Settings ở vị trí cố định giữa giao diện (giống Desktop)."""
    instagram_content.update_idletasks()
    phone_settings.place(relx=0.5, y=250, anchor="n")

# app.after(180, _position_phone_settings)  # ẨN khi mở app

# --- HÀNG 1: Định dạng lưu (ngang) + Proxy + Số lượng follow ---
top_bar_phone = tk.Frame(phone_settings, bg="white")
top_bar_phone.pack(fill="x", padx=6, pady=(4,6))

# Định dạng lưu
tk.Label(top_bar_phone, text="Định dạng lưu:", bg="white", font=rog_font_small).grid(row=0, column=0, sticky="w", padx=(0,6))

format_fields = ["Username","Pass","Mail","Cookie","2FA","Proxy","UID"]
save_format_phone = []
format_boxes_phone = []

def update_save_format_phone(*_):
    global save_format_phone
    save_format_phone = [cb.get() for cb in format_boxes_phone if cb.get()]
    try:
        save_config()
        log(f"💾 [Phone] Định dạng lưu: {'|'.join(save_format_phone)}")
    except Exception:
        pass

wanted_phone = ["Username","Pass","Mail","Cookie","2FA"]
for i in range(5):
    cb = ttk.Combobox(top_bar_phone, values=format_fields, state="readonly", width=10)
    cb.set(save_format_phone[i] if i < len(save_format_phone) else wanted_phone[i])
    cb.grid(row=0, column=i+1, padx=2)
    cb.bind("<<ComboboxSelected>>", update_save_format_phone)
    format_boxes_phone.append(cb)

# HÀNG 2: Proxy (IP:PORT) + Số lượng follow
row2_phone = tk.Frame(phone_settings, bg="white")
row2_phone.pack(fill="x", padx=6, pady=(0,6))

# Proxy
proxy_phone_frame_inline = tk.Frame(row2_phone, bg="white")
proxy_phone_frame_inline.pack(side="left", padx=(0,10))
tk.Label(proxy_phone_frame_inline, text="Proxy (IP:PORT)", bg="white", font=rog_font_small).pack(side="left", padx=(0,4))
proxy_phone_entry = tk.Entry(proxy_phone_frame_inline, width=20, bg="lightgray", justify="center")
proxy_phone_entry.pack(side="left")
proxy_phone_entry.insert(0, "")

# Số lượng follow
follow_phone_frame = tk.Frame(row2_phone, bg="white")
follow_phone_frame.pack(side="left")
phone_follow_count_var = tk.IntVar(value=10)
tk.Label(follow_phone_frame, text="FOLLOW COUNT:", bg="white", font=rog_font_small).pack(side="left", padx=(0,4))
ttk.Spinbox(follow_phone_frame, from_=1, to=30, textvariable=phone_follow_count_var, width=5).pack(side="left")

# ====================== BẢNG THIẾT BỊ 3 CỘT ======================
ttk.Label(phone_settings, text="Thiết bị ADB (chọn 1 hoặc nhiều):", background="white")\
   .pack(anchor="w", padx=8, pady=(8, 2))

cols = ("udid", "view", "pick", "status")
phone_device_tree = ttk.Treeview(phone_settings, columns=cols, show="headings", height=6)
phone_device_tree.heading("udid", text="DEVICE UDID")
phone_device_tree.heading("view", text="VIEW")
phone_device_tree.heading("pick", text="CHỌN")
phone_device_tree.heading("status", text="STATUS")
phone_device_tree.column("udid", width=220, anchor="w")
phone_device_tree.column("view", width=60, anchor="center")
phone_device_tree.column("pick", width=60, anchor="center")
phone_device_tree.column("status", width=100, anchor="center")
phone_device_tree.pack(fill="both", expand=True, padx=8)

try:
    phone_device_tree.bind("<Button-1>", _toggle_cell)
except Exception:
    pass

# ========== Thêm/Viết lại: Context menu cho phone_device_tree (Right-click) ==========
def _update_tree_tick_for_udid(udid: str):
    """Cập nhật hiển thị tick trên tree theo device_state."""
    try:
        st = device_state.get(udid, {"view": False, "pick": False})
        if phone_device_tree is not None and udid in phone_device_tree.get_children():
            phone_device_tree.set(udid, column="view", value=_tick(st.get("view", False)))
            phone_device_tree.set(udid, column="pick", value=_tick(st.get("pick", False)))
    except Exception:
        pass

def phone_select_all_devices():
    """Chọn toàn bộ thiết bị (cột CHỌN)."""
    try:
        for ud in list(device_state.keys()):
            device_state.setdefault(ud, {})["pick"] = True
            _update_tree_tick_for_udid(ud)
        log("✅ Đã chọn toàn bộ thiết bị (CHỌN).")
    except Exception as e:
        log(f"⚠️ Lỗi khi chọn toàn bộ thiết bị: {e}")

def phone_select_all_view():
    """Chọn toàn bộ view (cột VIEW)."""
    try:
        for ud in list(device_state.keys()):
            device_state.setdefault(ud, {})["view"] = True
            _update_tree_tick_for_udid(ud)
        log("✅ Đã chọn toàn bộ View.")
    except Exception as e:
        log(f"⚠️ Lỗi khi chọn toàn bộ View: {e}")

def phone_deselect_all_devices():
    """Bỏ chọn toàn bộ thiết bị (cột CHỌN)."""
    try:
        for ud in list(device_state.keys()):
            device_state.setdefault(ud, {})["pick"] = False
            _update_tree_tick_for_udid(ud)
        log("✅ Đã bỏ chọn toàn bộ thiết bị.")
    except Exception as e:
        log(f"⚠️ Lỗi khi bỏ chọn toàn bộ thiết bị: {e}")

def phone_deselect_all_view():
    """Bỏ chọn toàn bộ view (cột VIEW)."""
    try:
        for ud in list(device_state.keys()):
            device_state.setdefault(ud, {})["view"] = False
            _update_tree_tick_for_udid(ud)
        log("✅ Đã bỏ chọn toàn bộ View.")
    except Exception as e:
        log(f"⚠️ Lỗi khi bỏ chọn toàn bộ View: {e}")

def phone_select_selected_devices():
    """Chọn (tick CHỌN) cho các thiết bị đang được bôi đen (selected)."""
    try:
        sel = phone_device_tree.selection()
        if not sel:
            log("ℹ️ Chưa bôi đen thiết bị nào để chọn.")
            return
        for ud in sel:
            device_state.setdefault(ud, {})["pick"] = True
            _update_tree_tick_for_udid(ud)
        log(f"✅ Đã chọn {len(sel)} thiết bị đang bôi đen.")
    except Exception as e:
        log(f"⚠️ Lỗi khi chọn thiết bị đang bôi đen: {e}")

# ------------------- Connect / Disconnect TCP/IP helpers -------------------
def _resolve_device_ip(device_id: str) -> str | None:
    """Cố gắng lấy IP của device (wlan0 hoặc ip route)."""
    try:
        ip_info = subprocess.check_output(
            ["adb", "-s", device_id, "shell", "ip", "addr", "show", "wlan0"],
            encoding="utf-8", errors="ignore"
        )
        lines = [line.strip() for line in ip_info.splitlines() if "inet " in line]
        if lines:
            return lines[0].split()[1].split("/")[0]
    except Exception:
        pass
    try:
        route_out = subprocess.check_output(
            ["adb", "-s", device_id, "shell", "ip", "route"], encoding="utf-8", errors="ignore"
        )
        m = re.search(r"src\s+(\d+\.\d+\.\d+\.\d+)", route_out)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None

def connect_tcp(device_id: str, port: int = 5555):
    """Kết nối thiết bị adb qua TCP/IP (mặc định port=5555)."""
    try:
        ip = _resolve_device_ip(device_id)
        if not ip:
            raise Exception("Không tìm thấy IP (thiết bị chưa bật Wi-Fi?).")

        subprocess.run(["adb", "-s", device_id, "tcpip", str(port)], check=True)
        subprocess.run(["adb", "connect", f"{ip}:{port}"], check=True)
        log(f"✅ Đã kết nối {device_id} qua {ip}:{port}")
    except Exception as e:
        log(f"❌ Kết nối TCP/IP thất bại cho {device_id}: {e}")

def disconnect_tcp(device_id: str, port: int = 5555):
    """Ngắt kết nối ADB TCP/IP cho thiết bị."""
    try:
        ip = _resolve_device_ip(device_id)
        if ip:
            subprocess.run(["adb", "disconnect", f"{ip}:{port}"], check=False)
            subprocess.run(["adb", "disconnect", ip], check=False)
            log(f"⛔ Đã ngắt kết nối {device_id} ({ip}:{port})")
        else:
            subprocess.run(["adb", "disconnect", device_id], check=False)
            log(f"⛔ Đã gửi lệnh disconnect cho {device_id}")
    except Exception as e:
        log(f"⚠️ Ngắt TCP/IP thất bại cho {device_id}: {e}")

# --- song song nhiều thiết bị (theo tick CHỌN) ---
def phone_connect_tcp_prompt():
    """Kết nối TCP/IP song song cho các thiết bị được tick (CHỌN)."""
    try:
        sel = get_checked_udids("pick")  # lấy danh sách tick CHỌN
        if not sel:
            messagebox.showinfo("TCP/IP", "Vui lòng tick (CHỌN) ít nhất 1 thiết bị trong danh sách.")
            return

        port = 5555
        for ud in list(sel):
            threading.Thread(target=connect_tcp, args=(ud, port), daemon=True).start()

        log(f"🔌 Đang thực hiện kết nối TCP/IP cho {len(sel)} thiết bị ...")
    except Exception as e:
        log(f"⚠️ Lỗi phone_connect_tcp_prompt: {e}")

def phone_disconnect_tcp():
    """Ngắt kết nối TCP/IP song song cho các thiết bị được tick (CHỌN)."""
    try:
        sel = get_checked_udids("pick")
        if not sel:
            messagebox.showinfo("Disconnect TCP/IP", "Vui lòng tick (CHỌN) ít nhất 1 thiết bị trong danh sách.")
            return

        port = 5555
        for ud in list(sel):
            threading.Thread(target=disconnect_tcp, args=(ud, port), daemon=True).start()

        log(f"⛔ Đang ngắt kết nối TCP/IP cho {len(sel)} thiết bị ...")
    except Exception as e:
        log(f"⚠️ Lỗi phone_disconnect_tcp: {e}")

# Tạo Menu chuột phải (cập nhật các mục)
phone_tree_menu = tk.Menu(app, tearoff=0)
phone_tree_menu.add_command(label="✅ Chọn thiết bị đang bôi đen", command=phone_select_selected_devices)
phone_tree_menu.add_command(label="✅ Chọn toàn bộ thiết bị", command=phone_select_all_devices)
phone_tree_menu.add_command(label="✅ Chọn toàn bộ View", command=phone_select_all_view)
phone_tree_menu.add_separator()
phone_tree_menu.add_command(label="🔌 Connect TCP/IP (CHỌN)", command=phone_connect_tcp_prompt)
phone_tree_menu.add_command(label="⛔ Disconnect TCP/IP (CHỌN)", command=phone_disconnect_tcp)
phone_tree_menu.add_separator()
phone_tree_menu.add_command(label="❌ Bỏ chọn toàn bộ Thiết bị", command=phone_deselect_all_devices)
phone_tree_menu.add_command(label="❌ Bỏ chọn toàn bộ View", command=phone_deselect_all_view)
phone_tree_menu.add_separator()
phone_tree_menu.add_command(label="🔄 Refresh ADB Devices", command=refresh_adb_devices_table)
phone_tree_menu.add_command(label="🛑 Kill ADB & Reload", command=lambda: threading.Thread(target=kill_adb_and_reload, daemon=True).start())
phone_tree_menu.add_command(label="🗑️ Delete Pictures & Reboot (CHỌN)", command=lambda: threading.Thread(target=delete_pictures_and_reboot, daemon=True).start())
def _show_phone_tree_menu(event):
    try:
        row = phone_device_tree.identify_row(event.y)
        if row and row not in phone_device_tree.selection():
            phone_device_tree.selection_set(row)
        phone_tree_menu.tk_popup(event.x_root, event.y_root)
    finally:
        phone_tree_menu.grab_release()

# Bind chuột phải (Windows/Linux) + fallback macOS middle button
try:
    phone_device_tree.bind("<Button-3>", _show_phone_tree_menu)
    phone_device_tree.bind("<Button-2>", _show_phone_tree_menu)
except Exception:
    pass

# ---- Thêm: Ctrl+A để chọn tất cả hàng trong Treeview ----
def phone_select_all_rows(event=None):
    try:
        all_items = phone_device_tree.get_children()
        phone_device_tree.selection_set(all_items)
    except Exception:
        pass
    return "break"

try:
    phone_device_tree.bind("<Control-a>", phone_select_all_rows)
    phone_device_tree.bind("<Control-A>", phone_select_all_rows)
except Exception:
    pass

# HÀNG NÚT: Refresh | Kill ADB | Sắp xếp | Kích thước
buttons_row = tk.Frame(phone_settings, bg="white")
buttons_row.pack(fill="x", padx=8, pady=(4,6))

ttk.Button(buttons_row, text="REFRESH ADB DEVICES", command=refresh_adb_devices_table)\
   .pack(side="left", padx=(0,4))

ttk.Button(buttons_row, text="KILL ADB & RELOAD", 
           command=lambda: threading.Thread(target=kill_adb_and_reload, daemon=True).start())\
    .pack(side="left", padx=(0,4))

ttk.Button(buttons_row, text="ARRANGE PHONE VIEW", command=open_and_arrange)\
    .pack(side="left", padx=(0,4))

combo_res = ttk.Combobox(
    buttons_row,
    values=["360x640", "540x960", "720x1280", "1080x1920"],
    state="readonly",
    width=12
)
combo_res.set("360x640")
combo_res.bind("<<ComboboxSelected>>", change_resolution)
combo_res.pack(side="left")

ttk.Button(buttons_row, text="DELETE PIC",
           command=lambda: threading.Thread(target=delete_pictures_and_reboot, daemon=True).start())\
    .pack(side="left", padx=(0,4))

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

# ======================= HÀNG NÚT: Mở Proxy.txt | Chọn folder | scrcpy | Mở View =======================
actions_buttons = tk.Frame(phone_settings, bg="white")
actions_buttons.pack(fill="x", padx=PHONE_PADX, pady=(4, PHONE_PADY))

ttk.Button(actions_buttons, text="OPEN Proxy.txt", command=open_proxy_txt)\
   .pack(side="left", padx=(0, 3))
ttk.Button(actions_buttons, text="CHOOSE PHOTO FOLDER", command=choose_photo_folder_phone)\
   .pack(side="left", padx=(0, 3))
ttk.Button(actions_buttons, text="CHOOSE scrcpy.exe", command=choose_scrcpy_path)\
   .pack(side="left", padx=(0, 3))
ttk.Button(actions_buttons, text="OPEN VIEW PHONE",
           command=lambda: open_scrcpy_for_list(get_checked_udids("view")))\
   .pack(side="left")

# ======================= Network Mode =======================
net_label_frame = tk.Frame(phone_settings, bg="white")
net_label_frame.pack(fill="x", padx=PHONE_PADX, pady=(4, PHONE_PADY))

tk.Label(net_label_frame, text="CHOOSE WIFI:", bg="white", font=("ROG Fonts STRIX SCAR", 9, "bold")).pack(side="left", padx=(0,8))
ttk.Radiobutton(net_label_frame, text="WiFi", value="wifi", variable=phone_net_mode).pack(side="left", padx=4)
ttk.Radiobutton(net_label_frame, text="WARP", value="warp", variable=phone_net_mode).pack(side="left", padx=4)
ttk.Radiobutton(net_label_frame, text="PROXY", value="proxy", variable=phone_net_mode).pack(side="left", padx=4)
ttk.Radiobutton(net_label_frame, text="SIM 4G", value="sim", variable=phone_net_mode).pack(side="left", padx=4)
ttk.Radiobutton(net_label_frame, text="1.1.1.1", value="1.1.1.1", variable=phone_net_mode).pack(side="left", padx=4)

# ======================= Proxy Type =======================
proxy_format_var = tk.StringVar(value="ip_port")

try:
    proxy_format_var.trace_add('write', lambda *args: save_config())
except Exception:
    pass

proxy_type_frame = tk.Frame(phone_settings, bg="white")
proxy_type_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

tk.Label(proxy_type_frame, text="PROXY:", bg="white", font=("ROG Fonts STRIX SCAR", 9, "bold")).pack(side="left", padx=(0,8))
ttk.Radiobutton(proxy_type_frame, text="IP:PORT", variable=proxy_format_var, value="ip_port").pack(side="left", padx=4)
ttk.Radiobutton(proxy_type_frame, text="IP:PORT:USER:PASS", variable=proxy_format_var, value="ip_port_userpass").pack(side="left", padx=4)

# ======================= App Instagram =======================
def _persist_ig_choice():
    try:
        save_phone_paths()
    except Exception:
        pass

app_select_frame = tk.Frame(phone_settings, bg="white")
app_select_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

tk.Label(app_select_frame, text="APP:", bg="white", font=("ROG Fonts STRIX SCAR", 9, "bold")).pack(side="left", padx=(0,8))
ttk.Radiobutton(app_select_frame, text="INSTAGRAM", value="instagram",
                variable=phone_ig_app_var, command=_persist_ig_choice).pack(side="left", padx=4)
ttk.Radiobutton(app_select_frame, text="INSTAGRAM LITE", value="instagram_lite",
                variable=phone_ig_app_var, command=_persist_ig_choice).pack(side="left", padx=4)
ttk.Radiobutton(app_select_frame, text="CHROME", value="chrome",
                variable=phone_ig_app_var, command=_persist_ig_choice).pack(side="left", padx=4)
# ======================= MAIL SERVICE =======================
mail_frame = tk.Frame(phone_settings, bg="white")
mail_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

tk.Label(mail_frame, text="MAIL:", bg="white", font=("ROG Fonts STRIX SCAR", 9, "bold")).pack(side="left", padx=(0,8))
mail_phone_var = tk.StringVar(value="temp")
tk.Radiobutton(mail_frame, text="temp-mail.asia", variable=mail_phone_var, value="temp", bg="white").pack(side="left", padx=4)
tk.Radiobutton(mail_frame, text="DropMail.me", variable=mail_phone_var, value="drop", bg="white").pack(side="left", padx=4)

# ======================= JOB (Checkboxes) =======================
job_frame = tk.Frame(phone_settings, bg="white")
job_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

tk.Label(job_frame, text="JOB INSTAGRAM:", bg="white", font=("ROG Fonts STRIX SCAR", 9, "bold")).pack(side="left", padx=(0,8))

enable_2faphone    = tk.BooleanVar(value=False)
enable_uppost      = tk.BooleanVar(value=False)
enable_editprofile = tk.BooleanVar(value=False)
enable_autofollow  = tk.BooleanVar(value=False)
enable_proaccount  = tk.BooleanVar(value=False)

ttk.Checkbutton(job_frame, text="2FA", variable=enable_2faphone).pack(side="left", padx=4)
ttk.Checkbutton(job_frame, text="UP POST", variable=enable_uppost).pack(side="left", padx=4)
ttk.Checkbutton(job_frame, text="EDIT PROFILE", variable=enable_editprofile).pack(side="left", padx=4)
ttk.Checkbutton(job_frame, text="FOLLOW", variable=enable_autofollow).pack(side="left", padx=4)
ttk.Checkbutton(job_frame, text="PROFESSIONAL", variable=enable_proaccount).pack(side="left", padx=4)

# ======================= PROFESSIONAL ACCOUNT =======================
pro_settings_frame = tk.Frame(phone_settings, bg="white")
pro_settings_frame.pack(fill="x", padx=PHONE_PADX, pady=(2, PHONE_PADY))

tk.Label(pro_settings_frame, text="PRO:", bg="white", font=("ROG Fonts STRIX SCAR", 9, "bold")).pack(side="left", padx=(0,8))

CATEGORIES = [
    "Artist", "Musician/band", "Blogger", "Clothing (Brand)",
    "Community", "Digital creator", "Education", "Entrepreneur",
    "Health/beauty", "Editor", "Writer", "Personal blog",
    "Product/service", "Gamer", "Restaurant",
    "Beauty, cosmetic & personal care", "Grocery Store",
    "Photographer", "Shopping & retail", "Reel creator"
]
pro_category_var = tk.StringVar(value="Reel creator")
pro_type_var = tk.StringVar(value="Creator")

tk.Label(pro_settings_frame, text="Category:", bg="white").pack(side="left", padx=(0,4))
ttk.Combobox(pro_settings_frame, textvariable=pro_category_var, values=CATEGORIES, width=20, state="readonly").pack(side="left", padx=(0,10))

tk.Label(pro_settings_frame, text="Type:", bg="white").pack(side="left", padx=(0,4))
ttk.Combobox(pro_settings_frame, textvariable=pro_type_var, values=["Creator", "Business"], width=10, state="readonly").pack(side="left")

# ========================= ẨN/HIỆN 3 BẢNG SETTINGS THEO CHẾ ĐỘ =========================
def update_settings_visibility(*_):
    """Ẩn/hiện Desktop - Mobile - Phone Settings tùy theo chế độ GIAO DIỆN."""
    mode = ui_mode_var.get().strip().lower()
    try:
        # Ẩn tất cả trước
        desktop_settings.place_forget()
        mobile_settings.place_forget()
        phone_settings.place_forget()
        
        # Hiện và ENABLE frame tương ứng
        if mode == "desktop":
            _position_desktop_settings()
            _set_container_enabled(desktop_settings, enabled=True)
            _set_container_enabled(mobile_settings, enabled=False)
            _set_container_enabled(phone_settings, enabled=False)
        elif mode == "mobile":
            _position_mobile_settings()
            _set_container_enabled(desktop_settings, enabled=False)
            _set_container_enabled(mobile_settings, enabled=True)
            _set_container_enabled(phone_settings, enabled=False)
        elif mode == "phone":
            _position_phone_settings()
            _set_container_enabled(desktop_settings, enabled=False)
            _set_container_enabled(mobile_settings, enabled=False)
            _set_container_enabled(phone_settings, enabled=True)
        # else: không hiện gì cả (để trống)
    except Exception as e:
        print("⚠️ Lỗi update_settings_visibility:", e)

# Gắn sự kiện cho radio "GIAO DIỆN"
ui_mode_var.trace_add("write", lambda *_: update_settings_visibility())

# ======================= QUÉT THIẾT BỊ LẦN ĐẦU =======================
try:
    refresh_adb_devices_table()
except Exception:
    pass

# ========================= TAB 2 & 3 CONTENT =========================
# ===== TAB 2: CHECK LIVE =====
checklive_content = tk.Frame(app, bg="white")

# Status bar (LIVE/DIE/RATE) cho Check Live
checklive_status_frame = tk.Frame(checklive_content, bg="white")
checklive_status_frame.pack(side="top", anchor="w", pady=5, padx=5)

checklive_live_var = tk.StringVar(value="0")
checklive_die_var = tk.StringVar(value="0")
checklive_rate_var = tk.StringVar(value="0%")

rog_font_checklive = ("ROG Fonts STRIX SCAR", 13, "bold")
tk.Label(checklive_status_frame, text="LIVE:", fg="green", bg="white", font=rog_font_checklive).grid(row=0, column=0, padx=5)
tk.Label(checklive_status_frame, textvariable=checklive_live_var, fg="green", bg="white", font=rog_font_checklive).grid(row=0, column=1, padx=5)
tk.Label(checklive_status_frame, text="DIE:",  fg="red",   bg="white", font=rog_font_checklive).grid(row=0, column=2, padx=5)
tk.Label(checklive_status_frame, textvariable=checklive_die_var,  fg="red",   bg="white", font=rog_font_checklive).grid(row=0, column=3, padx=5)
tk.Label(checklive_status_frame, text="RATE:", fg="blue",  bg="white", font=rog_font_checklive).grid(row=0, column=6, padx=5)
tk.Label(checklive_status_frame, textvariable=checklive_rate_var, fg="blue",  bg="white", font=rog_font_checklive).grid(row=0, column=7, padx=5)

# Main frame cho Tree và Logs
checklive_main_frame = tk.Frame(checklive_content, bg="white")
checklive_main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Tree Frame
checklive_tree_frame = tk.LabelFrame(checklive_main_frame, text="Accounts", bg="white", font=("Arial", 10, "bold"))
checklive_tree_frame.pack(side="top", fill="both", expand=True, padx=5, pady=(0,5))

checklive_cols = ["STT","TRẠNG THÁI","USERNAME","PASS","MAIL","PHONE","COOKIE","2FA","TOKEN","IP","PROXY","LIVE","DIE","FOLLOW","POST","AVATAR","GENDER","BIO","PROFESSIONAL"]
checklive_tree = ttk.Treeview(checklive_tree_frame, columns=checklive_cols, show="headings", height=12)

# Scrollbars cho Tree
checklive_vsb = ttk.Scrollbar(checklive_tree_frame, orient="vertical", command=checklive_tree.yview)
checklive_tree.configure(yscrollcommand=checklive_vsb.set)
checklive_vsb.pack(side="right", fill="y")

checklive_hsb = ttk.Scrollbar(checklive_tree_frame, orient="horizontal", command=checklive_tree.xview)
checklive_tree.configure(xscrollcommand=checklive_hsb.set)
checklive_hsb.pack(side="bottom", fill="x")

checklive_tree.pack(fill="both", expand=True)

# Cấu hình columns và headings
for col in checklive_cols:
    checklive_tree.heading(col, text=col, anchor="center")
    checklive_tree.column(col, width=120, anchor="center")

# Tags cho LIVE/DIE
checklive_tree.tag_configure("LIVE", background="lightgreen")
checklive_tree.tag_configure("DIE", background="tomato")

# ===== CHỨC NĂNG CTRL+A VÀ CONTEXT MENU CHO CHECK LIVE TREE =====

# Hàm chọn tất cả items trong Tree (Ctrl+A)
def select_all_checklive(event=None):
    """Chọn tất cả items trong bảng Check Live Tree"""
    items = checklive_tree.get_children()
    for item in items:
        checklive_tree.selection_add(item)
    return "break"  # Ngăn không cho event lan truyền

# Bind Ctrl+A cho Tree
checklive_tree.bind("<Control-a>", select_all_checklive)
checklive_tree.bind("<Control-A>", select_all_checklive)

# Hàm xóa items đã chọn
def delete_selected_checklive():
    """Xóa các items đã chọn trong bảng Check Live"""
    selected = checklive_tree.selection()
    if not selected:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 tài khoản để xóa!")
        return
    
    confirm = messagebox.askyesno("Xác nhận", 
                                  f"Bạn có chắc muốn xóa {len(selected)} tài khoản đã chọn?")
    if confirm:
        for item in selected:
            checklive_tree.delete(item)
        
        # Cập nhật lại STT
        remaining_items = checklive_tree.get_children()
        for idx, item in enumerate(remaining_items, start=1):
            values = list(checklive_tree.item(item, "values"))
            values[0] = idx  # Cập nhật STT
            checklive_tree.item(item, values=values)
        
        messagebox.showinfo("Thành công", f"Đã xóa {len(selected)} tài khoản!")

# Hàm xóa tất cả items
def delete_all_checklive():
    """Xóa tất cả items trong bảng Check Live"""
    items = checklive_tree.get_children()
    if not items:
        messagebox.showinfo("Thông báo", "Bảng đang trống!")
        return
    
    confirm = messagebox.askyesno("Xác nhận", 
                                  f"Bạn có chắc muốn xóa TẤT CẢ {len(items)} tài khoản?")
    if confirm:
        for item in items:
            checklive_tree.delete(item)
        messagebox.showinfo("Thành công", "Đã xóa tất cả tài khoản!")

# Tạo Context Menu (Right-click menu)
checklive_context_menu = tk.Menu(app, tearoff=0, bg="white", fg="black", 
                                 font=("Arial", 10), activebackground="#0078D7", 
                                 activeforeground="white")

checklive_context_menu.add_command(label="➕ Thêm tài khoản", 
                                   command=lambda: open_add_account_window())
checklive_context_menu.add_separator()
checklive_context_menu.add_command(label="🗑️ Xóa đã chọn", 
                                   command=delete_selected_checklive)
checklive_context_menu.add_command(label="🗑️ Xóa tất cả", 
                                   command=delete_all_checklive)
checklive_context_menu.add_separator()
checklive_context_menu.add_command(label="✅ Chọn tất cả (Ctrl+A)", 
                                   command=select_all_checklive)

# Hàm hiển thị context menu
def show_checklive_context_menu(event):
    """Hiển thị context menu khi chuột phải"""
    try:
        checklive_context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        checklive_context_menu.grab_release()

# Bind chuột phải cho Tree
checklive_tree.bind("<Button-3>", show_checklive_context_menu)

# Hàm mở cửa sổ ADD ACCOUNT
def open_add_account_window():
    """Mở cửa sổ để thêm tài khoản vào bảng Check Live"""
    add_window = tk.Toplevel(app)
    add_window.title("Add Account")
    add_window.geometry("700x500")
    add_window.configure(bg="white")
    add_window.resizable(False, False)
    
    # Title
    title_label = tk.Label(add_window, text="THÊM TÀI KHOẢN", 
                           font=("ROG Fonts STRIX SCAR", 16, "bold"), 
                           bg="white", fg="black")
    title_label.pack(pady=10)
    
    # Frame cho định dạng
    format_frame = tk.LabelFrame(add_window, text="Định dạng tài khoản", 
                                 bg="white", font=("Arial", 10, "bold"))
    format_frame.pack(fill="x", padx=20, pady=(10, 5))
    
    # Dropdown chọn định dạng
    format_options = [
        "Username|Pass",
        "Username|Pass|Mail",
        "Username|Pass|Mail|Cookie",
        "Username|Pass|Mail|Cookie|2FA",
        "Username|Pass|Mail|2FA",
        "Mail|Pass",
        "Cookie"
    ]
    
    format_var = tk.StringVar(value="Username|Pass|Mail")
    
    tk.Label(format_frame, text="Chọn định dạng:", bg="white", 
             font=("Arial", 10)).pack(side="left", padx=10, pady=10)
    format_combo = ttk.Combobox(format_frame, textvariable=format_var, 
                                values=format_options, state="readonly", width=35)
    format_combo.pack(side="left", padx=10, pady=10)
    
    # Frame cho nhập tài khoản
    input_frame = tk.LabelFrame(add_window, text="Nhập tài khoản (mỗi dòng 1 tài khoản)", 
                               bg="white", font=("Arial", 10, "bold"))
    input_frame.pack(fill="both", expand=True, padx=20, pady=5)
    
    # Text widget để nhập nhiều dòng
    account_text = scrolledtext.ScrolledText(input_frame, width=70, height=15, 
                                             bg="lightyellow", fg="black", 
                                             font=("Consolas", 10))
    account_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Placeholder text
    placeholder = "Ví dụ:\nusername1|password1|email1@gmail.com\nusername2|password2|email2@gmail.com\n..."
    account_text.insert("1.0", placeholder)
    account_text.config(fg="gray")
    
    # Xóa placeholder khi focus
    def on_focus_in(event):
        if account_text.get("1.0", "end-1c") == placeholder:
            account_text.delete("1.0", "end")
            account_text.config(fg="black")
    
    def on_focus_out(event):
        if not account_text.get("1.0", "end-1c").strip():
            account_text.insert("1.0", placeholder)
            account_text.config(fg="gray")
    
    account_text.bind("<FocusIn>", on_focus_in)
    account_text.bind("<FocusOut>", on_focus_out)
    
    # Hàm thêm tài khoản vào Tree
    def add_accounts_to_tree():
        text_content = account_text.get("1.0", "end-1c").strip()
        
        if not text_content or text_content == placeholder:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tài khoản!")
            return
        
        lines = text_content.split("\n")
        added_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split("|")
            selected_format = format_var.get()
            
            # Parse theo định dạng đã chọn
            username = parts[0] if len(parts) > 0 else ""
            password = ""
            mail = ""
            cookie = ""
            twofa = ""
            
            if "Username|Pass|Mail|Cookie|2FA" in selected_format:
                password = parts[1] if len(parts) > 1 else ""
                mail = parts[2] if len(parts) > 2 else ""
                cookie = parts[3] if len(parts) > 3 else ""
                twofa = parts[4] if len(parts) > 4 else ""
            elif "Username|Pass|Mail|Cookie" in selected_format:
                password = parts[1] if len(parts) > 1 else ""
                mail = parts[2] if len(parts) > 2 else ""
                cookie = parts[3] if len(parts) > 3 else ""
            elif "Username|Pass|Mail|2FA" in selected_format:
                password = parts[1] if len(parts) > 1 else ""
                mail = parts[2] if len(parts) > 2 else ""
                twofa = parts[3] if len(parts) > 3 else ""
            elif "Username|Pass|Mail" in selected_format:
                password = parts[1] if len(parts) > 1 else ""
                mail = parts[2] if len(parts) > 2 else ""
            elif "Username|Pass" in selected_format:
                password = parts[1] if len(parts) > 1 else ""
            elif "Mail|Pass" in selected_format:
                mail = username  # Dòng đầu là mail
                password = parts[1] if len(parts) > 1 else ""
                username = mail.split("@")[0] if "@" in mail else mail
            elif "Cookie" in selected_format:
                cookie = username
                username = ""
            
            # Lấy STT tiếp theo
            current_items = checklive_tree.get_children()
            stt = len(current_items) + 1
            
            # Thêm vào Tree với 19 cột
            values = [
                stt,              # STT
                "Chưa check",     # TRẠNG THÁI
                username,         # USERNAME
                password,         # PASS
                mail,             # MAIL
                "",               # PHONE
                cookie,           # COOKIE
                twofa,            # 2FA
                "",               # TOKEN
                "",               # IP
                "",               # PROXY
                "",               # LIVE
                "",               # DIE
                "",               # FOLLOW
                "",               # POST
                "",               # AVATAR
                "",               # GENDER
                "",               # BIO
                ""                # PROFESSIONAL
            ]
            
            checklive_tree.insert("", "end", values=values)
            added_count += 1
        
        messagebox.showinfo("Thành công", f"Đã thêm {added_count} tài khoản vào bảng!")
        account_text.delete("1.0", "end")
        account_text.insert("1.0", placeholder)
        account_text.config(fg="gray")
    
    # Button frame
    btn_frame = tk.Frame(add_window, bg="white")
    btn_frame.pack(side="bottom", pady=15)
    
    # Nút Thêm
    add_btn = tk.Button(btn_frame, text="✅ THÊM TÀI KHOẢN", 
                       font=("ROG Fonts STRIX SCAR", 12, "bold"),
                       bg="#4CAF50", fg="white", 
                       command=add_accounts_to_tree,
                       padx=20, pady=10, cursor="hand2")
    add_btn.pack(side="left", padx=5)
    
    # Nút Đóng
    close_btn = tk.Button(btn_frame, text="❌ ĐÓNG", 
                         font=("ROG Fonts STRIX SCAR", 12, "bold"),
                         bg="#f44336", fg="white",
                         command=add_window.destroy,
                         padx=20, pady=10, cursor="hand2")
    close_btn.pack(side="left", padx=5)

# Button frame cho các nút điều khiển
checklive_btn_frame = tk.Frame(checklive_content, bg="white")
checklive_btn_frame.pack(side="bottom", pady=10)

# Nút ADD ACCOUNT
add_account_btn = tk.Button(checklive_btn_frame, text="➕ ADD ACCOUNT",
                           font=("ROG Fonts STRIX SCAR", 11, "bold"),
                           bg="#2196F3", fg="white",
                           command=open_add_account_window,
                           padx=15, pady=8, cursor="hand2")
add_account_btn.pack(side="left", padx=5)
# Nút CHECK LIVE
def check_live_accounts():
    messagebox.showinfo("CHECK LIVE", "Chức năng CHECK LIVE sẽ được phát triển ở đây!")

check_live_btn = tk.Button(checklive_btn_frame, text="🔍 CHECK LIVE",
                           font=("ROG Fonts STRIX SCAR", 11, "bold"),
                           bg="#00BFFF", fg="white",
                           command=check_live_accounts,
                           padx=15, pady=8, cursor="hand2")
check_live_btn.pack(side="left", padx=5)

# ===== TAB 3: HISTORY =====
history_content = tk.Frame(app, bg="white")
history_label = tk.Label(history_content, text="HISTORY CONTENT", 
                         font=("ROG Fonts STRIX SCAR", 16, "bold"), bg="white")
history_label.pack(expand=True)

# ===== TAB 4: GUIDE (HƯỚNG DẪN) =====
guide_content = tk.Frame(app, bg="white")
guide_title = tk.Label(guide_content, text="USER GUIDE", 
                       font=("ROG Fonts STRIX SCAR", 18, "bold"), bg="white", fg="black")
guide_title.pack(pady=20)

# Tạo scrollable frame cho hướng dẫn
guide_canvas = tk.Canvas(guide_content, bg="white", highlightthickness=0)
guide_scrollbar = tk.Scrollbar(guide_content, orient="vertical", command=guide_canvas.yview)
guide_frame = tk.Frame(guide_canvas, bg="white")

guide_frame.bind(
    "<Configure>",
    lambda e: guide_canvas.configure(scrollregion=guide_canvas.bbox("all"))
)

guide_canvas.create_window((0, 0), window=guide_frame, anchor="nw")
guide_canvas.configure(yscrollcommand=guide_scrollbar.set)

guide_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
guide_scrollbar.pack(side="right", fill="y")

# Nội dung hướng dẫn
guide_text = """
📋 INSTAGRAM AUTO CREATOR - USER GUIDE

1️⃣ INTERFACE SELECTION:
   • DESKTOP: Run on computer browser (Chrome)
   • MOBILE IPHONE 15: Simulate iPhone 15 device
   • PHONE (ANDROID): Control real Android devices via ADB

2️⃣ DESKTOP MODE:
   • Set number of threads and accounts to create
   • Configure proxy (IP:PORT format)
   • Choose mail service: temp-mail.asia or DropMail.me
   • Enable features: Follow, Bio+Ava+Post, 2FA, Professional account
   • Select network mode: WiFi, WARP, WARP-SPIN, or PROXY

3️⃣ MOBILE MODE:
   • Similar to Desktop but optimized for iPhone 15 simulation
   • Lighter settings for mobile browser automation

4️⃣ PHONE (ANDROID) MODE:
   • Connect Android devices via USB/WiFi ADB
   • Click "Refresh Device List" to detect devices
   • Select Instagram or Instagram Lite app
   • Configure network: WiFi, WARP, Proxy, or SIM 4G
   • Enable jobs: Follow, 2FA, Post, Edit Profile, Auto Follow, Professional

5️⃣ BEFORE STARTING:
   ⚠️ IMPORTANT: Click SAVE button before START!
   • The tool will warn you if settings are not saved
   • If you change settings, you must SAVE again before START

6️⃣ BUTTONS EXPLAINED:
   • RESTART: Restart the application
   • START: Begin account creation process
   • FILE REG: Open Live.txt to view created accounts
   • CHOOSE AVATAR: Select folder containing avatar images
   • SAVE: Save current settings (Required before START!)
   • CHOOSE CHROME: Select Chrome browser path

7️⃣ FILE REQUIREMENTS:
   • Live.txt: Output file for successful accounts
   • Die.txt: Output file for failed accounts
   • proxy.txt: List of proxies (one per line)
   • caption.txt: Bio text for accounts
   • Avatar folder: Contains profile images

8️⃣ PROFESSIONAL ACCOUNT:
   • Choose Category (Artist, Blogger, Creator, etc.)
   • Select Type: Creator or Business

9️⃣ NETWORK MODES:
   • WiFi: Use default internet connection
   • WARP: Use Cloudflare WARP VPN
   • WARP-SPIN: Rotate WARP connection for each account
   • PROXY: Use proxy list from proxy.txt
   • SIM 4G: Use mobile data (Phone mode only)

🔟 TIPS & TRICKS:
   • Always test with 1 thread first
   • Use different proxies to avoid IP blocks
   • Enable 2FA for better account security
   • Regular accounts last longer than bulk-created ones
   • Phone mode is most reliable but slower

⚠️ TROUBLESHOOTING:
   • If START is blocked: Click SAVE button first!
   • Chrome not found: Use CHOOSE CHROME button
   • Proxy errors: Check proxy.txt format
   • Phone not detected: Enable USB Debugging on Android
   • ADB connection: Run "Refresh Device List"

📞 SUPPORT:
   • Check logs in the application for detailed error messages
   • Ensure all required files are in the correct directory
   • For Phone mode, make sure ADB is properly installed

✅ REMEMBER: Always SAVE before START! ✅
"""

guide_label = tk.Label(guide_frame, text=guide_text, bg="white", 
                       font=("Consolas", 10), justify="left", anchor="w")
guide_label.pack(padx=20, pady=10, fill="both", expand=True)

# ===== TAB 5: UTILITIES (TIỆN ÍCH) =====
utilities_content = tk.Frame(app, bg="white")
utilities_title = tk.Label(
    utilities_content, text="UTILITIES",
    font=("ROG Fonts STRIX SCAR", 18, "bold"), bg="white", fg="black"
)
utilities_title.pack(pady=20)

# ----- Scrollable frame -----
util_canvas = tk.Canvas(utilities_content, bg="white", highlightthickness=0)
util_scrollbar = tk.Scrollbar(utilities_content, orient="vertical", command=util_canvas.yview)
util_frame = tk.Frame(util_canvas, bg="white")
util_frame.bind("<Configure>", lambda e: util_canvas.configure(scrollregion=util_canvas.bbox("all")))
util_canvas.create_window((0, 0), window=util_frame, anchor="nw")
util_canvas.configure(yscrollcommand=util_scrollbar.set)
util_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
util_scrollbar.pack(side="right", fill="y")

# ----- LOG AREA -----
tk.Label(
    util_frame, text="📜 LOG OUTPUT",
    font=("ROG Fonts STRIX SCAR", 14, "bold"),
    bg="white", fg="black"
).pack(anchor="w", pady=(0, 10))

log_frame = tk.Frame(util_frame, bg="black", bd=2, relief="sunken")
log_frame.pack(fill="both", expand=True)

log_box = tk.Text(
    log_frame, bg="black", fg="lime",
    insertbackground="white", font=("Consolas", 10), wrap="word"
)
log_box.pack(fill="both", expand=True)

def log_util(msg: str):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

# ======================= Pinterest Downloader =======================
tk.Label(util_frame, text="Tải ảnh từ Pinterest", font=("ROG Fonts STRIX SCAR", 13, "bold"), bg="white", fg="black").pack(anchor="w", pady=(10,5))

# ----- Đọc config -----
def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(data):
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

config = load_config()

# ----- Email và mật khẩu -----
row_email = tk.Frame(util_frame, bg="white"); row_email.pack(anchor="w", pady=2)
tk.Label(row_email, text="Email:", bg="white").pack(side="left", padx=(0,5))
pin_email_var = tk.StringVar(value=config.get("pinterest_email", ""))
email_entry = ttk.Entry(row_email, textvariable=pin_email_var, width=40)
email_entry.pack(side="left")

row_pass = tk.Frame(util_frame, bg="white"); row_pass.pack(anchor="w", pady=2)
tk.Label(row_pass, text="Mật khẩu:", bg="white").pack(side="left", padx=(0,5))
pin_pass_var = tk.StringVar(value=config.get("pinterest_pass", ""))
pass_entry = ttk.Entry(row_pass, textvariable=pin_pass_var, width=40, show="*")
pass_entry.pack(side="left")

# ----- Danh sách từ khóa Pinterest -----
pinterest_keywords = [
    "ảnh gái xinh", "girl cute", "hot girl dễ thương", "pretty girl portrait",
    "asian beauty", "korean girl", "vietnamese girl", "japanese girl",
    "chinese girl portrait", "fashion girl pose", "girl selfie", "smiling girl",
    "outdoor portrait", "aesthetic girl", "street fashion girl",
    "landscape photography", "mountain view", "beach sunset", "forest trail",
    "night city lights", "tropical island", "sky clouds aesthetic", "flower garden",
    "desert dunes", "winter snow view",
    "minimalist art", "aesthetic wallpaper", "vintage film photo", "street photography",
    "cyberpunk neon city", "coffee shop aesthetic", "interior design modern",
    "workspace inspiration", "anime girl art", "digital painting portrait"
]

pin_url_var = tk.StringVar()

# ----- Số lượng ảnh -----
tk.Label(util_frame, text="Số lượng ảnh muốn lưu:", bg="white", font=("Consolas", 11)).pack(anchor="w", pady=(8,0))
ava_count_var = tk.IntVar(value=30)
ava_count_entry = ttk.Entry(util_frame, textvariable=ava_count_var, width=8)
ava_count_entry.pack(anchor="w", pady=(0,8))

# ----- Chọn thư mục lưu -----
def select_ava_folder_util():
    folder = filedialog.askdirectory(title="Chọn thư mục ảnh lưu Pinterest")
    if folder:
        config = load_config()
        config["ava_folder_path"] = folder
        save_config(config)
        log_util(f"✅ Đã chọn thư mục lưu ảnh: {folder}")
    else:
        log_util("⚠️ Chưa chọn thư mục lưu ảnh.")

# ----- Hàm tạo URL -----
def build_pinterest_url(keyword):
    from urllib.parse import quote
    return f"https://www.pinterest.com/search/pins/?q={quote(keyword)}"

# ----- Đăng nhập -----
def pinterest_login(driver, email, password):
    driver.get("https://www.pinterest.com/login/")
    time.sleep(2)
    try:
        email_input = driver.find_element(By.NAME, "id")
        email_input.send_keys(email)
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(2)
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(10)
        # Skip popup nếu có
        try:
            skip = driver.find_element(By.XPATH, "//div[text()='Skip for now']")
            skip.click()
            log_util("➡️ Đã bỏ qua popup 'Skip for now'")
        except Exception:
            pass
    except Exception as e:
        log_util(f"⚠️ Lỗi đăng nhập: {e}")

# ----- Lấy ảnh -----
def collect_image_urls(driver, max_images=100, scroll_limit=30):
    urls, seen = [], set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    while len(urls) < max_images and scrolls < scroll_limit:
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            src = img.get_attribute("src") or ""
            if src and not src.startswith("data:") and src not in seen:
                seen.add(src)
                urls.append(src)
                if len(urls) >= max_images:
                    break
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = scrolls + 1 if new_height == last_height else 0
        last_height = new_height
    return urls[:max_images]

def download_image(session, url, folder, idx):
    try:
        r = session.get(url, timeout=10, stream=True)
        r.raise_for_status()
        ext = os.path.splitext(urlparse(url).path)[1] or ".jpg"
        path = os.path.join(folder, f"pinterest_{idx:04d}{ext}")
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception:
        return False

# ----- Bắt đầu tải -----
def start_pinterest_download():
    email = pin_email_var.get().strip()
    password = pin_pass_var.get().strip()
    if not (email and password):
        log_util("⚠️ Hãy nhập Email và Mật khẩu Pinterest.")
        return

    # Lưu lại email & pass
    config = load_config()
    config["pinterest_email"] = email
    config["pinterest_pass"] = password
    save_config(config)

    # Random từ khóa
    keyword = random.choice(pinterest_keywords)
    url = build_pinterest_url(keyword)
    pin_url_var.set(url)
    log_util(f"\n🕒 Bắt đầu lúc: {time.strftime('%H:%M:%S')}")
    log_util(f"🎯 Từ khóa ngẫu nhiên: {keyword}")
    log_util(f"🔗 URL Pinterest: {url}")

    folder = config.get("ava_folder_path", "")
    if not folder or not os.path.isdir(folder):
        log_util("⚠️ Chưa chọn thư mục lưu ảnh.")
        return

    max_images = ava_count_var.get()
    log_util(f"🚀 Đang khởi động Chrome (Pinterest)...")

    threading.Thread(target=_worker_pinterest, args=(email, password, url, max_images, folder), daemon=True).start()

def _worker_pinterest(email, password, url, max_images, folder):
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver = se_webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options())
        driver.maximize_window()
        pinterest_login(driver, email, password)
        driver.get(url)
        log_util("🔍 Đang cuộn và thu thập ảnh...")
        urls = collect_image_urls(driver, max_images=max_images)
        driver.quit()
        if not urls:
            log_util("⚠️ Không tìm thấy ảnh.")
            return
        session = requests.Session()
        total, ok = len(urls), 0
        for i, link in enumerate(urls, 1):
            log_util(f"⬇️ {i}/{total}: {link[:60]}...")
            if download_image(session, link, folder, i):
                ok += 1
        log_util(f"🏁 Hoàn tất. Đã lưu {ok}/{total} ảnh vào {folder}")
    except Exception as e:
        log_util(f"❌ Lỗi: {e}")

# ==== Nút điều khiển ====
start_btn = ttk.Button(util_frame, text="Bắt đầu tải Pinterest", command=start_pinterest_download, width=26)
start_btn.pack(pady=10)
ava_btn = ttk.Button(util_frame, text="Ava Folder (Chọn Folder)", command=select_ava_folder_util, width=24)
ava_btn.pack(pady=4)

# ===== TAB 6: MENU =====
menu_content = tk.Frame(app, bg="white")
menu_title = tk.Label(menu_content, text="MENU - QUICK ACCESS", 
                      font=("ROG Fonts STRIX SCAR", 18, "bold"), bg="white", fg="black")
menu_title.pack(pady=20)

# Container cho menu
menu_container = tk.Frame(menu_content, bg="white")
menu_container.pack(expand=True, fill="both", padx=40, pady=20)

menu_button_font = ("ROG Fonts STRIX SCAR", 12, "bold")


# Hiển thị tab mặc định (INSTAGRAM)
switch_tab("INSTAGRAM")

load_config()

def open_main_app():
    try:
        app.deiconify()   # hiện lại giao diện chính
    except Exception:
        pass

# gọi intro trước khi chạy main loop
show_intro(app, open_main_app)

app.mainloop()
