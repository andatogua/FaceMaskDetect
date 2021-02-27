from PyQt5.QtWidgets import QApplication
from controls.ui import MainWindow
from models.db.db import PrepareDatabase
import sys

def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    w = MainWindow()
    if PrepareDatabase():
        w.statusBar().showMessage('Conectado | Presione Iniciar para comenzar con las detecciones')
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()