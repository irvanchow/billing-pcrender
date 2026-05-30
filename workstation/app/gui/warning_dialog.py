from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class WarningDialog(QDialog):
    def __init__(self, remaining_seconds: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Waktu Hampir Habis!")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog { background: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; }
            QLabel { color: #856404; }
            QPushButton { background: #ffc107; border: none; border-radius: 4px;
                          padding: 8px 24px; font-weight: bold; color: #333; }
            QPushButton:hover { background: #e0a800; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        icon_label = QLabel("⚠️  PERHATIAN")
        icon_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        m, s = divmod(remaining_seconds, 60)
        self._msg = QLabel(f"Sisa waktu penggunaan Anda:\n<b>{m:02d}:{s:02d} menit</b>\n\nHubungi operator untuk perpanjangan.")
        self._msg.setFont(QFont("Arial", 11))
        self._msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self._msg)

        ok_btn = QPushButton("Saya Mengerti")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._auto_close = QTimer(self)
        self._auto_close.setSingleShot(True)
        self._auto_close.timeout.connect(self.accept)
        self._auto_close.start(15000)

    def _center(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
        )

    def showEvent(self, event):
        super().showEvent(event)
        self._center()
