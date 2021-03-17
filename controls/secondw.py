from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import os

class MainWindow (QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.path = os.getcwd()
        path_ui = os.path.join(self.path,r"view/secondw.ui")
        uic.loadUi(path_ui,self)