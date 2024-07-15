#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import tkinter as tk
import os, sys, time, json, shutil, datetime, threading
from pathlib import Path
from neotermcolor import colored
from tkinter import ttk, filedialog
from modules.session import Session
from modules.tails import clone_repos
from modules.listeners import edit_listener
from modules.controller import reload_listener
from modules.widgets import setup_widgets
from modules.widgets import DraggableTabsNotebook
from modules import profile, updater, settings, about, delivery, listeners, controller, payloads, tails, reporter, chat

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

class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.load_settings()
        self.sort_sessions()
        self.silent_error = False
        parent.protocol("WM_DELETE_WINDOW", self.on_close)

        for index in [0, 1]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        self.check_repos()
        self.text_tag_counter = 0
        self.event_viewer_logs = self.load_event_viewer_logs()

        self.clear_command = False
        self.command_history = Session.load_command_history()
        self.history_index = len(self.command_history)

        self.treeview_state = {}
        setup_widgets(parent, self)
        self.update_event_viewer()

        self.listeners = []
        self.listener_table = None
        self.web_delivery_process = None
        self.multi_delivery_process = None

        listeners.load_listeners(self)
        self.update_listeners_settings()
        delivery.periodically_update_webserver(self)
        delivery.periodically_update_multiserver(self)

        self.sessions = []
        self.session_id = 0
        self.saved_sessions = {}

        Session.load_saved_sessions(self)
        typing(colored("\n[>] Loading Event Viewer..\n", "yellow"))
        
        try:
            self.username = os.getlogin()
        except:
            self.username = "root"

        chat.start_server(self)
        self.client_socket = None
        self.team_chat_tab = chat.TeamChatTab(self.notebook)
        self.team_chat_tab.connect_to_server(self.username, "localhost")
        self.client_socket = self.team_chat_tab.get_socket()

    def load_settings(self):
        default_settings = {
            "settings": {
                "theme": "Blue",
                "nekomancer": "All Sessions"
            }
        }
        try:
            with open("data/settings.json", "r") as json_file:
                settings = json.load(json_file)["settings"]
                self.theme_var = tk.StringVar(value=settings.get("theme", "Blue"))
                self.saved_value = settings.get("nekomancer", "All Sessions")
 
        except:
            with open(settings_path, "w") as json_file:
                json.dump(default_settings, json_file, indent=4)
            self.theme_var = tk.StringVar(value="Blue")
            self.saved_value = "All Sessions"

    def check_updates(self):
        return updater.check_updates(self)

    def export_profile(self):
        return profile.export_profile(self)

    def open_settings(self):
        return settings.open_settings(self)

    def update_tails(self):
        return tails.update_tails(self)

    def about_window(self):
        return about.about_window(self)

    def multi_delivery(self):
        return delivery.multi_delivery(self)

    def web_delivery(self):
        return delivery.web_delivery(self)

    def listener_window(self):
        return listeners.listener_window(self)

    def show_listeners(self):
        return listeners.show_listeners(self)

    def add_listeners(self):
        return listeners.add_listeners(self)

    def load_listeners(self):
        return listeners.load_listeners(self)

    def open_multiserver_log_tab(self):
        return delivery.open_multiserver_log_tab(self)

    def open_webserver_log_tab(self):
        return delivery.open_webserver_log_tab(self)

    def open_multiserver_log_tab(self):
        return delivery.open_multiserver_log_tab(self)

    def kill_webserver(self):
        return delivery.kill_webserver(self)

    def kill_multiserver(self):
        return delivery.kill_multiserver(self)

    def windows_payload(self):
        return payloads.windows_payload(self)

    def linux_payload(self):
        return payloads.linux_payload(self)

    def webshell_payload(self):
        return payloads.webshell_payload(self)

    def webshell_generate(self):
        return payloads.webshell_generate(self)

    def pwncat_payload(self):
        return payloads.pwncat_payload(self)

    def netexec_payload(self):
        return payloads.netexec_payload(self)

    def check_repos(self):
        tails_dir = "tails"
        if not os.path.exists(tails_dir) or not any(os.path.isdir(os.path.join(tails_dir, entry)) for entry in os.listdir(tails_dir)):
            threading.Thread(target=clone_repos).start()

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
                kitsune_settings = json.load(json_file)["settings"]
        except:
            kitsune_settings = {"theme": "Blue", "nekomancer": "All Sessions"}

        kitsune_settings["theme"] = theme

        with open("data/settings.json", "w") as json_file:
            json.dump({"settings": kitsune_settings}, json_file, indent=4)

        self.theme_var.set(theme)
        
        try:
            selected_items = [self.treeview.item(item, 'values')[0] for item in self.treeview.selection()]

            self.save_treeview_state()

            self.treeview.delete(*self.treeview.get_children())

            if theme == "Blue":
                root.tk.call("set_theme", "blue")

            elif theme == "Green":
                root.tk.call("set_theme", "green")

            elif theme == "Purple":
                root.tk.call("set_theme", "purple")

            elif theme == "Red":
                root.tk.call("set_theme", "red")

            try:
                sessions_data = Session.load_sessions()
                self.treeview.tag_configure("disabled", foreground="gray")

                if sessions_data:
                    for session in sessions_data:
                        app.treeview.insert('', 'end', tags=['disabled'] ,values=(session["Session"], session["User"], session["Hostname"], session["IP Address"], session["Process"], session["PID"], session["Arch"], session["Listener"], session["Tail"]))

            except:
                pass

            for item in self.treeview.get_children():
                item_info = app.treeview.item(item)
                session_number = item_info['values']

                for item_id, state in self.treeview_state.items():
                    if int(item_id[0]) == int(session_number[0]):
                        if state == 'enabled':
                            self.treeview.tag_configure("enabled", foreground="#FFFFFF")
                            self.treeview.item(item, tags=('enabled',))

                for item_id in selected_items:
                    if int(item_id[0]) == int(session_number[0]):
                        self.treeview.selection_add(item)

            self.treeview.update()

        except:
            pass

    def update_listeners_settings(self):
        try:
            with open("data/settings.json", "r") as json_file:
                settings = json.load(json_file)["settings"]
                nekomancer_setting = settings.get("nekomancer", "All Sessions")
        except FileNotFoundError:
            print("Archivo de configuración no encontrado, utilizando valores predeterminados.")
            nekomancer_setting = "All Sessions"

        try:
            with open('data/listeners.json', 'r') as listeners_file:
                listeners_data = json.load(listeners_file)
        except FileNotFoundError:
            print("Archivo de listeners no encontrado, saltando actualización.")
            return

        if nekomancer_setting in ["Disabled", "Bind Only"]:
            new_state = "disabled"
        elif nekomancer_setting in ["All Sessions", "Reverse Only"]:
            new_state = "enabled"
        else:
            print("Configuración de Neokomancer desconocida, no se realizarán cambios.")
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
        split_log = log.split("] ", 1)

        if len(split_log) > 1:
            if len(self.event_viewer_logs) > 0:
                last_log = self.event_viewer_logs[-1]
                split_last_log = last_log[0].split("] ", 1)
                
                if len(split_last_log) > 1 and split_log[1] == split_last_log[1]:
                    self.event_viewer_logs[-1] = (log, tag, color)
                else:
                    self.event_viewer_logs.append((log, tag, color))
                    self.text_tag_counter += 1
            else:
                self.event_viewer_logs.append((log, tag, color))
                self.text_tag_counter += 1
        else:
            return

        self.save_event_viewer_logs()
        self.notify_event_viewer()
        self.update_event_viewer()

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
                self.entry.config(foreground="#c0c0c0")

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

    def remove_item(self, event):
        item = self.treeview.identify_row(event.y)
        if not item:
            return

        self.treeview.selection_set(item)

        def kill_session():
            if self.confirm_dialog() == "yes":
                self.treeview.item(item, tags=('disabled'))

        def restart_session():
            time.sleep(5)
            self.treeview.item(item, tags=('enabled'))

        def confirm_remove():
            if self.confirm_dialog() == "yes":
                if self.treeview.exists(item):
                    values = self.treeview.item(item, "values")
                    if values:
                        session_id = values[0]
                        self.treeview.delete(item)
                        self.remove_session_json(session_id)

        menu = tk.Menu(self.treeview, tearoff=False)
        menu.add_command(label="Disconnect", command=kill_session)
        menu.add_command(label="Remove", command=confirm_remove)
        menu.add_command(label="Restart", command=restart_session)
        menu.tk_popup(event.x_root, event.y_root)

    def confirm_remove(self, action):
        selected_item = self.listener_table.selection()
        if not selected_item:
            return

        listener_tail = self.listener_table.item(selected_item, "values")[4]
        listener_details = self.listener_table.item(selected_item, "values")

        if action == "Edit":
            edit_listener(self, listener_details)

        elif action == "Enable":
            reload_listener(self, self.session_id, listener_details, reload_listeners=True)
            self.listener_table.tag_configure("enabled", foreground="#FFFFFF")
            self.listener_table.item(selected_item, tags=('enabled',))
        
        elif action == "Disable":
            if self.confirm_dialog() == "yes":
                controller.kill_listeners(self, listener_details)
                app.listener_table.tag_configure("disabled", foreground="gray")
                app.listener_table.item(selected_item, tags=('disabled',))

        elif action == "Remove":
            if self.confirm_dialog() == "yes":
                controller.kill_listeners(self, listener_details)
                self.remove_listener_json(listener_details)
                self.listener_table.delete(selected_item)

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

    def module_warning(self):
        dialog = tk.Toplevel(self)
        dialog.title("Warning")
        dialog.focus_force()

        label = ttk.Label(dialog, text="This function is not yet implemented!")
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=20, pady=10)

        def on_enter_key(event):
            dialog.destroy()

        dialog.bind("<Return>", on_enter_key)

        def on_escape_key(event):
            dialog.destroy()

        dialog.bind("<Escape>", on_escape_key)

        yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
        yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    def report_deleted_success(self):
        dialog = tk.Toplevel(self)
        dialog.title("Success")
        dialog.focus_force()

        label = ttk.Label(dialog, text="All reports have been deleted!")
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=20, pady=10)

        def on_enter_key(event):
            dialog.destroy()

        dialog.bind("<Return>", on_enter_key)

        def on_escape_key(event):
            dialog.destroy()

        dialog.bind("<Escape>", on_escape_key)

        yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
        yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    def profile_deleted_success(self):
        dialog = tk.Toplevel(self)
        dialog.title("Success")
        dialog.focus_force()

        label = ttk.Label(dialog, text="All profiles have been deleted!")
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=20, pady=10)

        def on_enter_key(event):
            dialog.destroy()

        dialog.bind("<Return>", on_enter_key)

        def on_escape_key(event):
            dialog.destroy()

        dialog.bind("<Escape>", on_escape_key)

        yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
        yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    def project_saved_success(self):
        dialog = tk.Toplevel(self)
        dialog.title("Success")
        dialog.focus_force()

        label = ttk.Label(dialog, text="Report saved successfully!")
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=20, pady=10)

        def on_enter_key(event):
            dialog.destroy()

        dialog.bind("<Return>", on_enter_key)

        def on_escape_key(event):
            dialog.destroy()

        dialog.bind("<Escape>", on_escape_key)

        yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
        yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    def profile_saved_success(self):
        dialog = tk.Toplevel(self)
        dialog.title("Success")
        dialog.focus_force()

        label = ttk.Label(dialog, text="Profile saved successfully!")
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=20, pady=10)

        def on_enter_key(event):
            dialog.destroy()

        dialog.bind("<Return>", on_enter_key)

        def on_escape_key(event):
            dialog.destroy()

        dialog.bind("<Escape>", on_escape_key)

        yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
        yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    def generate_success(self):
        dialog = tk.Toplevel(self)
        dialog.title("Success")
        dialog.focus_force()

        os.system("chmod +x payloads -R")
        label = ttk.Label(dialog, text="Payload generated successfully!")
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=20, pady=10)

        def on_enter_key(event):
            dialog.destroy()

        dialog.bind("<Return>", on_enter_key)

        def on_escape_key(event):
            dialog.destroy()

        dialog.bind("<Escape>", on_escape_key)

        yes_button = ttk.Button(button_frame, text="Close", command=lambda: dialog.destroy())
        yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

    def confirm_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Confirmation")
        dialog.focus_force()

        label = ttk.Label(dialog, text="Are you sure?")
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=20, pady=10)

        def set_result(value):
            self.result = value
            dialog.destroy()

        def on_enter_key(event):
            set_result("yes")

        dialog.bind("<Return>", on_enter_key)

        def on_escape_key(event):
            set_result("no")

        dialog.bind("<Escape>", on_escape_key)

        yes_button = ttk.Button(button_frame, text="Yes", command=lambda: set_result("yes"))
        yes_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

        no_button = ttk.Button(button_frame, text="No", command=lambda: set_result("no"))
        no_button.pack(side=tk.LEFT, padx=5, pady=(0, 10))

        self.result = None
        
        while self.result not in ["yes", "no"]:
            self.update()

        return self.result

    def confirm_and_quit(self):
        if self.confirm_dialog() == "yes":
            print(colored("\n[!] Exiting.. Goodbye! :)\n", "red"))
            self.destroy()
            self.quit()

    def restart_app(self):
        print(colored("\n[!] Loading new profile..", "red"))
        self.destroy()

        os.execl(sys.executable, sys.executable, *sys.argv)

    def on_treeview_doubleclick(self, event):
        TAB_ORDER = ["Event Viewer", "Team Chat", "Listeners", "Multi Server Log", "Web Server Log"]

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
        commands = Session.load_commands_from_session(session_id)
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
        self.update()

    def on_double_click(app):
        selected_item = app.listener_table.selection()
        if selected_item:
            listener_details = app.listener_table.item(selected_item, "values")
            if listener_details:
                edit_listener(app, listener_details)

    def close_session(self):
        self.notebook.forget("current")

    def clear_data(self):
        if self.confirm_dialog() == "yes":
            self.remove_data()

    def remove_data(self):
        try:
            sessions = []
            saved_sessions = {}
            directory = "data"

            for listener in self.listeners:
                name = listener.get("Name")
                host = listener.get("Host")
                port = listener.get("Port")
                protocol = listener.get("Protocol")
                tail = listener.get("Tail")
                listener_details = (name, host, port, protocol, tail)
                controller.stop_listeners(self, listener_details)
            self.listener_table.delete(*self.listener_table.get_children())
        
        except:
            pass

        self.entry.delete(0, tk.END)
        data_path = "data"

        try:
            for item in os.listdir(data_path):
                item_path = os.path.join(data_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                else:
                    shutil.rmtree(item_path)
        except:
            pass

        self.event_viewer_logs = []
        self.command_history = []
        self.session_id = 0
        self.listeners = []
        self.log_data = []
        self.session = []
        self.logs = []
        self.log = []

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        try:
            current_user = os.getlogin()
        except:
            current_user = "root"
        
        label_text = f"[{current_time}] User *{current_user}* has reset all data!"

        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.config(foreground="#FF00FF")
        self.text.insert("end", label_text + "\n")
        self.text.config(state="disabled")

        self.add_event_viewer_log(label_text + "\n", 'color_login', "#FF00FF")

        self.treeview.delete(*self.treeview.get_children())

        current_tab = self.notebook.tab(self.notebook.select(), "text")
        for session in self.sessions:
            current_session = session
            current_session.label.config(state="normal")
            current_session.label.delete('1.0', tk.END)
            current_session.label.config(state="disabled")
            current_session.log.clear()

    def export_profile(self):
        profile.export_profile(app)

    def import_profile(self):
        profile.import_profile(app)

    def delete_profile(self):
        profile.delete_profile(app)

    def export_logs(self):
        reporter.export_logs(app)

    def clear_logs(self):
        reporter.clear_logs(app)

    def on_close(self):
        self.confirm_and_quit()
        
if __name__ == "__main__":
    check_and_copy_fonts()

    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")
    root.title("Kitsune - Command & Control - by @JoelGMSec")
    photo = tk.PhotoImage(file = 'themes/images/Kitsune.png')
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

    print(open("./themes/banner.txt", "r").read())
    print(colored("     -------- by @JoelGMSec --------\n","blue"))
                                  
    try:
        app = App(root)
        app.pack(fill="both", expand=True)
        app_thread = threading.Thread(target=root.mainloop())
        app_thread.start()

    except KeyboardInterrupt:
        print(colored("\n[!] Exiting.. Goodbye! :)\n", "red"))
        pass

    except Exception as e:
        print("\n".join( "-"*i+" "+j for i,j in enumerate(e.args)))
        pass
