#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import time
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter import font
from PIL import Image, ImageTk

def get_local_version():
    try:
        result = subprocess.run(["cat", "version.txt"], capture_output=True, text=True, check=True)
        local_version = result.stdout.strip()
        return local_version
    except:
        return None

version = get_local_version()

def about_window(app):
    try:
        if app.about_window and tk.Toplevel.winfo_exists(app.about_window):
            app.about_window.focus_force()
            return
    except:
        pass

    app.about_window = tk.Toplevel(app)
    app.about_window.geometry("525x255")
    app.about_window.title("About")
    app.about_window.focus_force()
    app.about_window.resizable(False, False)
    
    image_frame = tk.Frame(app.about_window)
    image_frame.pack(side="left", padx=(10, 0), pady=10)
    
    image = Image.open("themes/images/Kitsune.png")
    resized_image = image.resize((200, 200))  
    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.pack()
    
    info_frame = tk.Frame(app.about_window)
    info_frame.pack(side="right", padx=(0, 10), pady=10, fill="both")
    
    kitsune_label = tk.Label(info_frame, text="Kitsune Command & Control")
    kitsune_label.pack(padx=(0, 10), pady=(20, 0))

    name_label = tk.Label(info_frame, text="by @JoelGMSec", fg="#BABABA")
    name_label.pack(padx=(0, 10), pady=(0, 5))
    
    website_label = tk.Label(info_frame, text=f"Version: {version}")
    website_label.pack(padx=(0, 10), pady=(20, 0))
    
    url = "https://darkbyte.net"
    normal_font = font.Font(family="Lexend", size=15, weight="bold")
    underlined_font = font.Font(family="Lexend", size=15, weight="bold", underline=True)
    
    social_label = tk.Label(info_frame, text="darkbyte.net", fg="#FF0055", font=normal_font)
    social_label.bind("<Button-1>", lambda e: webbrowser.open(url))
    social_label.bind("<Enter>", lambda e: social_label.config(cursor="hand2", font=underlined_font))
    social_label.bind("<Leave>", lambda e: social_label.config(cursor="", font=normal_font))
    social_label.pack(padx=(0, 10), pady=(0, 5))

    license_label = tk.Label(info_frame, text="License: GNU GPL v3.0")
    license_label.pack(padx=(0, 10), pady=20)

    def on_enter_key(event):
        app.about_window.destroy()

    app.about_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.about_window.destroy()

    app.about_window.bind("<Escape>", on_escape_key)

    def rotate_image():
        try:
            while True:
                time.sleep(0.8)
                angle = 0
                step = -2
                while angle >= -16:
                    angle += step
                    rotated_image = image.rotate(angle, expand=False)
                    rotated_image = rotated_image.resize((200, 200))
                    photo = ImageTk.PhotoImage(rotated_image)
                    image_label.config(image=photo)
                    image_label.image = photo
                    time.sleep(0.001)

                step = 2
                while angle <= 16:
                    angle += step
                    rotated_image = image.rotate(angle, expand=False)
                    rotated_image = rotated_image.resize((200, 200))
                    photo = ImageTk.PhotoImage(rotated_image)
                    image_label.config(image=photo)
                    image_label.image = photo
                    time.sleep(0.001)

                while angle > 0:
                    angle -= step
                    rotated_image = image.rotate(angle, expand=False)
                    rotated_image = rotated_image.resize((200, 200))
                    photo = ImageTk.PhotoImage(rotated_image)
                    image_label.config(image=photo)
                    image_label.image = photo
                    time.sleep(0.001)
                time.sleep(10)

        except:
            pass

    rotation_thread = threading.Thread(target=rotate_image, daemon=True)
    rotation_thread.start()
