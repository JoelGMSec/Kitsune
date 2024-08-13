FROM debian:sid-slim
ENV DISPLAY=:0

LABEL maintainer="@JoelGMSec - https://darkbyte.net"

RUN apt-get update && apt-get install -y sudo git zip wget proxychains4
RUN wget https://archive.kali.org/archive-key.asc -O /etc/apt/trusted.gpg.d/kali-archive-key.asc
RUN echo "deb [arch=amd64] http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" >> /etc/apt/sources.list
RUN apt-get update && apt install -y build-essential gcc-mingw-w64-x86-64-win32 python3-pip python3-tk python3.11 powershell golang
RUN apt-get update && apt install -y dnscat2 evil-winrm villain
RUN python3.11 -m pip install pwncat-cs --break-system-packages
RUN wget https://github.com/Pennyw0rth/NetExec/releases/download/v1.2.0/nxc -O /usr/bin/netexec
RUN chmod +x /usr/bin/netexec
RUN cd /opt && git clone https://github.com/JoelGMSec/Kitsune
RUN git clone https://github.com/iagox86/dnscat2 /opt/Kitsune/tails/dnscat2
RUN git clone https://github.com/Hackplayers/evil-winrm /opt/Kitsune/tails/evil-winrm
RUN git clone https://github.com/JoelGMSec/HTTP-Shell /opt/Kitsune/tails/HTTP-Shell
RUN git clone https://github.com/Pennyw0rth/NetExec /opt/Kitsune/tails/NetExec
RUN git clone https://github.com/calebstewart/pwncat /opt/Kitsune/tails/pwncat
RUN git clone https://github.com/JoelGMSec/PyShell /opt/Kitsune/tails/PyShell
RUN git clone https://github.com/XiaoliChan/wmiexec-Pro /opt/Kitsune/tails/wmiexec-Pro
RUN pip3 install numpy --break-system-packages
RUN pip3 install -r /opt/Kitsune/requirements.txt --break-system-packages
RUN for i in $(find /opt/Kitsune/ -name requirements.txt) ; do cat $i >> /opt/Kitsune/reqs.txt ; done
RUN for i in $(cat /opt/Kitsune/reqs.txt) ; do pip3 install $i --break-system-packages ; done
RUN rm -f /opt/Kitsune/reqs.txt

WORKDIR /opt/Kitsune
ENTRYPOINT ["python3", "/opt/Kitsune/kitsune.py"]
