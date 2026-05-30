"""
Windows-only kiosk keyboard hook using Win32 API via ctypes.
On non-Windows systems this module is a no-op stub so the rest of the
app can be developed and tested on Linux/macOS.
"""
import ctypes
import platform
import sys

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    import ctypes.wintypes as wintypes

    WH_KEYBOARD_LL = 13
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_SYSKEYDOWN = 0x0104
    WM_SYSKEYUP = 0x0105

    # Virtual key codes to block
    _BLOCKED_VKEYS = {
        0x5B,  # VK_LWIN
        0x5C,  # VK_RWIN
        0x1B,  # VK_ESCAPE
        0x09,  # VK_TAB  (blocks Alt+Tab when Alt is held)
        0x24,  # VK_HOME
        0x23,  # VK_END
        0x2E,  # VK_DELETE
    }

    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("vkCode", wintypes.DWORD),
            ("scanCode", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    _HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    _hook_handle = None
    _hook_func_ref = None  # keep alive; GC would remove it otherwise

    def _make_hook_proc():
        def _proc(nCode, wParam, lParam):
            if nCode >= 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN, WM_KEYUP, WM_SYSKEYUP):
                kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                if kb.vkCode in _BLOCKED_VKEYS:
                    return 1
            return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
        return _HOOKPROC(_proc)

    def install() -> None:
        global _hook_handle, _hook_func_ref
        if _hook_handle:
            return
        _hook_func_ref = _make_hook_proc()
        _hook_handle = ctypes.windll.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            _hook_func_ref,
            ctypes.windll.kernel32.GetModuleHandleW(None),
            0,
        )

    def remove() -> None:
        global _hook_handle, _hook_func_ref
        if _hook_handle:
            ctypes.windll.user32.UnhookWindowsHookEx(_hook_handle)
            _hook_handle = None
            _hook_func_ref = None

    def set_topmost(hwnd: int, width: int, height: int) -> None:
        SWP_SHOWWINDOW = 0x0040
        HWND_TOPMOST = -1
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, width, height, SWP_SHOWWINDOW
        )

else:
    # Stub for non-Windows development
    def install() -> None:
        pass

    def remove() -> None:
        pass

    def set_topmost(hwnd: int, width: int, height: int) -> None:
        pass
