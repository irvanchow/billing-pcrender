from datetime import datetime, timezone

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from server.app.core.database import get_db
from server.app.core.session_manager import compute_remaining, extend_session, terminate_session
from shared.constants import SessionStatus, WARNING_THRESHOLD_SECONDS

_COLUMNS = ["ID", "PC", "Mahasiswa", "NIM", "PIN", "Status", "Sisa Waktu", "Aksi"]
_COL_IDX = {name: i for i, name in enumerate(_COLUMNS)}


class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(5000)
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Sesi Aktif</b>"))
        header.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(_COL_IDX["ID"], QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(_COL_IDX["Aksi"], QHeaderView.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def refresh(self):
        with get_db() as conn:
            rows = conn.execute(
                "SELECT s.*, w.name as pc_name FROM sessions s "
                "JOIN workstations w ON w.id = s.workstation_id "
                "WHERE s.status IN (?, ?) ORDER BY s.created_at DESC",
                (SessionStatus.PENDING.value, SessionStatus.ACTIVE.value),
            ).fetchall()

        self._table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            d = dict(row)
            remaining = compute_remaining(d.get("expires_at")) if d["status"] == SessionStatus.ACTIVE.value else None

            values = [
                str(d["id"]),
                d["pc_name"],
                d["student_name"],
                d["nim"],
                d["pin"],
                d["status"],
                self._fmt_remaining(remaining, d["status"]),
            ]
            for c_idx, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if d["status"] == SessionStatus.ACTIVE.value and remaining is not None:
                    if remaining <= WARNING_THRESHOLD_SECONDS:
                        item.setBackground(QColor("#fff3cd"))
                    else:
                        item.setBackground(QColor("#d4edda"))
                self._table.setItem(r_idx, c_idx, item)

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)

            extend_btn = QPushButton("+Perpanjang")
            extend_btn.setFixedHeight(26)
            extend_btn.clicked.connect(lambda _, sid=d["id"]: self._extend(sid))
            btn_layout.addWidget(extend_btn)

            end_btn = QPushButton("Akhiri")
            end_btn.setFixedHeight(26)
            end_btn.setStyleSheet("QPushButton { color: #dc3545; }")
            end_btn.clicked.connect(lambda _, sid=d["id"], name=d["student_name"]: self._terminate(sid, name))
            btn_layout.addWidget(end_btn)

            self._table.setCellWidget(r_idx, _COL_IDX["Aksi"], btn_widget)

    def _fmt_remaining(self, remaining: int | None, status: str) -> str:
        if status == SessionStatus.PENDING.value:
            return "Menunggu login"
        if remaining is None:
            return "-"
        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _extend(self, session_id: int):
        minutes, ok = QInputDialog.getInt(
            self, "Perpanjang Sesi", "Tambah durasi (menit):", value=30, min=5, max=480,
        )
        if not ok:
            return
        with get_db() as conn:
            result = extend_session(conn, session_id, minutes)
        if result is None:
            QMessageBox.warning(self, "Gagal", "Sesi tidak dapat diperpanjang.")
            return
        self.refresh()

    def _terminate(self, session_id: int, student_name: str):
        reply = QMessageBox.question(
            self, "Akhiri Sesi",
            f"Akhiri sesi {student_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        with get_db() as conn:
            terminate_session(conn, session_id)
        self.refresh()
