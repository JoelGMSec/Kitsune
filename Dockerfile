FROM debian:bookworm-slim
ENV DISPLAY=:0
LABEL maintainer="@JoelGMSec - https://darkbyte.net"

RUN apt-get update && apt-get install -y sudo git curl zip wget proxychains4 wkhtmltopdf unzip
RUN apt-get install -y build-essential gcc gcc-mingw-w64-x86-64-win32 python3-pip python3-tk 
RUN wget https://archive.kali.org/archive-key.asc -O /etc/apt/trusted.gpg.d/kali-archive-key.asc
RUN echo "deb [arch=amd64] http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" >> /etc/apt/sources.list
RUN apt-get update && apt install -y dnscat2 evil-winrm villain powershell golang python3-impacket python3.12-minimal python3.12-dev
RUN dpkg --force-all -r python3-rich python3-bcrypt python3-netifaces
RUN python3.12 -m pip install git+https://github.com/SafaSafari/pwncat --break-system-packages
RUN wget https://github.com/Pennyw0rth/NetExec/releases/download/v1.3.0/nxc-ubuntu-latest.zip
RUN unzip nxc-ubuntu-latest.zip > /dev/null ; rm nxc-ubuntu-latest.zip
RUN chmod +x nxc ; rm -f /usr/bin/netexec /usr/bin/nxc ; mv nxc /usr/bin/netexec ; ln -s /usr/bin/netexec /usr/bin/nxc
RUN cd /opt && git clone https://github.com/JoelGMSec/Kitsune
RUN git clone https://github.com/iagox86/dnscat2 /opt/Kitsune/tails/dnscat2
RUN git clone https://github.com/Hackplayers/evil-winrm /opt/Kitsune/tails/evil-winrm
RUN git clone https://github.com/JoelGMSec/HTTP-Shell /opt/Kitsune/tails/HTTP-Shell
RUN git clone https://github.com/Pennyw0rth/NetExec /opt/Kitsune/tails/NetExec
RUN git clone https://github.com/SafaSafari/pwncat /opt/Kitsune/tails/pwncat
RUN git clone https://github.com/JoelGMSec/PyShell /opt/Kitsune/tails/PyShell
RUN git clone https://github.com/XiaoliChan/wmiexec-Pro /opt/Kitsune/tails/wmiexec-Pro
RUN python3.12 -m pip install numpy --break-system-packages
RUN dpkg --force-all -r python3-setuptools python3-cryptography 
RUN python3.12 -m pip install setuptools==70 --break-system-packages
RUN python3.12 -m pip install -r /opt/Kitsune/requirements.txt --break-system-packages
RUN for i in $(find /opt/Kitsune/ -name requirements.txt) ; do cat $i >> /opt/Kitsune/reqs.txt ; done
RUN for i in $(cat /opt/Kitsune/reqs.txt) ; do python3.12 -m pip install $i --break-system-packages ; done
RUN rm -f /opt/Kitsune/reqs.txt

WORKDIR /opt/Kitsune
ENTRYPOINT ["python3.12", "/opt/Kitsune/kitsune.py"]