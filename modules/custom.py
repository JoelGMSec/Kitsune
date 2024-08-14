#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import sys
sys.dont_write_bytecode = True

import os
import json
import tkinter as tk
from tkinter import ttk
import importlib.util
from modules import dialog

def load_custom_modules(app, reload=False):
    if reload:
        dialog.reload_success(app)
    custom_dir = "custom"
    output_file = "data/modules.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    py_files = [f for f in os.listdir(custom_dir) if f.endswith('.py')]
    data = {
        "modules": []
    }

    for py_file in py_files:
        script_path = os.path.join(custom_dir, py_file)
        if os.path.isfile(script_path):
            description = ""
            try:
                module_name = os.path.splitext(py_file)[0]  # Obtener el nombre del módulo sin la extensión .py
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                module_obj = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module_obj)
                if hasattr(module_obj, 'get_description'):
                    description = module_obj.get_description()
                else:
                    description = "No description available"
            except:
                pass

            data["modules"].append({
                "name": module_name,
                "script": py_file,
                "description": description
            })

    data["modules"].sort(key=lambda x: x["name"])
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
        module_console_tab = tk.Frame(app.notebook)
        module_console_tab.config(background="#333333")
        existing_tabs = app.notebook.tabs()
        tab_texts = [app.notebook.tab(tab_id, "text") for tab_id in existing_tabs]

        tab_texts.append("Module Console")
        sorted_tabs = sorted(tab_texts)
        insert_index = sorted_tabs.index("Module Console")

        for idx, text in enumerate(sorted_tabs):
            if text == "Listeners":
                insert_index = insert_index + 1
                break
            elif text == "Team Chat":
                insert_index = insert_index + 1
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
            selectbackground="#1B1B1B",
            inactiveselectbackground="#1B1B1B",
            borderwidth=0
        )
        app.module_text.pack(expand=True, fill='both')
        app.scrollbar.config(command=app.module_text.yview)

        app.custom_menu = tk.Menu(app.module_text, tearoff=0)
        app.custom_menu.add_command(label="Copy", command=app.copy_custom_text)
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
            current_modules["modules"].sort(key=lambda x: x["name"])
            if current_modules.get("modules"):
                module_banner = "Custom Modules Loaded\n---------------------\n"
                display_message(app, module_banner, "#00FF99")
                
                for module in current_modules["modules"]:
                    module_info = f"[>] {module['name']}"
                    display_message(app, module_info, "#00AAFF")
                    module_info = f"{module.get('description')}\n"
                    display_message(app, module_info, "#FFFFFF")

            else:
                module_info = "[!] No custom modules found!"
                display_message(app, module_info, "#FF0055")
    else:
        module_info = "[!] No custom modules found!"
        display_message(app, module_info, "#FF0055")

    app.module_text.config(state='disabled')

def exec_custom_modules(app, caller, param1, param2):
    modules_file = "data/modules.json"
    combined_output = []

    if os.path.exists(modules_file):
        with open(modules_file, "r") as file:
            current_modules = json.load(file)
            for module in current_modules.get("modules", []):
                script_path = os.path.join("custom", module["script"])
                if os.path.isfile(script_path):
                    spec = importlib.util.spec_from_file_location(module["name"], script_path)
                    module_obj = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module_obj)
                    if hasattr(module_obj, 'main'):
                        output = module_obj.main(app, caller, param1, param2)
                        if output:
                            combined_output.append(output)
                            
    return "\n".join(combined_output) if combined_output else None
