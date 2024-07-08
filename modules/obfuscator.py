#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#    https://darkbyte.net #
#=========================#

import random
import string

def random_string(length=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def obfuscate_php(code):
    variables = {}
    tokens = code.split()
    for part in tokens:
        if part.startswith('$') and not part.startswith('$_'):
            var = part.split(';')[0].split('=')[0]
            if var not in variables:
                obfuscated_var = f"${random_string()}"
                variables[var] = obfuscated_var
                code = code.replace(var, obfuscated_var)

    lines = code.split('\n')
    obfuscated_lines = []
    for line in lines:
        obfuscated_line = line
        if not line.strip().startswith('//') and line.strip():
            if '=' in line and not line.strip().endswith(';'):
                obfuscated_line += ';'
            obfuscated_line += f" // {random_string()}"
        obfuscated_lines.append(obfuscated_line)

    return '\n'.join(obfuscated_lines)

def obfuscate_aspx(code):
    def random_string(length=8):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    def obfuscate_tag(tag):
        return f"{tag} {random_string()}"

    lines = code.split('\n')
    obfuscated_lines = []

    for line in lines:
        if '<%' in line or '<script' in line:
            obfuscated_line = line.replace('<%', obfuscate_tag('<%')).replace('<script', obfuscate_tag('<script'))
        else:
            obfuscated_line = line
        
        obfuscated_lines.append(obfuscated_line)

    return '\n'.join(obfuscated_lines)

def obfuscate_jsp(code):
    def random_string(length=8):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    def obfuscate_tag(tag):
        return f"{tag} {random_string()}"

    lines = code.split('\n')
    obfuscated_lines = []

    for line in lines:
        if '<%' in line:
            obfuscated_line = line.replace('<%', obfuscate_tag('<%'))
        elif '<script' in line:
            obfuscated_line = line.replace('<script', obfuscate_tag('<script'))
        else:
            obfuscated_line = line
        
        obfuscated_lines.append(obfuscated_line)

    return '\n'.join(obfuscated_lines)

def obfuscate_py3(code):
    def random_string(length=8):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    lines = code.split('\n')
    obfuscated_lines = []

    for line in lines:
        if '=' in line:
            line_parts = line.split('=')
            obfuscated_line = f"{line_parts[0]} = {line_parts[1].strip()} # {random_string()}"
        else:
            obfuscated_line = line
        
        obfuscated_lines.append(obfuscated_line)

    return '\n'.join(obfuscated_lines)

def obfuscate_sh(code):
    def random_string(length=8):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    lines = code.split('\n')
    obfuscated_lines = []

    for line in lines:
        if line.strip().startswith('function '):
            obfuscated_line = line.replace('function ', f"function_{random_string()} ")
        elif '=' in line:
            line_parts = line.split('=')
            obfuscated_line = f"{line_parts[0]}={line_parts[1].strip()} # {random_string()}"
        else:
            obfuscated_line = line
        
        obfuscated_lines.append(obfuscated_line)

    return '\n'.join(obfuscated_lines)

