#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import webbrowser
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess

def get_local_version():
    try:
        result = subprocess.run(["cat", "version.txt"], capture_output=True, text=True, check=True)
        local_version = result.stdout.strip()
        return local_version
    except:
        return None

version = get_local_version()

def callback(event):
    webbrowser.open_new("https://darkbyte.net")

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

    name_label = tk.Label(info_frame, text="by @JoelGMSec")
    name_label.pack(padx=(0, 10), pady=(0, 5))
    
    website_label = tk.Label(info_frame, text=f"Version: {version}")
    website_label.pack(padx=(0, 10), pady=(20, 0))
    
    social_label = tk.Label(info_frame, text="darkbyte.net", fg="#FF0055", cursor="hand2")
    social_label.bind("<Button-1>", callback)
    social_label.pack(padx=(0, 10), pady=(0, 5))
    
    license_label = tk.Label(info_frame, text="License: GNU GPL v3.0")
    license_label.pack(padx=(0, 10), pady=20)

    def on_enter_key(event):
        app.about_window.destroy()

    app.about_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.about_window.destroy()

    app.about_window.bind("<Escape>", on_escape_key)
