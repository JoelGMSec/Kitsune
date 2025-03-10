#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import sys
import json
import time
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk
from neotermcolor import colored
from modules.session import Session
from modules.chat import TeamChatTab
from modules import about, delivery, payloads, reporter
from modules import command, tails, custom, proxy, listeners
from modules import updater, profile, modules, nekomancer

def typing(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.02)

class ResizablePanedWindow(tk.PanedWindow):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._drag_data = {"y": 0, "index": None}
        self.bind("<B1-Motion>", self.on_separator_drag)

    def on_separator_drag(self, event):
        if self._drag_data["index"] is not None:
            new_height = event.y
            self.paneconfigure(self._drag_data["index"], height=new_height)

class DraggableTabsNotebook(ttk.Notebook):
    def __init__(self, master=None, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self._drag_data = {"x": 0, "y": 0, "index": None}
        self.protected_tabs = ["Event Viewer", "Team Chat"]
        self.context_menu = None
        self.enable_traversal()

        self.bind("<Button-3>", self.show_tab_menu)
        self.bind("<ButtonPress-1>", self.on_tab_press)
        self.bind("<B1-Motion>", self.on_tab_drag)
        self.bind("<ButtonRelease-1>", self.on_tab_release)
        self.bind('<Escape>', self.close_current_tab)
        self.bind('<Up>', self.move_treeview_up)
        self.bind('<Down>', self.move_treeview_down)
        self.bind('<Return>', app.on_treeview_doubleclick)

    def get_treeview(self):
        item = self.app.treeview.selection()
        if item:
            items = self.app.treeview.get_children()
            try:
                index = items.index(item[0])
                return index, items
            except ValueError:
                return -1, items
        return -1, []

    def move_treeview_up(self, event):
        try:
            index, items = self.get_treeview()
            if index > 0 and items:
                previous_index = index - 1
                previous_item = items[previous_index]
                self.app.treeview.selection_set(previous_item)
                self.app.treeview.focus(previous_item)
        except:
            pass

    def move_treeview_down(self, event):
        try:
            index, items = self.get_treeview()
            previous_index = index + 1
            previous_item = items[previous_index]
            self.app.treeview.selection_set(previous_item)
            self.app.treeview.focus(previous_item)
        except:
            pass

    def on_tab_press(self, event):
        try:
            clicked_tab_index = self.index("@%d,%d" % (event.x, event.y))
            clicked_tab_text = self.tab(clicked_tab_index, "text")
            self.tab(clicked_tab_index, state="normal")

            if clicked_tab_text in self.protected_tabs:
                return

            self._drag_data["index"] = clicked_tab_index
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
        except Exception:
            return

        if self.context_menu:
            self.context_menu.unpost()

    def on_tab_drag(self, event):
        time.sleep(0.4)
        if self._drag_data["index"] is None:
            return

        try:
            target_tab_index = self.index("@%d,%d" % (event.x, event.y))
            target_tab_text = self.tab(target_tab_index, "text")

            if target_tab_text in self.protected_tabs:
                return

            dragged_tab_text = self.tab(self._drag_data["index"], "text")
            if dragged_tab_text in self.protected_tabs:
                return

            self.insert(target_tab_index, self._drag_data["index"])
        except Exception:
            return

    def on_tab_release(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["index"] = None

    def show_tab_menu(self, event):
        tab = self.tk.call(self._w, "identify", "tab", event.x, event.y)
        if tab:
            tab_text = self.tab(tab, "text")
            if tab_text in self.protected_tabs:
                return

            self.context_menu_tab = tab
            self.select(tab)

            if not self.context_menu:
                self.context_menu = tk.Menu(self, tearoff=0)
                self.context_menu.add_command(label="Close", command=self.close_tab)
            self.context_menu.post(event.x_root, event.y_root)

    def close_tab(self):
        current_tab = self.context_menu_tab
        if current_tab:
            tab_text = self.tab(current_tab, "text")
            if tab_text not in self.protected_tabs:
                self.forget(current_tab)

    def close_current_tab(self, event):
        current_tab = self.select()
        if current_tab:
            current_tab_name = self.tab(current_tab, 'text')
            if current_tab_name not in self.protected_tabs:
                self.forget(current_tab)

def setup_widgets(root, app):
    menu_bar = tk.Menu(root, bd=0, relief="flat", tearoff=0)
    root.config(menu=menu_bar)
    home_menu = tk.Menu(menu_bar)
    
    settings_menu = tk.Menu(home_menu, tearoff=0)
    settings_menu.add_command(label="Nekomancer", command=lambda: nekomancer.open_settings(app))
    home_menu.add_cascade(label="Settings", menu=settings_menu)
    
    theme_submenu = tk.Menu(home_menu, tearoff=0)
    theme_var = app.theme_var.get()

    theme_submenu.add_radiobutton(label="Blue", variable=theme_var, value="Blue", command=lambda: app.change_theme("Blue"), selectcolor="white")
    theme_submenu.add_radiobutton(label="Green", variable=theme_var, value="Green", command=lambda: app.change_theme("Green"), selectcolor="white")
    theme_submenu.add_radiobutton(label="Purple", variable=theme_var, value="Purple", command=lambda: app.change_theme("Purple"), selectcolor="white")
    theme_submenu.add_radiobutton(label="Red", variable=theme_var, value="Red", command=lambda: app.change_theme("Red"), selectcolor="white")

    home_menu.add_cascade(label="Change Theme", menu=theme_submenu)
    home_menu.add_command(label="Proxification", command=lambda: proxy.set_proxy(app))
    home_menu.add_command(label="Update Tails", command=lambda: tails.update_tails(app))
    home_menu.add_command(label="Exit", command=app.confirm_and_quit)
    menu_bar.add_cascade(label=" Kitsune ", menu=home_menu)
    
    if app.theme_var.get() == "Blue":
        theme_submenu.invoke(0)
    if app.theme_var.get() == "Green":
        theme_submenu.invoke(1)
    if app.theme_var.get() == "Purple":
        theme_submenu.invoke(2)
    if app.theme_var.get() == "Red":
        theme_submenu.invoke(3)
    
    view_menu = tk.Menu(menu_bar, tearoff=0)
    view_menu.add_command(label="Event Viewer", command=app.restore_event_viewer)
    view_menu.add_command(label="Listeners", command=lambda: listeners.show_listeners(app))
    view_menu.add_command(label="Multi Server Log", command=lambda: delivery.open_multiserver_log_tab(app))
    view_menu.add_command(label="Team Chat", command=app.restore_team_chat)
    view_menu.add_command(label="Web Server Log", command=lambda: delivery.open_webserver_log_tab(app))
    menu_bar.add_cascade(label=" View ", menu=view_menu)
    
    payloads_menu = tk.Menu(menu_bar, tearoff=0)
    payloads_menu.add_command(label="Linux Bind Shell", command=lambda: payloads.pwncat_payload(app))
    payloads_menu.add_command(label="Linux Reverse Shell", command=lambda: payloads.linux_payload(app))
    payloads_menu.add_command(label="Web Shell (Bind)", command=lambda: payloads.webshell_payload(app))
    payloads_menu.add_command(label="Web Shell (Generate)", command=lambda: payloads.webshell_generate(app))
    payloads_menu.add_command(label="Windows Bind Shell", command=lambda: payloads.netexec_payload(app))
    payloads_menu.add_command(label="Windows Reverse Shell", command=lambda: payloads.windows_payload(app))
    menu_bar.add_cascade(label=" Payloads ", menu=payloads_menu)
    
    modules_menu = tk.Menu(menu_bar, tearoff=0)
    modules_menu.add_command(label="Module Console", command=lambda: custom.show_current_modules(app, False))
    modules_menu.add_command(label="Reload Modules", command=lambda: custom.show_current_modules(app, True))
    modules_menu.add_command(label="Update Modules", command=lambda: modules.update_modules(app))
    menu_bar.add_cascade(label=" Modules ", menu=modules_menu)
    
    attacks_menu = tk.Menu(menu_bar, tearoff=0)
    attacks_menu.add_command(label="Multi Server Delivery", command=lambda: delivery.multi_delivery(app))
    attacks_menu.add_command(label="Scripted Web Delivery", command=lambda: delivery.web_delivery(app))
    attacks_menu.add_command(label="Stop Multi Server", command=lambda: delivery.kill_multiserver(app))
    attacks_menu.add_command(label="Stop Web Server", command=lambda: delivery.kill_webserver(app))
    menu_bar.add_cascade(label=" Delivery ", menu=attacks_menu)
    
    profile_menu = tk.Menu(menu_bar, tearoff=0)
    profile_menu.add_command(label="Load Profile", command=lambda: profile.import_profile(app))
    profile_menu.add_command(label="Save Profile", command=lambda: profile.export_profile(app))
    profile_menu.add_command(label="Delete Profiles", command=lambda: profile.delete_profile(app))
    menu_bar.add_cascade(label=" Profile ", menu=profile_menu)
    
    reporting_menu = tk.Menu(menu_bar, tearoff=0)
    reporting_menu.add_command(label="Clear Logs", command=lambda: reporter.clear_logs(app))
    reporting_menu.add_command(label="Export Logs", command=lambda: reporter.export_logs(app))
    reporting_menu.add_command(label="Reset Data", command=app.confirm_and_clear)
    menu_bar.add_cascade(label="Reporting", menu=reporting_menu)
    
    Help_menu = tk.Menu(menu_bar, tearoff=0)
    Help_menu.add_command(label="About", command=lambda: about.about_window(app))
    Help_menu.add_command(label="Updates", command=lambda: updater.check_updates(app))
    Help_menu.add_command(label="Wiki", command=lambda: webbrowser.open_new("https://github.com/JoelGMSec/Kitsune"))
    menu_bar.add_cascade(label=" Help ", menu=Help_menu)
    
    app.paned = ttk.PanedWindow(app)
    app.paned.grid(row=0, column=0, columnspan=2, sticky="nsew")

    app.pane_1 = ttk.Frame(app.paned, padding=10)
    app.paned.add(app.pane_1, weight=1)

    style = ttk.Style()
    style.configure("Disabled.Treeview", foreground="#868686")
    style.map(
        "TCombobox",
        cursor=[
            ("invalid", "arrow"),
            ("readonly", "arrow"),
            ("disabled", "arrow"),
        ]
    )

    app.treeview = ttk.Treeview(
        app.pane_1,
        style="Disabled.Treeview",
        selectmode="browse",
        columns=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
        height=10,
        padding=(-4, -4, -4, 0),
    )
    app.treeview.dragging = False
    app.treeview.selected_item = None

    def focus_entry(event):
            app.entry.focus_set()
            return 'break'

    def on_treeview_click(event):
        item = app.treeview.identify('item', event.x, event.y)
        app.treeview.selected_item = item
        if not item:  
            app.treeview.selection_remove(app.treeview.selection())

    def on_drag_start(event):
        item = app.treeview.identify('item', event.x, event.y)
        if item:
            app.treeview.dragging = True

    def on_drag_stop(event):
        if app.treeview.dragging:
            item = app.treeview.identify('item', event.x, event.y)
            if item:
                app.treeview.dragging = False

    def on_drag_motion(event):
        if app.treeview.dragging:
            item = app.treeview.identify('item', event.x, event.y)
            moving_item = app.treeview.selection()[0] if app.treeview.selection() else None
            if item and moving_item and item != moving_item:
                item_index = app.treeview.index(item)
                app.treeview.move(moving_item, '', item_index)

    def on_up(app, event):
        current_tab = app.notebook.tab(app.notebook.select(), "text")
        if current_tab in ["Event Viewer", "Listeners", "Team Chat"]:
            return 

        if app.command_history:
            app.history_index = max(0, app.history_index - 1)
            app.entry.delete(0, tk.END)
            app.entry.insert(tk.END, app.command_history[app.history_index])

    def on_down(app, event):
        current_tab = app.notebook.tab(app.notebook.select(), "text")
        if current_tab in ["Event Viewer", "Listeners", "Team Chat"]:
            return 

        if app.command_history:
            app.history_index = min(len(app.command_history), app.history_index + 1)
            app.entry.delete(0, tk.END)
            if app.history_index != len(app.command_history):  
                app.entry.insert(tk.END, app.command_history[app.history_index])

    def on_ctrl_l(app, event):
        app.clear_command = True
        command.execute_command(app, event)

    def on_ctrl_c(app, event):
        app.entry.delete(0, tk.END)

    def close_current_tab_from_entry(event):
        app.notebook.close_current_tab(event)

    def switch_tab(event):
        key = event.keysym
        current_tab = app.notebook.select()
        tabs = app.notebook.tabs()
        current_index = tabs.index(current_tab)
        
        if key == 'Left':
            for _ in range(len(tabs)):
                current_index = (current_index - 1) if current_index > 0 else len(tabs) - 1
                if app.notebook.tab(tabs[current_index], "state") != "disabled":
                    app.notebook.select(tabs[current_index])
                    break
        
        elif key == 'Right':
            for _ in range(len(tabs)):
                current_index = (current_index + 1) if current_index < len(tabs) - 1 else 0
                if app.notebook.tab(tabs[current_index], "state") != "disabled":
                    app.notebook.select(tabs[current_index])
                    break

    try:
        sessions_data = Session.load_sessions(app)

        if sessions_data:
            for session in sessions_data:
                app.treeview.insert('', 'end', tags=['disabled'] ,values=(session["Session"], session["User"], session["Hostname"], session["IP Address"], session["Process"], session["PID"], session["Arch"], session["Listener"], session["Tail"]))

    except:
        pass

    app.treeview.column("#0", anchor="center", width=-100)
    app.treeview.column(1, anchor="center", width=80)
    app.treeview.column(2, anchor="center", width=140)
    app.treeview.column(3, anchor="center", width=180)
    app.treeview.column(4, anchor="center", width=140)
    app.treeview.column(5, anchor="center", width=140)
    app.treeview.column(6, anchor="center", width=50)
    app.treeview.column(7, anchor="center", width=50)
    app.treeview.column(8, anchor="center", width=50)
    app.treeview.column(9, anchor="center", width=100)
    app.treeview.column(10, anchor="center", width=-50)

    app.treeview.heading("#0", text="", anchor="w")
    app.treeview.heading(1, text="Session", anchor="center")
    app.treeview.heading(2, text="User", anchor="center")
    app.treeview.heading(3, text="Computer", anchor="center")
    app.treeview.heading(4, text="IP Address", anchor="center")
    app.treeview.heading(5, text="Process", anchor="center")
    app.treeview.heading(6, text="PID", anchor="center")
    app.treeview.heading(7, text="Arch", anchor="center")
    app.treeview.heading(8, text="Connection", anchor="center")
    app.treeview.heading(9, text="Tail", anchor="center")
    app.treeview.heading(10, text="", anchor="e")

    app.treeview.tag_configure("disabled", foreground="#868686")
    app.treeview.tag_configure("disabled_selected", foreground="#333333")

    def update_selection(event):
        selected_items = app.treeview.selection()
        for item in app.treeview.get_children():
            item_info = app.treeview.item(item)
            tags = item_info['tags']
            if "disabled" in tags or "disabled_selected" in tags:
                if item in selected_items:
                    app.treeview.item(item, tags=("disabled_selected",))
                else:
                    app.treeview.item(item, tags=("disabled",))
                
    app.treeview.bind("<<TreeviewSelect>>", update_selection)
    app.treeview.bind("<Button-3>", app.remove_item)
    app.treeview.bind("<Double-1>", app.on_treeview_doubleclick)
    app.treeview.bind("<Button-1>", on_drag_start, add='+')
    app.treeview.bind("<ButtonRelease-1>", on_drag_stop, add='+')
    app.treeview.bind("<B1-Motion>", on_drag_motion, add='+')
    app.treeview.bind("<Button-1>", on_treeview_click, add='+')  
    app.treeview.bind('<Return>', app.on_treeview_doubleclick)
    app.treeview.bind('<Escape>', close_current_tab_from_entry)
    app.treeview.bind('<Delete>', app.on_treeview_delete)
    app.treeview.bind('<Tab>', focus_entry)
    app.treeview.bind("<Left>", switch_tab)
    app.treeview.bind("<Right>", switch_tab)

    app.pane_2 = ttk.Frame(app.paned, padding=10)
    app.paned.add(app.pane_2, weight=1)

    separator_paned = ResizablePanedWindow(app.pane_2, orient=tk.VERTICAL)
    separator_label = tk.Label(separator_paned, text="•••••", font=("Consolas", 20), foreground="#c0c0c0", cursor="sb_v_double_arrow")
    separator_paned.add(separator_label)
    separator_paned.pack(pady=(0, 20))

    app.notebook = DraggableTabsNotebook(app.pane_2, height=580, app=app)
    app.tab_1 = tk.Frame(app.notebook, background="#333333")
    app.tab_1.pack(fill="both", expand=True)

    for index in [0, 1]:
        app.tab_1.columnconfigure(index=index, weight=1)
        app.tab_1.rowconfigure(index=index, weight=1)

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    try:
        current_user = os.getlogin()
    except:
        current_user = "root"

    style = ttk.Style()
    style.configure('custom.Vertical.TScrollbar', width=15)
    app.scrollbar = ttk.Scrollbar(app.tab_1, style='custom.Vertical.TScrollbar')
    app.scrollbar.pack(side="right", fill="y")

    app.text = tk.Text(
        app.tab_1,
        background="#333333",
        foreground="#FF00FF",
        padx=5,
        pady=5,
        wrap="word",
        state="disabled",
        highlightthickness=0,
        borderwidth=0,
        selectbackground="#1B1B1B",
        inactiveselectbackground="#1B1B1B",
        yscrollcommand=app.scrollbar.set,
        cursor="arrow"
    )

    if not app.fast_mode:
        typing(colored(f"[*] User <{current_user}> has joined the party!\n", "magenta"))
    
    label_text = f"[{current_time}] User <{current_user}> has joined the party!"
    app.text.config(font=("Consolas", 18, "bold"))
    app.text.config(state="normal")
    app.text.insert("end", label_text + "\n")
    app.text.config(state="disabled")
    app.add_event_viewer_log(label_text + "\n", 'color_login', "#FF00FF")
    app.scrollbar.config(command=app.text.yview)

    app.context_menu = tk.Menu(app.text, tearoff=0)
    app.context_menu.add_command(label="Copy", command=app.copy_text)
    app.context_menu.add_command(label="Clear", command=app.clear_text)
    app.text.bind("<Button-3>", app.show_context_menu)
    app.text.bind("<Control-c>", app.copy_text)
    app.text.bind("<Control-a>", app.select_all_text)

    existing_tabs = app.notebook.tabs()
    if existing_tabs:
        tab_texts = [app.notebook.tab(tab, "text") for tab in existing_tabs]
        tab_texts.append("Event Viewer")
        sorted_tabs = sorted(tab_texts)
        insert_index = sorted_tabs.index("Event Viewer")
        app.notebook.insert(existing_tabs[insert_index - 1], app.tab_1, text="Event Viewer")
    else:
        app.notebook.add(app.tab_1, text="Event Viewer")

    class AutoCompleteEntry(ttk.Entry):
        def __init__(self, master, history, notebook, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.matches = []
            self.notebook = notebook
            self.command_history = history
            self.password_mode = False
            self.real_text = ""

            self.bind("<KeyRelease>", self.on_key_release)
            self.bind("<Right>", self.on_right_arrow_press)
            self.bind("<Return>", self.on_return_press)
            self.bind("<Control-p>", self.toggle_password_mode)

            self.insert(tk.END, "Insert command here..")
            self.icursor(tk.END)

        def toggle_password_mode(self, event):
            self.password_mode = not self.password_mode
            if self.password_mode:
                self.config(show="*")
            else:
                self.config(show="")
            self.update_displayed_text()

        def update_displayed_text(self):
            if self.password_mode:
                self.insert(0, "*" * len(self.real_text))
            else:
                self.insert(0, self.real_text)
            self.icursor(len(self.real_text))
            self.icursor(tk.END)
            return

        def on_key_release(self, event):
            text = self.get()
            prefix = text.strip()
            current_index = self.index(tk.INSERT)

            if self.current_tab_is_excluded():
                return

            elif event.keysym in ["Return", "space", "Right", "BackSpace", "Left", "Up", "Down", "Tab", "Escape", "Control", "Home", "Delete"]:
                self.matches = None
                return

            else:
                if prefix:
                    self.icursor(current_index)
                    self.matches = [cmd for cmd in self.command_history if cmd.startswith(prefix)]
                    if self.matches:
                        self.show_match()
                        self.icursor(current_index)
                        return
                else:
                    self.icursor(current_index)
                    self.matches = []
                    return

        def show_match(self):
            if self.matches and not self.password_mode:
                current_index = self.index(tk.INSERT)
                text = self.get()
                prefix = text[:current_index]
                match = self.matches[0]
                match_text = match[len(prefix):]
                if match_text:
                    self.icursor(current_index)
                    self.delete(current_index, tk.END)
                    self.insert(current_index, match_text)
                    self.icursor(current_index + len(match_text))
                    self.select_range(current_index, tk.END)

        def on_right_arrow_press(self, event):
            if self.current_tab_is_excluded():
                return

            elif self.matches:
                self.delete(0, tk.END)
                self.insert(tk.END, self.matches[0])
                self.icursor(tk.END)
                return

            else:
                current_index = self.index(tk.INSERT)
                self.icursor(current_index + 1)
                return

        def on_return_press(self, event):
            if self.matches:
                cursor_position = self.index(tk.INSERT)
                command_text = self.get()[:cursor_position]
                self.delete(cursor_position, tk.END)
                command.execute_command(app, event, self.password_mode)
                self.password_mode = False
                self.config(show="")
                return
            
            else:
                self.icursor(tk.END)
                command_text = self.get()
                command.execute_command(app, event, self.password_mode)
                self.password_mode = False
                self.config(show="")
                return

        def current_tab_is_excluded(self):
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            return current_tab in ["Event Viewer", "Team Chat", "Listeners", "Module Console", "Multi Server Log", "Web Server Log"]

    app.entry = AutoCompleteEntry(app.master, app.command_history, app.notebook)
    app.entry.config(foreground="#BABABA")
    app.entry.bind("<FocusIn>", app.on_entry_focus_in)
    app.entry.bind("<FocusOut>", app.on_entry_focus_out)
    app.entry.bind('<Up>', lambda event: on_up(app, event))
    app.entry.bind('<Down>', lambda event: on_down(app, event))
    app.entry.bind("<Control-c>", lambda event: on_ctrl_c(app, event))
    app.entry.bind("<Control-l>", lambda event: on_ctrl_l(app, event))
    app.entry.bind('<Escape>', close_current_tab_from_entry)

    app.entry.pack(fill="both", expand=True, side="bottom", padx=10, pady=(0, 10))
    app.treeview.pack(fill="both", expand=True)
    app.notebook.pack(fill="both", expand=True)
    app.text.pack(fill="both", expand=True)
    app.config(background="#444444") 
