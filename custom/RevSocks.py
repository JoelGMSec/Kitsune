#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import sys
sys.dont_write_bytecode = True

def get_description():
    return "This module adds RevSocks to custom commands"

def main(app, caller, session, command):
    if caller == "command" and command == "help":
        output = "- revsocks: Execute RevSocks on current session and return SOCKS connection"
        return output
        
    if caller == "command" and command == "revsocks":
        command = "echo 'This function is not yet implemented!'"
        return command

    return None