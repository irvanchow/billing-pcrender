from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QMouseEvent
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from shared.constants import WARNING_THRESHOLD_SECONDS


class TimerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(240, 80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self._name_label = QLabel()
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_label.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(self._name_label)

        self._time_label = QLabel("00:00:00")
        self._time_label.setFont(QFont("Courier New", 22, QFont.Weight.Bold))
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._time_label)

        self._normal_style = """
            QWidget { background: rgba(33, 37, 41, 200); border-radius: 8px; }
            QLabel { color: white; }
        """
        self._warning_style = """
            QWidget { background: rgba(220, 53, 69, 210); border-radius: 8px; }
            QLabel { color: white; }
        """
        self.setStyleSheet(self._normal_style)

        self._drag_pos = None
        self._remaining = 0

        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(1000)

        self._position_bottom_right()

    def _position_bottom_right(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 60)

    def set_session(self, student_name: str, remaining_seconds: int):
        self._name_label.setText(student_name)
        self._remaining = remaining_seconds
        self._update_display()

    def sync_remaining(self, remaining_seconds: int):
        self._remaining = remaining_seconds

    def _tick(self):
        if self._remaining > 0:
            self._remaining -= 1
        self._update_display()

    def _update_display(self):
        h, rem = divmod(self._remaining, 3600)
        m, s = divmod(rem, 60)
        self._time_label.setText(f"{h:02d}:{m:02d}:{s:02d}")
        if self._remaining <= WARNING_THRESHOLD_SECONDS:
            self.setStyleSheet(self._warning_style)
        else:
            self.setStyleSheet(self._normal_style)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def closeEvent(self, event):
        event.ignore()
