from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import os

from models.detect import Worker1

class MainWindow (QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        path_ui = os.getcwd()
        path = os.path.join(path_ui,r"ui\dashboard.ui")
        uic.loadUi(path,self)

        self.Worker1 = Worker1()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.list_persons.connect(self.DetectUpdate)
        self.start_cam.clicked.connect(self.start_stream)
        self.stop_cam.clicked.connect(self.stop_stream)

    def start_stream(self):
        self.Worker1.start()
        print("[INFO] started video stream...")


    def stop_stream(self):
        self.Worker1.stop()


    def ImageUpdateSlot(self, Image):
        self.cam_label.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.Worker1.stop()

    def DetectUpdate(self, t,s,c):
        self.detect_person.setText(str(t))
        self.no_mask_person.setText(str(s))
        self.mask_person.setText(str(c))
    