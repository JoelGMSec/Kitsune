#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import time
import shutil
import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from modules import dialog

def on_combobox_focus(event):
    event.widget.selection_clear()

def export_profile(app):
    try:
        if app.export_window and tk.Toplevel.winfo_exists(app.export_window):
            app.export_window.focus_force()
            return
    except:
        pass

    app.export_window = tk.Toplevel(app)
    app.export_window.geometry("525x255")
    app.export_window.title("Save Profile")
    app.export_window.focus_force()
    app.export_window.resizable(False, False)

    image_frame = tk.Frame(app.export_window)
    image_frame.grid(row=0, column=1, padx=(10, 0), pady=20)

    image = Image.open("./themes/images/Floppy.png")
    resized_image = image.resize((200, 200))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    export_frame = tk.Frame(app.export_window)
    export_frame.grid(row=0, column=0, padx=(15, 0), pady=10, sticky="nsew")

    export_label = tk.Label(export_frame, text="Enter profile name")
    export_label.grid(row=0, column=0, padx=(15, 0), pady=(20, 0))

    name_label = tk.Label(export_frame, text="*Overwrited if exists*", fg="#00FF99")
    name_label.grid(row=1, column=0, padx=(15, 0), pady=(0, 5))

    selected_value = tk.StringVar(value="")  

    name_entry = ttk.Entry(export_frame, textvariable=tk.StringVar())
    name_entry.grid(row=2, column=0, padx=(15, 0), pady=(20, 0))

    def on_enter_key(event):
        save_profile(app, name_entry)

    app.export_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.export_window.destroy()

    app.export_window.bind("<Escape>", on_escape_key)

    def on_focus_entry(event):
        try:
            name_entry.configure(state="normal")
            name_entry.state(["!invalid"])
            name_entry.delete(0, tk.END)
            name_entry.configure(foreground="white")
            app.save_button.state(["!invalid"])
            app.save_button['state'] = '!invalid'
        except:
            pass

    name_entry.bind("<Button-1>", on_focus_entry)
    name_entry.bind("<FocusIn>", on_focus_entry)

    app.save_button = ttk.Button(export_frame, text="Save", command=lambda: save_profile(app, name_entry))
    app.save_button.grid(row=3, column=0, pady=(35, 10))  

def import_profile(app):
    try:
        if app.import_window and tk.Toplevel.winfo_exists(app.import_window):
            app.import_window.focus_force()
            return
    except:
        pass

    app.import_window = tk.Toplevel(app)
    app.import_window.geometry("525x255")
    app.import_window.title("Load Profile")
    app.import_window.focus_force()
    app.import_window.resizable(False, False)

    image_frame = tk.Frame(app.import_window)
    image_frame.grid(row=0, column=0, padx=(10, 0), pady=20)

    image = Image.open("./themes/images/Folder.png")
    resized_image = image.resize((200, 200))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    settings_frame = tk.Frame(app.import_window)
    settings_frame.grid(row=0, column=1, padx=(5, 0), pady=10, sticky="nsew")

    export_label = tk.Label(settings_frame, text="Select profile name")
    export_label.grid(row=0, column=1, padx=(5, 0), pady=(20, 0))

    name_label = tk.Label(settings_frame, text="*Loaded after restart*", fg="#FFCC00")
    name_label.grid(row=1, column=1, padx=(5, 0), pady=(0, 5))

    profiles = [name for name in os.listdir("profiles") if os.path.isdir(os.path.join("profiles", name))]
    profiles = sorted(profiles)
    if not profiles:  
        profiles = ["No profiles found!"]

    selected_value = tk.StringVar(value=profiles[0])

    app.profile_combobox = ttk.Combobox(settings_frame, values=profiles, textvariable=selected_value, state="readonly")
    app.profile_combobox.grid(row=2, column=1, padx=(15, 0), pady=(20, 0))

    if selected_value.get() == str("No profiles found!"):
        app.profile_combobox.configure(state="disabled")
        app.profile_combobox.configure(foreground="#c0c0c0")

    def on_enter_key(event):
        load_and_close(app, selected_value)

    def on_escape_key(event):
        app.import_window.destroy()

    app.profile_combobox.set(selected_value.get())
    app.import_window.bind("<Return>", on_enter_key)
    app.profile_combobox.bind("<FocusIn>", on_combobox_focus)
    app.import_window.bind("<Escape>", on_escape_key)

    app.save_button = ttk.Button(settings_frame, text="Load", command=lambda: load_and_close(app, selected_value))
    app.save_button.grid(row=3, column=1, pady=(35, 10))  

def delete_profile(app):
    profiles_path = "profiles"
    if dialog.confirm_dialog(app) == "yes":   
        if os.path.exists(profiles_path) and os.path.isdir(profiles_path):
            try:
                for folder_name in os.listdir(profiles_path):
                    folder_path = os.path.join(profiles_path, folder_name)
                    if os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
            except:
                pass
    
        dialog.profile_deleted_success(app)

def save_profile(app, name_entry):
    if name_entry.get():
        profile_name = name_entry.get().strip()
        if profile_name and profile_name != "Invalid profile name!": 
            profile_path = os.path.join("profiles", profile_name)
            data_path = "data"
            try:
                os.makedirs(profile_path, exist_ok=True)  
                for item in os.listdir(data_path):  
                    s = os.path.join(data_path, item)
                    d = os.path.join(profile_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
            except:
                pass

            app.export_window.destroy()
            dialog.profile_saved_success(app)

        else:
            name_entry.state(["invalid"])
            name_entry.delete(0, tk.END)
            name_entry.insert(0, "Invalid profile name!")
            name_entry.configure(foreground="#c0c0c0")
            name_entry.state(["readonly"])
            app.save_button.state(["invalid"])
            app.save_button['state'] = 'invalid'

    else:
        name_entry.state(["invalid"])
        name_entry.delete(0, tk.END)
        name_entry.insert(0, "Invalid profile name!")
        name_entry.configure(foreground="#c0c0c0")
        name_entry.state(["readonly"])
        app.save_button.state(["invalid"])
        app.save_button['state'] = 'invalid'

def load_and_close(app, selected_value):
    if selected_value.get() != str("No profiles found!"):
        if dialog.confirm_dialog(app) == "yes":
            app.import_window.destroy()
            app.remove_data()
            profile_name = selected_value.get()
            profile_path = os.path.join("profiles", profile_name)
            data_path = "data"

            try:
                for item in os.listdir(data_path):
                    item_path = os.path.join(data_path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    else:  
                        shutil.rmtree(item_path)

                for item in os.listdir(profile_path):
                    s = os.path.join(profile_path, item)
                    d = os.path.join(data_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)

                app.event_viewer_logs.clear()
                app.event_viewer_logs = []
                app.event_viewer_logs = app.load_event_viewer_logs()
                app.restart_app(selected_value.get())

            except:
                pass

            app.import_window.destroy()

    else:
        app.profile_combobox.state(["invalid"])
        app.save_button.state(["invalid"])
        app.save_button['state'] = 'invalid'
