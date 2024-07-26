#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import sys
sys.dont_write_bytecode = True

import os
import shutil
import subprocess

def get_description():
    return "This module automatically obfuscate all compiled payloads in \"Ps1\" format"

def main(app, caller, payload, format):
    if caller == "generate" and "Ps1" in format:
        payload_obfuscated = str(payload).split(".")[0] + "_obfuscated.ps1"
        shutil.copyfile(payload, payload_obfuscated)

        subprocess.run(["pwsh", "custom/Invoke-Stealth/Invoke-Stealth.ps1", payload_obfuscated, "-t", "all"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            if os.path.isfile(signature_path):
                os.remove(signature_path)
        except:
                pass
