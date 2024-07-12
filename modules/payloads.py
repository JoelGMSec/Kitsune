#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import json
import tkinter as tk
from tkinter import ttk
from modules import listeners
from modules.session import Session
from modules.connect import pwncat_thread
from modules.connect import pyshell_thread
from modules.controller import connect_session
from modules.generate import generate_payload
from modules.generate import generate_webshell

def on_combobox_focus(event):
    event.widget.selection_clear()

def windows_payload(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x330")
    listener_window.title("Windows Reverse Shell")
    listener_window.focus_force()

    selected_tail = tk.StringVar()
    selected_output = tk.StringVar()

    def update_listener_options(*args):
        selected_tail_value = selected_tail.get()
        filtered_listeners = [listener for listener in listeners.load_listeners(app) if listener["Tail"] == selected_tail_value]
        listener_names = [listener["Name"] for listener in filtered_listeners]
        port_listener_combobox['values'] = listener_names
        port_listener_combobox.set("")

    ttk.Label(listener_window, text="Tail").grid(row=1, column=0, padx=0, pady=15)
    windows_tail_entry = ttk.Combobox(listener_window, values=["HTTP-Shell", "DnsCat2", "Villain"], state="readonly", textvariable=selected_tail)
    
    windows_tail_entry.bind("<FocusIn>", on_combobox_focus)

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    windows_tail_entry.grid(row=1, column=1, padx=0, pady=15)
    windows_tail_entry.bind("<<ComboboxSelected>>", update_listener_options)

    ttk.Label(listener_window, text="Output").grid(row=2, column=0, padx=0, pady=15)
    windows_output_entry = ttk.Combobox(listener_window, values=["Dll", "Exe", "Ps1"], state="readonly", textvariable=selected_output)
    windows_output_entry.grid(row=2, column=1, padx=0, pady=15)

    windows_output_entry.bind("<FocusIn>", on_combobox_focus)

    ttk.Label(listener_window, text="Listener").grid(row=3, column=0, padx=0, pady=15)
    port_listener_combobox = ttk.Combobox(listener_window, state="readonly")
    port_listener_combobox.grid(row=3, column=1, padx=0, pady=15)

    port_listener_combobox.bind("<FocusIn>", on_combobox_focus)

    update_listener_options()

    def get_params_and_generate():
        if selected_tail.get() and selected_output.get() and port_listener_combobox.get():
            generate_payload(app, selected_tail.get(), selected_output.get(), port_listener_combobox.get())
            listener_window.destroy()

    def on_enter_key(event):
        get_params_and_generate()

    listener_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        listener_window.destroy()

    listener_window.bind("<Escape>", on_escape_key)

    ttk.Button(listener_window, text="Generate", command=get_params_and_generate).grid(row=4, column=0, padx=50, pady=20)
    ttk.Button(listener_window, text="Cancel", command=listener_window.destroy).grid(row=4, column=1, padx=20, pady=20)

def linux_payload(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x330")
    listener_window.title("Linux Reverse Shell")
    listener_window.focus_force()

    selected_tail = tk.StringVar()
    selected_output = tk.StringVar()

    def update_listener_options(*args):
        selected_tail_value = selected_tail.get()
        filtered_listeners = [listener for listener in listeners.load_listeners(app) if listener["Tail"] == selected_tail_value]
        listener_names = [listener["Name"] for listener in filtered_listeners]
        port_listener_combobox['values'] = listener_names
        port_listener_combobox.set("")

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    ttk.Label(listener_window, text="Tail").grid(row=1, column=0, padx=0, pady=15)
    linux_tail_entry = ttk.Combobox(listener_window, values=["HTTP-Shell", "DnsCat2", "PwnCat-CS"], state="readonly", textvariable=selected_tail)
    linux_tail_entry.grid(row=1, column=1, padx=0, pady=15)
    linux_tail_entry.bind("<<ComboboxSelected>>", update_listener_options)

    linux_tail_entry.bind("<FocusIn>", on_combobox_focus)

    ttk.Label(listener_window, text="Output").grid(row=2, column=0, padx=0, pady=15)
    linux_output_entry = ttk.Combobox(listener_window, values=["Bash", "Binary", "Python 3"], state="readonly", textvariable=selected_output)
    linux_output_entry.grid(row=2, column=1, padx=0, pady=15)

    linux_output_entry.bind("<FocusIn>", on_combobox_focus)

    ttk.Label(listener_window, text="Listener").grid(row=3, column=0, padx=0, pady=15)
    port_listener_combobox = ttk.Combobox(listener_window, state="readonly")
    port_listener_combobox.grid(row=3, column=1, padx=0, pady=15)

    port_listener_combobox.bind("<FocusIn>", on_combobox_focus)

    update_listener_options()

    def get_params_and_generate():
        if selected_tail.get() and selected_output.get() and port_listener_combobox.get():
            generate_payload(app, selected_tail.get(), selected_output.get(), port_listener_combobox.get())
            listener_window.destroy()

    def on_enter_key(event):
        get_params_and_generate()

    listener_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        listener_window.destroy()

    listener_window.bind("<Escape>", on_escape_key)

    ttk.Button(listener_window, text="Generate", command=get_params_and_generate).grid(row=4, column=0, padx=50, pady=20)
    ttk.Button(listener_window, text="Cancel", command=listener_window.destroy).grid(row=4, column=1, padx=20, pady=20)

def webshell_payload(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x330")
    listener_window.title("Web Shell (Bind)")
    listener_window.focus_force()

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    tail_label = ttk.Label(listener_window, text="Tail")
    tail_label.grid(row=1, column=0, padx=0, pady=15)

    tail_entry = ttk.Combobox(listener_window, values=["PyShell"], state="disabled")
    tail_entry.current(0)
    tail_entry.grid(row=1, column=1, padx=0, pady=15)

    tail_entry.bind("<FocusIn>", on_combobox_focus)

    params_label = ttk.Label(listener_window, text="Params")
    params_label.grid(row=2, column=0, padx=0, pady=15)

    params_entry = ttk.Entry(listener_window)
    params_entry.grid(row=2, column=1, padx=0, pady=15)

    method_label = ttk.Label(listener_window, text="Method")
    method_label.grid(row=3, column=0, padx=0, pady=15)

    method_combobox = ttk.Combobox(listener_window, values=["GET", "POST"], state="readonly")
    method_combobox.grid(row=3, column=1, padx=0, pady=15)

    method_combobox.bind("<FocusIn>", on_combobox_focus)

    def get_params_and_start_thread():
        params = params_entry.get()
        if params and method_combobox.get():
            pyshell_thread(app, params, method_combobox.get(), app.session_id, restart=False)
            listener_window.destroy()

    def on_enter_key(event):
        get_params_and_start_thread()

    listener_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        listener_window.destroy()

    listener_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(listener_window, text="Connect", command=get_params_and_start_thread)
    save_button.grid(row=4, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(listener_window, text="Cancel", command=listener_window.destroy)
    cancel_button.grid(row=4, column=1, padx=20, pady=20)

def webshell_generate(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x330")
    listener_window.title("Web Shell (Generate)")
    listener_window.focus_force()

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    tail_label = ttk.Label(listener_window, text="Tail")
    tail_label.grid(row=1, column=0, padx=0, pady=15)

    tail_entry = ttk.Combobox(listener_window, values=["PyShell"], state="disabled")
    tail_entry.current(0)
    tail_entry.grid(row=1, column=1, padx=0, pady=15)

    tail_entry.bind("<FocusIn>", on_combobox_focus)

    params_label = ttk.Label(listener_window, text="Format")
    params_label.grid(row=2, column=0, padx=0, pady=15)

    params_entry = ttk.Combobox(listener_window, values=["Asp", "Aspx", "Jsp", "Php", "Python 3", "Shell", "Tomcat", "Wordpress"], state="readonly")
    params_entry.grid(row=2, column=1, padx=0, pady=15)

    params_entry.bind("<FocusIn>", on_combobox_focus)

    method_label = ttk.Label(listener_window, text="Obfuscate")
    method_label.grid(row=3, column=0, padx=0, pady=15)

    method_combobox = ttk.Combobox(listener_window, values=["No", "Yes"], state="readonly")
    method_combobox.grid(row=3, column=1, padx=0, pady=15)

    method_combobox.bind("<FocusIn>", on_combobox_focus)

    def get_params_and_generate():
        if tail_entry.get() and params_entry.get() and method_combobox.get():
            generate_webshell(app, tail_entry.get(), params_entry.get(), method_combobox.get())
            listener_window.destroy()

    def on_enter_key(event):
        get_params_and_generate()

    listener_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        listener_window.destroy()

    listener_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(listener_window, text="Generate", command=get_params_and_generate)
    save_button.grid(row=4, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(listener_window, text="Cancel", command=listener_window.destroy)
    cancel_button.grid(row=4, column=1, padx=20, pady=20)

def pwncat_payload(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x330")
    listener_window.title("Linux Bind Shell")
    listener_window.focus_force()

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    tail_label = ttk.Label(listener_window, text="Tail")
    tail_label.grid(row=1, column=0, padx=0, pady=15)

    tail_entry = ttk.Combobox(listener_window, values=["PwnCat-CS"])
    tail_entry.current(0)
    tail_entry['state'] = 'disabled'
    tail_entry.grid(row=1, column=1, padx=0, pady=15)

    params_label = ttk.Label(listener_window, text="Params")
    params_label.grid(row=2, column=0, padx=0, pady=15)

    params_entry = ttk.Entry(listener_window)
    params_entry.grid(row=2, column=1, padx=0, pady=15)

    pwncat_pass_label = ttk.Label(listener_window, text="Password")
    pwncat_pass_label.grid(row=3, column=0, padx=0, pady=15)

    pwncat_pass = ttk.Entry(listener_window, show="*")
    pwncat_pass.grid(row=3, column=1, padx=0, pady=15)

    def get_params_and_start_thread():
        params = params_entry.get()
        if params and pwncat_pass.get():
            pwncat_thread(app, params, pwncat_pass.get(), app.session_id, restart=False)
            listener_window.destroy()

    def on_enter_key(event):
        get_params_and_start_thread()

    listener_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        listener_window.destroy()

    listener_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(listener_window, text="Connect", command=get_params_and_start_thread)
    save_button.grid(row=4, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(listener_window, text="Cancel", command=listener_window.destroy)
    cancel_button.grid(row=4, column=1, padx=20, pady=20)

def netexec_payload(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x615")
    listener_window.title("Windows Bind Shell")
    listener_window.focus_force()

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    tail_label = ttk.Label(listener_window, text="Tail")
    tail_label.grid(row=1, column=0, padx=0, pady=15)

    tail_entry = ttk.Combobox(listener_window, values=["NetExec", "Evil-WinRM", "WMIexec-Pro"], state="readonly")
    tail_entry.current(0)
    tail_entry.grid(row=1, column=1, padx=0, pady=15)

    tail_entry.bind("<FocusIn>", on_combobox_focus)

    ip_label = ttk.Label(listener_window, text="IP Address")
    ip_label.grid(row=2, column=0, padx=0, pady=15)

    ip_entry = ttk.Entry(listener_window)
    ip_entry.grid(row=2, column=1, padx=0, pady=15)

    user_label = ttk.Label(listener_window, text="Username")
    user_label.grid(row=3, column=0, padx=0, pady=15)

    user_entry = ttk.Entry(listener_window)
    user_entry.grid(row=3, column=1, padx=0, pady=15)

    auth_label = ttk.Label(listener_window, text="Authentication")
    auth_label.grid(row=4, column=0, padx=0, pady=15)

    auth_combobox = ttk.Combobox(listener_window, values=["Hash", "Password"], state="readonly")
    auth_combobox.grid(row=4, column=1, padx=0, pady=15)

    auth_combobox.bind("<FocusIn>", on_combobox_focus)

    nxc_pass_label = ttk.Label(listener_window, text="Credential")
    nxc_pass_label.grid(row=5, column=0, padx=0, pady=15)

    nxc_pass = ttk.Entry(listener_window)
    nxc_pass.grid(row=5, column=1, padx=0, pady=15)

    def on_auth_combobox_focus(event):
        selected_value = auth_combobox.get()

        if selected_value == "Password":
            nxc_pass['show'] = "*"
        else:
            nxc_pass['show'] = ""

    nxc_pass.bind("<FocusIn>", on_auth_combobox_focus)

    local_auth_label = ttk.Label(listener_window, text="Local Auth")
    local_auth_label.grid(row=6, column=0, padx=0, pady=15)

    local_auth_combobox = ttk.Combobox(listener_window, values=["No", "Yes"], state="readonly")
    local_auth_combobox.grid(row=6, column=1, padx=0, pady=15)

    local_auth_combobox.bind("<FocusIn>", on_combobox_focus)

    protocol_label = ttk.Label(listener_window, text="Protocol")
    protocol_label.grid(row=7, column=0, padx=0, pady=15)

    protocol_combobox = ttk.Combobox(listener_window, values=["MMSQL", "SMB", "WinRM", "WMI"], state="readonly")
    protocol_combobox.grid(row=7, column=1, padx=0, pady=15)

    protocol_combobox.bind("<FocusIn>", on_combobox_focus)

    def set_protocol(event):
        selected_tail = tail_entry.get()
        if selected_tail == "Evil-WinRM":
            local_auth_combobox.set("N/A")
            local_auth_combobox['state'] = 'disabled'
            protocol_combobox.set("WinRM")
            protocol_combobox['state'] = 'disabled'
        elif selected_tail == "NetExec":
            local_auth_combobox.set("")
            local_auth_combobox['state'] = 'readonly'
            protocol_combobox.set("")
            protocol_combobox['state'] = 'readonly'
        elif selected_tail == "WMIexec-Pro":
            local_auth_combobox.set("N/A")
            local_auth_combobox['state'] = 'disabled'
            protocol_combobox.set("WMI")
            protocol_combobox['state'] = 'disabled'

    tail_entry.bind("<<ComboboxSelected>>", set_protocol)

    def get_params_and_start_thread():
        params = str(ip_entry.get() + " -u " + user_entry.get() + " -p " + nxc_pass.get())
        if params and protocol_combobox.get() and tail_entry.get():
            if local_auth_combobox.get() == "Yes":
                params += " --local-auth"
            connect_session(app, params, protocol_combobox.get(), app.session_id, tail_entry.get())
            listener_window.destroy()

    def on_enter_key(event):
        get_params_and_start_thread()

    listener_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        listener_window.destroy()

    listener_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(listener_window, text="Connect", command=get_params_and_start_thread)
    save_button.grid(row=8, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(listener_window, text="Cancel", command=listener_window.destroy)
    cancel_button.grid(row=8, column=1, padx=20, pady=20)
