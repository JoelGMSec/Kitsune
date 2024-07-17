#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import json

def load_custom_modules(app):
	custom_dir = "custom"
	output_file = "data/custom.json"
	os.makedirs(os.path.dirname(output_file), exist_ok=True)

	folders = [f for f in os.listdir(custom_dir) if os.path.isdir(os.path.join(custom_dir, f))]
	data = {
	    "custom": []
	}

	for folder in folders:
	    script_name = f"{folder}.py"
	    script_path = os.path.join(custom_dir, script_name)
	    if os.path.isfile(script_path):
	        data["custom"].append({
	            "name": folder,
	            "script": script_name
	        })

	with open(output_file, 'w') as json_file:
	    json.dump(data, json_file, indent=4)
