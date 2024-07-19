#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import json
import tkinter as tk
from tkinter import ttk

def load_custom_modules(app, reload=False):
    if reload:
        app.reload_success()
    custom_dir = "custom"
    output_file = "data/modules.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    folders = [f for f in os.listdir(custom_dir) if os.path.isdir(os.path.join(custom_dir, f))]
    data = {
        "modules": []
    }

    for folder in folders:
        script_name = f"{folder}.py"
        script_path = os.path.join(custom_dir, script_name)
        if os.path.isfile(script_path):
            data["modules"].append({
                "name": folder,
                "script": script_name
            })

    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def open_module_console(app):
    module_console_tab_id = None
    for tab_id in app.notebook.tabs():
        if app.notebook.tab(tab_id, "text") == "Module Console":
            module_console_tab_id = tab_id
            app.notebook.select(module_console_tab_id)
            break

    if not module_console_tab_id:
        module_console_tab = ttk.Frame(app.notebook)
        existing_tabs = app.notebook.tabs()
        tab_texts = [app.notebook.tab(tab_id, "text") for tab_id in existing_tabs]

        insert_index = len(existing_tabs)
        for idx, text in enumerate(tab_texts):
            if text == "Listeners":
                insert_index = idx + 1
                break
            elif text == "Team Chat":
                insert_index = idx + 1
                break

        try:
            app.notebook.insert(insert_index, module_console_tab, text="Module Console")
        except:
            app.notebook.add(module_console_tab, text="Module Console")

        app.notebook.select(module_console_tab)
        app.notebook.tab(module_console_tab, state="normal")
        app.scrollbar = ttk.Scrollbar(module_console_tab)
        app.scrollbar.pack(side="right", fill="y")

        app.module_text = tk.Text(
            module_console_tab,
            wrap='word',
            state='disabled',
            yscrollcommand=app.scrollbar.set,
            background="#333333",
            foreground="#FF00FF",
            padx=5,
            pady=5,
            highlightthickness=0,
            borderwidth=0
        )
        app.module_text.pack(expand=True, fill='both')
        app.scrollbar.config(command=app.module_text.yview)

        app.custom_menu = tk.Menu(app.module_text, tearoff=0)
        app.custom_menu.add_command(label="Copy", command=app.copy_text)
        app.custom_menu.add_command(label="Reload", command=lambda: show_current_modules(app, True))
        app.module_text.bind("<Button-3>", app.show_custom_menu)

def display_message(app, message, color):
    try:
        current_content = app.module_text.get(1.0, tk.END)
        if message in current_content:
            return

        app.last_displayed_message = {"text": message, "color": color}
        app.module_text.config(font=("Consolas", 18, "bold"))
        app.module_text.config(state='normal')
        app.module_text.insert(tk.END, f"{message}\n", (color,))
        app.module_text.tag_config(color, foreground=color)
        app.module_text.config(state='disabled')
        app.module_text.see("end")
    except:
        pass

def show_current_modules(app, reload):
    open_module_console(app)
    load_custom_modules(app, reload)
    modules_file = "data/modules.json"
    
    app.module_text.config(state='normal')
    app.module_text.delete(1.0, tk.END)

    if os.path.exists(modules_file):
        with open(modules_file, "r") as file:
            current_modules = json.load(file)
            if current_modules.get("modules"):
                module_banner = "Custom Modules Loaded\n---------------------\n"
                display_message(app, module_banner, "#00FF99")
                
                for module in current_modules["modules"]:
                    module_info = f"[>] {module['name']}"
                    display_message(app, module_info, "#00AAFF")
            else:
                module_info = "[!] No custom modules found!"
                display_message(app, module_info, "#FF0055")
    else:
        module_info = "[!] No custom modules found!"
        display_message(app, module_info, "#FF0055")

    app.module_text.config(state='disabled')

