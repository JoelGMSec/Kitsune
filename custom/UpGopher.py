#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import sys
sys.dont_write_bytecode = True

def get_description():
    return "This module adds UpGopher to custom commands"

def main(app, caller, session, command):
    if caller == "command" and command == "help":
        output = "- upgopher: Execute UpGopher on current session and return URL:PORT"
        return output
        
    if caller == "command" and command == "upgopher":
        command = "echo 'This function is not yet implemented!'"
        return command

    return None