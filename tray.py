import sys
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QCursor, QIcon, QAction
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QToolTip
from tooltip import KeyListener
from pynput import keyboard
import platform
import os

class HotkeyListener(QObject):
    toggle_signal = pyqtSignal()  # signal per main thread

    def __init__(self):
        super().__init__()

    def start(self):
        # definisci combinazione Ctrl+Alt+K
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<alt>+k'),
            self.toggle_signal.emit
        )

        def for_canonical(f):
            return lambda k: f(listener.canonical(k))

        listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        )
        listener.start()


class TrayApp:
    def __init__(self):
        
        if platform.system() == "Darwin":  # macOS
            try:
                print("Setting macOS app to accessory mode to hide Dock icon...")
                from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
                NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
            except Exception as e:
                print(f"Warning: impossibile nascondere Dock icon: {e}")

        self.app = QApplication(sys.argv)
        self.enabled = True

        # Tray icon
        self.tray = QSystemTrayIcon()
        if getattr(sys, 'frozen', False):  # Se siamo in PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")        
        icon_path = os.path.join(base_path, "icon.png")
        self.tray.setIcon(QIcon(icon_path))
        self.tray.setToolTip("KeyPulse ⚡")

        # Menu
        self.menu = QMenu()

        # Toggle action
        self.toggle_action = QAction("Enable KeyPulse", self.menu)
        self.toggle_action.setCheckable(True)
        self.toggle_action.setChecked(True)
        # Aggiungi la descrizione della combinazione (solo visivo)
        self.toggle_action.setShortcutVisibleInContextMenu(True)
        self.toggle_action.setShortcut("Ctrl+Alt+K")  # visibile nel menu
        self.toggle_action.triggered.connect(self.toggle)
        self.menu.addAction(self.toggle_action)

        self.menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", self.menu)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)

        # Set menu e mostra tray
        self.tray.setContextMenu(self.menu)
        self.tray.show()

        # Listener ASCII thread-safe
        self.listener = KeyListener(self)
        self.listener.key_pressed.connect(self.show_tooltip)
        self.listener.start()

        # Hotkey globale thread-safe
        self.hotkey_listener = HotkeyListener()
        self.hotkey_listener.toggle_signal.connect(self.toggle_hotkey)
        self.hotkey_listener.start()

    # Toggle tray menu
    def toggle(self):
        self.enabled = self.toggle_action.isChecked()
        print(f"KeyPulse enabled: {self.enabled}")

    # Toggle hotkey (main thread safe)
    def toggle_hotkey(self):
        self.enabled = not self.enabled
        self.toggle_action.setChecked(self.enabled)

        msg = "KeyPulse ON" if self.enabled else "KeyPulse OFF"
        pos = QCursor.pos()
        QToolTip.showText(pos + QPoint(10, 10), msg)
        QTimer.singleShot(1000, QToolTip.hideText)

        print(f"KeyPulse enabled (hotkey): {self.enabled}")

    # Exit
    def exit_app(self):
        self.tray.hide()
        self.app.quit()

    # Run app
    def run(self):
        sys.exit(self.app.exec())

    # Tooltip ASCII thread-safe
    def show_tooltip(self, char):
        if not char:
            return
        try:
            ascii_code = ord(char)
        except TypeError:
            return

        pos = QCursor.pos()
        QToolTip.showText(pos + QPoint(10, 10), str(ascii_code))
        QTimer.singleShot(700, QToolTip.hideText)