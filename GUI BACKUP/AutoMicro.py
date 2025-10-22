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
            activeforeground="white"
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
