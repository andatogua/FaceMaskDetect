from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import os
import time
from datetime import datetime

from .detect import Worker1
from models.db.db import SaveLog

class MainWindow (QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.path = os.getcwd()
        path_ui = os.path.join(self.path,r"view/dashboard.ui")
        uic.loadUi(path_ui,self)

        self.Worker1 = Worker1()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.list_persons.connect(self.DetectUpdate)
        self.start_cam.clicked.connect(self.start_stream)
        self.stop_cam.clicked.connect(self.stop_stream)


    def start_stream(self):
        self.Worker1.start()
        self.statusBar().showMessage("Video iniciado")


    def stop_stream(self):
        self.Worker1.stop()
        self.statusBar().showMessage('Presione Iniciar para comenzar con las detecciones')


    def ImageUpdateSlot(self, Image):
        self.cam_label.setPixmap(QPixmap.fromImage(Image))


    def DetectUpdate(self, t,s,c,dt,image):
        self.detect_person.setText(str(t))
        self.no_mask_person.setText(str(s))
        self.mask_person.setText(str(c))

        if s > dt:
            #name = str(time.time())
            name = str(datetime.now())
            folder = 'saved'
            dir = os.path.join(self.path,folder)
            if not os.path.exists(dir):
                os.mkdir(dir)
            if SaveLog(s,t,name):
                self.SaveDetection(image,dir,name)

    
    def SaveDetection(self, image, dir,name):
        name = name.replace(':','-')
        img = image.copy()
        img = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        cv2.imwrite(dir+'/'+name+'.jpg',img)
        self.statusBar().showMessage('Última detección: {}'.format(name))