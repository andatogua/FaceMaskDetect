from PyQt5.QtWidgets import QApplication
from ui.ui import MainWindow

import sys

def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()