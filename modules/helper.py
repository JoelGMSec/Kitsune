#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

def command_help(session_data):
    try:
        with open("help/kitsune.txt", "r") as file:
            general_help = file.read()
    except:
        pass

    tail_help = ""

    if "netexec" in str(session_data):
        method = (str(session_data.nxc_method))

        if method == "smb":
            try:
                with open("help/nxc_smb.txt", "r") as file:
                    tail_help = file.read()
            except:
                pass

        if method == "wmi":
            try:
                with open("help/nxc_wmi.txt", "r") as file:
                    tail_help = file.read()
            except:
                pass

    if "pwncat-cs" in str(session_data):
        try:
            with open("help/pwncat-cs.txt", "r") as file:
                tail_help = file.read()
        except:
            pass

    if "PyShell" in str(session_data):
        try:
            with open("help/pyshell.txt", "r") as file:
                tail_help = file.read()
        except:
            pass

    if "HTTP-Shell" in str(session_data):
        try:
            with open("help/http-shell.txt", "r") as file:
                tail_help = file.read()
        except:
            pass

    if "Evil-WinRM" in str(session_data):
        try:
            with open("help/evil-winrm.txt", "r") as file:
                tail_help = file.read()
        except:
            pass

    if "wmiexec-pro" in str(session_data):
        try:
            with open("help/wmiexec-pro.txt", "r") as file:
                tail_help = file.read()
        except:
            pass

    if "Villain" in str(session_data):
        try:
            with open("help/villain.txt", "r") as file:
                tail_help = file.read()
        except:
            pass

    if tail_help != "":
        command_help_text = str(general_help + "\n" + tail_help.strip())

    else:
        command_help_text = str(general_help.strip())

    return command_help_text
