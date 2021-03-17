from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import os
import time
import sys
import numpy as np
from datetime import datetime,date,timedelta

from .detect import Worker1
from models.db.db import SaveLog,GetInfToday,GetInfYesterday

from .report import ReportWindow
from .week_report import WeekReportWindow
from .secondw import MainWindow as Second

class MainWindow (QMainWindow):
    img = np.ndarray
    play = False
    def __init__(self):
        QMainWindow.__init__(self)
        self.path = os.getcwd()
        path_ui = os.path.join(self.path,r"view/dashboard.ui")
        uic.loadUi(path_ui,self)

        self.move(0,0)


        self.Worker1 = Worker1()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.list_persons.connect(self.DetectUpdate)
        self.start_cam.clicked.connect(self.start_stream)
        self.stop_cam.clicked.connect(self.stop_stream)

        #self.scrollArea.setGeometry(QRect(10, 520, 281, 151))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gridLayoutWidget = QWidget()
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea.setWidget(self.gridLayoutWidget)

        self.LoadThumbnail()
        self.SetInfrac()

        self.actionReporte_Diario.triggered.connect(self.OpenReport)
        self.actionReporte_Semanal.triggered.connect(self.OpenWeekReport)
        
        self.actionSalir.triggered.connect(self.Exit)
        self.actiona.triggered.connect(self.SecondW)

    def start_stream(self):
        self.Worker1.start()
        self.statusBar().showMessage("Video iniciado")


    def stop_stream(self):
        self.Worker1.stop()
        self.statusBar().showMessage('Presione Iniciar para comenzar con las detecciones')
        self.play = False


    def ImageUpdateSlot(self, Image, t,s,c,i):
        self.cam_label.setPixmap(QPixmap.fromImage(Image))
        self.img = cv2.cvtColor(i,cv2.COLOR_BGR2RGB)
        self.detect_person.setText(str(t))
        self.no_mask_person.setText(str(s))
        self.mask_person.setText(str(c))
        self.play = True


    def DetectUpdate(self,dt,ni,image,name):
        name = str(datetime.now())
        folder = 'saved'
        dir = os.path.join(self.path,folder)
        if not os.path.exists(dir):
            os.mkdir(dir)
        if SaveLog(ni,dt,name):
            self.SaveDetection(image,dir,name)

    
    def SaveDetection(self, image, dir,name):
        name = name.replace(':','-')
        img = image.copy()
        img = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        cv2.imwrite(dir+'/'+name+'.jpg',img)
        self.statusBar().showMessage('Última detección: {}'.format(name))
        self.LoadThumbnail()
        self.SetInfrac()


    def LoadThumbnail(self):
        dir = os.path.join(self.path,'saved/')
        files = [ f for f in os.listdir(dir)]
        files = sorted(files)
        col = 0
        
        self.gridLayout.setVerticalSpacing(30)
        for file in reversed(files):
            #if files.index(file) > len(files) - 10 :
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            file_path=os.path.join(dir,file)
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(pixmap)
            thumbnail = QBoxLayout(QBoxLayout.TopToBottom)
            thumbnail.addWidget(img_label)
            self.gridLayout.addLayout(thumbnail,0,col, Qt.AlignCenter)

            img_label.mousePressEvent = \
                lambda e, \
                index=files.index(file), \
                file_path=file_path: \
                    self.on_thumbnail_click(file_path)
            
            if col == 10: break
            
            col += 1
        

    def on_thumbnail_click(self, file_path):
        self.pixmap = QPixmap(file_path)
        self.pixmap = self.pixmap.scaled(271, 271, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_infrac.setPixmap(self.pixmap)


    def GetDays(self):
        now = date.today()
        t = now + timedelta(-1)
        yesterday = str(t)
        now = str(now)
        return now,yesterday

    def SetInfrac(self):
        now,yesterday=self.GetDays()
        if GetInfToday != None:
            n,nn,tn = GetInfToday(now)
        if GetInfYesterday != None:
            y,ny,ty = GetInfYesterday(yesterday)
        if nn != None and nn != "":
            self.infrac_today.setText("{0} ({1:.1f}%)".format(n,((nn/tn)*100)))
        if ny != None and ny != "":
            self.infrac_yesterday.setText("{0} ({1:.1f}%)".format(y,((ny/ty)*100)))

       
    def OpenReport(self):
        r = ReportWindow()
        r.exec_()

    def OpenWeekReport(self):
        r = WeekReportWindow()
        r.exec_()

    def Exit(self):
        sys.exit(1)
    
    def SecondW(self):
        
        while self.play:
            cv2.imshow("Yo me cuido",self.img)
            key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # do a bit of cleanup
        cv2.destroyAllWindows()