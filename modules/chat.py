#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import json
import time
import errno
import select
import socket
import threading
import tkinter as tk
from tkinter import ttk

HEADER_LENGTH = 20
IP = "0.0.0.0"
PORT = 6667
CHAT_FILE = os.path.join("data", "chat.json")

if not os.path.exists("data"):
    os.makedirs("data")

if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as file:
        chat_history = json.load(file)
else:
    chat_history = {"logs": []}
    with open(CHAT_FILE, "w") as file:
        json.dump({"logs": []}, file)

user_colors = ["#00FF99", "#00AAFF", "#FFCC00", "#FF00FF"]
notification_color = "gray"
warning_color = "#FF0055"
user_color_map = {}

def save_message(log_entry):
    if log_entry["text"] in [log["text"] for log in chat_history["logs"]]:
        return
    
    chat_history["logs"].append(log_entry)
    with open(CHAT_FILE, "w") as file:
        json.dump(chat_history, file, indent=4)

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

def assign_color(username):
    if username not in user_color_map:
        color_index = len(user_color_map) % len(user_colors)
        user_color_map[username] = user_colors[color_index]
    return user_color_map[username]

def server_loop(app):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    sockets_list = [server_socket]
    clients = {}

    while True:
        time.sleep(1)
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if user is False:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                username = user['data'].decode('utf-8')
                color = assign_color(username)
                connection_message = f"*{username} has joined #Kitsune"
                log_entry = {
                    "text": connection_message,
                    "tag": "notification",
                    "color": notification_color
                }
                
                save_message(log_entry)
                app.team_chat_tab.display_message(connection_message, notification_color)
                message_header = f"{len(connection_message):<{HEADER_LENGTH}}".encode('utf-8')
                for client_socket in clients:
                    client_socket.send(user['header'] + user['data'] + message_header + connection_message.encode('utf-8'))
            else:
                message = receive_message(notified_socket)
                if message is False:
                    if notified_socket in clients:
                        username = clients[notified_socket]['data'].decode('utf-8')
                        disconnection_message = f"*{username} has left #Kitsune"
                        log_entry = {
                            "text": disconnection_message,
                            "tag": "notification",
                            "color": notification_color
                        }
                        save_message(log_entry)
                        app.team_chat_tab.display_message(disconnection_message, notification_color)
                        sockets_list.remove(notified_socket)
                        del clients[notified_socket]
                        message_header = f"{len(disconnection_message):<{HEADER_LENGTH}}".encode('utf-8')
                        for client_socket in clients:
                            client_socket.send(user['header'] + user['data'] + message_header + disconnection_message.encode('utf-8'))
                    continue

                user = clients.get(notified_socket)
                if user is None:
                    continue
                username = user['data'].decode('utf-8')
                message_text = message["data"].decode('utf-8')
                
                if message_text.startswith("/nick "):
                    new_username = message_text.split(" ", 1)[1]
                    if new_username:
                        old_username = username
                        user['data'] = new_username.encode('utf-8')
                        clients[notified_socket] = user
                        color = assign_color(new_username)
                        notification_message = f"*{old_username} is now {new_username}"
                        log_entry = {
                            "text": notification_message,
                            "tag": "notification",
                            "color": notification_color
                        }
                        save_message(log_entry)
                        app.team_chat_tab.display_message(notification_message, notification_color)
                        message_header = f"{len(notification_message):<{HEADER_LENGTH}}".encode('utf-8')
                        for client_socket in clients:
                            client_socket.send(user['header'] + user['data'] + message_header + notification_message.encode('utf-8'))
                    continue
                
                log_entry = {
                    "text": f"[{username}] > {message_text}",
                    "tag": "message",
                    "color": color
                }
                save_message(log_entry)
                app.notify_team_chat()
                app.team_chat_tab.display_message(log_entry["text"], log_entry["color"])
                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

def start_server(app):
    server_thread = threading.Thread(target=server_loop, args=(app,))
    server_thread.daemon = True
    server_thread.start()

class TeamChatTab():
    def __init__(app, notebook):
        app.last_displayed_message = {"text": "", "color": ""}
        app.notebook = notebook
        app.open_team_chat_tab()
        app.client_socket = None

    def notify_team_chat(app):
        for tab in app.notebook.tabs():
            current_tab = app.notebook.tab(app.notebook.select(), "text")   
            if current_tab != "Team Chat":
                for tab in app.notebook.tabs():
                    if app.notebook.tab(tab, "text") == "Team Chat":
                        app.notebook.tab(tab, state="disabled")
  
    def open_team_chat_tab(app):
        app.chat_tab = ttk.Frame(app.notebook)
        app.notebook.add(app.chat_tab, text="Team Chat")
        app.scrollbar = ttk.Scrollbar(app.chat_tab)
        app.scrollbar.pack(side="right", fill="y")

        app.text_area = tk.Text(
            app.chat_tab,
            wrap='word',
            state='disabled',
            yscrollcommand=app.scrollbar.set,
            background="#333333",
            foreground="#FF00FF",
            padx=5,
            pady=5,
            highlightthickness=0,
            borderwidth=0
        )
        app.text_area.pack(expand=True, fill='both')
        app.scrollbar.config(command=app.text_area.yview)
        app.load_chat_history()

        app.context_menu = tk.Menu(app.text_area, tearoff=0)
        app.context_menu.add_command(label="Copy", command=app.copy_chat_text)
        app.context_menu.add_command(label="Clear", command=app.clear_chat_text)
        app.text_area.bind("<Button-3>", app.show_context_menu)

    def copy_chat_text(app):
        try:
            selected_text = app.text_area.selection_get()
            app.text_area.clipboard_clear()
            app.text_area.clipboard_append(selected_text)
            app.text_area.tag_remove(tk.SEL, "1.0", tk.END)
        except:
            pass

    def clear_chat_text(app):
        app.text_area.config(state="normal")
        app.text_area.delete('1.0', tk.END)
        app.text_area.config(state="disabled")
        return
        
    def show_context_menu(app, event):
        app.context_menu.tk_popup(event.x_root, event.y_root)

    def clear_chat_logs(app):
        app.team_chat_tab.text_area.config(state="normal")
        app.team_chat_tab.text_area.delete('1.0', tk.END)
        app.team_chat_tab.text_area.config(state="disabled")
        app.entry.delete(0, tk.END)
        return

    def load_chat_history(app):
        app.text_area.config(state='normal')
        app.text_area.delete(1.0, tk.END)
        loaded_logs = set()
        with open(CHAT_FILE, "r") as file:
            chat_history = json.load(file)
            for log in chat_history["logs"]:
                if log["text"] not in loaded_logs:
                    app.display_message(log["text"], log["color"])
                    loaded_logs.add(log["text"])
        app.text_area.config(state='disabled')

    def display_message(app, message, color):
        try:
            current_content = app.text_area.get(1.0, tk.END)
            if message in current_content:
                return

            app.last_displayed_message = {"text": message, "color": color}
            app.text_area.config(font=("Consolas", 18, "bold"))
            app.text_area.config(state='normal')
            app.text_area.insert(tk.END, f"{message}\n", (color,))
            app.text_area.tag_config(color, foreground=color)
            app.text_area.config(state='disabled')
            app.text_area.see("end")
        except:
            pass

    def connect_to_server(app, username, new_ip=IP):
        try:
            app.username = username
            app.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            app.client_socket.connect((new_ip, PORT))
            app.client_socket.setblocking(False)
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            app.client_socket.send(username_header + username.encode('utf-8'))
            notification_message = f"*Connecting to #Kitsune on {new_ip}.."
            TeamChatTab.display_message(app, notification_message, notification_color)        
            log_entry = {
                "text": f"{notification_message}",
                "tag": "notification",
                "color": notification_color
            }
            save_message(log_entry)
            app.start_receiving_thread()
        except:
            pass

    def start_receiving_thread(app):
        receive_thread = threading.Thread(target=app.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

    def receive_messages(app):
        while True:
            time.sleep(1)
            try:
                username_header = app.client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    return
                username_length = int(username_header.decode('utf-8').strip())
                username = app.client_socket.recv(username_length).decode('utf-8')
                color = assign_color(username)
                message_header = app.client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = app.client_socket.recv(message_length).decode('utf-8')

                if message.startswith("*"):
                    log_entry = {
                        "text": f"{message}",
                        "tag": "notification",
                        "color": notification_color
                    }
                    save_message(log_entry) 
                    app.display_message(f"{message}", notification_color)

                else:
                    log_entry = {
                        "text": f"[{username}] > {message}",
                        "tag": "message",
                        "color": color
                    }
                    save_message(log_entry)
                    app.notify_team_chat()
                    app.display_message(log_entry["text"], log_entry["color"])

            except:
                pass

    def send_message(app, event):
        message = app.entry.get()
        if message:
            if message == "/help":
                notification_message = "   .:[ Kitsune Team Server Chat ]:.   "
                app.team_chat_tab.display_message(notification_message, "white")
                notification_message = "--------------------------------------"
                app.team_chat_tab.display_message(notification_message, "white")
                notification_message = "/clear: Clear this chat message window"
                app.team_chat_tab.display_message(notification_message, "white")
                notification_message = "/connect: Connect to Kitsune Team Chat"
                app.team_chat_tab.display_message(notification_message, "white")
                notification_message = "/help: Show Kitsune Team Chat commands"
                app.team_chat_tab.display_message(notification_message, "white")
                notification_message = "/nick: Change your nick to another one"
                app.team_chat_tab.display_message(notification_message, "white")
                notification_message = "--------------------------------------"
                app.team_chat_tab.display_message(notification_message, "white")
                app.entry.delete(0, tk.END)
                return

            elif message == "/clear":
                app.team_chat_tab.text_area.config(state="normal")
                app.team_chat_tab.text_area.delete('1.0', tk.END)
                app.team_chat_tab.text_area.config(state="disabled")
                app.entry.delete(0, tk.END)
                return

            elif message == "/nick":
                notification_message = "USAGE: /nick new_nick"
                app.team_chat_tab.display_message(notification_message, warning_color)
                app.entry.delete(0, tk.END)
                return

            elif message == "/connect":
                notification_message = "USAGE: /connect hostname"
                app.team_chat_tab.display_message(notification_message, warning_color)
                app.entry.delete(0, tk.END)
                return

            elif message.startswith("/connect "):
                new_ip = message.split(" ", 1)[1]
                if new_ip:
                    app.entry.delete(0, tk.END)
                    app.team_chat_tab.connect_to_server(app.username, new_ip)
                return

            elif message.startswith("/nick "):
                new_username = message.split(" ", 1)[1]
                if new_username:
                    old_username = app.username
                    app.username = new_username
                    app.entry.delete(0, tk.END)

                    change_nick_message = f"/nick {new_username}"
                    message_encoded = change_nick_message.encode('utf-8')
                    message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
                    app.client_socket.send(message_header + message_encoded)
                return 

            app.entry.delete(0, tk.END)
            message_encoded = message.encode('utf-8')
            message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
            app.client_socket.send(message_header + message_encoded)

    def get_socket(app):
        return app.client_socket
