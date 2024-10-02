#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import json
import webbrowser
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from modules import dialog

def callback(event):
    webbrowser.open_new("https://darkbyte.net")

def on_combobox_focus(event):
    event.widget.selection_clear()

def open_settings(app):
    try:
        if app.settings_window and tk.Toplevel.winfo_exists(app.settings_window):
            app.settings_window.focus_force()
            return
    except:
        pass

    settings = app.load_settings()
    app.settings_window = tk.Toplevel(app)
    app.settings_window.geometry("525x255")
    app.settings_window.title("Settings")
    app.settings_window.focus_force()
    app.settings_window.resizable(False, False)

    image_frame = tk.Frame(app.settings_window)
    image_frame.grid(row=0, column=1, padx=(10, 0), pady=20)

    image = Image.open("./themes/images/Nekomancer.png")
    resized_image = image.resize((200, 200))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    settings_frame = tk.Frame(app.settings_window)
    settings_frame.grid(row=0, column=0, padx=(15, 0), pady=10, sticky="nsew")

    nekomancer_label = tk.Label(settings_frame, text="Auto-Recover Connections")
    nekomancer_label.grid(row=0, column=0, padx=(15, 0), pady=(20, 0))

    name_label = tk.Label(settings_frame, text="(a.k.a Nekomancer)", fg="#BABABA")
    name_label.grid(row=1, column=0, padx=(15, 0), pady=(0, 5))

    selected_value = tk.StringVar(value=settings.get("nekomancer", "All Sessions"))

    nekomancer_combobox = ttk.Combobox(settings_frame, values=["All Sessions", "Bind Only", "Reverse Only", "Disabled"], textvariable=selected_value, state="readonly")
    nekomancer_combobox.grid(row=2, column=0, padx=(15, 0), pady=(20, 0))
    
    nekomancer_combobox.set(selected_value.get())

    nekomancer_combobox.bind("<FocusIn>", on_combobox_focus)

    def on_enter_key(event):
        save_and_close(app, selected_value)

    app.settings_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.settings_window.destroy()

    app.settings_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(settings_frame, text="Save", command=lambda: save_and_close(app, selected_value))
    save_button.grid(row=3, column=0, pady=(35, 10))  

def save_and_close(app, selected_value):
    app.saved_value = selected_value.get()  

    data = {
        "settings": {
            "theme": app.theme_var.get(),  
            "nekomancer": selected_value.get(),
        }
    }

    with open("data/settings.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    app.settings_window.destroy()
    dialog.settings_success(app)
