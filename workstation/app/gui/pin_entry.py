from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PinEntry(QWidget):
    pin_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        prompt = QLabel("Masukkan PIN Sesi Anda")
        prompt.setFont(QFont("Arial", 14))
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt.setStyleSheet("color: white;")
        layout.addWidget(prompt)

        self._pin_display = QLineEdit()
        self._pin_display.setReadOnly(True)
        self._pin_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pin_display.setFont(QFont("Courier New", 28, QFont.Weight.Bold))
        self._pin_display.setEchoMode(QLineEdit.EchoMode.Password)
        self._pin_display.setFixedSize(220, 60)
        self._pin_display.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.15);
                border: 2px solid rgba(255,255,255,0.5);
                border-radius: 8px;
                color: white;
                letter-spacing: 8px;
            }
        """)
        layout.addWidget(self._pin_display, alignment=Qt.AlignmentFlag.AlignCenter)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._error_label)

        keypad = QGridLayout()
        keypad.setSpacing(8)
        btn_style = """
            QPushButton {
                background: rgba(255,255,255,0.18);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(255,255,255,0.32); }
            QPushButton:pressed { background: rgba(255,255,255,0.45); }
        """
        for i, digit in enumerate("123456789"):
            btn = QPushButton(digit)
            btn.setFixedSize(70, 55)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda _, d=digit: self._append(d))
            keypad.addWidget(btn, i // 3, i % 3)

        clear_btn = QPushButton("⌫")
        clear_btn.setFixedSize(70, 55)
        clear_btn.setStyleSheet(btn_style)
        clear_btn.clicked.connect(self._backspace)
        keypad.addWidget(clear_btn, 3, 0)

        zero_btn = QPushButton("0")
        zero_btn.setFixedSize(70, 55)
        zero_btn.setStyleSheet(btn_style)
        zero_btn.clicked.connect(lambda: self._append("0"))
        keypad.addWidget(zero_btn, 3, 1)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(70, 55)
        ok_btn.setStyleSheet(btn_style.replace("rgba(255,255,255,0.18)", "rgba(40,167,69,0.7)"))
        ok_btn.clicked.connect(self._submit)
        keypad.addWidget(ok_btn, 3, 2)

        layout.addLayout(keypad)

    def _append(self, digit: str):
        current = self._pin_display.text()
        if len(current) < 6:
            self._pin_display.setText(current + digit)
            self._error_label.setText("")

    def _backspace(self):
        self._pin_display.setText(self._pin_display.text()[:-1])
        self._error_label.setText("")

    def _submit(self):
        pin = self._pin_display.text()
        if len(pin) != 6:
            self._error_label.setText("PIN harus 6 digit")
            return
        self.pin_submitted.emit(pin)

    def show_error(self, msg: str):
        self._error_label.setText(msg)
        self._pin_display.clear()

    def clear(self):
        self._pin_display.clear()
        self._error_label.setText("")

    def keyPressEvent(self, event):
        key = event.key()
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            self._append(str(key - Qt.Key.Key_0))
        elif key == Qt.Key.Key_Backspace:
            self._backspace()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._submit()
