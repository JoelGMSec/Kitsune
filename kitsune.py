#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import sys
sys.dont_write_bytecode = True

import psutil
import argparse
import requests
import subprocess
import tkinter as tk
import os, time, json, shutil, datetime, threading
from pathlib import Path
from neotermcolor import colored
from tkinter import ttk, filedialog
from modules.session import Session
from modules.tails import clone_repos
from modules.listeners import edit_listener
from modules.controller import reload_listener
from modules.widgets import setup_widgets
from modules.widgets import DraggableTabsNotebook
from modules import delivery, listeners, controller, chat
from modules import custom, proxy, modules, dialog, updater, nekomancer

def typing(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.02)

def check_and_copy_fonts():
    home_dir = os.path.expanduser("~")
    fonts_dir = os.path.join(home_dir, ".local/share/fonts")
    source_fonts_dir = os.path.join("./themes/fonts")
    
    fonts_to_check = ["Consolas.ttf", "Lexend-SemiBold.ttf"]
    
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    for font in fonts_to_check:
        font_path = os.path.join(fonts_dir, font)
        source_font_path = os.path.join(source_fonts_dir, font)
        
        if not os.path.exists(font_path):
            if os.path.exists(source_font_path):
                shutil.copy2(source_font_path, font_path)

class App(tk.Frame):
    def __init__(self, parent, fast_mode):
        parent.withdraw()
        tk.Frame.__init__(self, parent)
        self.load_settings()
        self.proxy_status = False
        self.silent_error = False
        self.fast_mode = fast_mode
        self.session_block_until = 0
        self.config(background="#444444")
        parent.protocol("WM_DELETE_WINDOW", self.on_close)

        for index in [0, 1]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        self.text_tag_counter = 0
        self.used_ports = [61098, 61099, 61100]
        self.event_viewer_logs = self.load_event_viewer_logs()

        self.clear_command = False
        self.command_history = Session.load_command_history()
        self.history_index = len(self.command_history)

        self.listeners = []
        self.listener_table = None
        self.web_delivery_process = None
        self.multi_delivery_process = None

        setup_widgets(parent, self)
        threading.Thread(target=self.initialize_app, args=(parent, fast_mode), daemon=True).start()

    def initialize_app(self, parent, fast_mode):
        self.check_repos()
        self.check_modules()
        self.update_listeners_settings()
        listeners.load_listeners(self)
        delivery.start_updating_multiserver_log(self)

        self.sessions = []
        self.session_id = 0
        self.saved_sessions = {}

        self.session_restarts = {}
        self.treeview_state = {}
        self.update_event_viewer()
        proxy.load_proxy_settings(self)

        Session.load_saved_sessions(self)
        if not self.fast_mode:
            typing(colored("\n[>] Loading Event Viewer..\n", "yellow"))
        try:
            self.username = os.getlogin()
        except:
            self.username = "root"

        chat.start_server(self)
        custom.load_custom_modules(self)

        self.client_socket = None
        self.team_chat_tab = chat.TeamChatTab(self.notebook)
        self.team_chat_tab.connect_to_server(self.username, "localhost")
        self.client_socket = self.team_chat_tab.get_socket()
        threading.Thread(target=self.check_version).start()
        app.after(100, root.deiconify)

    def check_version(self):
        try:
            time.sleep(1)
            response = requests.get("https://raw.githubusercontent.com/JoelGMSec/Kitsune/main/version.txt")
            response.raise_for_status()  
            remote_version = response.text.strip()
            local_version = updater.get_local_version()
            if remote_version > local_version:
                dialog.new_version(app)

        except:
            pass

    def load_settings(self):
        default_settings = {
            "settings": {
                "theme": "Blue",
                "nekomancer": "All Sessions"
            }
        }

        try:
            with open("data/settings.json", "r") as json_file:
                settings = json.load(json_file)

            if "settings" not in settings:
                settings["settings"] = default_settings["settings"]
                with open("data/settings.json", "w") as json_file:
                    json.dump(settings, json_file, indent=4)

            self.theme_var = tk.StringVar(value=settings["settings"].get("theme", "Blue"))
            self.saved_value = settings["settings"].get("nekomancer", "All Sessions")

        except (json.JSONDecodeError, FileNotFoundError):
            settings = default_settings
            try:
                with open("data/settings.json", "r") as json_file:
                    existing_data = json.load(json_file)
                    existing_data.update(default_settings)
                    settings = existing_data
            except:
                pass

            with open("data/settings.json", "w") as json_file:
                json.dump(settings, json_file, indent=4)

            self.theme_var = tk.StringVar(value="Blue")
            self.saved_value = "All Sessions"

        return settings

    def listener_window(self):
        return listeners.listener_window(self)

    def add_listeners(self):
        return listeners.add_listeners(self)

    def load_listeners(self):
        return listeners.load_listeners(self)

    def check_repos(self):
        tails_dir = "tails"
        if not os.path.exists(tails_dir) or not any(os.path.isdir(os.path.join(tails_dir, entry)) for entry in os.listdir(tails_dir)):
            threading.Thread(target=clone_repos).start()

    def check_modules(self):
        custom_dir = "custom"
        if not os.path.exists(custom_dir) or not any(os.path.isdir(os.path.join(custom_dir, entry)) for entry in os.listdir(custom_dir)):
            threading.Thread(target=modules.clone_repos).start()

    def get_next_ports(self):
        next_ports = self.used_ports[-3:]
        new_ports = [port + 3 for port in next_ports]
        self.used_ports.extend(new_ports)
        return new_ports

    def sort_sessions(self):
        try:
            with open('data/sessions.json', 'r') as f:
                sessions_data = json.load(f)
        except FileNotFoundError:
            sessions_data = []

        sorted_sessions = sorted(sessions_data, key=lambda s: int(s['Session']))
        for i, session in enumerate(sorted_sessions, start=1):
            session['Session'] = i

        with open('data/sessions.json', 'w') as f:
            json.dump(sorted_sessions, f, indent=4)

    def change_theme(self, theme):
        try:
            with open("data/settings.json", "r") as json_file:
                settings_data = json.load(json_file)

            if "settings" not in settings_data:
                settings_data["settings"] = {}

            if settings_data["settings"].get("theme") != theme:
                settings_data["settings"]["theme"] = theme
                with open("data/settings.json", "w") as json_file:
                    json.dump(settings_data, json_file, indent=4)

            self.theme_var.set(theme)

            theme_map = {"Blue": "blue", "Green": "green", "Purple": "purple", "Red": "red"}
            if theme in theme_map:
                root.tk.call("set_theme", theme_map[theme])

        except:
            settings_data = {"settings": {"theme": "Blue"}}
            with open("data/settings.json", "w") as json_file:
                json.dump(settings_data, json_file, indent=4)

    def update_listeners_settings(self):
        try:
            with open("data/settings.json", "r") as json_file:
                settings = json.load(json_file)["settings"]
                nekomancer_setting = settings.get("nekomancer", "All Sessions")
        except FileNotFoundError:
            nekomancer_setting = "All Sessions"

        try:
            with open('data/listeners.json', 'r') as listeners_file:
                listeners_data = json.load(listeners_file)
        except FileNotFoundError:
            return

        if nekomancer_setting in ["Disabled", "Bind Only"]:
            new_state = "disabled"
        elif nekomancer_setting in ["All Sessions", "Reverse Only"]:
            new_state = "enabled"
        else:
            return

        for listener in listeners_data:
            listener["State"] = new_state

        with open('data/listeners.json', 'w') as listeners_file:
            json.dump(listeners_data, listeners_file, indent=4)

    def save_treeview_state(self):
        for item in self.treeview.get_children():
            item_id = self.treeview.item(item, 'values')[0]
            state = 'enabled' if 'disabled' not in self.treeview.item(item, 'tags') else 'disabled'
            self.treeview_state[item_id] = state

    def update_treeview(self):
        previous_items = {}
        for item in self.treeview.get_children():
            values = self.treeview.item(item, "values")
            key = (values[1], values[2], values[7], values[8])
            tags = self.treeview.item(item, "tags")
            previous_items[key] = (item, values, tags)

        for item in self.treeview.get_children():
            self.treeview.detach(item)

        try:
            with open('data/sessions.json', 'r') as f:
                sessions_data = json.load(f)
        except FileNotFoundError:
            sessions_data = []

        for session in sessions_data:
            key = (session["User"], session["Hostname"], session["Listener"], session["Tail"])
            if key in previous_items:
                item_id, values, tags = previous_items[key]
                self.treeview.move(item_id, '', 'end')
                self.treeview.item(item_id, values=(
                    session["Session"], session["User"], session["Hostname"], session["IP Address"],
                    session["Process"], session["PID"], session["Arch"], session["Listener"], session["Tail"]
                ), tags=tags)
            else:
                self.treeview.insert('', 'end', values=(
                    session["Session"], session["User"], session["Hostname"], session["IP Address"],
                    session["Process"], session["PID"], session["Arch"], session["Listener"], session["Tail"]
                ), tags=('enabled',))

    def count_session(self):
        existing_sessions = [int(session.split()[1]) for session in self.saved_sessions]
        if not existing_sessions:
            return 1
        else:
            return max(existing_sessions) + 1

    def save_event_viewer_logs(self):
        logs_file = Path("data/events.json")
        logs_data = {"logs": [{"text": log, "tag": tag, "color": color} for log, tag, color in self.event_viewer_logs]}
        with open(logs_file, "w") as file:
            json.dump(logs_data, file, indent=4)

    def load_event_viewer_logs(self):
        logs_file = Path("data/events.json")
        if logs_file.is_file():
            with open(logs_file, "r") as file:
                logs_data = json.load(file)
            logs = []
            for log in logs_data.get("logs", []):
                text = log['text']
                tag = log['tag']
                color = log['color']
                logs.append((text, tag, color))
            return logs
        return []

    def notify_event_viewer(self):
        for tab in self.notebook.tabs():
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab != "Event Viewer":
                for tab in self.notebook.tabs():
                    if self.notebook.tab(tab, "text") == "Event Viewer":
                        self.notebook.tab(tab, state="disabled")

    def notify_team_chat(self):
        for tab in self.notebook.tabs():
            current_tab = self.notebook.tab(self.notebook.select(), "text")   
            if current_tab != "Team Chat":
                for tab in self.notebook.tabs():
                    if self.notebook.tab(tab, "text") == "Team Chat":
                        self.notebook.tab(tab, state="disabled")

    def notify_command_session(self, session_title):
        for tab in self.notebook.tabs():
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab != session_title:
                for tab in self.notebook.tabs():
                    if self.notebook.tab(tab, "text") == session_title:
                        self.notebook.tab(tab, state="disabled")

    def notify_web_delivery(self):
        for tab in self.notebook.tabs():
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab != "Web Server Log":
                for tab in self.notebook.tabs():
                    if self.notebook.tab(tab, "text") == "Web Server Log":
                        self.notebook.tab(tab, state="disabled")

    def notify_multi_delivery(self):
        for tab in self.notebook.tabs():
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab != "Multi Server Log":
                for tab in self.notebook.tabs():
                    if self.notebook.tab(tab, "text") == "Multi Server Log":
                        self.notebook.tab(tab, state="disabled")
                        
    def restore_team_chat(self):
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == "Team Chat":
                self.notebook.select(tab)
                return

    def restore_event_viewer(self):
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == "Event Viewer":
                self.notebook.select(tab)
                return

    def update_event_viewer(self):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        for log, tag, color in self.event_viewer_logs:
            self.text.tag_config(tag, foreground=color)
            self.text.insert(tk.END, log, tag)
        self.text.config(state="disabled")
        self.text.see("end")

    def add_event_viewer_log(self, log, tag, color):
        if time.time() < self.session_block_until:
            return

        split_log = log.split("] ", 1)
        if len(split_log) > 1:
            if len(self.event_viewer_logs) > 0:
                last_log = self.event_viewer_logs[-1]
                split_last_log = last_log[0].split("] ", 1)
                if len(split_last_log) > 1 and split_log[1] == split_last_log[1]:
                    self.event_viewer_logs[-1] = (log, tag, color)
                    return 
                else:
                    self.event_viewer_logs.append((log, tag, color))
                    self.text_tag_counter += 1
            else:
                self.event_viewer_logs.append((log, tag, color))
                self.text_tag_counter += 1
        else:
            return

        self.text.config(state="normal")
        self.text.tag_config(tag, foreground=color)
        self.text.insert(tk.END, log, tag)
        self.text.config(state="disabled")
        self.text.see("end")
        self.save_event_viewer_logs()
        self.notify_event_viewer()

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def show_delivery_menu(self, event):
        self.delivery_menu.tk_popup(event.x_root, event.y_root)

    def show_multi_menu(self, event):
        self.multi_menu.tk_popup(event.x_root, event.y_root)

    def show_custom_menu(self, event):
        self.custom_menu.tk_popup(event.x_root, event.y_root)
    
    def copy_text(self, event=None):
        try:
            selected_text = self.text.selection_get()
            self.text.clipboard_clear()
            self.text.clipboard_append(selected_text)
            self.text.tag_remove(tk.SEL, "1.0", tk.END)
        except:
            pass

    def select_all_text(self, event=None):
        self.text.config(state="normal")
        if self.text.get("1.0", tk.END).strip():
            self.text.tag_add(tk.SEL, "1.0", tk.END)
            self.text.mark_set(tk.INSERT, "1.0")
            self.text.see(tk.END)
        self.text.config(state="disabled")
        return "break" 

    def select_custom_text(self, event=None):
        self.module_text.config(state="normal")
        last_line_start = self.module_text.index("end-1l linestart")
        if self.module_text.get("1.0", last_line_start).strip():
            self.module_text.tag_add(tk.SEL, "1.0", last_line_start)
            self.module_text.mark_set(tk.INSERT, "1.0")
            self.module_text.see(tk.END)
        self.module_text.config(state="disabled")
        return "break"

    def copy_custom_text(self, event=None):
        try:
            selected_text = self.module_text.selection_get()
            self.module_text.clipboard_clear()
            self.module_text.clipboard_append(selected_text)
            self.module_text.tag_remove(tk.SEL, "1.0", tk.END)
        except:
            pass

    def clear_text(self):
        self.clear_data()

    def on_entry_focus_in(self, event):
        if self.entry:
            current_text = self.entry.get()

            if current_text.strip() == "Insert command here..":
                self.entry.delete(0, tk.END)
                self.entry.config(foreground="#ffffff")
            else:
                self.entry.config(foreground="#ffffff")

    def on_entry_focus_out(self, event):
        if self.entry:
            current_text = self.entry.get()
            
            if not current_text.strip():
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Insert command here..")
                self.entry.config(foreground="#BABABA")

    def remove_session_tab(self, session_id):
       for tab in self.notebook.tabs():
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab != f"Session {session_id}":
                for tab in self.notebook.tabs():
                    if self.notebook.tab(tab, "text") == f"Session {session_id}":
                        self.notebook.forget(tab)
            
            if current_tab == f"Session {session_id}":
                self.notebook.forget("current")

    def remove_session_json(self, session_id):
        sessions_file = Path("data/sessions.json")
        if sessions_file.is_file():
            with open(sessions_file, "r") as file:
                sessions_data = json.load(file)

            session_id = int(session_id)
            sessions = [session for session in sessions_data if session.get("Session") != session_id]

            max_session_id = max(session.get("Session") for session in sessions) if sessions else 0
            self.session_id = max_session_id

            with open(sessions_file, "w") as file:
                json.dump(sessions, file, indent=4)
        
            session_key = f"Session {session_id}"
            if session_key in self.saved_sessions:
                del self.saved_sessions[session_key]

        return self.session_id

    def remove_listener_json(self, listener_details):
        name, host, port, protocol, tail = listener_details

        listeners_file = Path("data/listeners.json")
        if listeners_file.is_file():
            with open(listeners_file, "r") as file:
                listeners_data = json.load(file)

            filtered_listeners = [
            listener for listener in listeners_data 
            if not (
                listener.get("Name") == name and
                listener.get("Host") == host and
                listener.get("Port") == port and
                listener.get("Protocol") == protocol and
                listener.get("Tail") == tail
                )
            ]

        with open(listeners_file, "w") as file:
            json.dump(filtered_listeners, file, indent=4)

    def on_treeview_delete(self, event):
        selected_item = self.treeview.selection()
        if selected_item:
            item = selected_item[0]
            parent = self.treeview.parent(item)
            siblings = self.treeview.get_children(parent)
            index = siblings.index(item)

            if dialog.confirm_dialog(self) == "yes":
                try:
                    if self.treeview.exists(item):
                        values = self.treeview.item(item, "values")
                        if values:
                            session_id = values[0]
                            self.treeview.delete(item)
                            self.remove_session_tab(session_id)
                            self.remove_session_json(session_id)
                            self.sort_sessions()
                            self.update_treeview()

                        if index > 0:
                            previous_item = siblings[index - 1]
                            self.treeview.selection_set(previous_item)
                            self.treeview.focus(previous_item)
                        elif len(siblings) > 1: 
                            next_item = siblings[1] if index == 0 else siblings[0]
                            self.treeview.selection_set(next_item)
                            self.treeview.focus(next_item)
                
                except:
                    pass

    def on_delete_treeview(self, event):
        selected_item = self.treeview.selection()
        if selected_item:
            item = selected_item[0]
            parent = self.treeview.parent(item)
            siblings = self.treeview.get_children(parent)
            index = siblings.index(item)

            try:
                if self.treeview.exists(item):
                    values = self.treeview.item(item, "values")
                    if values:
                        session_id = values[0]
                        self.treeview.delete(item)
                        self.remove_session_tab(session_id)
                        self.remove_session_json(session_id)
                        self.sort_sessions()
                        self.update_treeview()

                    if index > 0:
                        previous_item = siblings[index - 1]
                        self.treeview.selection_set(previous_item)
                        self.treeview.focus(previous_item)
                    elif len(siblings) > 1: 
                        next_item = siblings[1] if index == 0 else siblings[0]
                        self.treeview.selection_set(next_item)
                        self.treeview.focus(next_item)
            
            except:
                pass

    def remove_item(self, event):
        item = self.treeview.identify_row(event.y)
        if not item:
            return

        self.treeview.selection_set(item)

        def kill_session():
            if dialog.confirm_dialog(self) == "yes":
                if self.treeview.exists(item):
                    values = self.treeview.item(item, "values")
                    if values:
                        session_id = values[0]
                        session_title = "Session " + str(session_id)
                        self.treeview.item(item, tags=('disabled_selected'))

        def restart_session():
            if dialog.confirm_dialog(self) == "yes":
                if self.treeview.exists(item):
                    values = self.treeview.item(item, "values")
                    if values:
                        session_id = values[0]
                        session_title = "Session " + str(session_id)
                        self.treeview.item(item, tags=('disabled_selected'))
                        controller.retry_session(self, session_title)

        def confirm_remove():
            if dialog.confirm_dialog(self) == "yes":
                if self.treeview.exists(item):
                    values = self.treeview.item(item, "values")
                    if values:
                        session_id = values[0]
                        self.on_delete_treeview(item)

        menu = tk.Menu(self.treeview, tearoff=False)
        menu.add_command(label="Restart", command=restart_session)
        menu.add_command(label="Remove", command=confirm_remove)
        menu.add_command(label="Disconnect", command=kill_session)
        menu.tk_popup(event.x_root, event.y_root)

    def confirm_remove(self, action):
        selected_item = self.listener_table.selection()
        if not selected_item:
            return

        selected_item = selected_item[0]
        listener_tail = self.listener_table.item(selected_item, "values")[4]
        listener_details = self.listener_table.item(selected_item, "values")
        listener_status = self.listener_table.item(selected_item, "tags")

        if action == "Edit":
            edit_listener(self, listener_details)

        elif action == "Enable":
            reload_listener(self, self.session_id, listener_details, reload_listeners=True)
            self.listener_table.tag_configure("enabled", foreground="#FFFFFF")
            self.listener_table.item(selected_item, tags=('enabled',))
        
        elif action == "Disable":
            if "enabled" in listener_status:
                if dialog.confirm_dialog(self) == "yes":
                    controller.kill_listeners(self, listener_details)
                    self.listener_table.tag_configure("disabled_selected", foreground="#333333")
                    self.listener_table.item(selected_item, tags=('disabled_selected',))

        elif action == "Remove":
            if dialog.confirm_dialog(self) == "yes":
                parent = self.listener_table.parent(selected_item)
                siblings = self.listener_table.get_children(parent)
                index = siblings.index(selected_item)

                controller.kill_listeners(self, listener_details)
                self.remove_listener_json(listener_details)
                self.listener_table.delete(selected_item)

                if index > 0:
                    previous_item = siblings[index - 1]
                    self.listener_table.selection_set(previous_item)
                    self.listener_table.focus(previous_item)
                elif len(siblings) > 1:
                    next_item = siblings[1] if index == 0 else siblings[0]
                    self.listener_table.selection_set(next_item)
                    self.listener_table.focus(next_item)

    def remove_listener(self, event):
        item = self.listener_table.identify_row(event.y)
        if not item:
            return

        self.listener_table.selection_set(item)

        menu = tk.Menu(self.listener_table, tearoff=False)
        menu.add_command(label="Edit", command=lambda: self.confirm_remove("Edit"))
        menu.add_command(label="Enable", command=lambda: self.confirm_remove("Enable"))
        menu.add_command(label="Disable", command=lambda: self.confirm_remove("Disable"))
        menu.add_command(label="Remove", command=lambda: self.confirm_remove("Remove"))
        menu.tk_popup(event.x_root, event.y_root)

    def confirm_and_quit(self):
        if dialog.confirm_dialog(self) == "yes":
            if not self.fast_mode:
                print(colored("\n[!] Exiting.. Goodbye! :)\n", "red"))
            self.config(background="#444444")
            delivery.stop_multiserver(self)
            delivery.stop_webserver(self)
            self.destroy()
            self.quit()

    def restart_app(self, profile):
        if not self.fast_mode:
            print(colored(f"\n[!] Loading \"{profile}\" profile..", "red"))
        
        current_process = psutil.Process()
        for child in current_process.children(recursive=True):
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass

        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv, "-restart")

    def on_treeview_doubleclick(self, event):
        TAB_ORDER = ["Event Viewer", "Team Chat", "Listeners", "Module Console", "Multi Server Log", "Web Server Log"]

        try:
            item = self.treeview.selection()[0]
            values = self.treeview.item(item, "values")
            session_id = values[0]
            title = "Session " + session_id

        except:
            return

        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == title:
                self.notebook.select(tab)
                return

        for session in self.sessions:
            if session.title == title:
                self.sessions.remove(session)
                break

        session_data = self.saved_sessions[title]
        commands = Session.load_commands_from_session(self, session_id)
        new_session = Session(title, session_data, commands)
        new_session.reload_command_session()
        new_session.add_to_notebook(self.notebook)
        self.sessions.append(new_session)

        tab_texts = [self.notebook.tab(tab, "text") for tab in self.notebook.tabs()]
        sorted_tabs = [tab for tab in TAB_ORDER if tab in tab_texts] + sorted([tab for tab in tab_texts if tab not in TAB_ORDER])
        if title not in sorted_tabs:
            sorted_tabs.append(title)
        insert_index = sorted_tabs.index(title)

        self.notebook.insert(insert_index, new_session, text=title)
        self.notebook.select(insert_index)

    def on_double_click(self):
        selected_item = self.listener_table.selection()
        if selected_item:
            listener_details = self.listener_table.item(selected_item, "values")
            if listener_details:
                edit_listener(self, listener_details)

    def close_session(self):
        self.notebook.forget("current")

    def clear_data(self):
        try:
            current_user = os.getlogin()
        except:
            current_user = "root"

        try:
            logs_file = Path("data/events.json")
            logs_data = {"logs": []}
            if logs_file.is_file():
                os.remove(logs_file) 
            self.event_viewer_logs = self.load_event_viewer_logs()

        except:
            pass

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        label_text = f"[{current_time}] User <{current_user}> has joined the party!"
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.config(state="disabled")
        self.add_event_viewer_log(label_text + "\n", 'color_login', "#FF00FF")

    def confirm_and_clear(self):
        if dialog.confirm_dialog(self) == "yes":
            self.remove_data()

    def remove_data(self):
        try:
            self.session_block_until = 30
            self.event_viewer_logs = []
            self.command_history = []
            self.saved_sessions = {}
            self.session_id = 0
            self.listeners = []
            self.log_data = []
            self.sessions = []
            self.session = []
            self.logs = []
            self.log = []

            for listener in self.listeners:
                name = listener.get("Name")
                host = listener.get("Host")
                port = listener.get("Port")
                protocol = listener.get("Protocol")
                tail = listener.get("Tail")
                listener_details = (name, host, port, protocol, tail)
                controller.stop_listeners(self, listener_details)
                delivery.stop_multiserver(self)
                delivery.stop_webserver(self)
            self.listener_table.delete(*self.listener_table.get_children())
        
        except:
            pass

        try:
            data_path = "data"
            for item in os.listdir(data_path):
                item_path = os.path.join(data_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                else:
                    shutil.rmtree(item_path)
        except:
            pass

        try:
            existing_tabs = self.notebook.tabs()
            event_viewer_tab = None

            if existing_tabs:
                for tab in existing_tabs:
                    tab_text = self.notebook.tab(tab, "text")
                    if tab_text == "Event Viewer":
                        event_viewer_tab = tab
                    elif tab_text != "Team Chat":
                        self.notebook.forget(tab)

            if event_viewer_tab:
                self.notebook.tab(event_viewer_tab, state="normal")
                self.notebook.select(event_viewer_tab)

        except:
            pass

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        try:
            current_user = os.getlogin()
        except:
            current_user = "root"
        
        label_text = f"[{current_time}] User <{current_user}> has joined the party!"
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.config(state="disabled")
        self.add_event_viewer_log(label_text + "\n", 'color_login', "#FF00FF")
        self.treeview.delete(*self.treeview.get_children())

    def clear_delivery_logs(self, log_text, log_type):
        log_text.config(state="normal")
        log_text.delete(1.0, 'end')
        log_text.config(state="disabled")

        if log_type == "multi":
            if self.multi_delivery_process and self.multi_delivery_process.is_alive():
                message = "[>] Multi Server is running..\n"
                color_tag = "color_input"
            else:
                message = "[!] Multi Server is not running!\n"
                color_tag = "color_error"
            log_text.config(state="normal")
            log_text.insert('end', f"{message}\n", color_tag)
            log_text.config(state="disabled")

            multiserver_file = Path("data/multiserver.json")
            if multiserver_file.exists():
                with open(multiserver_file, 'r+') as f:
                    data = json.load(f)
                    data["Log"] = []
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
            delivery.open_multiserver_log_tab(self)

        if log_type == "web":
            if self.web_delivery_process and self.web_delivery_process.poll() is None:
                message = "[>] Web Server is running..\n"
                color_tag = "color_input"
            else:
                message = "[!] Web Server is not running!\n"
                color_tag = "color_error"
            log_text.config(state="normal")
            log_text.insert('end', f"{message}\n", color_tag)
            log_text.config(state="disabled")

            webserver_file = Path("data/webserver.json")
            if webserver_file.exists():
                with open(webserver_file, 'r+') as f:
                    data = json.load(f)
                    data["Log"] = []
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
            delivery.open_webserver_log_tab(self)

    def on_close(self):
        self.confirm_and_quit()
        
if __name__ == "__main__":
    check_and_copy_fonts()

    parser = argparse.ArgumentParser()
    parser.add_argument('-fast', action='store_true')
    parser.add_argument('-restart', action='store_true')
    args = parser.parse_args()
    restart_mode = args.restart
    fast_mode = args.fast

    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.config(background="#444444")
    root.geometry(f"{screen_width}x{screen_height}")
    root.title("Kitsune - Command & Control - by @JoelGMSec")
    photo = tk.PhotoImage(file='themes/images/Kitsune.png')
    root.wm_iconphoto(False, photo)

    settings_path = Path("data/settings.json")
    if settings_path.exists():
        try:
            with settings_path.open("r") as json_file:
                kitsune_settings = json.load(json_file)["settings"]
                theme_name = kitsune_settings.get("theme").lower()
                root.tk.call("source", "themes/kitsune.tcl")
                root.tk.call("set_theme", theme_name)
        except:
            pass
    else:
        root.tk.call("source", "themes/kitsune.tcl")
        root.tk.call("set_theme", "blue")

    temp_path = f'/tmp/Kitsune'
    shutil.rmtree(temp_path, ignore_errors=True)

    if not fast_mode and not restart_mode:
        print(open("./themes/banner.txt", "r").read())
        print(colored("     -------- by @JoelGMSec --------\n", "blue"))

    try:
        app = App(root, fast_mode)
        app.pack(fill="both", expand=True)
        root.mainloop()

    except KeyboardInterrupt:
        if not fast_mode:
            print(colored("\n[!] Exiting.. Goodbye! :)\n", "red"))
        pass

    except:
        pass
