#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import json
import time
import pexpect
import datetime
from threading import Thread
from modules import controller
from modules.session import Session
from modules.command import execute_command_nxc

def connect_pwncat(app, params, method, session, restart):
    from modules.command import read_output_pwncat

    ip_address = "ip a | grep inet | grep -v inet6 | grep -v 127 | awk '{print $2}'"
    commands = ["$null", "$null", "$null", "$null", "whoami", "head -1 /etc/hostname", ip_address, "echo $$", "ps -p $$ -o comm=", "uname -m"]
    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "Unknown",  
        "Arch": "Unknown",  
        "Listener": "Unknown",  
        "Tail": "PwnCat-CS",
        "Method": method,
        "Params": params
    }

    pwncat_path = f'/tmp/Kitsune/pwncat'
    os.makedirs(pwncat_path, exist_ok=True)
    
    if method:
        session_info["Listener"] = "SSH"
        user = params.split("@")[0]
        host = params.split("@")[1]
        pasw = method

        if app.proxy_status:
            session_data = pexpect.spawn(f'proxychains4 -q python3.11 /usr/local/bin/pwncat-cs ssh://{user}:{pasw}@{host}', cwd=pwncat_path, echo=False, use_poll=True)  
        else:
            session_data = pexpect.spawn(f'python3.11 /usr/local/bin/pwncat-cs ssh://{user}:{pasw}@{host}', cwd=pwncat_path, echo=False, use_poll=True)  
    else:
        session_info["Listener"] = "BIND"
        if app.proxy_status:
            session_data = pexpect.spawn(f'proxychains4 -q python3.11 /usr/local/bin/pwncat-cs connect://{params}', cwd=pwncat_path, echo=False, use_poll=True)  
        else:
            session_data = pexpect.spawn(f'python3.11 /usr/local/bin/pwncat-cs connect://{params}', cwd=pwncat_path, echo=False, use_poll=True)  

    session_data.timeout = 1

    try:
        session_data.expect("registered", timeout=None)  
        session_data.sendline("back")

        for cmd in commands:
            session_data.sendline(cmd) ; time.sleep(0.2)
            output = read_output_pwncat(session_data, cmd)

            try:
                if cmd.startswith("whoami"):
                    session_info["User"] = output.lower().strip()
                elif cmd.startswith("head -1"):
                    session_info["Hostname"] = output.lower().strip()
                elif cmd.startswith("ip a"):
                    if "grep" in output:
                        session_info["IP Address"] = output.split("'")[-1].strip().split("/")[0]
                    else:
                        session_info["IP Address"] = output.split("/")[0].strip()
                elif cmd.startswith("echo"):
                    session_info["PID"] = output.strip()
                elif cmd.startswith("ps -p"):
                    session_info["Process"] = output.lower().strip()
                elif cmd.startswith("uname -m"):
                    if "64" in output:
                        session_info["Arch"] = "x64"
                    else:
                        session_info["Arch"] = "x86"
            except:
                pass

        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:

            if not restart:
                session_info["Session"] = app.count_session()

            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(session_id)
            Session.save_session(session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):  
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        error_message = f"[{current_time}] Error: Failed connecting via PwnCat-CS!\n"
        app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def pwncat_thread(app, params, method, session, restart):
    def run_pwncat():
        try:
            connect_pwncat(app, params, method, session, restart)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Connecting via PwnCat-CS to {params}..\n"
    app.add_event_viewer_log(connecting_line, 'color_listen', "#FFCC00")

    pwncat_thread = Thread(target=run_pwncat)
    pwncat_thread.daemon = True
    pwncat_thread.start()
    return pwncat_thread

def connect_pyshell(app, params, method, session, restart):
    from modules.command import read_output_nonblocking

    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "Unknown",  
        "Arch": "Unknown",  
        "Listener": method.upper(),  
        "Tail": "PyShell",
        "Method": method,
        "Params": params
    }

    pyshell_path = "tails/PyShell/pyshell.py"

    if app.proxy_status:
        command = f"proxychains4 -q {os.sys.executable} {pyshell_path} {params} {method}"
    else:
        command = f"{os.sys.executable} {pyshell_path} {params} {method}"
    
    session_data = pexpect.spawn(command, echo=False, use_poll=True)
    session_data.timeout = 1

    try:
        session_data.expect("PyShell", timeout=None)  

        session_data.sendline("whoami")
        output = read_output_nonblocking(session_data, "whoami")
        
        get_host = "[System.Net.Dns]::GetHostByName($env:computerName).Hostname"
        get_ip = "(Get-WmiObject -Class Win32_NetworkAdapterConfiguration | where {$_.DefaultIPGateway -ne $null}).IPAddress | select-object -first 1"
        get_process = '(Get-WmiObject Win32_Process -Filter "ProcessId = $pid").ProcessName'
        get_arch = "(Get-CimInstance Win32_operatingsystem).OSArchitecture.split()[0]"
        windows_commands = [get_host, get_ip, "$pid", get_process, get_arch]
        linux_commands = ["head -1 /etc/hostname", "ip a | grep inet | grep -v inet6 | grep -v 127 | awk '{print $2}'", "echo $$", "ps -p $$ -o comm=", "uname -m"]

        if '\\' in output:
            commands = windows_commands
            session_info["User"] = (output.split('\\')[1]).lower().strip()
        else:
            commands = linux_commands
            session_info["User"] = output.lower().strip()
    
        for cmd in commands:
            session_data.sendline(cmd)
            output = read_output_nonblocking(session_data, cmd)

            if "GetHostByName" in cmd or cmd.startswith("head -1 /etc/hostname"):
                session_info["Hostname"] = output.lower().split()[0].strip()
            elif "DefaultIPGateway" in cmd or cmd.startswith("ip a"):
                session_info["IP Address"] = output.split("/")[0].strip()
            elif cmd.startswith("$pid") or cmd.startswith("echo"):
                session_info["PID"] = output
            elif "ProcessName" in cmd or cmd.startswith("ps -p"):         
                if "$pid" in commands and not output:
                    session_info["Process"] = "powershell.exe"
                else:
                    session_info["Process"] = output.lower().strip()
            elif "Get-CimInstance" in cmd or cmd.startswith("uname -m"):
                if "64" in output:
                    session_info["Arch"] = "x64"
                else:
                    session_info["Arch"] = "x86"

        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:

            if not restart:
                session_info["Session"] = app.count_session()

            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(session_id)
            Session.save_session(session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        error_message = f"[{current_time}] Error: Failed to connect via PyShell!\n"
        app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def pyshell_thread(app, params, method, session, restart):
    def run_pyshell():
        try:
            connect_pyshell(app, params, method, session, restart)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Connecting via PyShell to {params.split()[0]}..\n"
    app.add_event_viewer_log(connecting_line, 'color_listen', "#FFCC00")

    pyshell_thread = Thread(target=run_pyshell)
    pyshell_thread.daemon = True
    pyshell_thread.start()
    return pyshell_thread

def connect_netexec(app, params, method, session, restart):
    method = method.lower()

    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "Unknown",  
        "Arch": "Unknown",  
        "Listener": method.upper(),  
        "Tail": "NetExec",
        "Method": method,
        "Params": params
    }

    try:
        get_host = '"[System.Net.Dns]::GetHostByName($env:computerName).Hostname"'
        get_ip = '"$ip=((Get-WmiObject -Class Win32_NetworkAdapterConfiguration | where {$_.DefaultIPGateway -ne $null}).IPAddress | select-object -first 1) ; $ip"'
        get_process = '"$proc=(Get-WmiObject Win32_Process -Filter ProcessId=$pid).ProcessName ; $proc"'
        get_arch = '"$arch=(Get-CimInstance Win32_operatingsystem).OSArchitecture.split()[0] ; $arch"'
        commands = ["whoami", get_host, get_ip, "$pid", get_process, get_arch]

        class SessionData:
            def __init__(self, nxc_method=None, nxc_params=None):
                self.nxc_method = method
                self.nxc_params = params

        session_data = SessionData(nxc_method=method, nxc_params=params)

        for cmd in commands:
            output = execute_command_nxc(app, session_data, cmd)
            if output:
                if cmd.startswith("whoami"):
                    session_info["User"] = (output.split('\\')[1]).lower().strip()
                elif cmd == get_host:
                    session_info["Hostname"] = output.lower().strip()
                elif cmd == get_ip:
                    session_info["IP Address"] = output.split("/")[0].strip() 
                elif cmd.startswith("$pid"):
                    session_info["PID"] = output.strip()
                elif cmd == get_process:
                    session_info["Process"] = output.lower().strip()
                elif cmd == get_arch:
                    if "64" in output:
                        session_info["Arch"] = "x64"
                    else:
                        session_info["Arch"] = "x86"
               
        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:

            if not restart:
                session_info["Session"] = app.count_session()

            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(session_id)
            Session.save_session(session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        error_message = f"[{current_time}] Error: Failed to connect via NetExec!\n"
        app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def netexec_thread(app, params, method, session, restart):
    def run_netexec():
        try:
            connect_netexec(app, params, method, session, restart)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Connecting via NetExec to {params.split()[0]}..\n"
    app.add_event_viewer_log(connecting_line, 'color_listen', "#FFCC00")

    netexec_thread = Thread(target=run_netexec)
    netexec_thread.daemon = True
    netexec_thread.start()
    return netexec_thread

def connect_evilwinrm(app, params, method, session, restart):
    from modules.command import read_output_nonblocking
    method = method.lower()

    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "Unknown",  
        "Arch": "Unknown",  
        "Listener": method.upper(),  
        "Tail": "Evil-WinRM",
        "Method": method,
        "Params": params
    }

    evilwinrm_path = f'/tmp/Kitsune/evilwinrm'
    os.makedirs(evilwinrm_path, exist_ok=True)
    
    if app.proxy_status:
        session_data = pexpect.spawn(f'proxychains4 -q evil-winrm -i {params}', cwd=evilwinrm_path, echo=False, use_poll=True)  
    else:
        session_data = pexpect.spawn(f'evil-winrm -i {params}', cwd=evilwinrm_path, echo=False, use_poll=True)  
    session_data.timeout = 1

    try:
        session_data.expect_exact("*Evil-WinRM*", timeout=None)  
        session_data.sendline("\n")

        get_host = "[System.Net.Dns]::GetHostByName($env:computerName).Hostname"
        get_ip = "(Get-WmiObject -Class Win32_NetworkAdapterConfiguration | where {$_.DefaultIPGateway -ne $null}).IPAddress | select-object -first 1"
        get_process = '(Get-WmiObject Win32_Process -Filter "ProcessId = $pid").ProcessName'
        get_arch = "(Get-CimInstance Win32_operatingsystem).OSArchitecture.split()[0]"
        commands = ["whoami", get_host, get_ip, "$pid", get_process, get_arch]

        for cmd in commands:
            session_data.sendline(cmd) ; time.sleep(0.2)
            output = read_output_nonblocking(session_data, cmd)

            if output:
                if cmd.startswith("whoami"):
                    session_info["User"] = (output.split('\\')[1]).lower().strip()
                elif cmd == get_host:
                    session_info["Hostname"] = output.lower().strip()
                elif cmd == get_ip:
                    session_info["IP Address"] = output.split("\n")[0].strip() 
                elif cmd.startswith("$pid"):
                    session_info["PID"] = output.strip()
                elif cmd == get_process:
                    session_info["Process"] = output.lower().strip()
                elif cmd == get_arch:
                    if "64" in output:
                        session_info["Arch"] = "x64"
                    else:
                        session_info["Arch"] = "x86"

        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:

            if not restart:
                session_info["Session"] = app.count_session()

            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(session_id)
            Session.save_session(session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        error_message = f"[{current_time}] Error: Failed to connect via Evil-WinRM!\n"
        app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def evilwinrm_thread(app, params, method, session, restart):
    def run_evilwinrm():
        try:
            connect_evilwinrm(app, params, method, session, restart)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Connecting via Evil-WinRM to {params.split()[0]}..\n"
    app.add_event_viewer_log(connecting_line, 'color_listen', "#FFCC00")

    evilwinrm_thread = Thread(target=run_evilwinrm)
    evilwinrm_thread.daemon = True
    evilwinrm_thread.start()
    return evilwinrm_thread

def connect_wmiexecpro(app, params, method, session, restart):
    from modules.command import read_output_wmiexecpro
    method = method.lower()

    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "powershell.exe",  
        "Arch": "Unknown",  
        "Listener": method.upper(),  
        "Tail": "WMIexec-Pro",
        "Method": method,
        "Params": params
    }

    user_wmi = params.split()[2]
    pass_wmi = params.split()[4]
    host_wmi = params.split()[0]

    wmiexecpro_path = "tails/wmiexec-Pro"
    
    if app.proxy_status:
        command = f"proxychains4 -q {os.sys.executable} wmiexec-pro.py '{user_wmi}:{pass_wmi}'@{host_wmi} exec-command -shell"
    else:
        command = f"{os.sys.executable} wmiexec-pro.py '{user_wmi}:{pass_wmi}'@{host_wmi} exec-command -shell"

    session_data = pexpect.spawn(command, cwd=wmiexecpro_path, echo=True, use_poll=True)
    session_data.timeout = 1

    try:
        session_data.expect("execute", timeout=None)  
        session_data.sendline("sleep 7")
        session_data.expect("time", timeout=None)

        get_host = "[System.Net.Dns]::GetHostByName($env:computerName).Hostname"
        get_ip = "(Get-WmiObject -Class Win32_NetworkAdapterConfiguration | where {$_.DefaultIPGateway -ne $null}).IPAddress | select-object -first 1"
        get_process = '(Get-WmiObject Win32_Process -Filter "ProcessId = $pid").ProcessName'
        get_arch = "(Get-CimInstance Win32_operatingsystem).OSArchitecture.split()[0]"
        commands = ["whoami", get_host, get_ip, "$pid", get_arch]

        for cmd in commands:
            session_data.sendline(f"powershell '{cmd}'")
            output = read_output_wmiexecpro(session_data, cmd)
            
            if output:
                if cmd.startswith("whoami"):
                    session_info["User"] = output.lower().strip()
                elif cmd == get_host:
                    session_info["Hostname"] = output.lower().strip()
                elif cmd == get_ip:
                    session_info["IP Address"] = output.split("\n")[0].strip() 
                elif cmd.startswith("$pid"):
                    session_info["PID"] = output.strip()
                elif cmd == get_process:
                    session_info["Process"] = output.lower().strip()
                elif cmd == get_arch:
                    if "64" in output:
                        session_info["Arch"] = "x64"
                    else:
                        session_info["Arch"] = "x86"

        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:

            if not restart:
                session_info["Session"] = app.count_session()

            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(session_id)
            Session.save_session(session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        error_message = f"[{current_time}] Error: Failed to connect via WMIexec-Pro!\n"
        app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def wmiexecpro_thread(app, params, method, session, restart):
    def run_wmiexecpro():
        try:
            connect_wmiexecpro(app, params, method, session, restart)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Connecting via WMIexec-Pro to {params.split()[0]}..\n"
    app.add_event_viewer_log(connecting_line, 'color_listen', "#FFCC00")

    wmiexecpro_thread = Thread(target=run_wmiexecpro)
    wmiexecpro_thread.daemon = True
    wmiexecpro_thread.start()
    return wmiexecpro_thread
