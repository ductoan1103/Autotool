import os
import threading
import time
import re
from urllib.parse import urlparse

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    raise RuntimeError("tkinter is required for the GUI (usually included with standard Python).")


DOWNLOAD_TIMEOUT = 15
SCROLL_PAUSE = 1.0


def init_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1200, 900)
    return driver


def pinterest_login(driver, email, password):
    driver.get("https://www.pinterest.com/login/")
    time.sleep(2)

    email_input = driver.find_element(By.NAME, "id")
    pass_input = driver.find_element(By.NAME, "password")

    email_input.clear()
    email_input.send_keys(email)
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)

    time.sleep(5)  # wait for login to complete


def collect_image_urls_from_page(driver, max_images=100, scroll_limit=30):
    img_urls = []
    seen = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    scrolls = 0
    while len(img_urls) < max_images and scrolls < scroll_limit:
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            src = img.get_attribute('src') or ''
            srcset = img.get_attribute('srcset') or ''
            url = None
            if src and not src.startswith('data:'):
                url = src
            elif srcset:
                candidates = [s.strip().split(' ')[0] for s in srcset.split(',') if s.strip()]
                if candidates:
                    url = candidates[-1]
            if url and url not in seen:
                seen.add(url)
                img_urls.append(url)
                if len(img_urls) >= max_images:
                    break

        divs = driver.find_elements(By.XPATH, "//*[contains(@style,'background-image')]")
        for d in divs:
            style = d.get_attribute('style') or ''
            m = re.search(r"url\(([^)]+)\)", style)
            if m:
                url = m.group(1).strip(' \"\'')
                if url and not url.startswith('data:') and url not in seen:
                    seen.add(url)
                    img_urls.append(url)
                    if len(img_urls) >= max_images:
                        break

        driver.execute_script('window.scrollBy(0, window.innerHeight);')
        time.sleep(SCROLL_PAUSE)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scrolls += 1
        else:
            scrolls = 0
        last_height = new_height

    return img_urls[:max_images]


def download_image(session, url, folder, idx, timeout=DOWNLOAD_TIMEOUT):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = session.get(url, headers=headers, timeout=timeout, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get('content-type', '')
        if 'image' not in content_type:
            ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'
        else:
            if 'jpeg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'

        filename = f"pinterest_{idx:04d}{ext}"
        path = os.path.join(folder, filename)
        with open(path, 'wb') as f:
            for chunk in resp.iter_content(1024 * 8):
                if chunk:
                    f.write(chunk)
        return path
    except Exception:
        return None


class PinterestSaverGUI:
    def __init__(self, root):
        self.root = root
        root.title('Pinterest Image Saver (with Login)')

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky='nsew')

        ttk.Label(frm, text='Email:').grid(row=0, column=0, sticky='w')
        self.email_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.email_var, width=40).grid(row=0, column=1, sticky='we', pady=2)

        ttk.Label(frm, text='Password:').grid(row=1, column=0, sticky='w')
        self.pass_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.pass_var, width=40, show='*').grid(row=1, column=1, sticky='we', pady=2)

        ttk.Label(frm, text='Pinterest page/search URL:').grid(row=2, column=0, sticky='w')
        self.url_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.url_var, width=70).grid(row=3, column=0, columnspan=3, sticky='we', pady=4)

        ttk.Label(frm, text='Max images to download:').grid(row=4, column=0, sticky='w')
        self.max_var = tk.IntVar(value=30)
        ttk.Entry(frm, textvariable=self.max_var, width=10).grid(row=4, column=1, sticky='w')

        ttk.Label(frm, text='Save folder:').grid(row=5, column=0, sticky='w')
        self.folder_var = tk.StringVar(value=os.path.join(os.getcwd(), 'pinterest_images'))
        ttk.Entry(frm, textvariable=self.folder_var, width=50).grid(row=5, column=1, sticky='w')
        ttk.Button(frm, text='Browse', command=self.browse_folder).grid(row=5, column=2, sticky='w')

        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text='Run browser headless', variable=self.headless_var).grid(row=6, column=0, sticky='w')

        self.start_btn = ttk.Button(frm, text='Start', command=self.start_download)
        self.start_btn.grid(row=7, column=0, pady=10, sticky='w')

        self.progress = ttk.Label(frm, text='Idle')
        self.progress.grid(row=7, column=1, columnspan=2, sticky='w')

        root.columnconfigure(0, weight=1)
        frm.columnconfigure(0, weight=1)

        self._stop_flag = False

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        url = self.url_var.get().strip()
        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()

        if not (url and email and password):
            messagebox.showerror('Error', 'Please enter Email, Password and URL.')
            return

        try:
            max_images = int(self.max_var.get())
        except Exception:
            messagebox.showerror('Error', 'Please enter a valid number for max images.')
            return

        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)

        self.start_btn.config(state='disabled')
        self.progress.config(text='Logging in...')
        threading.Thread(target=self._worker, args=(email, password, url, max_images, folder, self.headless_var.get()), daemon=True).start()

    def _worker(self, email, password, url, max_images, folder, headless):
        try:
            driver = init_driver(headless=headless)
        except Exception as e:
            self._finish('Failed to start browser: ' + str(e))
            return

        try:
            pinterest_login(driver, email, password)
            driver.get(url)
            time.sleep(3)

            self._set_progress('Collecting image URLs...')
            urls = collect_image_urls_from_page(driver, max_images=max_images)
            driver.quit()

            if not urls:
                self._finish('No image URLs found. Page may require login or uses heavy javascript.')
                return

            self._set_progress(f'Found {len(urls)} images. Downloading...')
            session = requests.Session()
            downloaded = 0
            for i, img_url in enumerate(urls, start=1):
                if self._stop_flag:
                    break
                self._set_progress(f'Downloading {i}/{len(urls)}')
                path = download_image(session, img_url, folder, i)
                if path:
                    downloaded += 1
                time.sleep(0.2)

            self._finish(f'Done. Downloaded {downloaded}/{len(urls)} images to {folder}')
        except Exception as e:
            try:
                driver.quit()
            except Exception:
                pass
            self._finish('Error: ' + str(e))

    def _set_progress(self, text):
        def cb():
            self.progress.config(text=text)
        self.root.after(0, cb)

    def _finish(self, text):
        def cb():
            self.progress.config(text=text)
            self.start_btn.config(state='normal')
        self.root.after(0, cb)


if __name__ == '__main__':
    root = tk.Tk()
    app = PinterestSaverGUI(root)
    root.mainloop()
