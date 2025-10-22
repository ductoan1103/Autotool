import tkinter as tk

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
            "TAB": self.create_tab_tab,
            "CHECK LIVE": self.create_tab_check,
            "UTILITIES": self.create_tab_util,
            "GUIDE": self.create_tab_guide,
            "MENU": self.create_tab_menu
        }

        # === Nút Tab ===
        for name in ["TAB", "CHECK LIVE", "UTILITIES", "GUIDE"]:
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

        self.current_tab = "TAB"
        self.show_tab("TAB")

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
        tk.Label(self.content_frame, text="Nội dung TAB",
                 bg="white", font=("ROG Fonts STRIX SCAR", 13, "bold")).pack(pady=20)

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
