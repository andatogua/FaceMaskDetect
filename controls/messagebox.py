from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class TimerMessageBox(QMessageBox):
    def __init__(self, timeout=3, parent=None):
        super(TimerMessageBox, self).__init__(parent)
        self.setWindowTitle("Atención..!!")
        self.setIcon(QMessageBox.Warning)
        self.time_to_wait = timeout
        self.setText("Número máximo de personas sin mascarillas superado..!")
        self.setStandardButtons(QMessageBox.NoButton)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

    def changeContent(self):
        self.setText("Número máximo de personas sin mascarillas superado..!\nPor favor use mascarilla")
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.close()