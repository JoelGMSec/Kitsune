#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import re
import sys
import time
import json
import bisect
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk
from neotermcolor import colored

def typing(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.02)

class Session(tk.Frame):
    def __init__(self, title, session_data, commands):
        super().__init__()
        self.log = []
        self.tabs = []
        self.title = title
        self.tab_id = None
        self.text_widget = None
        self.commands = commands
        self.session_data = session_data
        self.config(background="#333333")

        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        self.label = tk.Text(
            self, 
            yscrollcommand=self.scrollbar.set,
            pady=5,
            padx=5,
            bg="#333333",   
            borderwidth=0, 
            highlightbackground="#333333", 
            highlightthickness=0,
            selectbackground="#1B1B1B", 
            inactiveselectbackground="#1B1B1B",
            state="disabled",
            cursor="arrow"
        )

        self.label.config(font=("Consolas", 18, "bold"))
        self.label.pack(fill="both", expand=True)
        self.scrollbar.config(command=self.label.yview)
        self.context_menu = tk.Menu(self.label, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_session_text)
        self.context_menu.add_command(label="Clear", command=self.clear_session_text)
        self.label.bind("<Button-3>", self.show_context_menu)
        self.label.bind("<Control-c>", self.copy_session_text)
        self.label.bind("<Control-a>", self.select_all_text)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def copy_session_text(self, event=None):
        try:
            selected_text = self.label.selection_get()
            self.label.clipboard_clear()
            self.label.clipboard_append(selected_text)
            self.label.tag_remove(tk.SEL, "1.0", tk.END)
        except:
            pass

    def select_all_text(self, event=None):
        self.label.config(state="normal")
        last_line_start = self.label.index("end-1l linestart")
        if self.label.get("1.0", last_line_start).strip():
            self.label.tag_add(tk.SEL, "1.0", last_line_start)
            self.label.mark_set(tk.INSERT, "1.0")
            self.label.see(tk.END)
        self.label.config(state="disabled")
        return "break"

    def clear_session_text(self):
        self.label.config(state="normal")
        self.label.delete('1.0', tk.END)
        self.label.config(state="disabled")
        self.clear_logs()
        return

    def add_to_notebook(self, notebook):
        self.notebook = notebook
        self.notebook.add(self, text=self.title)

    def get_label(self, app):
        for tab in app.notebook.tabs():
            if app.notebook.tab(tab, "text") == self.title:
                return app.notebook.nametowidget(tab).label
        return None

    def reload_command_session(self):
        self.load_logs()
        self.update_log_display()

    def load_commands_from_session(app, session_id):
        sessions = Session.load_sessions(app)
        for session in sessions:
            if session['Session'] == session_id:
                return session.get('Commands', [])
        return []

    def find_existing_session(app, user, hostname, listener, tail):
        new_session = None
        try:
            with open('data/sessions.json', 'r') as file:
                sessions_data = json.load(file)
        except:
            return None

        for session in sessions_data:
            if (session.get('User') == user and session.get('Hostname') == hostname and
                session.get('Listener') == listener and session.get('Tail') == tail):
                return session['Session']
            else:
                new_session = app.count_session()
        return new_session

    def load_saved_sessions(app):
        from modules.controller import restart_session
        from modules.controller import start_listeners
        app.sort_sessions()
        
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        label_text = f"[{current_time}] Nekomancer is enabled! Recovering connections.."

        try:
            with open('data/sessions.json', 'r') as f:
                sessions_data = json.load(f)
        except:
            sessions_data = []
            app.session_id = 0

        if sessions_data:
            if not app.fast_mode:
                typing(colored("\n[>] Looking for previous sessions..\n","yellow"))

            for session in sessions_data:
                title = 'Session ' + str(session['Session'])
                app.saved_sessions[title] = session
                restart_session(app, session, False)
                if not app.fast_mode:
                    print(colored(f"[+] {title} loaded successfully!","green"))
                app.session_id = max(app.session_id, session['Session'])
                time.sleep(0.1)

        with open('data/settings.json', 'r') as settings_file:
            settings_data = json.load(settings_file)
            nekomancer_setting = settings_data.get('settings', {}).get('nekomancer', '')

        if nekomancer_setting == "All Sessions" or nekomancer_setting == "Reverse Only":
            start_listeners(app, app.session_id, reload_listeners=True)
            if app.saved_sessions:
                if not app.fast_mode:
                    typing(colored("\n[!] Nekomancer is enabled! Recovering connections..\n","red"))
                app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")

        if nekomancer_setting == "Bind Only":
            if app.saved_sessions:
                if not app.fast_mode:
                    typing(colored("\n[!] Nekomancer is enabled! Recovering connections..\n","red"))
                app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")

        return app.session_id

    def load_sessions(app):
        try:
            app.sort_sessions()
            with open('data/sessions.json') as f:
                sessions = json.load(f)
                if not isinstance(sessions, list):
                    return []
                for session in sessions:
                    if not isinstance(session, dict):
                        return []
                sessions = sorted(sessions, key=lambda s: s['Session'])
                return sessions
        except:
            return []

    def find_next_session_number(app):
        sessions = Session.load_sessions(app)
        existing_numbers = {session['Session'] for session in sessions}
        next_number = 1
        while next_number in existing_numbers:
            next_number += 1
        return next_number

    def save_session(app, session_info, commands):
        if app.session_block_until != 0:
            return

        try:
            sessions = Session.load_sessions(app)
            
            session_exists = False
            for i, session in enumerate(sessions):
                if session['Session'] == session_info['Session']:
                    session_exists = True
                    sessions[i] = session_info
                    sessions[i]['Commands'] = commands
                    break
            
            if not session_exists:
                session_info['Commands'] = commands
                session_info['Session'] = Session.find_next_session_number(app)
                sessions.append(session_info)
            
            with open('data/sessions.json', 'w') as f:
                json.dump(sessions, f, indent=4)

        except:
            pass

    def clear_logs(self):
        try:
            with open('data/sessions.json', 'r') as f:
                sessions = json.load(f)

            session_id = int(self.title.split(' ')[1])  
            for session in sessions:
                if session['Session'] == session_id:  
                    session['Commands'] = []
                    break

            with open('data/sessions.json', 'w') as f:
                json.dump(sessions, f, indent=4)

            self.log = []

        except:
            pass

    def save_logs(self):
        try:
            with open('data/sessions.json', 'r') as f:
                sessions = json.load(f)
            log_data = self.log
            session_id = int(self.title.split(' ')[1])  
            for session in sessions:
                if session['Session'] == session_id:  
                    session['Commands'] = log_data
                    break
            with open('data/sessions.json', 'w') as f:
                json.dump(sessions, f, indent=4)
        except:
            pass

    def load_logs(self):
        try:
            with open('data/sessions.json', 'r') as f:
                sessions = json.load(f)
                session_id = int(self.title.split(' ')[1])  
                for session in sessions:
                    if session['Session'] == session_id:  
                        self.log = session.get('Commands', [])
                        break
        except:
            pass

    def update_log_display(self):
        self.label.config(state="normal")
        self.label.delete(1.0, "end")
        url_pattern = re.compile(r"https?://[^\s]+")
        
        for entry in self.log:
            command = entry['Command']
            output = entry['Output']
            self.label.tag_config("color1", foreground="#00AAFF")
            self.label.tag_config("color2", foreground="#00FF99")
            self.label.tag_config("color3", foreground="#FFFFFF")
            self.label.tag_config("url", foreground="#FFFFFF", underline=True)
            
            log_text = f"kitsune> "
            self.label.insert("end", log_text, "color1")
            log_text = f"{command}\n"
            self.label.insert("end", log_text, "color3")
            log_text = f"[>] Output:\n"
            self.label.insert("end", log_text, "color2")

            parts = url_pattern.split(output)
            urls = url_pattern.findall(output)
            
            for i, part in enumerate(parts):
                self.label.insert("end", part, "color3")
                if i < len(urls):
                    url = urls[i]
                    start_index = self.label.index("end")
                    self.label.insert("end", url, "url")
                    self.label.tag_bind("url", "<Button-1>", lambda e, url=url: self.open_url(url))
                    self.label.tag_bind("url", "<Enter>", lambda e: self.label.config(cursor="hand2"))
                    self.label.tag_bind("url", "<Leave>", lambda e: self.label.config(cursor="xterm"))

            self.label.insert("end", "\n\n", "color3")
        self.label.config(state="disabled")
        self.label.see("end")

    def open_url(self, url):
        webbrowser.open(url) 

    def load_command_history():
        try:
            with open('data/commands.json', 'r') as f:
                return json.load(f)
        except:
            return []

    def save_command_history(history):
        with open('data/commands.json', 'w') as f:
            json.dump(history, f, indent=4)

    def add_session_to_treeview(app, session_info, session_data):
        if app.session_block_until != 0:
            return

        title = f"Session {session_info['Session']}"
        app.treeview.tag_configure("enabled", foreground="#FFFFFF")

        try:
            if title in app.saved_sessions:
                app.saved_sessions[title] = session_data
                session_id = str(title.split()[1])
                item_selected = False
                old_item = None

                for item in app.treeview.get_children():
                    item_info = app.treeview.item(item)
                    session_number = item_info['values']

                    if str(session_id) == str(session_number[0]) and session_info["Tail"] == item_info['values'][8]:
                        old_item = item
                        if app.treeview.selection() and app.treeview.selection()[0] == item:
                            item_selected = True
                        break

                if old_item:
                    session_ids_tails = [(int(app.treeview.item(child, 'values')[0]), app.treeview.item(child, 'values')[8]) for child in app.treeview.get_children()]
                    insert_index = bisect.bisect_left(session_ids_tails, (int(session_info["Session"]), session_info["Tail"]))
                    app.treeview.item(old_item, values=(session_info["Session"], session_info["User"], session_info["Hostname"], session_info["IP Address"], session_info["Process"], session_info["PID"], session_info["Arch"], session_info["Listener"], session_info["Tail"]), tags=('enabled',))

                    for item in app.treeview.get_children():
                        item_info = app.treeview.item(item)
                        values = item_info['values']

                        if str(values[0]) == str(session_info["Session"]) and session_info["Tail"] == values[8]:
                            if item_selected:
                                app.treeview.selection_set(item)
                                break

            else:
                app.saved_sessions[title] = session_data
                session_ids_tails = [(int(app.treeview.item(child, 'values')[0]), app.treeview.item(child, 'values')[8]) for child in app.treeview.get_children()]
                insert_index = bisect.bisect_left(session_ids_tails, (int(session_info["Session"]), session_info["Tail"]))
                app.treeview.insert('', insert_index, values=(session_info["Session"], session_info["User"], session_info["Hostname"], session_info["IP Address"], session_info["Process"], session_info["PID"], session_info["Arch"], session_info["Listener"], session_info["Tail"]), tags=('enabled',))

        except:
            pass

    def disable_session(app, session_title):
        from modules.controller import retry_session
        for session in app.sessions:
            try:
                if session.title == session_title:
                    session_id = session_title
                    
                session_number = str(session_id.split()[1])
                for item in app.treeview.get_children():
                    item_info = app.treeview.item(item)
                    values = item_info['values']
                    tags = item_info['tags']

                    app.treeview.tag_configure("disabled", foreground="#868686")
                    app.treeview.tag_configure("disabled_selected", foreground="#333333")
                    selected_items = app.treeview.selection()

                    if str(values[0]) == str(session_number):

                        if item in selected_items:
                            app.treeview.item(item, tags=("disabled_selected",))
                        else:
                            app.treeview.item(item, tags=("disabled",))

                retry_session(app, session_title)

            except:
                pass

    def enable_session(app, session_title):
        app.treeview.tag_configure("enabled", foreground="#FFFFFF") 
        session_id = "Session 0"
        for session in app.sessions:
            try:
                if session.title == session_title:
                    session_id = session_title
                    
                session_number = str(session_id.split()[1])
                for item in app.treeview.get_children():
                    item_info = app.treeview.item(item)
                    values = item_info['values']

                    if str(values[0]) == str(session_number):
                        app.treeview.item(item, tags=('enabled',))
                        break

            except:
                pass

    def add_new_session(app, title, session_id, session_info, session_data):
        if app.session_block_until != 0:
            return

        for session in app.sessions:
            if session.title == title:
                app.sessions.remove(session)
                break

        session_data = app.saved_sessions[title]  
        commands = Session.load_commands_from_session(app, session_id)
        new_session = Session(title, session_data, commands)
        new_session.reload_command_session()
        if not app.fast_mode:
            print(colored(f"[+] New connection from {session_info['Hostname']} on {title}!","green"))

        previously_selected = False
        for tab in app.notebook.tabs():
            tab_title = app.notebook.tab(tab, "text")
            if tab_title == title:
                previously_selected = app.notebook.tab(app.notebook.select(), "text") == title
                app.notebook.forget(tab)
                new_session.add_to_notebook(app.notebook)
                app.sessions.append(new_session)

                tab_texts = [app.notebook.tab(tab, "text") for tab in app.notebook.tabs()]
                sorted_tabs = sorted(tab_texts + [title])
                insert_index = sorted_tabs.index(title)

                if "Web Server Log" in sorted_tabs:
                    insert_index = insert_index + 1
                app.notebook.insert(insert_index + 1, new_session, text=title)

                if previously_selected:
                    for tab in app.notebook.tabs():
                        tab_title = app.notebook.tab(tab, "text")
                        if tab_title == title:
                            app.notebook.select(tab)
                            break
