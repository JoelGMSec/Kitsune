#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import time
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def clone_repos(name_label=None):
    repos = [
        "https://github.com/iagox86/dnscat2",
        "https://github.com/Hackplayers/evil-winrm",
        "https://github.com/JoelGMSec/HTTP-Shell",
        "https://github.com/Pennyw0rth/NetExec",
        "https://github.com/calebstewart/pwncat",
        "https://github.com/JoelGMSec/PyShell",
        "https://github.com/t3l3machus/Villain",
        "https://github.com/XiaoliChan/wmiexec-Pro"
    ]

    base_dir = "./tails"

    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    for repo in repos:
        repo_name = repo.split('/')[-1]
        repo_dir = os.path.join(base_dir, repo_name)
        
        try:
            subprocess.run(["git", "clone", repo, repo_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            if name_label:
                name_label.config(text="Error updating tails!", fg="red")
            return

    powercat_repo = "https://github.com/besimorhino/powercat"
    powercat_dir = os.path.join(base_dir, "dnscat2", "client", "win32", "powercat")
    
    try:
        subprocess.run(["git", "clone", powercat_repo, powercat_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        if name_label:
            name_label.config(text="Error updating tails!", fg="red")
        return

    dnscat2_client_url = "https://downloads.skullsecurity.org/dnscat2/dnscat2-v0.07-client-x86.tar.bz2"
    dnscat2_client_dir = os.path.join(base_dir, "dnscat2", "client")
    
    os.makedirs(dnscat2_client_dir, exist_ok=True)
    try:
        subprocess.run(["wget", "-q", dnscat2_client_url, "-O", os.path.join(dnscat2_client_dir, "dnscat2-v0.07-client-x86.tar.bz2")], check=True)
        subprocess.run(["tar", "-xf", os.path.join(dnscat2_client_dir, "dnscat2-v0.07-client-x86.tar.bz2"), "-C", dnscat2_client_dir], check=True)
        os.remove(os.path.join(dnscat2_client_dir, "dnscat2-v0.07-client-x86.tar.bz2"))
    except:
        if name_label:
            name_label.config(text="Error updating tails!", fg="red")
        return

    if name_label:
        name_label.config(text="All are up to date!", fg="#00AAFF")

def update_tails(app):
    try:
        if app.tails_window and tk.Toplevel.winfo_exists(app.tails_window):
            app.tails_window.focus_force()
            return
    except:
        pass
        
    app.tails_window = tk.Toplevel(app)
    app.tails_window.geometry("525x255")
    app.tails_window.title("Update Tails")
    app.tails_window.focus_force()
    app.tails_window.resizable(False, False)

    image_frame = tk.Frame(app.tails_window)
    image_frame.grid(row=0, column=1, padx=(40, 0), pady=(15, 0))

    image = Image.open("./themes/images/GitHub.png")
    resized_image = image.resize((200, 200))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    updates_frame = tk.Frame(app.tails_window)
    updates_frame.grid(row=0, column=0, padx=(22, 0), pady=10, sticky="nsew")

    updates_label = tk.Label(updates_frame, text="Downloading tails..")
    updates_label.grid(row=0, column=0, padx=(22, 0), pady=(20, 0))

    name_label = tk.Label(updates_frame, text="*Please wait*", fg="#BABABA")
    name_label.grid(row=1, column=0, padx=(22, 0), pady=10)

    progressbar = ttk.Progressbar(updates_frame, mode="indeterminate", length=220)
    progressbar.grid(row=2, column=0, padx=(22, 0), pady=(20, 10))
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
        app.tails_window.destroy()

    app.tails_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.tails_window.destroy()

    app.tails_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(updates_frame, text="Close", command=lambda: app.tails_window.destroy())
    save_button.grid(row=3, column=0, padx=(22, 0), pady=(25, 0))
