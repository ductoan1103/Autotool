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

class App(tk.Tk):
    def open_tree_window(self):
        tree_win = tk.Toplevel(self)
        tree_win.title("Tree Table")
        tree_win.geometry("1200x600")
        tree_win.configure(bg="white")

        columns = [
            "STT", "STATUS", "MAIL", "PASS", "PHONE", "COOKIE", "TOKEN", "2FA", "OAUTH2",
            "IMAP", "POP3", "GRAPH API", "LIVE", "DIE", "FAIL"
        ]
        tree = ttk.Treeview(tree_win, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80, anchor="center")
        tree.pack(fill="x", padx=10, pady=(10,0))

        # Thanh cuộn cho bảng
        scrollbar = tk.Scrollbar(tree_win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Thêm bảng log dưới bảng tree
        log_frame = tk.Frame(tree_win, bg="white")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))
        log_label = tk.Label(log_frame, text="LOG", bg="white", font=("ROG Fonts STRIX SCAR", 12, "bold"))
        log_label.pack(anchor="w")
        log_text = scrolledtext.ScrolledText(log_frame, height=10, bg="#f8f8f8", font=("Consolas", 10))
        log_text.pack(fill="both", expand=True)

        def add_log(msg):
            log_text.insert(tk.END, msg + "\n")
            log_text.see(tk.END)

        # Lấy danh sách thiết bị đã tick từ self.device_vars
        checked_devices = [dev for dev, var in getattr(self, 'device_vars', []) if var.get()]
        if not checked_devices:
            messagebox.showwarning("Chưa chọn thiết bị", "Vui lòng tick ít nhất 1 thiết bị để bắt đầu.")
            return

        # Tạo dòng cho mỗi thiết bị đã tick với STATUS ban đầu
        item_ids = []
        for idx, dev in enumerate(checked_devices):
            item_id = tree.insert("", "end", values=(idx+1, "Đang kết nối...", "", "", "", "", "", "", "", "", "", "", "", "", ""))
            item_ids.append(item_id)

        def connect_device(idx, dev, item_id):
            APPIUM_HOST = "127.0.0.1"
            APPIUM_PORT = 4723
            status = ""
            def update_status(msg):
                tree.item(item_id, values=(idx+1, msg, "", "", "", "", "", "", "", "", "", "", "", "", ""))
                add_log(f"[{dev}] {msg}")
            update_status("Kết nối Appium...")
            try:
                caps = {
                    "platformName": "Android",
                    "automationName": "UiAutomator2",
                    "udid": dev,
                    "appPackage": "com.android.settings",
                    "appActivity": ".Settings",
                    "newCommandTimeout": 180,
                    "adbExecTimeout": 120000,
                    "uiautomator2ServerLaunchTimeout": 120000,
                    "noReset": True,
                    "autoGrantPermissions": True,
                }
                opts = UiAutomator2Options().load_capabilities(caps)
                driver = webdriver.Remote(
                    command_executor=f"http://{APPIUM_HOST}:{APPIUM_PORT}/wd/hub",
                    options=opts
                )
                driver.implicitly_wait(4)
                update_status("Đã kết nối Appium")

                # Clear data Outlook
                update_status("Đang clear Outlook...")
                try:
                    driver.execute_script('mobile: shell', {
                        'command': 'pm',
                        'args': ['clear', 'com.microsoft.office.outlook']
                    })
                    update_status("Đã clear Outlook")
                except Exception:
                    update_status("Clear Outlook FAIL")

                # Clear WARP
                for pkg in [
                    'com.cloudflare.onedotonedotonedotone',
                    'com.cloudflare.onedotonedotone',
                    'com.cloudflare.warp',
                ]:
                    update_status(f"Đang clear {pkg}...")
                    try:
                        driver.execute_script('mobile: shell', {
                            'command': 'pm',
                            'args': ['clear', pkg]
                        })
                        update_status(f"Đã clear {pkg}")
                    except Exception:
                        update_status(f"Clear {pkg} FAIL")

                # Clear Super Proxy
                update_status("Đang clear Super Proxy...")
                try:
                    driver.execute_script('mobile: shell', {
                        'command': 'pm',
                        'args': ['clear', 'com.scheler.superproxy']
                    })
                    update_status("Đã clear Super Proxy")
                except Exception:
                    update_status("Clear Super Proxy FAIL")

                # Kill all app
                update_status("Đang kill all app...")
                try:
                    udid = dev
                    import subprocess
                    subprocess.call(["adb", "-s", udid, "shell", "am", "kill-all"])
                    for pkg in [
                        'com.microsoft.office.outlook',
                        'com.cloudflare.onedotonedotonedotone',
                        'com.cloudflare.onedotonedotone',
                        'com.cloudflare.warp',
                        'com.scheler.superproxy',
                    ]:
                        subprocess.call(["adb", "-s", udid, "shell", "am", "force-stop", pkg])
                    update_status("Đã kill all app")
                except Exception:
                    update_status("Kill all app FAIL")

                # Cấp toàn bộ quyền cho app Outlook
                update_status("Đang cấp quyền cho Outlook...")
                try:
                    perms = [
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
                        "android.permission.POST_NOTIFICATIONS",
                        "android.permission.READ_MEDIA_IMAGES",
                        "android.permission.READ_MEDIA_VIDEO",
                        "android.permission.READ_MEDIA_AUDIO",
                    ]
                    pkg_outlook = "com.microsoft.office.outlook"
                    for p in perms:
                        try:
                            driver.execute_script('mobile: shell', {
                                'command': 'pm',
                                'args': ['grant', pkg_outlook, p]
                            })
                        except Exception:
                            pass
                    update_status("Đã cấp quyền cho Outlook")
                except Exception:
                    update_status("Cấp quyền Outlook FAIL")

                # Áp dụng cách mở app như Auto.py
                pkg = "com.microsoft.office.outlook"
                activities = [
                    "com.microsoft.office.outlook.MainActivity",
                    ".MainActivity",
                ]
                opened = False
                update_status("Đang mở Outlook...")
                # Thử start_activity
                for act in activities:
                    try:
                        driver.start_activity(pkg, act)
                        update_status(f"Đã mở Outlook ({act})")
                        opened = True
                        break
                    except Exception:
                        continue
                # Nếu chưa mở được, thử activate_app
                if not opened:
                    try:
                        driver.activate_app(pkg)
                        update_status("Đã activate Outlook")
                        opened = True
                    except Exception:
                        pass
                # Nếu vẫn chưa mở được, thử monkey
                if not opened:
                    try:
                        udid = dev
                        subprocess.call([
                            "adb", "-s", udid, "shell", "monkey", "-p", pkg,
                            "-c", "android.intent.category.LAUNCHER", "1"
                        ])
                        update_status("Đã mở Outlook bằng monkey")
                        opened = True
                    except Exception:
                        update_status("Mở Outlook FAIL")

                # Sau khi mở app xong, chờ 13 giây rồi ấn CREATE NEW ACCOUNT
                if opened:
                    update_status("Chờ 13 giây sau khi mở Outlook...")
                    time.sleep(13)
                update_status("Hoàn tất!")
            except Exception as e:
                status = f"FAIL: {e}"[:40]
                update_status(status)

        def connect_all():
            for idx, dev in enumerate(checked_devices):
                connect_device(idx, dev, item_ids[idx])

        threading.Thread(target=connect_all, daemon=True).start()
    def __init__(self):
        super().__init__()
        self.title("Instagram GUI")
        self.geometry("900x600")
        self.configure(bg="white")

        rog_font = ("ROG Fonts STRIX SCAR", 11, "bold")

        # === Thanh trên cùng ===
        self.top_bar = tk.Frame(self, bg="black", height=50)
        self.top_bar.pack(side="top", fill="x")

        self.title_label = tk.Label(
            self.top_bar, text="TAB",
            fg="white", bg="black",
            font=("ROG Fonts STRIX SCAR", 18, "bold")
        )
        self.title_label.pack(pady=5)

        # === Thanh trái ===
        self.side_bar = tk.Frame(self, bg="black", width=150)
        self.side_bar.pack(side="left", fill="y")

        # === Các tab chính (bao gồm MENU) ===
        self.tabs = {
            "MICROSOFT": self.create_tab_tab,
            "CHECK LIVE": self.create_tab_check,
            "UTILITIES": self.create_tab_util,
            "GUIDE": self.create_tab_guide,
            "MENU": self.create_tab_menu
        }

        # === Nút Tab ===
        for name in ["MICROSOFT", "CHECK LIVE", "UTILITIES", "GUIDE"]:
            btn = tk.Button(
                self.side_bar, text=name,
                fg="white", bg="black",
                font=rog_font,
                bd=0, command=lambda n=name: self.show_tab(n)
            )
            btn.pack(pady=10, fill="x")

        # === Nút MENU riêng ===
        self.menu_btn = tk.Button(
            self.side_bar, text="MENU",
            fg="white", bg="black",
            font=rog_font,
            bd=0, command=lambda: self.show_tab("MENU")
        )
        self.menu_btn.pack(side="bottom", pady=15, fill="x")

        # === Vùng nội dung ===
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.current_tab = "MICROSOFT"
        self.show_tab("MICROSOFT")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_tab(self, name):
        self.clear_content()
        self.current_tab = name
        self.title_label.config(text=name)
        self.tabs[name]()

    # === Nội dung từng tab ===
    def create_tab_tab(self):
        tk.Label(self.content_frame, text="MICROSOFT",
                 bg="white", font=("ROG Fonts STRIX SCAR", 13, "bold")).pack(pady=20)
        start_btn = tk.Button(
            self.content_frame,
            text="START",
            font=("ROG Fonts STRIX SCAR", 12, "bold"),
            bg="black", fg="white",
            padx=20, pady=10,
            bd=0,
            activebackground="black",
            activeforeground="white",
            command=self.open_tree_window
        )
        start_btn.pack(pady=10)

        # Bảng settings (khung bo viền, tiêu đề SETTINGS)
        settings_frame = tk.Frame(self.content_frame, bg="white", highlightbackground="black", highlightthickness=4)
        settings_frame.place(relx=0.5, rely=0.55, anchor="n", width=700, height=220)

        # Canvas để chứa nội dung có thể cuộn
        canvas = tk.Canvas(settings_frame, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        # Thanh cuộn dọc
        scrollbar = tk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame chứa nội dung settings bên trong canvas
        inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 30), window=inner_frame, anchor="nw", width=670)

        # Tiêu đề SETTINGS nằm giữa khung
        settings_label = tk.Label(settings_frame, text="SETTINGS", bg="white", fg="black", font=("ROG Fonts STRIX SCAR", 15, "bold"))
        settings_label.place(relx=0.5, y=0, anchor="n")

        # --- Bảng danh sách thiết bị ---
        device_label = tk.Label(inner_frame, text="Danh sách thiết bị:", bg="white", font=("ROG Fonts STRIX SCAR", 12, "bold"))
        device_label.pack(anchor="w", padx=10, pady=(10,0))

        # Frame chứa danh sách thiết bị và nút
        device_list_frame = tk.Frame(inner_frame, bg="white")
        device_list_frame.pack(fill="x", padx=10)

        # Nút Refresh ADB
        def refresh_adb():
            # Lấy danh sách thiết bị từ adb
            import subprocess
            try:
                result = subprocess.check_output(["adb", "devices"], encoding="utf-8")
                lines = result.strip().split("\n")[1:]
                devices = [line.split("\t")[0] for line in lines if "device" in line]
            except Exception as e:
                devices = []
            update_device_list(devices)

        # Nút Kill ADB & Reload
        def kill_adb_reload():
            import subprocess
            try:
                subprocess.call(["adb", "kill-server"])
                subprocess.call(["adb", "start-server"])
            except Exception as e:
                pass
            refresh_adb()

        refresh_btn = tk.Button(device_list_frame, text="Refresh ADB", bg="black", fg="white", font=("ROG Fonts STRIX SCAR", 10, "bold"), command=refresh_adb)
        refresh_btn.pack(side="left", padx=5, pady=5)
        kill_reload_btn = tk.Button(device_list_frame, text="Kill ADB & Reload", bg="black", fg="white", font=("ROG Fonts STRIX SCAR", 10, "bold"), command=kill_adb_reload)
        kill_reload_btn.pack(side="left", padx=5, pady=5)

        # Frame chứa các thiết bị với ô tích
        devices_check_frame = tk.Frame(inner_frame, bg="white")
        devices_check_frame.pack(fill="x", padx=10, pady=5)

        self.device_vars = []
        def update_device_list(devices):
            for widget in devices_check_frame.winfo_children():
                widget.destroy()
            self.device_vars.clear()
            for dev in devices:
                var = tk.BooleanVar()
                cb = tk.Checkbutton(devices_check_frame, text=dev, variable=var, bg="white", font=("ROG Fonts STRIX SCAR", 10))
                cb.pack(anchor="w")
                self.device_vars.append((dev, var))

        # Khởi tạo lần đầu (có thể chưa có thiết bị)
        update_device_list([])
        # Đảm bảo canvas cuộn đúng khi nội dung thay đổi
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner_frame.bind("<Configure>", on_configure)

    def create_tab_check(self):
        tk.Label(self.content_frame, text="Nội dung CHECK LIVE",
                 bg="white", font=("ROG Fonts STRIX SCAR", 13, "bold")).pack(pady=20)

    def create_tab_util(self):
        tk.Label(self.content_frame, text="Nội dung UTILITIES",
                 bg="white", font=("ROG Fonts STRIX SCAR", 13, "bold")).pack(pady=20)

    def create_tab_guide(self):
        tk.Label(self.content_frame, text="Nội dung GUIDE",
                 bg="white", font=("ROG Fonts STRIX SCAR", 13, "bold")).pack(pady=20)

    def create_tab_menu(self):
        tk.Label(self.content_frame, text="Nội dung MENU",
                 bg="white", font=("ROG Fonts STRIX SCAR", 13, "bold")).pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()
