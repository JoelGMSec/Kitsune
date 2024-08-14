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
    return "This module automatically obfuscate all scripts in \"Ps1\" format"

def main(app, caller, payload, format):
    if caller == "generate" and "Ps1" in format:
        tmp_payload = os.path.join("/tmp", os.path.basename(payload))
        payload_obfuscated = str(payload).split(".")[0] + "_obfuscated.ps1"
        shutil.copyfile(payload, tmp_payload)
        subprocess.run(["pwsh", "Invoke-Stealth.ps1", tmp_payload, "-t", "all"], check=True, cwd="custom/Invoke-Stealth/", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.move(tmp_payload, payload_obfuscated)
