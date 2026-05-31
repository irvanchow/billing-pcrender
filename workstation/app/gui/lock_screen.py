import os
import sys

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from workstation.app.api_client import unlock_with_pin
from workstation.app.core import kiosk_lock
from workstation.app.core.config import PC_ID
from workstation.app.gui.pin_entry import PinEntry


def _logo_path() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
    return os.path.join(base, "logo.png")


class LockScreen(QWidget):
    unlocked = pyqtSignal(int, str, str)  # session_id, student_name, expires_at
    it_exit_requested = pyqtSignal()  # Signal untuk IT exit

    def __init__(self, screen_geometry=None, parent=None):
        super().__init__(parent)
        self._screen_geo = screen_geometry
        self._build_ui()
        self._setup_window()
        self._focus_guard = QTimer(self)
        self._focus_guard.timeout.connect(self._assert_topmost)
        self._focus_guard.start(500)

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        if self._screen_geo:
            self.setGeometry(self._screen_geo)
        else:
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("QWidget { background: qlineargradient("
                           "x1:0, y1:0, x2:1, y2:1, "
                           "stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460); }")

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(_logo_path())
        if not pix.isNull():
            logo_label.setPixmap(pix.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(logo_label)

        # Title
        title = QLabel("IDB Bali — PC Render")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-top: 8px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._status_label = QLabel(f"PC-{PC_ID} — Tersedia")
        self._status_label.setFont(QFont("Arial", 12))
        self._status_label.setStyleSheet("color: rgba(255,255,255,0.7); margin-bottom: 24px;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        self._pin_entry = PinEntry()
        self._pin_entry.pin_submitted.connect(self._on_pin_submitted)
        self._pin_entry.installEventFilter(self)  # Intercept keys before PinEntry
        layout.addWidget(self._pin_entry, alignment=Qt.AlignmentFlag.AlignCenter)

    def _assert_topmost(self):
        geo = self.geometry()
        kiosk_lock.set_topmost(int(self.winId()), geo.width(), geo.height())
        if not self.isActiveWindow():
            self.activateWindow()
            self.raise_()

    def _on_pin_submitted(self, pin: str):
        try:
            result = unlock_with_pin(pin)
        except RuntimeError as e:
            self._pin_entry.show_error(str(e))
            return
        self._pin_entry.clear()
        self.unlocked.emit(
            result["session_id"],
            result["student_name"],
            result["expires_at"],
        )

    def show_locked(self):
        self._status_label.setText(f"PC-{PC_ID} — Tersedia")
        self._pin_entry.clear()
        kiosk_lock.install()
        self._focus_guard.start(500)
        self.show()
        self._assert_topmost()

    def hide_locked(self):
        self._focus_guard.stop()
        kiosk_lock.remove()
        self.hide()

    def closeEvent(self, event):
        event.ignore()

    def eventFilter(self, obj, event):
        """Intercept keyboard events from PinEntry to catch IT escape key"""
        if event.type() == QEvent.Type.KeyPress:
            # Check for Ctrl+Shift+Q
            ctrl_shift = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
            if event.key() == Qt.Key.Key_Q and (event.modifiers() & ctrl_shift) == ctrl_shift:
                self.it_exit_requested.emit()
                return True  # Block event from reaching PinEntry

        # Pass event to target widget
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        # Check for Ctrl+Shift+Q
        ctrl_shift = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
        if event.key() == Qt.Key.Key_Q and (event.modifiers() & ctrl_shift) == ctrl_shift:
            self.it_exit_requested.emit()
            return

        # Pass to parent for normal handling
        super().keyPressEvent(event)
