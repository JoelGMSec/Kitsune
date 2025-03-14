#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import shutil
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def clone_repos(name_label=None):
    repos = [
        "https://github.com/JoelGMSec/Invoke-Stealth",
        "https://github.com/peass-ng/PEASS-ng",
        "https://github.com/kost/revsocks",
        "https://github.com/secretsquirrel/SigThief",
        "https://github.com/wanetty/upgopher"
    ]

    base_dir = "./custom"

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for repo in repos:
        repo_name = repo.split("/")[-1]
        dir_path = os.path.join(base_dir, repo_name)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    for repo in repos:
        repo_name = repo.split('/')[-1]
        repo_dir = os.path.join(base_dir, repo_name)
        
        try:
            subprocess.run(["git", "clone", repo, repo_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            if name_label:
                name_label.config(text="Error updating modules!", fg="red")
            return

    if name_label:
        name_label.config(text="All are up to date!", fg="#00AAFF")

def update_modules(app):
    try:
        if app.modules_window and tk.Toplevel.winfo_exists(app.modules_window):
            app.modules_window.focus_force()
            return
    except:
        pass
        
    app.modules_window = tk.Toplevel(app)
    app.modules_window.geometry("525x255")
    app.modules_window.title("Update Modules")
    app.modules_window.focus_force()
    app.modules_window.resizable(False, False)

    image_frame = tk.Frame(app.modules_window)
    image_frame.grid(row=0, column=1, padx=(20, 30), pady=(20, 0))

    image = Image.open("./themes/images/Modules.png")
    resized_image = image.resize((195, 195))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    updates_frame = tk.Frame(app.modules_window)
    updates_frame.grid(row=0, column=0, padx=(20, 0), pady=10, sticky="nsew")

    updates_label = tk.Label(updates_frame, text="Downloading modules..")
    updates_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0))

    name_label = tk.Label(updates_frame, text="*Please wait*", fg="#BABABA")
    name_label.grid(row=1, column=0, padx=(16, 0), pady=10)

    progressbar = ttk.Progressbar(updates_frame, mode="indeterminate", length=220)
    progressbar.grid(row=2, column=0, padx=(16, 0), pady=(20, 10))
    progressbar.start()  
    stop_blink_event = threading.Event()

    def interpolate_color(color1, color2, factor):
        c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        c = [int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3)]
        return "#%02x%02x%02x" % tuple(c)

    def blink_label(stop_event):
        step = 0
        while not stop_event.is_set():
            factor = abs((step % 200) - 100) / 100.0
            current_color = interpolate_color("#BABABA", "#444444", factor)
            app.after(0, name_label.config, {'foreground': current_color})
            step += 1
            time.sleep(0.005)

    blink_thread = threading.Thread(target=blink_label, args=(stop_blink_event,))
    blink_thread.start()

    def clone_repos_thread():
        try:
            clone_repos(name_label)
            stop_blink_event.set()
            blink_thread.join()
            if name_label:
                name_label.config(text="All are up to date!", fg="#00AAFF")
        except:
            if name_label:
                name_label.config(text="Error updating tails!", fg="red")

    threading.Thread(target=clone_repos_thread).start()

    def on_enter_key(event):
        app.modules_window.destroy()

    app.modules_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.modules_window.destroy()

    app.modules_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(updates_frame, text="Close", command=lambda: app.modules_window.destroy())
    save_button.grid(row=3, column=0, padx=(16, 0), pady=(25, 0))
