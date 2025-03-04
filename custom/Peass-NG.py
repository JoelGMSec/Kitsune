#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import sys
sys.dont_write_bytecode = True

def get_description():
    return "This module adds LinPEAS & WinPEAS to custom commands"

def main(app, caller, session, title, command):
    if caller == "command" and command == "help":
        output = "- linpeas: Execute LinPeas on current session and download results\n" \
                 + "- winpeas: Execute WinPeas on current session and download results"
        return output
        
    if caller == "command" and command == "linpeas":
        command = "print: 'This function is not yet implemented!'"
        return command

    if caller == "command" and command == "winpeas":
        command = "print: 'This function is not yet implemented!'"
        return command

    return None
