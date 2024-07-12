#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import json
import time
import shutil
import datetime
import subprocess
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def on_combobox_focus(event):
    event.widget.selection_clear()

def export_logs(app):
    settings_window = tk.Toplevel(app)
    settings_window.geometry("525x255")
    settings_window.title("Export Logs")
    settings_window.focus_force()

    image_frame = tk.Frame(settings_window)
    image_frame.grid(row=0, column=1, padx=(10, 0), pady=20)

    image = Image.open("./themes/images/Logs.png")
    resized_image = image.resize((200, 200))  

    photo = ImageTk.PhotoImage(resized_image)

    image_label = tk.Label(image_frame, image=photo)
    image_label.image = photo  
    image_label.grid(row=0, column=0)

    settings_frame = tk.Frame(settings_window)
    settings_frame.grid(row=0, column=0, padx=(15, 0), pady=10, sticky="nsew")

    nekomancer_label = tk.Label(settings_frame, text="Enter project name")
    nekomancer_label.grid(row=0, column=0, padx=(15, 0), pady=(20, 0))

    name_label = tk.Label(settings_frame, text="*Overwrited if exists*", fg="#00FF99")
    name_label.grid(row=1, column=0, padx=(15, 0), pady=(0, 5))

    selected_value = tk.StringVar(value="")  

    name_entry = ttk.Entry(settings_frame, textvariable=tk.StringVar())
    name_entry.grid(row=2, column=0, padx=(15, 0), pady=(20, 0))

    def on_enter_key(event):
        save_project(settings_window, name_entry, app)

    settings_window.bind("<Return>", on_enter_key)

    def on_escape_key(event):
        settings_window.destroy()

    settings_window.bind("<Escape>", on_escape_key)

    save_button = ttk.Button(settings_frame, text="Save", command=lambda: save_project(settings_window, name_entry, app))
    save_button.grid(row=3, column=0, pady=(35, 10))  

def save_project(settings_window, name_entry, app):
    if name_entry.get():
        profile_name = name_entry.get().strip()
        if profile_name:  
            profile_path = os.path.join("reports")
            data_path = "data"
            try:
                os.makedirs(profile_path, exist_ok=True)  
                for item in os.listdir(data_path):  
                    s = os.path.join(data_path, item)
                    d = os.path.join(profile_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
            except:
                pass

        try:
            json_file_path = os.path.join(profile_path, "sessions.json")
            html_file_path = os.path.join(profile_path + "/" + profile_name + ".html")
            json_to_html(json_file_path, html_file_path)

            for file_name in os.listdir(profile_path):
                if file_name.endswith('.json'):
                    os.remove(os.path.join(profile_path, file_name))
        except:
            pass

        settings_window.destroy()
        app.project_saved_success()

def clear_logs(app):
    profiles_path = "reports"
    if app.confirm_dialog() == "yes":
        if os.path.exists(profiles_path) and os.path.isdir(profiles_path):
            try:
                for folder_name in os.listdir(profiles_path):
                    folder_path = os.path.join(profiles_path, folder_name)
                    if os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
                    elif os.path.isfile(folder_path):
                        os.remove(folder_path)
                app.report_deleted_success()

            except:
                pass

def json_to_html(json_file_path, html_file_path):
    with open(json_file_path, 'r') as file:
        sessions = json.load(file)
    
    logo_filename = "Kitsune.png"
    logo_path = os.path.join(os.path.dirname(html_file_path), logo_filename)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kitsune - Command & Control - REPORT</title>
        <style>
            body {{
                font-family: Consolas;
                font-weight: bold;
                background-color: #fff;
                margin: 0;
                padding: 0;
            }}
           .header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                background-color: #333;
                color: white;
                padding: 10px;
            }}
            .header img {{
                height: 105px;
                margin-right: 20px;
            }}
            .header .title-container {{
                display: flex;
                flex-direction: column;
            }}
            .header h1 {{
                margin: 0;
                font-size: 42px;
                font-family: Lexend;
            }}
            .header h2 {{
                margin: 0;
                font-size: 31px;
                font-family: Lexend;
                color: #c0c5ca;
                margin-top: -10px;
            }}
            .header .report {{
                font-size: 62px;
                font-family: Lexend;
                margin-left: auto;
                margin-right: 10px;
                background: -webkit-linear-gradient(90deg, #ff2b43, #af2b43 65%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .content {{
                padding: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                table-layout: fixed;
            }}
            th, td {{
                text-align: left;
                padding: 8px;
                word-wrap: break-word;
                overflow-wrap: break-word;
                white-space: normal;
                font-family: Lexend;
                background-color: #eaecee;
            }}
            th {{
                font-family: Lexend;
                color: white;
                background-color: #BF2B43;
            }}
            tr:nth-child(even) th, tr:nth-child(even) td {{
                background-color: #f2f3f3;
            }}
            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                overflow-wrap: break-word;
                font-size: 1.1em;
                margin-block: 0px;
            }}
            th.command, td.command {{
                width: 175px; /* Ajusta el valor según el ancho deseado */
            }}
            th.user, td.user {{
                width: 175px;
            }}
            th.computer, td.computer {{
                width: 190px;
            }}
            th.ip-address, td.ip-address {{
                width: 175px;
            }}
            th.process, td.process {{
                width: 175px;
            }}
            th.pid, td.pid {{
                width: 145px;
            }}
            th.arch, td.arch {{
                width: 120px;
            }}
            th.connection, td.tail {{
                width: 150px;
            }}
            th.tail, td.tail {{
                width: auto;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="../themes/images/Kitsune.png" alt="">
            <div class="title-container">
                <h1>Kitsune</h1>
                <h2>Command & Control</h2>
            </div>
            <div class="report">REPORT</div>
        </div>
        <div class="content">
    """

    for session in sessions:
        html_content += f"""
        <h2 style="font-family: Lexend;">Session {session['Session']}</h2>
        <table>
            <tr>
                <th class="user">User</th>
                <th class="computer">Computer</th>
                <th class="ip-address">IP Address</th>
                <th class="process">Process</th>
                <th class="pid">PID</th>
                <th class="arch">Arch</th>
                <th class="connection">Connection</th>
                <th class="tail">Tail</th>
            </tr>
            <tr>
                <td class="user">{session['User']}</td>
                <td class="computer">{session['Hostname']}</td>
                <td class="ip-address">{session['IP Address']}</td>
                <td class="process">{session['Process']}</td>
                <td class="pid">{session['PID']}</td>
                <td class="arch">{session['Arch']}</td>
                <td class="connection">{session['Listener']}</td>
                <td class="tail">{session['Tail']}</td>
            </tr>
        <table>
            <tr>
                <th class="command">Command</th>
                <th>Output</th>
            </tr>
        """
        for command in session['Commands']:
            html_content += f"""
            <tr>
                <td class="command">{command['Command']}</td>
                <td><pre>{command['Output']}</pre></td>
            </tr>
            """
        html_content += "</table><br>"

    html_content += """
        </div>
    </body>
    </html>
    """

    with open(html_file_path, 'w') as file:
        file.write(html_content)
