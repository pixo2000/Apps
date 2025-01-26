import threading
from gui import run_gui
from listener import monitor_clipboard


# fix closing gui not stopping other threads


if __name__ == '__main__':
    clipboard_thread = threading.Thread(target=monitor_clipboard)
    clipboard_thread.start()

    run_gui()
    clipboard_thread.join()