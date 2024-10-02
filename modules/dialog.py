#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import time
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def new_version(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Updates")
    dialog.focus_force()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text="New version available!")
    label.pack(padx=20, pady=20)
    url = "https://github.com/JoelGMSec/Kitsune"

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        webbrowser.open(url)
        dialog.destroy()
    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()
    dialog.bind("<Escape>", on_escape_key)

    def run_update():
        threading.Thread(target=webbrowser.open, args=(url,)).start()
        dialog.destroy()

    yes_button = ttk.Button(button_frame, text="Download", command=lambda: run_update())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))


def settings_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text="Settings saved successfully!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def proxy_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text="Proxy configured successfully!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def report_deleted_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text="All reports have been deleted!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def profile_deleted_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text="All profiles have been deleted!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def report_saved_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text="Report saved successfully!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def profile_saved_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text="Profile saved successfully!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def generate_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    os.system("chmod +x payloads -R")
    label = ttk.Label(dialog, text="Payload generated successfully!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def reload_success(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Success")
    dialog.focus_force()
    dialog.resizable(False, False)

    os.system("chmod +x payloads -R")
    label = ttk.Label(dialog, text="Modules reloaded successfully!")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def delivery_error(app, server):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Error")
    dialog.focus_force()
    dialog.resizable(False, False)

    if server == "multiserver":
        label = ttk.Label(dialog, text="Multi Server is not running!")
        label.pack(padx=20, pady=20)

    if server == "webserver":
        label = ttk.Label(dialog, text="Web Server is not running!")
        label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def on_enter_key(event):
        dialog.destroy()

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        dialog.destroy()

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

def confirm_dialog(app):
    try:
        if app.dialog_window and tk.Toplevel.winfo_exists(app.dialog_window):
            app.dialog_window.focus_force()
            return
    except:
        pass

    dialog = tk.Toplevel(app)
    app.dialog_window = dialog 
    dialog.title("Confirmation")
    dialog.focus_force()
    dialog.resizable(False, False)
    
    label = ttk.Label(dialog, text="Are you sure?")
    label.pack(padx=20, pady=20)

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)

    def set_result(value):
        app.result = value
        dialog.destroy()

    def on_enter_key(event):
        set_result("yes")

    dialog.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        set_result("no")

    dialog.bind("<Escape>", on_escape_key)

    yes_button = ttk.Button(button_frame, text="Yes", command=lambda: set_result("yes"))
    yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    no_button = ttk.Button(button_frame, text="No", command=lambda: set_result("no"))
    no_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    app.result = None
    
    while app.result not in ["yes", "no"]:
        app.update()

    return app.result
