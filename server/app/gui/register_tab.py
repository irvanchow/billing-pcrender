from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from server.app.core.database import get_db
from server.app.core.pin_generator import generate_unique_pin
from server.app.core.session_manager import create_session
from shared.constants import SessionStatus


class RegisterTab(QWidget):
    session_created = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        form_box = QGroupBox("Data Mahasiswa")
        form = QFormLayout(form_box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Nama lengkap mahasiswa")
        self._nim_edit = QLineEdit()
        self._nim_edit.setPlaceholderText("NIM mahasiswa")

        self._prodi_combo = QComboBox()
        for prodi in [
            "Desain Komunikasi Visual",
            "Desain Interior",
            "Arsitektur",
            "Desain Mode",
            "Bisnis Digital",
            "Manajemen Retail",
            "Sistem & Teknologi Informasi",
        ]:
            self._prodi_combo.addItem(prodi)

        keterangan_widget = QWidget()
        keterangan_layout = QVBoxLayout(keterangan_widget)
        keterangan_layout.setContentsMargins(0, 0, 0, 0)
        keterangan_layout.setSpacing(2)
        self._keterangan_edit = QPlainTextEdit()
        self._keterangan_edit.setPlaceholderText("Tulis keterangan tambahan... (opsional)")
        self._keterangan_edit.setFixedHeight(80)
        self._keterangan_counter = QLabel("0/500")
        self._keterangan_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._keterangan_edit.textChanged.connect(self._update_keterangan_counter)
        keterangan_layout.addWidget(self._keterangan_edit)
        keterangan_layout.addWidget(self._keterangan_counter)

        self._pc_combo = QComboBox()
        self._pc_combo.addItem("PC-1", 1)
        self._pc_combo.addItem("PC-2", 2)
        self._pc_combo.addItem("PC-3", 3)
        self._pc_combo.addItem("PC-4", 4)

        self._duration_spin = QSpinBox()
        self._duration_spin.setRange(5, 480)
        self._duration_spin.setValue(60)
        self._duration_spin.setSuffix(" menit")

        form.addRow("Nama Mahasiswa:", self._name_edit)
        form.addRow("NIM:", self._nim_edit)
        form.addRow("Program Studi:", self._prodi_combo)
        form.addRow("Keterangan:", keterangan_widget)
        form.addRow("Workstation:", self._pc_combo)
        form.addRow("Durasi:", self._duration_spin)

        layout.addWidget(form_box)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._create_btn = QPushButton("Buat Sesi & Generate PIN")
        self._create_btn.setFixedHeight(40)
        self._create_btn.setDefault(True)
        self._create_btn.clicked.connect(self._on_create)
        btn_row.addWidget(self._create_btn)
        layout.addLayout(btn_row)

        self._pin_box = QFrame()
        self._pin_box.setFrameShape(QFrame.Shape.StyledPanel)
        self._pin_box.hide()
        pin_layout = QVBoxLayout(self._pin_box)
        pin_layout.setSpacing(8)

        pin_title = QLabel("PIN Sesi")
        pin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_layout.addWidget(pin_title)

        self._pin_label = QLabel()
        font = QFont("Courier New", 36, QFont.Weight.Bold)
        self._pin_label.setFont(font)
        self._pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pin_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        pin_layout.addWidget(self._pin_label)

        self._pin_info = QLabel()
        self._pin_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_layout.addWidget(self._pin_info)

        copy_btn = QPushButton("Salin PIN")
        copy_btn.clicked.connect(self._copy_pin)
        pin_layout.addWidget(copy_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self._pin_box)
        layout.addStretch()

    def _update_keterangan_counter(self):
        text = self._keterangan_edit.toPlainText()
        if len(text) > 500:
            cursor = self._keterangan_edit.textCursor()
            self._keterangan_edit.setPlainText(text[:500])
            self._keterangan_edit.setTextCursor(cursor)
        self._keterangan_counter.setText(f"{min(len(text), 500)}/500")

    def _on_create(self):
        name = self._name_edit.text().strip()
        nim = self._nim_edit.text().strip()
        if not name or not nim:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Nama dan NIM harus diisi.")
            return

        workstation_id = self._pc_combo.currentData()
        duration = self._duration_spin.value()
        program_studi = self._prodi_combo.currentText()
        keterangan = self._keterangan_edit.toPlainText().strip()

        with get_db() as conn:
            occupied = conn.execute(
                "SELECT id FROM sessions WHERE workstation_id = ? AND status IN (?, ?)",
                (workstation_id, SessionStatus.PENDING.value, SessionStatus.ACTIVE.value),
            ).fetchone()
            if occupied:
                pc_name = self._pc_combo.currentText()
                QMessageBox.warning(
                    self, "PC Sedang Digunakan",
                    f"{pc_name} sedang memiliki sesi aktif.\nAkhiri sesi tersebut terlebih dahulu.",
                )
                return

            pin = generate_unique_pin(conn)
            create_session(conn, workstation_id, name, nim, program_studi, keterangan, duration, pin)

        self._pin_label.setText("  ".join(pin))
        pc_name = self._pc_combo.currentText()
        self._pin_info.setText(f"PC: {pc_name}   |   Durasi: {duration} menit")
        self._pin_box.show()

        self._name_edit.clear()
        self._nim_edit.clear()
        self._keterangan_edit.clear()
        self._duration_spin.setValue(60)

        self.session_created.emit()

    def _copy_pin(self):
        from PyQt6.QtWidgets import QApplication
        pin_text = self._pin_label.text().replace("  ", "")
        QApplication.clipboard().setText(pin_text)
