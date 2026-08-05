import ctypes
from ctypes import wintypes
import os
import re
import subprocess
import json

TH32CS_SNAPPROCESS = 0x00000002
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND)
    ]

def enumerate_processes():
    processes = []
    h_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if h_snapshot == -1:
        return []
    
    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    
    if ctypes.windll.kernel32.Process32First(h_snapshot, ctypes.byref(pe)):
        while True:
            exe_name = pe.szExeFile.decode('latin1', errors='ignore')
            processes.append({
                "pid": pe.th32ProcessID,
                "name": exe_name,
                "parent_pid": pe.th32ParentProcessID,
                "threads": pe.cntThreads
            })
            if not ctypes.windll.kernel32.Process32Next(h_snapshot, ctypes.byref(pe)):
                break
                
    ctypes.windll.kernel32.CloseHandle(h_snapshot)
    return processes

def get_process_path(pid):
    h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h_process:
        return None
    
    buf = ctypes.create_string_buffer(520) # WCHAR capacity
    size = wintypes.DWORD(260)
    # Using Unicode version for wider compatibility
    success = ctypes.windll.kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size))
    ctypes.windll.kernel32.CloseHandle(h_process)
    
    if success:
        # buf is WCHAR buffer, cast and decode
        return ctypes.cast(buf, ctypes.c_wchar_p).value
    return None

def get_process_command_lines():
    cmd_lines = {}
    try:
        # Try WMIC first
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        output = subprocess.check_output(
            ["wmic", "process", "get", "ProcessId,CommandLine"],
            startupinfo=startupinfo,
            stderr=subprocess.DEVNULL
        ).decode('latin1', errors='ignore')
        
        lines = output.strip().split('\n')[1:]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = re.search(r'\s+(\d+)$', line)
            if match:
                pid = int(match.group(1))
                cmd = line[:match.start()].strip()
                cmd_lines[pid] = cmd
    except Exception:
        # Fallback to PowerShell
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process | Select-Object ProcessId, CommandLine | ConvertTo-Json"],
                startupinfo=startupinfo,
                stderr=subprocess.DEVNULL
            ).decode('latin1', errors='ignore')
            
            data = json.loads(output)
            if isinstance(data, list):
                for item in data:
                    pid = item.get("ProcessId")
                    cmd = item.get("CommandLine")
                    if pid and cmd:
                        cmd_lines[pid] = cmd
            elif isinstance(data, dict):
                pid = data.get("ProcessId")
                cmd = data.get("CommandLine")
                if pid and cmd:
                    cmd_lines[pid] = cmd
        except Exception:
            pass
    return cmd_lines

def check_pe_imports(filepath):
    """
    Parses a PE file and extracts functions imported from USER32.dll 
    related to keyboard input hook/interception.
    """
    if not filepath or not os.path.exists(filepath):
        return []
        
    try:
        with open(filepath, 'rb') as f:
            if f.read(2) != b'MZ':
                return []
            f.seek(0x3C)
            pe_offset = int.from_bytes(f.read(4), 'little')
            f.seek(pe_offset)
            if f.read(4) != b'PE\0\0':
                return []
            
            # Read COFF header
            f.seek(2, 1) # Skip Machine
            num_sections = int.from_bytes(f.read(2), 'little')
            f.seek(12, 1) # Skip Timestamp, symbol pointers
            size_optional_header = int.from_bytes(f.read(2), 'little')
            f.seek(2, 1) # Skip Characteristics
            
            # Optional Header Magic
            magic = int.from_bytes(f.read(2), 'little')
            is_pe32_plus = magic == 0x20B  # PE32+ (64-bit)
            
            # Import data directory entry is at relative offset 104 (PE32) or 120 (PE32+)
            opt_header_start = pe_offset + 4 + 20
            import_dir_entry_offset = opt_header_start + (120 if is_pe32_plus else 104)
            
            f.seek(import_dir_entry_offset)
            import_rva = int.from_bytes(f.read(4), 'little')
            import_size = int.from_bytes(f.read(4), 'little')
            
            if import_rva == 0 or import_size == 0:
                return []
            
            # Read Section Headers to convert RVA to File Offset
            sections = []
            f.seek(opt_header_start + size_optional_header)
            for _ in range(num_sections):
                sec_name = f.read(8).rstrip(b'\0').decode('latin1', errors='ignore')
                misc = int.from_bytes(f.read(4), 'little')
                virtual_address = int.from_bytes(f.read(4), 'little')
                raw_data_size = int.from_bytes(f.read(4), 'little')
                raw_data_ptr = int.from_bytes(f.read(4), 'little')
                f.seek(16, 1) # Skip relocation & line number info
                sections.append({
                    'name': sec_name,
                    'va': virtual_address,
                    'size': misc,
                    'raw_ptr': raw_data_ptr,
                    'raw_size': raw_data_size
                })
            
            def rva_to_offset(rva):
                for sec in sections:
                    if sec['va'] <= rva < sec['va'] + max(sec['size'], sec['raw_size']):
                        return sec['raw_ptr'] + (rva - sec['va'])
                return None
            
            import_offset = rva_to_offset(import_rva)
            if import_offset is None:
                return []
            
            f.seek(import_offset)
            suspicious_funcs = [
                'SetWindowsHookEx', 
                'GetAsyncKeyState', 
                'GetKeyState', 
                'RegisterRawInputDevices', 
                'GetRawInputData'
            ]
            found_funcs = []
            
            while True:
                # 20 bytes entry in import directory table
                ilt_rva = int.from_bytes(f.read(4), 'little')
                f.seek(8, 1) # Skip TimeDateStamp & ForwarderChain
                name_rva = int.from_bytes(f.read(4), 'little')
                iat_rva = int.from_bytes(f.read(4), 'little')
                
                if ilt_rva == 0 and name_rva == 0:
                    break
                
                curr_pos = f.tell()
                
                # Resolve DLL name
                dll_name_offset = rva_to_offset(name_rva)
                if dll_name_offset is not None:
                    f.seek(dll_name_offset)
                    dll_name = b""
                    while True:
                        char = f.read(1)
                        if char == b"\0" or len(char) == 0:
                            break
                        dll_name += char
                    dll_name = dll_name.decode('latin1', errors='ignore').lower()
                    
                    if dll_name == 'user32.dll':
                        ilt_offset = rva_to_offset(ilt_rva or iat_rva)
                        if ilt_offset is not None:
                            f.seek(ilt_offset)
                            ptr_size = 8 if is_pe32_plus else 4
                            while True:
                                entry = int.from_bytes(f.read(ptr_size), 'little')
                                if entry == 0:
                                    break
                                
                                # Ignore ordinal imports (MSB is set)
                                msb_mask = 1 << (ptr_size * 8 - 1)
                                if not (entry & msb_mask):
                                    name_offset = rva_to_offset(entry)
                                    if name_offset is not None:
                                        inner_pos = f.tell()
                                        f.seek(name_offset + 2) # Skip Hint
                                        func_name = b""
                                        while True:
                                            char = f.read(1)
                                            if char == b"\0" or len(char) == 0:
                                                break
                                            func_name += char
                                        func_name = func_name.decode('latin1', errors='ignore')
                                        f.seek(inner_pos)
                                        
                                        for susp in suspicious_funcs:
                                            if susp in func_name:
                                                found_funcs.append(func_name)
                f.seek(curr_pos)
                
            return list(set(found_funcs))
    except Exception:
        return []

def check_registered_raw_input_devices():
    """
    Checks if there are registered raw input devices on the system.
    Returns list of matching keyboard sinks.
    """
    user32 = ctypes.windll.user32

    # Declare argtypes so Python 3.13 passes correct types
    user32.GetRegisteredRawInputDevices.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(wintypes.UINT), wintypes.UINT
    ]
    user32.GetRegisteredRawInputDevices.restype = wintypes.UINT

    num_devices = wintypes.UINT(0)
    cb_size     = wintypes.UINT(ctypes.sizeof(RAWINPUTDEVICE))

    # First call with NULL buffer to get count
    res = user32.GetRegisteredRawInputDevices(None, ctypes.byref(num_devices), cb_size)
    # Returns (UINT)-1 on error – compare as signed
    if ctypes.c_int(res).value == -1:
        return []

    dev_list = []
    if num_devices.value > 0:
        devices = (RAWINPUTDEVICE * num_devices.value)()
        res = user32.GetRegisteredRawInputDevices(
            ctypes.byref(devices), ctypes.byref(num_devices), cb_size
        )
        if ctypes.c_int(res).value != -1:
            for i in range(num_devices.value):
                # usUsagePage = 1, usUsage = 6 → Keyboard
                if devices[i].usUsagePage == 1 and devices[i].usUsage == 6:
                    dev_list.append({
                        "usage_page": devices[i].usUsagePage,
                        "usage":      devices[i].usUsage,
                        "flags":      devices[i].dwFlags,
                        "hwnd":       devices[i].hwndTarget,
                    })
    return dev_list

class KeyloggerDetector:
    def __init__(self):
        pass
        
    def scan_system(self):
        """
        Runs a comprehensive heuristic scan of running processes and windows subsystems.
        """
        scan_logs = ["Initiating System Keystroke Interception Diagnostic...",
                     "Enumerating active processes...",
                     "Checking registered Raw Input sinks...",
                     "Analyzing Import Address Tables (IAT) for User32 keyboard APIs..."]
        
        processes = enumerate_processes()
        cmd_lines = get_process_command_lines()
        registered_raw_inputs = check_registered_raw_input_devices()
        
        # Track whether a raw input listener was detected
        raw_input_detected = len(registered_raw_inputs) > 0
        if raw_input_detected:
            scan_logs.append(f"[WARNING] Detected {len(registered_raw_inputs)} active Raw Input keyboard listeners!")
            
        reports = []
        highest_threat = 0
        current_pid = os.getpid()
        
        for p in processes:
            pid = p["pid"]
            name = p["name"]
            
            # Skip idle process / system process that we can't open anyway
            if pid in (0, 4):
                continue
                
            path = get_process_path(pid)
            cmd = cmd_lines.get(pid, "")
            
            # Skip scanning our own process for clean reports, though we could scan it
            if pid == current_pid:
                continue
                
            threat_score = 0
            reasons = []
            
            # Heuristic 1: Command line analysis (highly specific to Python simulators)
            suspicious_args = ["PROJECTmain.py", "win32_keylogger", "app.py", "keylogger.py", "keylog.txt"]
            for arg in suspicious_args:
                if arg.lower() in cmd.lower():
                    threat_score += 45
                    reasons.append(f"Command line contains suspicious script signature: '{arg}'")
                    break
                    
            # Heuristic 2: Suspicious process names
            suspicious_names = ["keylog", "logger", "spykey", "keyboardhook", "hookkey"]
            for sname in suspicious_names:
                if sname in name.lower():
                    threat_score += 35
                    reasons.append(f"Process executable name match: '{name}'")
                    break
                    
            # Heuristic 3: PE imports parsing
            imported_apis = []
            if path and os.path.exists(path):
                imported_apis = check_pe_imports(path)
                
            if imported_apis:
                threat_score += 25
                apis_str = ", ".join(imported_apis)
                reasons.append(f"Imports Win32 keyboard interception APIs: [{apis_str}]")
                # Escalations based on specific critical API presence
                if any("SetWindowsHook" in api for api in imported_apis):
                    threat_score += 15
                if any("GetAsyncKeyState" in api for api in imported_apis):
                    threat_score += 10
                if any("RegisterRawInput" in api for api in imported_apis):
                    threat_score += 15
                    
            # Heuristic 4: Is in Temp directory
            if path and ("\\temp\\" in path.lower() or "\\tmp\\" in path.lower()):
                threat_score += 15
                reasons.append("Executable running from temporary directory")
                
            # If the process is a Python instance running our dashboard/script, scale down
            # to prevent it from confusing users unless it matches exact keylogger signature.
            # However, if it's the actual background keylogger running from command line, it's correct to show it.
            
            if threat_score > 100:
                threat_score = 100
                
            if threat_score >= 25:
                highest_threat = max(highest_threat, threat_score)
                reports.append({
                    "pid": pid,
                    "name": name,
                    "path": path or "Access Denied / System",
                    "cmd": cmd or "Access Denied",
                    "threat_score": threat_score,
                    "reasons": reasons,
                    "apis": imported_apis
                })
                
        # Sort reports by threat score descending
        reports.sort(key=lambda x: x["threat_score"], reverse=True)
        
        scan_logs.append("Diagnostic complete.")
        scan_logs.append(f"Scanned {len(processes)} active processes. Flagged {len(reports)} suspicious items.")
        
        # Calculate system state
        system_status = "Secure"
        if highest_threat > 70:
            system_status = "Critical"
        elif highest_threat >= 30:
            system_status = "Warning"
            
        return {
            "status": system_status,
            "threat_level": highest_threat,
            "raw_input_sinks": len(registered_raw_inputs),
            "reports": reports,
            "logs": scan_logs
        }
