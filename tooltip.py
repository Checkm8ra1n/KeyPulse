from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal


class KeyListener(QObject):
    key_pressed = pyqtSignal(str)

    def __init__(self, tray_app):
        super().__init__()
        self.tray_app = tray_app
        self.listener = keyboard.Listener(on_press=self.on_press)

    def start(self):
        self.listener.start()

    def on_press(self, key):
        if not self.tray_app.enabled:
            return

        try:
            char = key.char
            self.key_pressed.emit(char)  # manda al main thread
        except AttributeError:
            pass