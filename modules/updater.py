#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import time
import requests
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk
from modules import dialog
from PIL import Image, ImageTk

def get_local_version():
    try:
        result = subprocess.run(["cat", "version.txt"], capture_output=True, text=True, check=True)
        local_version = result.stdout.strip()
        return local_version
    except:
        return None

version = get_local_version()

def check_updates(app):
    try:
        if app.updates_window and tk.Toplevel.winfo_exists(app.updates_window):
            app.updates_window.focus_force()
            return
    except:
        pass

    def interpolate_color(color1, color2, factor):
        c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        c = [int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3)]
        return "#%02x%02x%02x" % tuple(c)

    def blink_label(stop_event):
        try:
            step = 0
            while not stop_event.is_set():
                factor = abs((step % 200) - 100) / 100.0
                current_color = interpolate_color("#BABABA", "#444444", factor)
                if name_label.winfo_exists():
                    app.after(0, name_label.config, {'foreground': current_color})
                
                step += 1
                time.sleep(0.005)
        except:
            pass

    app.updates_window = tk.Toplevel(app)
    app.updates_window.geometry("525x255")
    app.updates_window.title("Updates")
    app.updates_window.focus_force()
    app.updates_window.resizable(False, False)

    image_frame = tk.Frame(app.updates_window)
    image_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 0))

    image = Image.open("./themes/images/Updates.png")
    resized_image = image.resize((210, 210))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    updates_frame = tk.Frame(app.updates_window)
    updates_frame.grid(row=0, column=0, padx=(20, 0), pady=10, sticky="nsew")

    updates_label = tk.Label(updates_frame, text="Checking for updates..")
    updates_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0))

    name_label = tk.Label(updates_frame, text="*Please wait*", fg="#BABABA")
    name_label.grid(row=1, column=0, padx=(20, 0), pady=10)

    progressbar = ttk.Progressbar(updates_frame, mode="indeterminate", length=220)
    progressbar.grid(row=2, column=0, padx=(20, 0), pady=(20, 10))
    progressbar.start()

    stop_blink_event = threading.Event()
    blink_thread = threading.Thread(target=blink_label, args=(stop_blink_event,))
    blink_thread.start()

    def check_version():
        time.sleep(3)
        try:
            response = requests.get("https://raw.githubusercontent.com/JoelGMSec/Kitsune/main/version.txt")
            response.raise_for_status()  
            remote_version = response.text.strip()
            stop_blink_event.set()
            blink_thread.join()
            
            if app.updates_window and tk.Toplevel.winfo_exists(app.updates_window):
                if remote_version != version:
                    app.after(0, name_label.config, {'text': "New version found!", 'fg': "#00AAFF"})
                    app.after(0, save_button.config, {'text': "Download"})
                else:
                    app.after(0, name_label.config, {'text': "No updates found!", 'fg': "#00AAFF"})
                   
        except:
            pass

        return remote_version

    remote_version = threading.Thread(target=check_version).start()
    url = "https://github.com/JoelGMSec/Kitsune"

    def on_enter_key(event):
        app.updates_window.destroy()
    app.updates_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.updates_window.destroy()
    app.updates_window.bind("<Escape>", on_escape_key)

    def run_update():
        if remote_version != version:
            if save_button.cget("text") == "Download":
                threading.Thread(target=webbrowser.open, args=(url,)).start()
        app.updates_window.destroy()

    save_button = ttk.Button(updates_frame, text="Close", command=run_update)
    save_button.grid(row=3, column=0, padx=(20, 0), pady=(25, 0))
