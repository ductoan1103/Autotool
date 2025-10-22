import tkinter as tk
from tkinter import messagebox
import threading
import time
import subprocess
import requests

class WarpController(tk.Tk):
    # === Hàm điều khiển WARP ===
    def warp_on(self):
        try:
            subprocess.run(["warp-cli", "connect"], check=True)
            self.log("🌐 Đã bật Cloudflare WARP")
            time.sleep(3)
            self.update_ip_label()
        except Exception as e:
            self.log(f"❌ Lỗi bật WARP: {repr(e)}")

    def warp_off(self):
        try:
            subprocess.run(["warp-cli", "disconnect"], check=True)
            self.log("🌐 Đã tắt Cloudflare WARP")
            time.sleep(3)
        except Exception as e:
            self.log(f"❌ Lỗi tắt WARP: {repr(e)}")

    def warp_change_ip(self):
        try:
            self.log("🔄 Đang đổi IP WARP...")
            subprocess.run(["warp-cli", "disconnect"], check=True)
            time.sleep(2)
            subprocess.run(["warp-cli", "connect"], check=True)
            time.sleep(3)
            self.update_ip_label()
            ip = requests.get("https://api.ipify.org").text
            self.log(f"✅ IP WARP mới: {ip}")
        except Exception as e:
            self.log(f"❌ Lỗi đổi IP WARP: {repr(e)}")
    def update_ip_label(self):
        try:
            ip = requests.get("https://api.ipify.org").text
            self.ip_label.config(text=f"IP hiện tại: {ip}")
        except Exception as e:
            self.ip_label.config(text="IP hiện tại: Lỗi!")
            self.log(f"❌ Lỗi lấy IP: {repr(e)}")
    def __init__(self):
        super().__init__()
        self.title("WARP Controller")
        self.geometry("520x330")
        self.resizable(False, False)

        # Log area
        self.log_text = tk.Text(self, height=6, bg="black", fg="lime", font=("Consolas", 12))
        self.log_text.pack(fill=tk.X)
        self.log_text.insert(tk.END, "[00:00:00] Đã bật tự động reset WARP\n")
        self.log_text.config(state=tk.DISABLED)

        # IP label
        self.ip_label = tk.Label(self, text="IP hiện tại: ...", fg="blue", font=("Arial", 12, "bold"))
        self.ip_label.pack(pady=10)

        # Reset time
        self.reset_frame = tk.Frame(self)
        self.reset_frame.pack()
        tk.Label(self.reset_frame, text="Thời gian reset (giây):").pack(side=tk.LEFT)
        self.reset_time_var = tk.StringVar(value="300")
        self.reset_entry = tk.Entry(self.reset_frame, textvariable=self.reset_time_var, width=6)
        self.reset_entry.pack(side=tk.LEFT)

        # Countdown label
        self.countdown_var = tk.StringVar(value="")
        self.countdown_label = tk.Label(self, textvariable=self.countdown_var, fg="red", font=("Arial", 12, "bold"))
        self.countdown_label.pack(pady=5)

        # Buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)
        # Nút chuyển trạng thái WARP ON/OFF
        self.warp_enabled = False
        self.warp_toggle_btn = tk.Button(self.button_frame, text="WARP OFF", width=15, bg="red", fg="white", command=self.toggle_warp)
        self.warp_toggle_btn.pack(side=tk.LEFT, padx=5)
        self.btn_rotate = tk.Button(self.button_frame, text="WARP Xoay", width=15, command=self.toggle_warp_rotate)
        self.btn_rotate.pack(side=tk.LEFT, padx=5)

        # Check IP button
        self.btn_check_ip = tk.Button(self, text="Kiểm tra IP", width=20, command=self.check_ip)
        self.btn_check_ip.pack(pady=10)

        # Trạng thái WARP Xoay
        self.warp_rotating = False
        self.warp_rotate_thread = None

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def toggle_warp(self):
        self.warp_enabled = not self.warp_enabled
        if self.warp_enabled:
            self.warp_toggle_btn.config(text="WARP ON", bg="green", fg="white", state="disabled")
            self.log("🌐 WARP mode ENABLED - sẽ dùng WARP, bỏ qua proxy.")
        else:
            self.warp_toggle_btn.config(text="WARP OFF", bg="red", fg="white", state="normal")
            self.log("🌐 WARP mode DISABLED - sẽ dùng proxy nếu có.")

    def turn_on_warp(self):
        if not self.warp_enabled:
            self.toggle_warp()
        self.log("[{}] Bật WARP".format(time.strftime('%H:%M:%S')))
        self.warp_on()

    def turn_off_warp(self):
        if self.warp_enabled:
            self.toggle_warp()
        self.log("[{}] Tắt WARP".format(time.strftime('%H:%M:%S')))
        self.warp_off()

    def toggle_warp_rotate(self):
        if not self.warp_rotating:
            self.warp_rotating = True
            self.btn_rotate.config(text="Dừng WARP Xoay")
            self.log("[{}] Bắt đầu WARP Xoay".format(time.strftime('%H:%M:%S')))
            self.warp_rotate_thread = threading.Thread(target=self.warp_rotate_loop, daemon=True)
            self.warp_rotate_thread.start()
        else:
            self.warp_rotating = False
            self.btn_rotate.config(text="WARP Xoay")
            self.log("[{}] Dừng WARP Xoay".format(time.strftime('%H:%M:%S')))

    def warp_rotate_loop(self):
        while self.warp_rotating:
            self.turn_on_warp()
            try:
                seconds = int(self.reset_time_var.get())
            except ValueError:
                seconds = 300
            self.log(f"[WARP Xoay] Đợi {seconds} giây...")
            for remain in range(seconds, 0, -1):
                if not self.warp_rotating:
                    self.countdown_var.set("")
                    return
                self.countdown_var.set(f"Đang chạy WARP: còn {remain} giây")
                time.sleep(1)
            self.countdown_var.set("")
            self.turn_off_warp()
            self.log("[WARP Xoay] Nghỉ 6 giây...")
            for remain in range(6, 0, -1):
                if not self.warp_rotating:
                    self.countdown_var.set("")
                    return
                self.countdown_var.set(f"Đang nghỉ: còn {remain} giây")
                time.sleep(1)
            self.countdown_var.set("")
        self.log("[WARP Xoay] Đã dừng.")
        self.countdown_var.set("")

    def check_ip(self):
        self.log("[{}] Kiểm tra IP".format(time.strftime('%H:%M:%S')))
        self.update_ip_label()

if __name__ == "__main__":
    app = WarpController()
    app.mainloop()
