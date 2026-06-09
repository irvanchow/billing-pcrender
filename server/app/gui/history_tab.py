from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QDate

from server.app.core.database import get_db

_COLUMNS = ["ID", "Tanggal", "PC", "Mahasiswa", "NIM", "Durasi", "Diperpanjang", "Status", "Mulai", "Selesai"]


class HistoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = 1
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Tanggal:"))
        self._date_edit = QDateEdit(QDate.currentDate())
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        filter_row.addWidget(self._date_edit)

        filter_row.addWidget(QLabel("PC:"))
        self._pc_combo = QComboBox()
        self._pc_combo.addItem("Semua", None)
        self._pc_combo.addItem("PC-1", 1)
        self._pc_combo.addItem("PC-2", 2)
        self._pc_combo.addItem("PC-3", 3)
        self._pc_combo.addItem("PC-4", 4)
        filter_row.addWidget(self._pc_combo)

        search_btn = QPushButton("Cari")
        search_btn.clicked.connect(self._on_search)
        filter_row.addWidget(search_btn)
        filter_row.addStretch()

        self._info_label = QLabel()
        filter_row.addWidget(self._info_label)

        prev_btn = QPushButton("◀ Sebelumnya")
        prev_btn.clicked.connect(self._prev_page)
        self._prev_btn = prev_btn
        filter_row.addWidget(prev_btn)

        next_btn = QPushButton("Selanjutnya ▶")
        next_btn.clicked.connect(self._next_page)
        self._next_btn = next_btn
        filter_row.addWidget(next_btn)

        layout.addLayout(filter_row)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def _on_search(self):
        self._page = 1
        self.refresh()

    def _prev_page(self):
        if self._page > 1:
            self._page -= 1
            self.refresh()

    def _next_page(self):
        self._page += 1
        self.refresh()

    def refresh(self):
        date_str = self._date_edit.date().toString("yyyy-MM-dd")
        ws_id = self._pc_combo.currentData()
        limit = 50

        clauses = ["DATE(s.created_at) = ?"]
        params: list = [date_str]
        if ws_id:
            clauses.append("s.workstation_id = ?")
            params.append(ws_id)

        where = "WHERE " + " AND ".join(clauses)
        count_row = None
        with get_db() as conn:
            count_row = conn.execute(
                f"SELECT COUNT(*) FROM sessions s {where}", params
            ).fetchone()
            total = count_row[0] if count_row else 0

            offset = (self._page - 1) * limit
            rows = conn.execute(
                f"SELECT s.*, w.name as pc_name FROM sessions s "
                f"JOIN workstations w ON w.id = s.workstation_id "
                f"{where} ORDER BY s.created_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset],
            ).fetchall()

        total_pages = max(1, (total + limit - 1) // limit)
        self._info_label.setText(f"Hal {self._page}/{total_pages} | Total: {total}")
        self._prev_btn.setEnabled(self._page > 1)
        self._next_btn.setEnabled(self._page < total_pages)

        self._table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            d = dict(row)
            total_dur = d["duration_minutes"] + d["extended_minutes"]
            ext_str = f"+{d['extended_minutes']} mnt" if d["extended_minutes"] else "-"
            started = d.get("started_at", "")[:16] if d.get("started_at") else "-"
            ended = d.get("ended_at", "")[:16] if d.get("ended_at") else "-"
            values = [
                str(d["id"]),
                d["created_at"][:10],
                d["pc_name"],
                d["student_name"],
                d["nim"],
                f"{total_dur} mnt",
                ext_str,
                d["status"],
                started,
                ended,
            ]
            for c_idx, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(r_idx, c_idx, item)
