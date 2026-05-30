import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


def _get_icon() -> QIcon:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
    path = os.path.join(base, "icon.ico")
    if os.path.exists(path):
        return QIcon(path)
    return QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, main_window, parent=None):
        super().__init__(_get_icon(), parent)
        self._window = main_window
        self.setToolTip("IDB PC Rental — Operator")
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        menu = QMenu()
        show_action = menu.addAction("Tampilkan")
        show_action.triggered.connect(self._show_window)
        menu.addSeparator()
        quit_action = menu.addAction("Keluar")
        quit_action.triggered.connect(QApplication.quit)
        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()
