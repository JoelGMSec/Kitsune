#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#    https://darkbyte.net #
#=========================#

import os
import json
import tkinter as tk
from tkinter import ttk
from modules import controller
from modules.controller import reload_listener

def load_listeners(app):
    try:
        with open('data/listeners.json', 'r') as file:
            app.listeners = json.load(file)

    except:
        if not os.path.exists('data/listeners.json'):
            with open('data/listeners.json', 'w') as file:
                json.dump([], file, indent=4)

    return app.listeners

def add_listeners(app, listener_window, name, host, port, protocol, tail):
    from modules.session import Session

    with open('data/listeners.json', 'r') as file:
        listeners = json.load(file)

    listeners.append({"Name": name, "Host": host, "Port": port, "Protocol": protocol, "Tail": tail, "State":"enabled"})

    with open('data/listeners.json', 'w') as file:
        json.dump(listeners, file, indent=4)

    if app.listener_table.winfo_exists():
        app.listener_table.insert('', 'end', values=(name, host, port, protocol, tail))

    session = Session.load_sessions()
    app.listeners = listeners
    controller.new_listener(app, session, reload_listeners=False)

    listener_window.destroy()

def on_combobox_focus(event):
    event.widget.selection_clear()

def listener_window(app):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x475")
    listener_window.title("New Listener")
    listener_window.focus_force()

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    name_label = ttk.Label(listener_window, text="Name")
    name_label.grid(row=1, column=0, padx=0, pady=15)

    name_entry = ttk.Entry(listener_window)
    name_entry.grid(row=1, column=1, padx=0, pady=15)

    host_label = ttk.Label(listener_window, text="Host")
    host_label.grid(row=2, column=0, padx=0, pady=15)

    host_entry = ttk.Entry(listener_window)
    host_entry.grid(row=2, column=1, padx=0, pady=15)

    port_label = ttk.Label(listener_window, text="Port")
    port_label.grid(row=3, column=0, padx=0, pady=15)

    port_entry = ttk.Entry(listener_window)
    port_entry.grid(row=3, column=1, padx=0, pady=15)

    tail_label = ttk.Label(listener_window, text="Tail")
    tail_label.grid(row=4, column=0, padx=0, pady=15)

    tail_combo = ttk.Combobox(listener_window, values=["HTTP-Shell", "DnsCat2", "PwnCat-CS", "Villain"], state="readonly")
    tail_combo.grid(row=4, column=1, padx=0, pady=15)

    tail_combo.bind("<FocusIn>", on_combobox_focus)

    proto_label = ttk.Label(listener_window, text="Protocol")
    proto_label.grid(row=5, column=0, padx=0, pady=15)

    proto_combo = ttk.Combobox(listener_window, values=[""], state="disable")
    proto_combo.grid(row=5, column=1, padx=0, pady=15)

    proto_combo.bind("<FocusIn>", on_combobox_focus)

    def set_tail(event):
        selected_tail = tail_combo.get()
        if selected_tail == "HTTP-Shell":
            proto_combo.set("HTTP/S")
            proto_combo['state'] = 'disabled'
        elif selected_tail == "DnsCat2":
            proto_combo.set("DNS")
            proto_combo['state'] = 'disabled'
        elif selected_tail == "PwnCat-CS":
            proto_combo.set("TCP")
            proto_combo['state'] = 'disabled'
        elif selected_tail == "Villain":
            proto_combo.set("TCP")
            proto_combo['state'] = 'disabled'
        else:
            proto_combo.set("")
            proto_combo['state'] = 'readonly'

    tail_combo.bind("<<ComboboxSelected>>", set_tail)

    save_button = ttk.Button(listener_window, text="Save", command=lambda: add_listeners(app, listener_window, name_entry.get(), host_entry.get(), port_entry.get(), proto_combo.get(), tail_combo.get()))
    save_button.grid(row=6, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(listener_window, text="Cancel", command=listener_window.destroy)
    cancel_button.grid(row=6, column=1, padx=20, pady=20)

def show_listeners(app):
    for tab in app.notebook.tabs():
        if app.notebook.tab(tab, "text") == "Listeners":
            app.notebook.select(tab)
            return

    style = ttk.Style()
    style.configure('Background.TFrame', background='#333333')

    listener_tab = ttk.Frame(app.notebook, style='Background.TFrame')
    listener_tab.pack(fill="both", expand=True)

    app.listener_table_label = ttk.Frame(app.paned)
    app.listener_table_label = ttk.Label(listener_tab, text="Listeners")

    app.listener_table = ttk.Treeview(listener_tab, columns=("name", "host", "port", "proto", "tail", "blank"), padding=(-4, -4, -4, 0))
    app.listener_table.heading("#0", text="", anchor="w")
    app.listener_table.heading("name", text="Name", anchor="center")
    app.listener_table.heading("host", text="Host", anchor="center")
    app.listener_table.heading("port", text="Port", anchor="center")
    app.listener_table.heading("proto", text="Protocol", anchor="center")
    app.listener_table.heading("tail", text="Tail", anchor="center")
    app.listener_table.heading("blank", text="", anchor="e")
    app.listener_table.column("#0", width=-150, anchor="w")
    app.listener_table.column("name", width=100, anchor="center")
    app.listener_table.column("host", width=90, anchor="center")
    app.listener_table.column("port", width=90, anchor="center")
    app.listener_table.column("proto", width=90, anchor="center")
    app.listener_table.column("tail", width=120, anchor="center")
    app.listener_table.column("blank", width=-150, anchor="e")
    app.listener_table_label.configure(padding=-20)
    app.listener_table.pack(fill="both", expand=True)

    app.listener_table.bind("<Double-1>", lambda event: app.on_double_click())

    style.configure('Background.TFrame', background='#333333')
    bottom_frame = ttk.Frame(listener_tab, style='Background.TFrame')
    bottom_frame.pack(side="bottom", fill="both", padx=10, pady=10)
    bottom_frame.place(relx=0.5, rely=0.5, anchor="center")

    def edit_listener():
        selected_item = app.listener_table.selection()
        if selected_item:
            app.confirm_remove("Edit")

    def enable_listener():
        selected_item = app.listener_table.selection()
        if selected_item:
            app.confirm_remove("Enable")

    def disable_listener():
        selected_item = app.listener_table.selection()
        if selected_item:
            app.confirm_remove("Disable")

    def remove_listener():
        selected_item = app.listener_table.selection()
        if selected_item:
            app.confirm_remove("Remove")

    new_listener_button = ttk.Button(bottom_frame, text="Add", command=lambda: listener_window(app))
    new_listener_button.pack(side="left", padx=5, pady=5)

    edit_listener_button = ttk.Button(bottom_frame, text="Edit", command=edit_listener)
    edit_listener_button.pack(side="left", padx=5, pady=5)

    enable_listener_button = ttk.Button(bottom_frame, text="Enable", command=enable_listener)
    enable_listener_button.pack(side="left", padx=5, pady=5)

    remove_listener_button = ttk.Button(bottom_frame, text="Disable", command=disable_listener)
    remove_listener_button.pack(side="left", padx=5, pady=5)

    restart_listener_button = ttk.Button(bottom_frame, text="Remove", command=remove_listener)
    restart_listener_button.pack(side="left", padx=5, pady=5)

    bottom_frame.pack_configure(anchor="center")

    listener_tab.columnconfigure(0, weight=1)
    listener_tab.rowconfigure(1, weight=1)
    existing_tabs = app.notebook.tabs()
    app.listener_table.delete(*app.listener_table.get_children())
    listeners = load_listeners(app)

    if app.listener_table.winfo_exists():
        for listener in listeners:
            name = listener["Name"]
            host = listener["Host"]
            port = listener["Port"]
            protocol = listener["Protocol"]
            tail = listener["Tail"]
            state = listener.get("State", "enabled")  

            item_id = app.listener_table.insert('', 'end', values=(name, host, port, protocol, tail))
            app.listener_table.item(item_id, tags=(listener["State"],))

        app.listener_table.tag_configure("enabled", foreground="#FFFFFF")
        app.listener_table.tag_configure("disabled", foreground="gray")

    def on_treeview_click(event):
        item = app.listener_table.identify('item', event.x, event.y)
        if not item:  
            app.listener_table.selection_remove(app.listener_table.selection())

    app.listener_table.bind("<Button-1>", on_treeview_click, add='+')  
    app.listener_table.bind("<Button-3>", app.remove_listener)

    if len(existing_tabs) > 2:
        tab_texts = [app.notebook.tab(tab, "text") for tab in existing_tabs]

        tab_texts.append("Listeners")
        sorted_tabs = sorted(tab_texts)
        insert_index = sorted_tabs.index("Listeners")

        app.notebook.insert(insert_index + 1, listener_tab, text="Listeners")
        app.notebook.select(listener_tab)

    else:
        app.notebook.add(listener_tab, text="Listeners")
        app.notebook.select(listener_tab)

def edit_listener(app, listener_details):
    listener_window = tk.Toplevel(app)
    listener_window.geometry("570x475")
    listener_window.title("Edit Listener")
    listener_window.focus_force()

    white_label = ttk.Label(listener_window, text="")
    white_label.grid(row=0, column=0, padx=0, pady=0)

    name_label = ttk.Label(listener_window, text="Name")
    name_label.grid(row=1, column=0, padx=0, pady=15)
    name_entry = ttk.Entry(listener_window)
    name_entry.grid(row=1, column=1, padx=0, pady=15)
    name_entry.insert(0, listener_details[0])  

    host_label = ttk.Label(listener_window, text="Host")
    host_label.grid(row=2, column=0, padx=0, pady=15)
    host_entry = ttk.Entry(listener_window)
    host_entry.grid(row=2, column=1, padx=0, pady=15)
    host_entry.insert(0, listener_details[1])  

    port_label = ttk.Label(listener_window, text="Port")
    port_label.grid(row=3, column=0, padx=0, pady=15)
    port_entry = ttk.Entry(listener_window)
    port_entry.grid(row=3, column=1, padx=0, pady=15)
    port_entry.insert(0, listener_details[2])  

    tail_label = ttk.Label(listener_window, text="Tail")
    tail_label.grid(row=4, column=0, padx=0, pady=15)
    tail_combo = ttk.Combobox(listener_window, values=["HTTP-Shell", "DnsCat2", "PwnCat-CS", "Villain"], state="readonly")
    tail_combo.grid(row=4, column=1, padx=0, pady=15)
    tail_combo.set(listener_details[4])  

    tail_combo.bind("<FocusIn>", on_combobox_focus)

    proto_label = ttk.Label(listener_window, text="Protocol")
    proto_label.grid(row=5, column=0, padx=0, pady=15)
    proto_combo = ttk.Combobox(listener_window, values=[""], state="disabled")
    proto_combo.grid(row=5, column=1, padx=0, pady=15)
    proto_combo.set(listener_details[3])  

    proto_combo.bind("<FocusIn>", on_combobox_focus)

    def set_tail(event):
        selected_tail = tail_combo.get()
        if selected_tail == "HTTP-Shell":
            proto_combo.set("HTTP/S")
            proto_combo['state'] = 'disabled'
        elif selected_tail == "DnsCat2":
            proto_combo.set("DNS")
            proto_combo['state'] = 'disabled'
        elif selected_tail == "PwnCat-CS":
            proto_combo.set("TCP")
            proto_combo['state'] = 'disabled'
        elif selected_tail == "Villain":
            proto_combo.set("TCP")
            proto_combo['state'] = 'disabled'
        else:
            proto_combo.set("")
            proto_combo['state'] = 'readonly'

    tail_combo.bind("<<ComboboxSelected>>", set_tail)

    save_button = ttk.Button(listener_window, text="Save", command=lambda: update_listener(app, listener_window, listener_details, name_entry.get(), host_entry.get(), port_entry.get(), proto_combo.get(), tail_combo.get()))
    save_button.grid(row=6, column=0, padx=50, pady=20)

    cancel_button = ttk.Button(listener_window, text="Cancel", command=listener_window.destroy)
    cancel_button.grid(row=6, column=1, padx=20, pady=20)

def update_listener(app, listener_window, old_details, name, host, port, protocol, tail):
    new_details = (name, host, port, protocol, tail)
    if old_details == new_details:
        listener_window.destroy()
        return

    with open('data/listeners.json', 'r') as file:
        listeners = json.load(file)

    for listener in listeners:
        if listener["Name"] == old_details[0]:  
            listener["Name"] = name
            listener["Host"] = host
            listener["Port"] = port
            listener["Protocol"] = protocol
            listener["Tail"] = tail
            break

    with open('data/listeners.json', 'w') as file:
        json.dump(listeners, file, indent=4)

    listener_window.destroy()

    try:
        selected = app.listener_table.selection()
        selected_id = None
        if selected:
            selected_details = app.listener_table.item(selected, "values")
            selected_id = selected_details[0]  

        listener_states = {}
        for item in app.listener_table.get_children():
            item_details = app.listener_table.item(item, "values")
            item_state = app.listener_table.item(item, "tags")
            listener_states[item_details[0]] = item_state[0]  

        for item in app.listener_table.get_children():
            app.listener_table.delete(item)
        
        for listener in load_listeners(app):
            item_id = app.listener_table.insert('', 'end', values=(listener["Name"], listener["Host"], listener["Port"], listener["Protocol"], listener["Tail"]))
            
            if listener["Name"] in listener_states and listener_states[listener["Name"]] == "disabled":
                listener_state = "disabled"
                app.listener_table.item(item_id, tags=('disabled',))
            else:
                app.listener_table.item(item_id, tags=('enabled',))
                if listener["Name"] == new_details[0]:
                    listener_state = "enabled"
                    controller.kill_listeners(app, old_details)
                    reload_listener(app, app.session_id, new_details, reload_listeners=True)

        app.listener_table.tag_configure("enabled", foreground="#FFFFFF")  
        app.listener_table.tag_configure("disabled", foreground="gray")
        
        if selected_id:
            for item in app.listener_table.get_children():
                item_details = app.listener_table.item(item, "values")
                if item_details[0] == selected_id:  
                    app.listener_table.selection_set(item)
                    break

        for listener in listeners:
            if listener["Name"] == old_details[0]:  
                listener["Name"] = name
                listener["Host"] = host
                listener["Port"] = port
                listener["Protocol"] = protocol
                listener["Tail"] = tail
                listener["State"] = listener_state
                break

        with open('data/listeners.json', 'w') as file:
            json.dump(listeners, file, indent=4)

    except:
        pass
