from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from server.app.gui.dashboard_tab import DashboardTab
from server.app.gui.history_tab import HistoryTab
from server.app.gui.register_tab import RegisterTab
from server.app.gui.tray_icon import TrayIcon


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IDB Bali — Sistem Peminjaman PC Render")
        self.setMinimumSize(QSize(900, 600))

        tabs = QTabWidget()
        self._register_tab = RegisterTab()
        self._dashboard_tab = DashboardTab()
        self._history_tab = HistoryTab()

        tabs.addTab(self._register_tab, "Daftar Sesi")
        tabs.addTab(self._dashboard_tab, "Sesi Aktif")
        tabs.addTab(self._history_tab, "Riwayat")
        self.setCentralWidget(tabs)

        self._register_tab.session_created.connect(self._dashboard_tab.refresh)

        self._tray = TrayIcon(self, self)
        self._tray.show()

        tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int):
        if index == 1:
            self._dashboard_tab.refresh()
        elif index == 2:
            self._history_tab.refresh()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._tray.showMessage(
            "IDB PC Rental",
            "Aplikasi berjalan di background. Klik ikon tray untuk membuka.",
        )
