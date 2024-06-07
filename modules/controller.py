#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#    https://darkbyte.net #
#=========================#

import os
import sys
import time
import json
import datetime
import subprocess
from threading import Thread
from neotermcolor import colored
from modules.session import Session
from modules.reverse import pwncat_rev_thread
from modules.reverse import http_shell_thread
from modules.reverse import dnscat2_thread
from modules.connect import netexec_thread
from modules.connect import evilwinrm_thread
from modules.connect import pyshell_thread
from modules.connect import pwncat_thread
from modules.connect import wmiexecpro_thread

def typing(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.02)

def reload_listener(app, session, listener_details, reload_listeners=False):
    restart = True
    if not hasattr(app, 'listener_processes'):
        app.listener_processes = {}

    name, host, port, protocol, tail = listener_details
    listener_id = f"{tail}:{host}:{port}"

    if listener_id not in app.listener_processes:
        if tail == "HTTP-Shell":
            app.listener_processes[listener_id] = http_shell_thread(app, host, port, name, session, restart)

        if tail == "PwnCat-CS":
            app.listener_processes[listener_id] = pwncat_rev_thread(app, host, port, name, session, restart)

        if tail == "DnsCat2":
            app.listener_processes[listener_id] = dnscat2_thread(app, host, port, name, session, restart)

    listeners = app.load_listeners()

    for listener in listeners:
        if listener["Name"] == listener_details[0]:  
            listener["Name"] = name
            listener["Host"] = host
            listener["Port"] = port
            listener["Protocol"] = protocol
            listener["Tail"] = tail
            listener["State"] = "enabled"
            break

    with open('data/listeners.json', 'w') as file:
        json.dump(listeners, file, indent=4)

def new_listener(app, session, reload_listeners=False):
    restart = False
    if not hasattr(app, 'listener_processes'):
        app.listener_processes = {}

    for listener in app.listeners:
        name = listener.get("Name")
        host = listener.get("Host")
        port = listener.get("Port")
        protocol = listener.get("Protocol")
        tail = listener.get("Tail")

        listener_id = f"{tail}:{host}:{port}"
        if listener_id not in app.listener_processes:
            if tail == "HTTP-Shell":
                app.listener_processes[listener_id] = http_shell_thread(app, host, port, name, session, restart)

            if tail == "PwnCat-CS":
                app.listener_processes[listener_id] = pwncat_rev_thread(app, host, port, name, session, restart)

            if tail == "DnsCat2":
                app.listener_processes[listener_id] = dnscat2_thread(app, host, port, name, session, restart)

def start_listeners(app, session, reload_listeners=False):
    if not hasattr(app, 'listener_processes'):
        app.listener_processes = {}

    listeners = app.load_listeners()

    with open('data/settings.json', 'r') as settings_file:
        settings_data = json.load(settings_file)
        nekomancer_setting = settings_data.get('settings', {}).get('nekomancer', '')

    if nekomancer_setting == "All Sessions" or nekomancer_setting == "Reverse Only":
        if reload_listeners and app.listeners:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")

            typing(colored("\n[>] Reloading previous listeners..\n", "yellow"))
            label_text = f"[{current_time}] Listeners found in JSON file! Reloading.."

            app.text.config(state="normal")
            app.text.config(foreground="#FF0055")
            app.text.insert("end", label_text + "\n")
            app.text.config(state="disabled")

            app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")

    for listener in app.listeners:
        name = listener.get("Name")
        host = listener.get("Host")
        port = listener.get("Port")
        protocol = listener.get("Protocol")
        tail = listener.get("Tail")
        time.sleep(0.1)
        
        print(colored(f"[+] {name} - {host}:{port} - {protocol} - {tail}","green"))
        listener_details = (name, host, port, protocol, tail)

        reload_listener(app, session, listener_details, reload_listeners=False)

def kill_listeners(app, listener_details):
    app.silent_error = True
    name = listener_details[0]
    host = listener_details[1]
    port = listener_details[2]
    protocol = listener_details[3]
    tail = listener_details[4]
    key = f"{tail}:{host}:{port}"

    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')

        for pid in pids:
            if pid:
                subprocess.run(['kill', pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
        if key in app.listener_processes:
            del app.listener_processes[key]

    except Exception as e:
        pass

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")

    label_text = f"[{current_time}] Listener {listener_details[0]} on port {listener_details[2]} was killed!"

    app.text.config(state="normal")
    app.text.config(foreground="#FF0055")
    app.text.insert("end", label_text + "\n")
    app.text.config(state="disabled")

    time.sleep(0.2)
    app.silent_error = False
    app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")

    listeners = app.load_listeners()

    for listener in listeners:
        if listener["Name"] == listener_details[0]:  
            listener["Name"] = name
            listener["Host"] = host
            listener["Port"] = port
            listener["Protocol"] = protocol
            listener["Tail"] = tail
            listener["State"] = "disabled"
            break

    with open('data/listeners.json', 'w') as file:
        json.dump(listeners, file, indent=4)

def stop_listeners(app, listener_details):
    app.silent_error = True
    name = listener_details[0]
    host = listener_details[1]
    port = listener_details[2]
    protocol = listener_details[3]
    tail = listener_details[4]
    key = f"{tail}:{host}:{port}"

    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')

        for pid in pids:
            if pid:
                subprocess.run(['kill', pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
        if key in app.listener_processes:
            del app.listener_processes[key]

    except Exception as e:
        pass

    time.sleep(0.2)
    app.silent_error = False
 
    listeners = app.load_listeners()

    for listener in listeners:
        if listener["Name"] == listener_details[0]:  
            listener["Name"] = name
            listener["Host"] = host
            listener["Port"] = port
            listener["Protocol"] = protocol
            listener["Tail"] = tail
            listener["State"] = "disabled"
            break

    with open('data/listeners.json', 'w') as file:
        json.dump(listeners, file, indent=4)

def connect_session(app, params, method, session, tail):
    if tail == 'NetExec':
        netexec_thread(app, params, method, session, restart=False)

    if tail == 'Evil-WinRM':
        evilwinrm_thread(app, params, method, session, restart=False)

    if tail == 'PyShell':
        pyshell_thread(app, params, method, session, restart=False)

    if tail == 'PwnCat-CS':
        pwncat_thread(app, params, method, session, restart=False)

    if tail == 'WMIexec-Pro':
        wmiexecpro_thread(app, params, method, session, restart=False)

def restart_session(app, session_data):
    with open('data/settings.json', 'r') as settings_file:
        settings_data = json.load(settings_file)
        nekomancer_setting = settings_data.get('settings', {}).get('nekomancer', '')

    if nekomancer_setting == "All Sessions" or nekomancer_setting == "Bind Only":

        def delayed_restart():
            user = session_data.get('User')
            hostname = session_data.get('Hostname')
            ip_address = session_data.get('IP Address')
            listener = session_data.get('Listener')
            tail = session_data.get('Tail')
            method = session_data.get('Method')
            params = session_data.get('Params')
            result = None

            existing_sessions = Session.load_sessions()

            matching_session = None
            for existing_session in existing_sessions:
                if (existing_session.get('User') == user and
                    existing_session.get('Hostname') == hostname and
                    existing_session.get('Tail') == tail and
                    existing_session.get('Method') == method):
                    matching_session = existing_session
                    break

            if matching_session:
                session = matching_session['Session']
         
                if tail == 'NetExec':
                    netexec_thread(app, params, method, session, restart=True)

                elif tail == 'Evil-WinRM':
                    evilwinrm_thread(app, params, method, session, restart=True)

                elif tail == 'PyShell':
                    pyshell_thread(app, params, method, session, restart=True)

                elif tail == 'PwnCat-CS' and listener == 'SSH':
                    pwncat_thread(app, params, method, session, restart=True)

                elif tail == 'WMIexec-Pro':
                    wmiexecpro_thread(app, params, method, session, restart=True)

                try:
                    for item in app.treeview.get_children():
                        item_info = app.treeview.item(item)
                        session_number = item_info['values']
                        if str(session) == str(session_number[0]):
                            if str(item_info['tags']) == "['disabled']":
                                result = False
                            else:
                                result = True
                except:
                    pass

                return result

        app.after(4500, delayed_restart)

def retry_session(app, session_title):
    with open('data/settings.json', 'r') as settings_file:
        settings_data = json.load(settings_file)
        nekomancer_setting = settings_data.get('settings', {}).get('nekomancer', '')

    if nekomancer_setting == "All Sessions" or nekomancer_setting == "Bind Only":

        while True:
            try:
                with open('data/sessions.json', 'r') as f:
                    sessions_data = json.load(f)
            except:
                sessions_data = []
                pass
            
            for session in sessions_data:
                if str(session['Session']) == str(session_title.split()[1]):
                    for item in app.treeview.get_children():
                        item_info = app.treeview.item(item)
                        session_number = item_info['values']

                        if str(session['Session']) == str(session_number[0]):
                            if str(item_info['tags']) == "['disabled']":
                                restart_session(app, session)
                                time.sleep(30)
                            else:
                                return  
