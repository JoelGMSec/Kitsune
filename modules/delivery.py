#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import re
import ssl
import json
import time
import atexit
import asyncio
import logging
import datetime
import threading
import subprocess
import http.server
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from modules import dialog
from impacket import smbserver
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from shenaniganfs.nfs_utils import serve_nfs
from shenaniganfs.fs import SimpleFS, SimpleDirectory, SimpleFile, VerifyingFileHandleEncoder
from shenaniganfs.fs_manager import EvictingFileSystemManager, create_fs

def on_combobox_focus(event):
    event.widget.selection_clear()

def regex_text(text):
    dynamic_text = r"(\d+\.\d+\.\d+\.\d+) - - \[(\d+/\w+/\d+ )(\d+:\d+:\d+)\] \"(.*?)\" (\d+) -"
    results = re.findall(dynamic_text, text)
    regex_text = []
    for result in results:
        ip, fecha, hora, peticion, codigo = result
        regex_text.append(f"[{hora}] CODE: {codigo} - FROM: {ip} - {peticion}")
    return regex_text

def regex_multi_text(text):
    dynamic_text = r"^[^:]*:[^:]*:"
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    regex_text = []

    cleaned_text = re.sub(dynamic_text, '', text)
    lines = cleaned_text.splitlines()
    for line in lines:
        if line.strip():
            regex_text.append(f"[{current_time}] {line.strip()}")

    return regex_text

def copy_text(app, log_text):
    try:
        selected_text = log_text.selection_get()
        log_text.clipboard_clear()
        log_text.clipboard_append(selected_text)
        log_text.tag_remove(tk.SEL, "1.0", tk.END)
    except Exception as e:
        print(e)
        pass

def start_updating_multiserver_log(app):
    def update_loop():
        while True:
            try:
                multiserver_file = Path('data/multiserver.json')
                if multiserver_file.exists():
                    with open(multiserver_file, 'r') as f:
                        log_data = json.load(f)
                        old_entries = log_data.get("Log", [])

                time.sleep(0.2)
                if multiserver_file.exists():
                    with open(multiserver_file, 'r') as f:
                        log_data = json.load(f)
                        log_entries = log_data.get("Log", [])

                    if log_entries != old_entries:
                        update_multiserver_log_tab(app)
            except:
                pass

    thread = threading.Thread(target=update_loop)
    thread.daemon = True
    thread.start()

def start_web_delivery(ip, port, protocol, app):
    stop_webserver(app)
    webserver_file = Path('data/webserver.json')
    server_address = (ip, port)

    if webserver_file.exists():
        with open(webserver_file, 'r') as f:
            log_data = json.load(f)
            log_entries = log_data.get("Log", [])
    else:
        log_data = {}
        log_entries = []

    log_data.update({
        "Protocol": protocol,
        "IP Address": ip,
        "Listening Port": port,
        "Path": "../Kitsune/Payloads\n"
    })

    log_data["Log"] = log_entries

    with open(webserver_file, 'w') as f:
        json.dump(log_data, f, indent=4)

    script_path = os.path.join(os.getcwd(), "payloads")
 
    try:
        if protocol == "HTTPS":
            command = [os.sys.executable, 'modules/https.py', ip, script_path, str(port)]
            app.web_delivery_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        else:
            command = [os.sys.executable, '-m', 'http.server', '--bind', ip, '-d', script_path, str(port)]
            app.web_delivery_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def capture_output(process, filename):
            while True:
                time.sleep(0.2)
                output = process.stdout.readline()
                if process.poll() is not None and not output:
                    break
                if output:
                    output = output.strip().decode()
                    log_lines = regex_text(output)
                    with open(filename, 'r+') as f:
                        log_data = json.load(f)
                        log_data["Log"].extend(log_lines)
                        f.seek(0)
                        json.dump(log_data, f, indent=4)
                        f.truncate()
                    app.notify_web_delivery()
                    update_webserver_log_tab(app)

        thread = threading.Thread(target=capture_output, args=(app.web_delivery_process, 'data/webserver.json'))
        thread.daemon = True
        thread.start()
        
        atexit.register(app.web_delivery_process.terminate)
        update_webserver_log_tab(app)
        app.notify_web_delivery()
        return app.web_delivery_process

    except:
        pass

def update_multiserver_log_tab(app):
    multiserver_file = Path("data/multiserver.json")
    try:
        with open(multiserver_file, 'r') as f:
            log_data = json.load(f)
        for tab in app.notebook.tabs():
            if app.notebook.tab(tab, "text") == "Multi Server Log":
                multiserver_tab = tab
                break
        else:
            return

        log_text = app.notebook.nametowidget(multiserver_tab).winfo_children()[1]
        log_text.config(state="normal")
        log_text.delete(1.0, 'end')

        log_text.tag_configure("color_error", foreground="#FF0055")
        log_text.tag_configure("color_success", foreground="#00FF99")
        log_text.tag_configure("color_listen", foreground="#FFCC00")
        log_text.tag_configure("color_input", foreground="#00AAFF")

        if app.multi_delivery_process and app.multi_delivery_process.is_alive():
            message = "[>] Multi Server is running..\n"
            color_tag = "color_input"
        else:
            message = "[!] Multi Server is not running!\n"
            color_tag = "color_error"

        log_text.insert('end', f"{message}\n", color_tag)

        for key, value in log_data.items():
            if key == "Log":
                for line in value:
                    log_text.insert('end', f"{line}\n", "color_listen")
            else:
                log_text.insert('end', f"{key}: {value}\n", "color_success")

        log_text.config(state="disabled")
        log_text.see("end")

    except:
        pass

def update_webserver_log_tab(app):
    webserver_file = Path("data/webserver.json")
    try:
        with open(webserver_file, 'r') as f:
            log_data = json.load(f)
        for tab in app.notebook.tabs():
            if app.notebook.tab(tab, "text") == "Web Server Log":
                webserver_tab = tab
                break
        else:
            return

        log_text = app.notebook.nametowidget(webserver_tab).winfo_children()[1]
        log_text.config(state="normal")
        log_text.delete(1.0, 'end')

        log_text.tag_configure("color_error", foreground="#FF0055")
        log_text.tag_configure("color_success", foreground="#00FF99")
        log_text.tag_configure("color_listen", foreground="#FFCC00")
        log_text.tag_configure("color_input", foreground="#00AAFF")

        if app.web_delivery_process:
            message = "[>] Web Server is running..\n"
            color_tag = "color_input"
        else:
            message = "[!] Web Server is not running!\n"
            color_tag = "color_error"

        log_text.insert('end', f"{message}\n", color_tag)

        for key, value in log_data.items():
            if key == "Log":
                for line in value:
                    log_text.insert('end', f"{line}\n", "color_listen")
            else:
                log_text.insert('end', f"{key}: {value}\n", "color_success")

        log_text.config(state="disabled")
        log_text.see("end")

    except:
        pass

def open_webserver_log_tab(app):
    webserver_file = Path("data/webserver.json")

    try:
        with open(webserver_file, 'r') as f:
            log_data = json.load(f)

    except:
        log_data = {}

    for tab in app.notebook.tabs():
        if app.notebook.tab(tab, "text") == "Web Server Log":
            app.notebook.select(tab)
            update_webserver_log_tab(app)
            return

    tab = tk.Frame(app.notebook)
    tab.config(background="#333333")
    existing_tabs = app.notebook.tabs()
    tab_texts = [app.notebook.tab(tab_id, "text") for tab_id in existing_tabs]

    insert_index = len(existing_tabs)
    for idx, text in enumerate(tab_texts):
        if text.startswith("Session"):
            insert_index = idx
            break

    existing_tabs = app.notebook.tabs()
    tab_texts = [app.notebook.tab(tab_id, "text") for tab_id in existing_tabs]

    insert_index = len(existing_tabs)
    for idx, text in enumerate(tab_texts):
        if text.startswith("Session"):
            insert_index = idx
            break

    tab = tk.Frame(app.notebook)
    tab.config(background="#333333")
    app.notebook.add(tab, text="Web Server Log")
    if insert_index < 0 or insert_index > len(existing_tabs):
        insert_index = len(existing_tabs)
    app.notebook.insert(insert_index, tab, text="Web Server Log")
    scrollbar = ttk.Scrollbar(tab)
    scrollbar.pack(side="right", fill="y")

    log_text = tk.Text(
        tab,
        background="#333333",
        foreground="#FFCC00",
        padx=5,
        pady=5,
        wrap="word",
        highlightthickness=0,
        selectbackground="#1B1B1B",
        inactiveselectbackground="#1B1B1B",
        borderwidth=0,
        yscrollcommand=scrollbar.set
    )
    log_text.pack(fill="both", expand=True)
    scrollbar.config(command=log_text.yview)

    log_text.config(state="normal")
    log_text.delete(1.0, 'end')

    log_text.tag_configure("color_error", foreground="#FF0055")
    log_text.tag_configure("color_success", foreground="#00FF99")
    log_text.tag_configure("color_listen", foreground="#FFCC00")
    log_text.tag_configure("color_input", foreground="#00AAFF")

    app.delivery_menu = tk.Menu(log_text, tearoff=0)
    app.delivery_menu.add_command(label="Copy", command=lambda: copy_text(app, log_text))
    app.delivery_menu.add_command(label="Clear", command=lambda: app.clear_delivery_logs(log_text, "web"))
    log_text.bind("<Button-3>", app.show_delivery_menu)

    if app.web_delivery_process and app.web_delivery_process.poll() is None:
        message = "[>] Web Server is running..\n"
        color_tag = "color_input"
    else:
        message = "[!] Web Server is not running!\n"
        color_tag = "color_error"

    log_text.insert('end', f"{message}\n", color_tag)

    try:
        for key, value in log_data.items():
            log_text.insert('end', f"{key}: {value}\n")
    except:
        pass

    log_text.config(font=("Consolas", 18, "bold"))
    log_text.config(state="disabled")
    app.notebook.select(tab)
    update_webserver_log_tab(app)

def open_multiserver_log_tab(app):
    multiserver_file = Path("data/multiserver.json")

    try:
        with open(multiserver_file, 'r') as f:
            log_data = json.load(f)

    except:
        log_data = {}

    for tab in app.notebook.tabs():
        if app.notebook.tab(tab, "text") == "Multi Server Log":
            app.notebook.select(tab)
            update_multiserver_log_tab(app)
            return

    tab = tk.Frame(app.notebook)
    tab.config(background="#333333")
    existing_tabs = app.notebook.tabs()
    tab_texts = [app.notebook.tab(tab_id, "text") for tab_id in existing_tabs]

    tab_texts.append("Multi Server Log")
    sorted_tabs = sorted(tab_texts)
    insert_index = sorted_tabs.index("Multi Server Log")

    for idx, text in enumerate(sorted_tabs):
        if text == "Session*":
            insert_index = insert_index - 1
            break
        elif text == "Listeners":
            insert_index = insert_index + 1
            break
        elif text == "Team Chat":
            insert_index = insert_index + 1
            break

    try:
        app.notebook.insert(insert_index, tab, text="Multi Server Log")
    except:
        app.notebook.add(tab, text="Multi Server Log")
    scrollbar = ttk.Scrollbar(tab)
    scrollbar.pack(side="right", fill="y")

    log_text = tk.Text(
        tab,
        background="#333333",
        foreground="#FFCC00",
        padx=5,
        pady=5,
        wrap="word",
        highlightthickness=0,
        selectbackground="#1B1B1B",
        inactiveselectbackground="#1B1B1B",
        borderwidth=0,
        yscrollcommand=scrollbar.set
    )
    log_text.pack(fill="both", expand=True)
    scrollbar.config(command=log_text.yview)

    log_text.config(state="normal")
    log_text.delete(1.0, 'end')

    log_text.tag_configure("color_error", foreground="#FF0055")
    log_text.tag_configure("color_success", foreground="#00FF99")
    log_text.tag_configure("color_listen", foreground="#FFCC00")
    log_text.tag_configure("color_input", foreground="#00AAFF")

    app.multi_menu = tk.Menu(log_text, tearoff=0)
    app.multi_menu.add_command(label="Copy", command=lambda: copy_text(app, log_text))
    app.multi_menu.add_command(label="Clear", command=lambda: app.clear_delivery_logs(log_text, "multi"))
    log_text.bind("<Button-3>", app.show_multi_menu)

    if app.multi_delivery_process and app.multi_delivery_process.is_alive():
        message = "[>] Multi Server is running..\n"
        color_tag = "color_input"
    else:
        message = "[!] Multi Server is not running!\n"
        color_tag = "color_error"

    log_text.insert('end', f"{message}\n", color_tag)

    try:
        for key, value in log_data.items():
            log_text.insert('end', f"{key}: {value}\n")
    except:
        pass

    log_text.config(font=("Consolas", 18, "bold"))
    log_text.config(state="disabled")
    app.notebook.select(tab)
    update_multiserver_log_tab(app)

def web_delivery(app):
    try:
        if app.web_window and tk.Toplevel.winfo_exists(app.web_window):
            app.web_window.focus_force()
            return
    except:
        pass

    app.web_window = tk.Toplevel(app)
    app.web_window.geometry("570x330")
    app.web_window.title("Scripted Web Delivery")
    app.web_window.focus_force()
    app.web_window.resizable(False, False)

    white_label = ttk.Label(app.web_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    ip_label = ttk.Label(app.web_window, text="IP Address")
    ip_label.grid(row=1, column=0, padx=0, pady=15)

    ip_entry = ttk.Entry(app.web_window)
    ip_entry.insert(0, "0.0.0.0")
    ip_entry.grid(row=1, column=1, padx=0, pady=15)

    port_label = ttk.Label(app.web_window, text="Port")
    port_label.grid(row=2, column=0, padx=0, pady=15)

    port_entry = ttk.Entry(app.web_window)
    port_entry.insert(0, "80")
    port_entry.grid(row=2, column=1, padx=0, pady=15)

    script_label = ttk.Label(app.web_window, text="Protocol")
    script_label.grid(row=3, column=0, padx=0, pady=15)

    http_combobox = ttk.Combobox(app.web_window, values=["HTTP", "HTTPS"], state="readonly")
    http_combobox.grid(row=3, column=1, padx=0, pady=15)
    http_combobox.current(0)
    
    def update_port(event):
        protocol = http_combobox.get()
        if protocol == "HTTPS":
            port_entry.delete(0, tk.END)
            port_entry.insert(0, "443")
        else:
            port_entry.delete(0, tk.END)
            port_entry.insert(0, "80")

    http_combobox.bind("<<ComboboxSelected>>", update_port)
    http_combobox.bind("<FocusIn>", on_combobox_focus)

    def on_enter_key(event):
        server_status(ip_entry.get(), port_entry.get(), http_combobox.get(), app)

    app.web_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.web_window.destroy()

    app.web_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(app.web_window, text="Publish", command=lambda: server_status(ip_entry.get(), port_entry.get(), http_combobox.get(), app))
    save_button.grid(row=4, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(app.web_window, text="Cancel", command=app.web_window.destroy)
    cancel_button.grid(row=4, column=1, padx=20, pady=20)

def server_status(ip, port, protocol, app):
    process = start_web_delivery(ip, port, protocol, app)

    if process is not None:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")  
        new_line = f"[{current_time}] Web Server is listening on port {port} now..\n"
        app.add_event_viewer_log(new_line, 'color_login', "#FF00FF")

    else:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")  
        new_line = f"[{current_time}] Error starting Web Server on {port}!\n"
        app.add_event_viewer_log(new_line, 'color_error', "#FF0055")  

    app.web_window.destroy()
    app.web_delivery_port = port
    return app.web_delivery_port

def stop_multiserver(app):
    if app.multi_delivery_process is not None:
        try:
            if app.multi_delivery_protocol == "FTP":
                app.ftp_server_process.close_all()
            elif app.multi_delivery_protocol == "SMB":
                app.smb_server_process.stop()
            elif app.multi_delivery_protocol == "NFS":
                app.nfs_server_process.stop()
                app.nfs_server_process.close()
        
        except:
            pass
        
        finally:
            app.multi_delivery_process = None
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] {app.multi_delivery_protocol} Server on port {app.multi_delivery_port} was killed!\n"
            app.add_event_viewer_log(new_line, 'color_error', "#FF0055")
            update_multiserver_log_tab(app)

def stop_webserver(app):
    if app.web_delivery_process is not None and app.web_delivery_process.poll() is None:
        app.web_delivery_process.terminate()
        app.web_delivery_process = None  
    
        current_time = datetime.datetime.now().strftime("%H:%M:%S")  
        new_line = f"[{current_time}] Web Server on port {app.web_delivery_port} was killed!\n"
        app.add_event_viewer_log(new_line, 'color_error', "#FF0055") 
        update_webserver_log_tab(app)

def kill_multiserver(app):
    if app.multi_delivery_process is not None:
        if dialog.confirm_dialog(app) == "yes":
            try:
                stop_multiserver(app)
            except:
                pass
    else:
        dialog.delivery_error(app, "multiserver")

def kill_webserver(app):
    if app.web_delivery_process is not None and app.web_delivery_process.poll() is None:
        if dialog.confirm_dialog(app) == "yes":
            app.web_delivery_process.terminate()
            app.web_delivery_process = None  
        
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] Web Server on port {app.web_delivery_port} was killed!\n"
            app.add_event_viewer_log(new_line, 'color_error', "#FF0055")
            update_webserver_log_tab(app)

    else:
        dialog.delivery_error(app, "webserver")

def multi_delivery(app):
    try:
        if app.multi_window and tk.Toplevel.winfo_exists(app.multi_window):
            app.multi_window.focus_force()
            return
    except:
        pass

    app.multi_window = tk.Toplevel(app)
    app.multi_window.geometry("570x330")
    app.multi_window.title("Multi-Server Delivery")
    app.multi_window.focus_force()
    app.multi_window.resizable(False, False)

    white_label = ttk.Label(app.multi_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    ip_label = ttk.Label(app.multi_window, text="IP Address")
    ip_label.grid(row=1, column=0, padx=0, pady=15)

    ip_entry = ttk.Entry(app.multi_window)
    ip_entry.insert(0, "0.0.0.0")
    ip_entry.grid(row=1, column=1, padx=0, pady=15)

    port_label = ttk.Label(app.multi_window, text="Port")
    port_label.grid(row=2, column=0, padx=0, pady=15)

    port_entry = ttk.Entry(app.multi_window)
    port_entry.insert(0, "21")
    port_entry.grid(row=2, column=1, padx=0, pady=15)

    script_label = ttk.Label(app.multi_window, text="Protocol")
    script_label.grid(row=3, column=0, padx=0, pady=15)

    multi_combobox = ttk.Combobox(app.multi_window, values=["FTP", "NFS", "SMB"], state="readonly")
    multi_combobox.grid(row=3, column=1, padx=0, pady=15)
    multi_combobox.current(0)
    
    def update_port(event):
        protocol = multi_combobox.get()
        if protocol == "FTP":
            port_entry.delete(0, tk.END)
            port_entry.insert(0, "21")
        if protocol == "NFS":
            port_entry.delete(0, tk.END)
            port_entry.insert(0, "2049")
        if protocol == "SMB":
            port_entry.delete(0, tk.END)
            port_entry.insert(0, "445")

    multi_combobox.bind("<<ComboboxSelected>>", update_port)
    multi_combobox.bind("<FocusIn>", on_combobox_focus)

    def start_server():
        protocol = multi_combobox.get()
        ip = ip_entry.get()
        port = port_entry.get()
        start_multi_server(ip, port, protocol, app)
        app.multi_window.destroy()

    def on_enter_key(event):
        start_server()

    app.multi_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        app.multi_window.destroy()

    app.multi_window.bind("<Escape>", on_escape_key)
            
    save_button = ttk.Button(app.multi_window, text="Publish", command=start_server)
    save_button.grid(row=4, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(app.multi_window, text="Cancel", command=app.multi_window.destroy)
    cancel_button.grid(row=4, column=1, padx=20, pady=20)

def start_ftp_server(ip, port, app):
    os.makedirs('/tmp/Kitsune', exist_ok=True)

    def read_and_update_log():
        log_file_path = "/tmp/Kitsune/ftp.log"
        json_file_path = "data/multiserver.json"
        last_read_size = 0

        while True:
            time.sleep(1)

            if not os.path.exists(log_file_path):
                continue

            with open(log_file_path, "r") as log_file:
                log_file.seek(last_read_size)
                new_log_content = log_file.readlines()
                last_read_size = log_file.tell()

            if os.path.exists(json_file_path):
                with open(json_file_path, "r") as json_file:
                    data = json.load(json_file)
            else:
                data = {
                    "Protocol": "FTP",
                    "IP Address": ip,
                    "Listening Port": port,
                    "Path": "../Kitsune/Payloads",
                    "Log": []
                }

            for line in new_log_content:
                if line.strip():
                    clean_data = regex_multi_text(line.strip())
                    clean_data = str(clean_data)
                    clean_data = clean_data.replace("['","").replace("']","")
                    clean_data = clean_data.replace('["','').replace('"]','')
                    data["Log"].append(clean_data)
                    app.notify_multi_delivery()
                    update_multiserver_log_tab(app)

            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

    threading.Thread(target=read_and_update_log, daemon=True).start()

    authorizer = DummyAuthorizer()
    authorizer.add_anonymous("payloads")
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Simple FTP Server"
    handler.passive_ports = range(60000, 65535)
    address = (ip, port)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5

    try:
        logging.basicConfig(filename="/tmp/Kitsune/ftp.log", level=logging.INFO)
        app.ftp_server_process = server
        atexit.register(app.ftp_server_process.close_all)
        server.serve_forever()

    except:
        pass

def start_smb_server(ip, port, app):
    def read_smb_logs():
        log_file_path = "/tmp/Kitsune/smb.log"
        json_file_path = "data/multiserver.json"
        last_read_size = 0

        while True:
            time.sleep(1)
            if not os.path.exists(log_file_path):
                continue

            try:
                with open(log_file_path, "r") as log_file:
                    log_file.seek(last_read_size)
                    new_log_content = log_file.readlines()
                    last_read_size = log_file.tell()

                if os.path.exists(json_file_path):
                    with open(json_file_path, "r") as json_file:
                        data = json.load(json_file)
                else:
                    data = {
                        "Protocol": "SMB",
                        "IP Address": ip,
                        "Listening Port": port,
                        "Path": "../Kitsune/Payloads",
                        "Log": []
                    }

                for line in new_log_content:
                    if line.strip():
                        clean_data = regex_multi_text(line.strip())
                        clean_data = str(clean_data)
                        clean_data = clean_data.replace("['","").replace("']","")
                        clean_data = clean_data.replace('["','').replace('"]','')
                        data["Log"].append(clean_data)
                        app.notify_multi_delivery()
                        update_multiserver_log_tab(app)

                with open(json_file_path, "w") as json_file:
                    json.dump(data, json_file, indent=4)

            except:
                pass
                
    threading.Thread(target=read_smb_logs, daemon=True).start()
    smb_server_path = '/tmp/Kitsune'
    os.makedirs(smb_server_path, exist_ok=True)
    logging.basicConfig(filename="/tmp/Kitsune/smb.log", level=logging.INFO)
    
    try:
        server = smbserver.SimpleSMBServer(listenAddress=ip, listenPort=int(port))
        server.addShare("payloads", "payloads", "payloads")
        server.setSMB2Support(True)
        server.setSMBChallenge("")
        server.setLogFile(os.path.join(smb_server_path, "smb.log"))
        app.smb_server_process = server
        atexit.register(app.smb_server_process.stop)
        server.start()
    
    except:
        pass

def start_nfs_server(ip, port, app):
    def read_nfs_logs():
        log_file_path = "/tmp/Kitsune/nfs.log"
        json_file_path = "data/multiserver.json"
        last_read_size = 0

        while True:
            time.sleep(1)
            if not os.path.exists(log_file_path):
                continue

            try:
                with open(log_file_path, "r") as log_file:
                    log_file.seek(last_read_size)
                    new_log_content = log_file.readlines()
                    last_read_size = log_file.tell()

                if os.path.exists(json_file_path):
                    with open(json_file_path, "r") as json_file:
                        data = json.load(json_file)
                else:
                    data = {
                        "Protocol": "NFS",
                        "IP Address": ip,
                        "Listening Port": port,
                        "Path": "/tmp/Kitsune/Payloads",
                        "Log": []
                    }

                for line in new_log_content:
                    if line.strip():
                        clean_data = regex_multi_text(line.strip())
                        clean_data = str(clean_data)
                        clean_data = clean_data.replace("['","").replace("']","")
                        clean_data = clean_data.replace('["','').replace('"]','')
                        data["Log"].append(clean_data)
                        app.notify_multi_delivery()
                        update_multiserver_log_tab(app)

                with open(json_file_path, "w") as json_file:
                    json.dump(data, json_file, indent=4)

            except:
                pass

    threading.Thread(target=read_nfs_logs, daemon=True).start()
    
    async def run_nfs_server(app):
        try:
            fs_manager = EvictingFileSystemManager(
                VerifyingFileHandleEncoder(os.urandom(32)),
                factories={
                    b"/tmp/Kitsune/Payloads": lambda call_ctx: create_fs(
                        lambda *args, **kwargs: SimpleFS(
                            size_quota=100*1024, 
                            entries_quota=100, 
                            *args, **kwargs
                        ),
                        call_ctx,
                        read_only=False
                    ),
                },
            )
            await serve_nfs(fs_manager, use_internal_rpcbind=True)

        except:
            pass

    nfs_server_path = '/tmp/Kitsune'
    os.makedirs(nfs_server_path, exist_ok=True)
    logging.basicConfig(filename="/tmp/Kitsune/nfs.log", level=logging.INFO)
    
    try:
        app.nfs_server_process = asyncio.run(run_nfs_server(app))
        atexit.register(app.nfs_server_process.stop)

    except:
        pass

def start_multi_server(ip, port, protocol, app):
    stop_multiserver(app)
    multiserver_file = Path('data/multiserver.json')
    app.multi_delivery_port = port 
    if multiserver_file.exists():
        multiserver_file.unlink()
    log_data = {
        "Protocol": protocol,
        "IP Address": ip,
        "Listening Port": port,
        "Path": "../Kitsune/Payloads\n",
        "Log": []
    }

    with open(multiserver_file, 'w') as f:
        json.dump(log_data, f, indent=4)

    if protocol == "FTP":
        app.multi_delivery_process = threading.Thread(target=start_ftp_server, args=(ip, port, app), daemon=True)
        app.multi_delivery_process.start()
        app.multi_delivery_protocol = "FTP"
    elif protocol == "SMB":
        app.multi_delivery_process = threading.Thread(target=start_smb_server, args=(ip, port, app), daemon=True)
        app.multi_delivery_process.start()
        app.multi_delivery_protocol = "SMB"
    elif protocol == "NFS":
        app.multi_delivery_process = threading.Thread(target=start_nfs_server, args=(ip, port, app), daemon=True)
        app.multi_delivery_process.start()
        app.multi_delivery_protocol = "NFS"

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    new_line = f"[{current_time}] {protocol} Server is listening on port {port} now..\n"
    app.add_event_viewer_log(new_line, 'color_login', "#FF00FF")
    update_multiserver_log_tab(app)
    return app.multi_delivery_process
