#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import sys
import json
import tkinter as tk
from tkinter import ttk
from modules import dialog

def on_combobox_focus(event):
    event.widget.selection_clear()

def set_proxy(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x330")
    listener_window.title("Proxification")
    listener_window.focus_force()

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    tail_label = ttk.Label(listener_window, text="Status")
    tail_label.grid(row=1, column=0, padx=0, pady=15)

    tail_entry = ttk.Combobox(listener_window, values=["Disabled","Enabled"], state="readonly")
    tail_entry.current(0)
    tail_entry.grid(row=1, column=1, padx=0, pady=15)
    tail_entry.bind("<FocusIn>", on_combobox_focus)

    params_label = ttk.Label(listener_window, text="IP:PORT")
    params_label.grid(row=2, column=0, padx=0, pady=15)

    params_entry = ttk.Entry(listener_window)
    params_entry.grid(row=2, column=1, padx=0, pady=15)
    params_entry.insert(0, "127.0.0.1:1080")
    params_entry.bind("<FocusIn>", on_combobox_focus)

    method_label = ttk.Label(listener_window, text="Protocol")
    method_label.grid(row=3, column=0, padx=0, pady=15)

    method_combobox = ttk.Combobox(listener_window, values=["SOCKS", "HTTP"], state="readonly")
    method_combobox.current(0)
    method_combobox.grid(row=3, column=1, padx=0, pady=15)
    method_combobox.bind("<FocusIn>", on_combobox_focus)

    def get_params_and_generate():
        if tail_entry.get() and params_entry.get() and method_combobox.get():
            app.proxy_status = tail_entry.get() == "Enabled"
            save_proxy_settings(tail_entry.get(), params_entry.get(), method_combobox.get())
            listener_window.destroy()
            dialog.proxy_success(app)

    def on_enter_key(event):
        get_params_and_generate()

    listener_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        listener_window.destroy()

    listener_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(listener_window, text="Save", command=get_params_and_generate)
    save_button.grid(row=4, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(listener_window, text="Cancel", command=listener_window.destroy)
    cancel_button.grid(row=4, column=1, padx=20, pady=20)

    load_proxy_settings(app)
    load_proxy_window(app, tail_entry, params_entry, method_combobox)

def load_proxy_settings(app):
    try:
        with open("data/proxy.json", "r") as f:
            proxy_settings = json.load(f)
            app.proxy_status = proxy_settings.get("status", "Disabled") == "Enabled"
            if app.proxy_status:
                protocol = proxy_settings.get("protocol", "SOCKS")
                ip_port = proxy_settings.get("ip_port", "127.0.0.1:1080")
                host, port = ip_port.split(":")
                update_proxychains_conf(protocol, host, port)
            return proxy_settings

    except FileNotFoundError:
        app.proxy_status = False
        return {"status": "Disabled", "ip_port": "127.0.0.1:1080", "protocol": "SOCKS"}

def save_proxy_settings(status, ip_port, protocol):
    proxy_settings = {
        "status": status,
        "ip_port": ip_port,
        "protocol": protocol
    }
    os.makedirs("data", exist_ok=True)
    with open("data/proxy.json", "w") as f:
        json.dump(proxy_settings, f, indent=4)

    if status == "Enabled":
        update_proxychains_conf(protocol, ip_port.split(":")[0], ip_port.split(":")[1])

def load_proxy_window(app, tail_entry, params_entry, method_combobox):
    try:
        with open("data/proxy.json", "r") as f:
            proxy_settings = json.load(f)
            tail_entry.set(proxy_settings.get("status", "Disabled"))
            params_entry.delete(0, tk.END)
            params_entry.insert(0, proxy_settings.get("ip_port", "127.0.0.1:1080"))
            method_combobox.set(proxy_settings.get("protocol", "SOCKS"))
            app.proxy_status = proxy_settings.get("status", "Disabled") == "Enabled"
    except FileNotFoundError:
        app.proxy_status = False

def update_proxychains_conf(proto, host, port):
    if not proto or not host or not port:
        return

    config_path = "/etc/proxychains4.conf"
    
    if not os.path.isfile(config_path):
        return
    
    try:
        with open(config_path, 'r') as f:
            lines = f.readlines()
        
        if proto.lower() == "socks":
            proto = "socks5"
        lines[-2] = "\n"
        lines[-1] = f"{proto.lower()} {host} {port}\n"

        with open(config_path, 'w') as f:
            f.writelines(lines)
        
    except:
        pass
