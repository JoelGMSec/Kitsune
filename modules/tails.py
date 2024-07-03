#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#    https://darkbyte.net #
#=========================#

import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def clone_repos(name_label=None):
    repos = [
        "https://github.com/JoelGMSec/HTTP-Shell",
        "https://github.com/JoelGMSec/PyShell",
        "https://github.com/calebstewart/pwncat",
        "https://github.com/t3l3machus/Villain",
        "https://github.com/XiaoliChan/wmiexec-Pro",
        "https://github.com/Pennyw0rth/NetExec",
        "https://github.com/iagox86/dnscat2",
        "https://github.com/Hackplayers/evil-winrm"
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
            name_label.config(text=f"Error updating tails!")

    if not name_label:
        pass
    else:
        name_label.config(text="All are up to date!", fg="#00AAFF")

def update_tails(app):
    updates_window = tk.Toplevel(app)
    updates_window.geometry("525x255")
    updates_window.title("Update Tails")
    updates_window.focus_force()

    image_frame = tk.Frame(updates_window)
    image_frame.grid(row=0, column=1, padx=(50, 0), pady=(20, 0))

    image = Image.open("./themes/images/GitHub.png")
    resized_image = image.resize((200, 200))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    updates_frame = tk.Frame(updates_window)
    updates_frame.grid(row=0, column=0, padx=(20, 0), pady=10, sticky="nsew")

    updates_label = tk.Label(updates_frame, text="Downloading tails..")
    updates_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0))

    name_label = tk.Label(updates_frame, text="")
    name_label.grid(row=1, column=0, padx=(20, 0), pady=10)

    progressbar = ttk.Progressbar(updates_frame, mode="indeterminate", length=200)
    progressbar.grid(row=2, column=0, pady=(20, 10))
    progressbar.start()  

    updates_window.after(1000, lambda: clone_repos(name_label))

    save_button = ttk.Button(updates_frame, text="Close", command=lambda: updates_window.destroy())
    save_button.grid(row=3, column=0, pady=(25, 0))  
