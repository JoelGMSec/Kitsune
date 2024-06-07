#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#    https://darkbyte.net #
#=========================#

import sys
import time
import json
import bisect
import datetime
import tkinter as tk
from tkinter import ttk
from neotermcolor import colored

def typing(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.02)

class Session(ttk.Frame):
    def __init__(self, title, session_data, commands):
        super().__init__()
        self.log = []
        self.tabs = []
        self.title = title
        self.tab_id = None
        self.text_widget = None
        self.commands = commands
        self.session_data = session_data
        
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        
        self.label = tk.Text(self, yscrollcommand=self.scrollbar.set, bg="#333333",
        borderwidth=0, highlightbackground="#333333", highlightthickness=0, state="disabled")
        self.label.config(font=("Consolas", 18, "bold"))
        self.label.pack(fill="both", expand=True)
        self.scrollbar.config(command=self.label.yview)

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

    def load_commands_from_session(session_id):
        sessions = Session.load_sessions()
        for session in sessions:
            if session['Session'] == session_id:
                return session.get('Commands', [])
        return []

    def find_existing_session(app, user, hostname, listener, tail):
        try:
            with open('data/sessions.json', 'r') as file:
                sessions_data = json.load(file)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:       
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
        
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        label_text = f"[{current_time}] Nekomancer is enabled! Recovering connections.."

        try:
            with open('data/sessions.json', 'r') as f:
                sessions_data = json.load(f)
        except FileNotFoundError:
            sessions_data = []
            app.session_id = 0

        if sessions_data:
            typing(colored("\n[>] Looking for previous sessions..\n","yellow"))

            for session in sessions_data:
                title = 'Session ' + str(session['Session'])
                app.saved_sessions[title] = session
                restart_session(app, session)
                print(colored(f"[+] {title} loaded successfully!","green"))
                app.session_id = max(app.session_id, session['Session'])
                time.sleep(0.1)

        with open('data/settings.json', 'r') as settings_file:
            settings_data = json.load(settings_file)
            nekomancer_setting = settings_data.get('settings', {}).get('nekomancer', '')

        if nekomancer_setting == "All Sessions" or nekomancer_setting == "Reverse Only":
            start_listeners(app, app.session_id, reload_listeners=True)
            if app.saved_sessions:
                typing(colored("\n[!] Nekomancer is enabled! Recovering connections..\n","red"))
                
                app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")

        if nekomancer_setting == "Bind Only":
            if app.saved_sessions:
                typing(colored("\n[!] Nekomancer is enabled! Recovering connections..\n","red"))

                app.add_event_viewer_log(label_text + "\n", 'color_error', "#FF0055")

        return app.session_id

    def load_sessions():
        try:
            with open('data/sessions.json') as f:
                sessions = json.load(f)
                if not isinstance(sessions, list):
                    print("Error: sessions.json does not contain a list")
                    return []
                for session in sessions:
                    if not isinstance(session, dict):
                        print("Error: session is not a dictionary")
                        return []
                sessions = sorted(sessions, key=lambda s: s['Session'])
                return sessions
        except:
            return []

    def save_session(session_info, commands):
        sessions = Session.load_sessions()
        for i, session in enumerate(sessions):
            if session['Session'] == session_info['Session']:
                sessions[i] = session_info
                sessions[i]['Commands'] = commands
                break
        else:
            session_info['Commands'] = commands
            sessions.append(session_info)

        if not isinstance(sessions, list):
            sessions = [sessions]

        sessions = sorted(sessions, key=lambda s: s['Session'])

        with open('data/sessions.json', 'w') as f:
            json.dump(sessions, f, indent=4)

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
        except FileNotFoundError:
            print("Error: No se encontró sessions.json.")

    def load_logs(self):
        try:
            with open('data/sessions.json', 'r') as f:
                sessions = json.load(f)
                session_id = int(self.title.split(' ')[1])  
                for session in sessions:
                    if session['Session'] == session_id:  
                        self.log = session.get('Commands', [])
                        break
        except FileNotFoundError:
            pass

    def update_log_display(self):
        self.label.config(state="normal")
        self.label.delete(1.0, "end")  
        
        for entry in self.log:
            command = entry['Command']
            output = entry['Output']
            self.label.tag_config("color1", foreground="#00AAFF")
            self.label.tag_config("color2", foreground="#00FF99")
            self.label.tag_config("color3", foreground="#FFFFFF")
            log_text = f"kitsune> "
            self.label.insert("end", log_text, "color1")
            log_text = f"{command}\n"
            self.label.insert("end", log_text, "color3")
            log_text = f"[>] Output:\n"
            self.label.insert("end", log_text, "color2")
            log_text = f"{output}\n\n"
            self.label.insert("end", log_text, "color3")
            
        self.label.config(state="disabled")
        self.label.see("end")  

    def load_command_history():
        try:
            with open('data/commands.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_command_history(history):
        with open('data/commands.json', 'w') as f:
            json.dump(history, f, indent=4)

    def add_session_to_treeview(app, session_info, session_data):
        title = f"Session {session_info['Session']}"
        app.treeview.tag_configure("enabled", foreground="#FFFFFF")

        if title in app.saved_sessions:
            app.saved_sessions[title] = session_data

            session_id = str(title.split()[1])

            for item in app.treeview.get_children():
                item_info = app.treeview.item(item)
                session_number = item_info['values']

                if str(session_id) == str(session_number[0]) and session_info["Tail"] == item_info['values'][8]:
                    if app.treeview.selection() and app.treeview.selection()[0] == item:
                        item_selected = True
                    else:
                        item_selected = False
                    app.treeview.delete(item)
                    break

            session_ids_tails = [(int(app.treeview.item(child, 'values')[0]), app.treeview.item(child, 'values')[8]) for child in app.treeview.get_children()]
            insert_index = bisect.bisect_left(session_ids_tails, (int(session_info["Session"]), session_info["Tail"]))

            app.treeview.insert('', insert_index, values=(session_info["Session"], session_info["User"], session_info["Hostname"], session_info["IP Address"], session_info["Process"], session_info["PID"], session_info["Arch"], session_info["Listener"], session_info["Tail"]), tags=('enabled',))

            try:
                for item in app.treeview.get_children():
                    item_info = app.treeview.item(item)
                    values = item_info['values']

                    if str(values[0]) == str(session_info["Session"]) and session_info["Tail"] == values[8]:
                        if item_selected:
                            app.treeview.selection_set(item)
                            break
            except:
                pass

        else:
            app.saved_sessions[title] = session_data
            session_ids_tails = [(int(app.treeview.item(child, 'values')[0]), app.treeview.item(child, 'values')[8]) for child in app.treeview.get_children()]
            insert_index = bisect.bisect_left(session_ids_tails, (int(session_info["Session"]), session_info["Tail"]))
            app.treeview.insert('', insert_index, values=(session_info["Session"], session_info["User"], session_info["Hostname"], session_info["IP Address"], session_info["Process"], session_info["PID"], session_info["Arch"], session_info["Listener"], session_info["Tail"]), tags=('enabled',))

        app.update()

    def disable_session(app, session_title):
        from modules.controller import retry_session
        app.treeview.tag_configure("disabled", foreground="gray") 
        for session in app.sessions:
            try:
                if session.title == session_title:
                    session_id = session_title
                    
                session_number = str(session_id.split()[1])
                for item in app.treeview.get_children():
                    item_info = app.treeview.item(item)
                    values = item_info['values']

                    if str(values[0]) == str(session_number):
                        app.treeview.item(item, tags=('disabled',))
                        break
                
                app.update()
                retry_session(app, session_title)

            except:
                pass

    def enable_session(app, session_title):
        app.treeview.tag_configure("enabled", foreground="#FFFFFF") 
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

                app.update()

            except:
                pass

    def add_new_session(app, title, session_id, session_info, session_data):
        for session in app.sessions:
            if session.title == title:
                app.sessions.remove(session)
                break

        session_data = app.saved_sessions[title]  
        commands = Session.load_commands_from_session(session_id)
        new_session = Session(title, session_data, commands)
        new_session.reload_command_session()
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
                app.notebook.insert(insert_index, new_session, text=title)

                if previously_selected:
                    for tab in app.notebook.tabs():
                        tab_title = app.notebook.tab(tab, "text")
                        if tab_title == title:
                            app.notebook.select(tab)
                            break

                app.update()
