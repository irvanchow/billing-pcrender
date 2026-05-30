import sys

from PyQt6.QtCore import QMetaObject, Qt, pyqtSlot
from PyQt6.QtWidgets import QApplication

from workstation.app.api_client import PollingThread, report_expired
from workstation.app.core.session_state import SessionState, State
from workstation.app.gui.lock_screen import LockScreen
from workstation.app.gui.timer_overlay import TimerOverlay
from workstation.app.gui.warning_dialog import WarningDialog
from shared.constants import WARNING_THRESHOLD_SECONDS


class KioskController:
    """Owns all app state and coordinates UI components."""

    def __init__(self, qt_app: QApplication):
        self._app = qt_app
        self._state = SessionState()

        self._lock_screens: list[LockScreen] = []
        for screen in qt_app.screens():
            ls = LockScreen(screen_geometry=screen.geometry())
            ls.unlocked.connect(self._on_unlocked)
            self._lock_screens.append(ls)

        self._timer_overlay = TimerOverlay()
        self._polling = PollingThread(on_status=self._on_poll_result)

    def start(self):
        for ls in self._lock_screens:
            ls.show_locked()
        self._polling.start()

    def show_lock(self):
        self._timer_overlay.hide()
        for ls in self._lock_screens:
            ls.show_locked()

    def hide_lock(self):
        for ls in self._lock_screens:
            ls.hide_locked()
        self._timer_overlay.show()

    def show_warning(self):
        remaining = self._state.remaining_seconds()
        dlg = WarningDialog(remaining_seconds=remaining)
        dlg.exec()

    def _on_unlocked(self, session_id: int, student_name: str, expires_at: str):
        self._state.activate(session_id, student_name, expires_at)
        remaining = self._state.remaining_seconds()
        self._timer_overlay.set_session(student_name, remaining)
        self.hide_lock()

    def _on_poll_result(self, data: dict):
        status = data.get("status")

        if status == "ACTIVE":
            if self._state.state == State.LOCKED:
                return

            new_expires = data.get("expires_at")
            if new_expires:
                self._state.sync_expiry(new_expires)
                remaining_from_server = data.get("remaining_seconds", 0)
                self._timer_overlay.sync_remaining(remaining_from_server)

            remaining = self._state.remaining_seconds()
            if remaining <= 0:
                self._expire()
                return

            if remaining <= WARNING_THRESHOLD_SECONDS and not self._state.warning_shown:
                self._state.warning_shown = True
                QMetaObject.invokeMethod(
                    self._app, "on_show_warning", Qt.ConnectionType.QueuedConnection
                )

        elif status == "LOCK":
            QMetaObject.invokeMethod(
                self._app, "on_force_lock", Qt.ConnectionType.QueuedConnection
            )

        elif status == "IDLE":
            if self._state.state == State.ACTIVE:
                self._state.lock()
                QMetaObject.invokeMethod(
                    self._app, "on_force_lock", Qt.ConnectionType.QueuedConnection
                )

    def _expire(self):
        if self._state.state == State.ACTIVE:
            report_expired(self._state.session_id)
        self._state.lock()
        QMetaObject.invokeMethod(
            self._app, "on_force_lock", Qt.ConnectionType.QueuedConnection
        )


class KioskApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("IDB Kiosk Timer")
        self.setQuitOnLastWindowClosed(False)
        self._controller = KioskController(self)

    def start(self):
        self._controller.start()

    @pyqtSlot()
    def on_force_lock(self):
        self._controller._state.lock()
        self._controller.show_lock()

    @pyqtSlot()
    def on_show_warning(self):
        self._controller.show_warning()


def main():
    app = KioskApp(sys.argv)
    app.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
