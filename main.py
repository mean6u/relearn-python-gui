import sys
from PyQt6.QtWidgets import QApplication
from pyqtgui import guilauncher

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = guilauncher()
    gui.show()
    sys.exit(app.exec())