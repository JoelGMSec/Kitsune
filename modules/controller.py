#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
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
from modules.reverse import villain_thread
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
            app.listener_processes[listener_id] = http_shell_thread(app, host, port, name, session)

        if tail == "PwnCat-CS":
            app.listener_processes[listener_id] = pwncat_rev_thread(app, host, port, name, session)

        if tail == "DnsCat2":
            app.listener_processes[listener_id] = dnscat2_thread(app, host, port, name, session)

        if tail == "Villain":
            app.listener_processes[listener_id] = villain_thread(app, host, port, name, session)
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
                app.listener_processes[listener_id] = http_shell_thread(app, host, port, name, session)

            if tail == "PwnCat-CS":
                app.listener_processes[listener_id] = pwncat_rev_thread(app, host, port, name, session)

            if tail == "DnsCat2":
                app.listener_processes[listener_id] = dnscat2_thread(app, host, port, name, session)

            if tail == "Villain":
                app.listener_processes[listener_id] = villain_thread(app, host, port, name, session)

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
            if not app.fast_mode:
                typing(colored("\n[>] Reloading previous listeners..\n", "yellow"))
            label_text = f"[{current_time}] Listeners found in JSON file! Reloading.."
            app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")

    for listener in app.listeners:
        name = listener.get("Name")
        host = listener.get("Host")
        port = listener.get("Port")
        protocol = listener.get("Protocol")
        tail = listener.get("Tail")
        if not app.fast_mode:
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

    except:
        pass

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")

    label_text = f"[{current_time}] Listener {listener_details[0]} on port {listener_details[2]} was killed!"
    app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")
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

    for item in app.treeview.get_children():
        item_info = app.treeview.item(item)
        values = item_info['values']
        tags = item_info['tags']

        app.treeview.tag_configure("disabled", foreground="#868686")
        app.treeview.tag_configure("disabled_selected", foreground="#333333")
        selected_items = app.treeview.selection()

        if str(values[-2]) == listener["Name"]:
            if item in selected_items:
                app.treeview.item(item, tags=("disabled_selected",))
            else:
                app.treeview.item(item, tags=("disabled",))

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

    except:
        pass

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

def restart_session(app, session_data, retry):
    with open('data/settings.json', 'r') as settings_file:
        settings_data = json.load(settings_file)
        nekomancer_setting = settings_data.get('settings', {}).get('nekomancer', '')

    if nekomancer_setting == "All Sessions" or nekomancer_setting == "Bind Only":
        if not hasattr(app, 'session_restarts'):
            app.session_restarts = {}

        session_id = session_data.get('Session')
        tail = session_data.get('Tail')
        listener = session_data.get('Listener')
        method = session_data.get('Method')
        session_key = f"{session_id}:{tail}:{listener}:{method}"

        if session_key in app.session_restarts:
            return False

        app.session_restarts[session_key] = True

        def delayed_restart():
            try:
                user = session_data.get('User')
                hostname = session_data.get('Hostname')
                ip_address = session_data.get('IP Address')
                listener = session_data.get('Listener')
                tail = session_data.get('Tail')
                method = session_data.get('Method')
                params = session_data.get('Params')
                result = None

                existing_sessions = Session.load_sessions(app)

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

                    for item in app.treeview.get_children():
                        item_info = app.treeview.item(item)
                        session_number = item_info['values']
                        if str(session) == str(session_number[0]):
                            result = str(item_info['tags']) != "['disabled']"

                return result

            finally:
                if session_key in app.session_restarts:
                    del app.session_restarts[session_key]

        if not retry:
            app.after(4500, delayed_restart)
        else:
            app.after(1500, delayed_restart)
        return True

def retry_session(app, session_title):
    with open('data/settings.json', 'r') as settings_file:
        settings_data = json.load(settings_file)
        nekomancer_setting = settings_data.get('settings', {}).get('nekomancer', '')

    if nekomancer_setting == "All Sessions" or nekomancer_setting == "Bind Only":
        try:
            with open('data/sessions.json', 'r') as f:
                sessions_data = json.load(f)
        except:
            sessions_data = []
            pass
        
        if not hasattr(app, 'session_retries'):
            app.session_retries = {}

        for session in sessions_data:
            if str(session['Session']) == str(session_title.split()[1]):
                for item in app.treeview.get_children():
                    item_info = app.treeview.item(item)
                    session_number = item_info['values']

                    if str(session['Session']) == str(session_number[0]):
                        session_key = f"{session['Session']}:{session.get('Tail')}:{session.get('Listener')}:{session.get('Method')}"
                        if session_key in app.session_retries:
                            return False
                        app.session_retries[session_key] = True 

                        if session.get('Tail') in ["HTTP-Shell", "PwnCat-CS", "Villain"]:
                            session_tail = session.get('Tail')
                            session_listener = session.get('Listener')

                            if session.get('Listener') == "SSH" and session.get('Tail') == "PwnCat-CS":
                                restart_session(app, session, True)

                            else:
                                listeners = app.load_listeners()
                                for listener in listeners:
                                    if session_listener == listener["Name"]:
                                        if session_tail in listener["Tail"]:
                                            name = listener["Name"]
                                            host = listener["Host"]
                                            port = listener["Port"]
                                            protocol = listener["Protocol"]
                                            tail = listener["Tail"]
                                            listener_details = (name, host, port, protocol, tail)
                                            kill_listeners(app, listener_details)
                                            
                                            def delayed_reload():
                                                reload_listener(app, session, listener_details, reload_listeners=True)
                                            app.after(1500, delayed_reload)

                        else:
                            restart_session(app, session, True)
                        del app.session_retries[session_key]
                        
        return True

