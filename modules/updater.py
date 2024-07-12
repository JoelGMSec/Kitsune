#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import subprocess

def get_local_version():
    try:
        result = subprocess.run(["cat", "version.txt"], capture_output=True, text=True, check=True)
        local_version = result.stdout.strip()
        return local_version
    except subprocess.CalledProcessError as e:
        return None

version = get_local_version()

def check_updates(app):
    updates_window = tk.Toplevel(app)
    updates_window.geometry("525x255")
    updates_window.title("Updates")
    updates_window.focus_force()

    image_frame = tk.Frame(updates_window)
    image_frame.grid(row=0, column=1, padx=(30, 0), pady=(20, 0))

    image = Image.open("./themes/images/Updates.png")
    resized_image = image.resize((200, 200))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    updates_frame = tk.Frame(updates_window)
    updates_frame.grid(row=0, column=0, padx=(20, 0), pady=10, sticky="nsew")

    updates_label = tk.Label(updates_frame, text="Checking for updates..")
    updates_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0))

    name_label = tk.Label(updates_frame, text="")
    name_label.grid(row=1, column=0, padx=(20, 0), pady=10)

    progressbar = ttk.Progressbar(updates_frame, mode="indeterminate", length=200)
    progressbar.grid(row=2, column=0, pady=(20, 10))
    progressbar.start()  

    def check_version():
        try:
            response = requests.get("https://raw.githubusercontent.com/JoelGMSec/Kitsune/main/version.txt")
            response.raise_for_status()  
            remote_version = response.text.strip()

            if remote_version != version:
                name_label.config(text="New version found!", fg="#00AAFF")
            else:
                name_label.config(text="No updates found!", fg="#00AAFF")
        except:
            name_label.config(text="No updates found!", fg="#00AAFF")

    updates_window.after(1000, check_version)

    def on_enter_key(event):
        updates_window.destroy()

    updates_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        updates_window.destroy()

    updates_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(updates_frame, text="Close", command=lambda: updates_window.destroy())
    save_button.grid(row=3, column=0, pady=(25, 0))  
