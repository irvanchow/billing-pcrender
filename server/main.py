import sys
import threading

import uvicorn

from server.app.core.config import HOST, PORT, write_default_config
from server.app.core.database import init_db


def start_api_server():
    from server.app.api.router import app
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


def main():
    write_default_config()
    init_db()

    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()

    # Import PyQt6 here so headless environments can still run the API-only mode
    try:
        from PyQt6.QtWidgets import QApplication
        from server.app.gui.main_window import MainWindow

        qt_app = QApplication(sys.argv)
        qt_app.setApplicationName("IDB PC Rental — Operator")
        qt_app.setQuitOnLastWindowClosed(False)

        window = MainWindow()
        window.show()

        sys.exit(qt_app.exec())
    except ImportError:
        print(f"Server running on http://{HOST}:{PORT}")
        api_thread.join()


if __name__ == "__main__":
    main()
