#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import re
import time
import random
import pexpect
import tkinter as tk
from tkinter import ttk
from threading import Thread
from modules.session import Session
from modules.chat import TeamChatTab
from modules.helper import command_help

def execute_command_nxc(app, session_data, command):
    method = session_data.nxc_method
    params = session_data.nxc_params

    netexec_path = "/tmp/Kitsune/netexec"
    os.makedirs(netexec_path, exist_ok=True)

    try:
        with open("help/nxc_cmd.txt", "r") as file:
            nxc_cmd = file.read()
    except:
        pass

    else:
        if command in nxc_cmd:
            if app.proxy_status:
                current_process = pexpect.spawn(f"proxychains4 -q netexec {method} {params} -M {command}'", cwd=netexec_path, echo=True, use_poll=True)
            else:
                current_process = pexpect.spawn(f"netexec {method} {params} -M {command}'", cwd=netexec_path, echo=True, use_poll=True)
        else:
            if app.proxy_status:
                current_process = pexpect.spawn(f"proxychains4 -q netexec {method} {params} -x 'powershell {command}'", cwd=netexec_path, echo=True, use_poll=True)
            else:
                current_process = pexpect.spawn(f"netexec {method} {params} -x 'powershell {command}'", cwd=netexec_path, echo=True, use_poll=True)

        current_process.timeout = 1  
        
        try:
            current_process.expect(pexpect.EOF, timeout=30)  
            output = current_process.before.decode("utf-8") 

            inicio_amarillo = re.compile(r'\x1B\[1;33m')  
            fin_color = re.compile(r'\x1B\[0m')  
            
            lineas = output.split('\n')
            lineas_amarillas = []
            
            for linea in lineas:
                if inicio_amarillo.search(linea) and not "(Pwn3d!)" in linea:  
                    linea_limpia = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', linea)
                    linea_limpia = linea_limpia.split(maxsplit=4)[-1]
                    lineas_amarillas.append(linea_limpia)
            
            output = "\n".join(lineas_amarillas)

            output = re.sub(r'^\[\*\].*?name:.*?domain:.*\)', '', output)
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            output = ansi_escape.sub('', output)
            output = re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', output)

            lines = output.split("\n")
            while lines and lines[0].strip() == "":
                lines.pop(0)
            while lines and lines[-1].strip() == "":
                lines.pop(-1)
            if lines:
                lines[0] = lines[0].lstrip()
            output = "\n".join(lines)

            lines = output.split("\n")
            if command.split()[0] in lines[0].strip():
                output = "\n".join(lines[1:])  

        except:
            output = None

    return output

def read_output_wmiexecpro(session_data, command):
    session_data.expect("Results", timeout=10)
    
    def read_buffer(session_data):
        output = b''
        while True:
            try:
                block = session_data.read_nonblocking(size=999, timeout=0.2)
                output += block
                if not block:
                    break
            except pexpect.exceptions.TIMEOUT:
                break
        return output

    attempts = 0
    output = read_buffer(session_data)
    while not output and attempts < 100:  
        time.sleep(0.1)
        session_data.write("\n")
        output = read_buffer(session_data)
        attempts += 1
    output = output.decode("utf-8").replace("\r", "")
    output = re.sub(r'^.*C:\\Windows\\system32>', '', output, flags=re.MULTILINE)

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    output = re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', output)
    prompt_pattern = re.compile(r'\[-\] ')
    output = prompt_pattern.sub('', output)

    lines = output.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop(-1)
    if lines:
        lines[0] = lines[0].lstrip()
    output = "\n".join(lines)

    lines = output.split("\n")
    if command.split()[0] in lines[0].strip():
        output = "\n".join(lines[1:])
    
    output = re.sub(r'C:\\Windows\\System32>', '', output).strip()
    return output

def read_output_dnscat2(session_data, command):
    def read_buffer(session_data):
        output = b''
        while True:
            try:
                block = session_data.read_nonblocking(size=999, timeout=0.2)
                output += block
                if not block:
                    break
            except pexpect.exceptions.TIMEOUT:
                break
        return output

    attempts = 0
    output = read_buffer(session_data)
    while not output and attempts < 100:  
        time.sleep(0.1)
        session_data.write("\n")
        output = read_buffer(session_data)
        attempts += 1
    output = output.decode("utf-8").replace("\r", "")    
    output = re.sub(r'sh .*?>', '', output)
    output = re.sub(r'bash .*?>', '', output)
    output = re.sub(r'cmd .*?>', '', output)
    output = re.sub(r'powershell .*?>', '', output)
    output = re.sub(r'PS .*?>', '', output)
    output = re.sub(r'dnscat2>', '', output)
    output = re.sub(r'unnamed .*?>', '', output)
    output = re.sub(r'POTENTIAL CACHE HIT', '', output)

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    output = re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', output)
    prompt_pattern = re.compile(r'\[-\] ')
    output = prompt_pattern.sub('', output)

    lines = output.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop(-1)
    if lines:
        lines[0] = lines[0].lstrip()
    output = "\n".join(lines)

    lines = output.split("\n")
    if command.split()[0] in lines[0].strip():
        output = "\n".join(lines[1:])  

    return output

def read_output_pwncat(session_data, command):
    def read_buffer(session_data):
        output = b''
        while True:
            try:
                block = session_data.read_nonblocking(size=999, timeout=0.2)
                output += block
                if not block:
                    break
            except pexpect.exceptions.TIMEOUT:
                break
        return output

    attempts = 0
    output = read_buffer(session_data)
    while not output and attempts < 100:  
        time.sleep(0.1)
        session_data.write("\n")
        output = read_buffer(session_data)
        attempts += 1
    output = output.decode("utf-8").replace("\r", "")
    output = re.sub(r'\n.*\ue0b0', '', output)
    output = re.sub(r'\[.*\ue0b0', '', output)

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    output = re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', output)

    pwncat_prompt_pattern = re.compile(r'\(remote\) .*.')
    output = pwncat_prompt_pattern.sub('', output)
    pwncat_msg_pattern = re.compile(r'\(local\) .*.')
    output = pwncat_msg_pattern.sub('', output)
    pwncat_msg_pattern = re.compile(r'.*  \>\n')
    output = pwncat_msg_pattern.sub('', output)

    lines = output.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop(-1)
    if lines:
        lines[0] = lines[0].lstrip()
    output = "\n".join(lines)

    lines = output.split("\n")
    if command.split()[0] in lines[0].strip():
        output = "\n".join(lines[1:])  

    return output

def read_output_nonblocking(session_data, command):
    def read_buffer(session_data):
        output = b''
        while True:
            try:
                block = session_data.read_nonblocking(size=999, timeout=0.2)
                output += block
                if not block:
                    break
            except pexpect.exceptions.TIMEOUT:
                break
        return output

    attempts = 0
    output = read_buffer(session_data)
    while not output and attempts < 100:  
        time.sleep(0.1)
        session_data.write("\n")
        output = read_buffer(session_data)
        attempts += 1
    output = output.decode("utf-8").replace("\r", "")
    output = re.sub(r'\n.*\ue0b0', '', output)
    output = re.sub(r'\[.*\ue0b0', '', output)

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    output = re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', output)
    prompt_pattern = re.compile(r'(PS .*?>|\*Evil-WinRM\* PS .*?>)')
    output = prompt_pattern.sub('', output)
    prompt_pattern = re.compile(r'\[!\] ')
    output = prompt_pattern.sub('', output)

    villain_prompt_pattern = re.compile(r'(.*\\.*>)')
    output = villain_prompt_pattern.sub('', output)
    villain_prompt_pattern = re.compile(r'(\[Shell\] .*\n)')
    output = villain_prompt_pattern.sub('', output)

    lines = output.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop(-1)
    if lines:
        lines[0] = lines[0].lstrip()
    output = "\n".join(lines)

    lines = output.split("\n")
    if command.split()[0] in lines[0].strip():
        output = "\n".join(lines[1:])  

    return output

def execute_command(app, event):
    current_tab = app.notebook.tab(app.notebook.select(), "text")
    if "Team Chat" in current_tab:
        if app.clear_command:
            app.clear_command = False
            TeamChatTab.clear_chat_logs(app)
        else:
            TeamChatTab.send_message(app, event)

    else:
        if app.clear_command:
            command = "clear"
            stripped_command = "clear"
            app.clear_command = False

        else:
            command = app.entry.get()
            stripped_command = command.strip()  

        if not stripped_command:
            return

        if stripped_command in app.command_history:
            app.command_history.remove(stripped_command)

        if stripped_command not in ["close", "clear"]:
            app.command_history.append(stripped_command)
            Session.save_command_history(app.command_history)

        app.history_index = len(app.command_history)

        if command == "exit":
            app.entry.delete(0, tk.END)
            current_tab = app.notebook.tab(app.notebook.select(), "text")
            if "Event Viewer" in current_tab:
                app.confirm_and_quit()

        if command == "close":
            app.entry.delete(0, tk.END)
            current_tab = app.notebook.tab(app.notebook.select(), "text")
            if not "Event Viewer" in current_tab:
                app.notebook.forget("current")
            if "Event Viewer" in current_tab:
                app.confirm_and_quit()

        elif command == "clear":
            app.entry.delete(0, tk.END)
            current_tab_title = app.notebook.tab(app.notebook.select(), "text")
     
            if current_tab_title in ["Listeners"]:
                if app.confirm_dialog() == "yes":
                    pass

            if current_tab_title in ["Event Viewer"]:
                app.clear_logs()

            for session in app.sessions:
                if session.title == current_tab_title:
                    session.log.clear()
                    label = session.get_label(app)
                    if label is not None:
                        label.config(state="normal")
                        label.delete('1.0', tk.END)
                        label.config(state="disabled")
                    break

        else:
            try:
                current_session = ""
                current_tab = app.notebook.tab(app.notebook.select(), "text")
                for session in app.sessions:
                    if session.title == current_tab:
                        current_session = session
                        break

                if current_session:
                    current_session.label.tag_config("color_input", foreground="#00AAFF")
                    current_session.label.tag_config("color_output", foreground="#00FF99")
                    current_session.label.tag_config("color_reset", foreground="#FFFFFF")

                    current_session.label.config(state="normal")
                    log_text = "kitsune> "
                    current_session.label.insert("end", log_text, "color_input")
                    log_text = f"{command}\n"
                    current_session.label.insert("end", log_text, "color_reset")
                    current_session.label.config(state="disabled")
                    current_session.label.see("end")

                    def execute_read_output_nonblocking():
                        nonlocal command
                        nonlocal current_session
                        nonlocal current_tab
                        disable_session = False

                        try:
                            if "netexec" in str(current_session.session_data):
                                if command != "help":
                                    output = execute_command_nxc(app, current_session.session_data, command)
                            
                            elif "wmiexec-pro" in str(current_session.session_data):
                                if command != "help":
                                    current_session.session_data.write(f"powershell '{command}' \n")
                                    output = read_output_wmiexecpro(current_session.session_data, command)
                            
                            elif "dnscat2" in str(current_session.session_data):
                                if command != "help":
                                    current_session.session_data.sendline("\n")
                                    current_session.session_data.sendline(command)
                                    time.sleep(3)
                                    output = read_output_dnscat2(current_session.session_data, command)

                            elif "pwncat-cs" in str(current_session.session_data):
                                if command != "help":
                                    current_session.session_data.write(command + "\n")  
                                    output = read_output_pwncat(current_session.session_data, command)

                            elif "Villain" in str(current_session.session_data):
                                if command == "upload*":
                                    current_session.session_data.sendline("exit")
                                    time.sleep(3)
                                    current_session.session_data.sendline("sessions")
                                    current_session.session_data.expect("Windows", timeout=None)
                                    villain_id = session_data.before.decode()
                                    current_session.session_data.sendline(command + " " + villain_id)
                                    time.sleep(3)
                                    output = read_output_nonblocking(current_session.session_data, command)
                                    current_session.session_data.sendline(shell + " " + villain_id)

                                if command == "kill":
                                    current_session.session_data.sendline("exit")
                                    time.sleep(3)
                                    current_session.session_data.sendline("sessions")
                                    current_session.session_data.expect("Windows", timeout=None)
                                    villain_id = session_data.before.decode()
                                    current_session.session_data.sendline(kill + " " + villain_id)
                                    time.sleep(3)
                                    current_session.session_data.sendline("flee")
                                    output = "Session terminated."
                                    disable_session = True

                                else:
                                    current_session.session_data.write(command + "\n")  
                                    output = read_output_nonblocking(current_session.session_data, command)

                            else:
                                if command != "help":
                                    current_session.session_data.write(command + "\n")  
                                    output = read_output_nonblocking(current_session.session_data, command)

                            if command.startswith("cd "):
                                output = "Changing directory.."

                            if command == "help":
                                output = command_help(current_session.session_data)

                            if command == "kill" or command == "exit":
                                output = "Disconnected.."
                                disable_session = True

                            if command == "del*" or command == "rm*":
                                output = "Success!"

                            if not output:
                                output = "Error: No output from command!"
                        
                        except:
                            output = "Error: No response from client!"
                            disable_session = True

                        current_session.text_widget = current_session.label
                        current_session.log.append({"Command": command, "Output": output})
                        current_session.save_logs()

                        current_session.label.config(state="normal")
                        log_text = "[>] Output:\n"
                        current_session.label.insert("end", log_text, "color_output")
                        current_session.label.config(state="disabled")
                        current_session.label.see("end")
                        current_session.label.config(state="normal")
                        log_text = f"{output}\n\n"
                        current_session.label.insert("end", log_text, "color_reset")
                        current_session.label.config(state="disabled")
                        current_session.label.see("end")
                        app.update()

                        current_tab = app.notebook.tab(app.notebook.select(), "text")
                        for session in app.sessions:
                            if session.title == current_tab:
                                session.reload_command_session()
                                
                        app.notify_command_session(current_session.title)

                        if disable_session:
                            Session.disable_session(app, current_tab)
                            disable_session = False
                        else:
                            Session.enable_session(app, current_tab)

                    thread = Thread(target=execute_read_output_nonblocking)
                    thread.start()

                app.entry.delete(0, tk.END)

            except:
                pass
