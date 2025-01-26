import threading
from gui import run_gui
from listener import monitor_clipboard


# fix closing gui not stopping other threads
# self msg, copy to clipboard, copy to clipboard with comma, copy to clipboard with space
# on entry change, add functions to read and change entrys

# on hover tutorial
# global varialbe for clipboard


if __name__ == '__main__':
    clipboard_thread = threading.Thread(target=monitor_clipboard)
    clipboard_thread.start()

    run_gui()
    clipboard_thread.join()