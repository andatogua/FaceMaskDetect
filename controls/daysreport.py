from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from datetime import datetime,date,timedelta

import numpy as np

from models.db.db import GetInfToday, GetTotals, GetLastData, GetInfOneDay,GetInfYesterday, GetDayDataDownload
from .canvas import MplCanvas

import csv

class DaysReportWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.path = os.getcwd()
        path_ui = os.path.join(self.path,r"view/days_report.ui")
        uic.loadUi(path_ui,self)

        self.move(0,0)

        self.dateEdit.setMaximumDate(datetime.now())
        self.dateEdit.setDate(datetime.now())
        self.dateEdit.dateChanged.connect(self.DateChange)

        self.dateEdit_2.setMaximumDate(datetime.now())
        self.dateEdit_2.setDate(datetime.now() + timedelta(-1))
        self.dateEdit_2.dateChanged.connect(self.DateChange)

        self.download_button1.clicked.connect(self.downloaddata)

        self.spt= MplCanvas(self, width=5, height=1, dpi=100)
        self.gridLayout.addWidget(self.spt)

        self.DateChange()

    def DateChange(self):
        one = self.dateEdit.date().toString('yyyy-MM-dd')
        two = self.dateEdit_2.date().toString('yyyy-MM-dd')

        day_one = GetInfOneDay(one)
        day_two = GetInfOneDay(two)
        
        self.label_5.setText('0')
        self.label_7.setText('0')

        self.spt.axes.clear()
        x = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']


        if len(day_one) != 0:
            i1,t1,_ = GetInfYesterday(one)
            self.label_5.setText('{0:.1f}'.format((i1/t1)*100))
            x_one = np.zeros(24,dtype=int)
            for d in day_one:
                i = x.index(d[2])
                x_one[i] = d[0]
            
            xt = np.arange(len(x))
            self.spt.axes.plot(x,x_one,label="Día 1: {}".format(one))
            self.spt.axes.set_ylabel('N° Personas sin mascarilla')
            self.spt.axes.set_xlabel('Hora del día')
            self.spt.axes.set_xticklabels(x,size='xx-small')
            
            

        if len(day_two) != 0:
            i2,t2,_ = GetInfYesterday(str(two))
            self.label_7.setText('{0:.1f}'.format((i2/t2)*100))
            x_two = np.zeros(24,dtype=int)
            for d in day_two:
                i = x.index(d[2])
                x_two[i] = d[0]

            self.spt.axes.plot(x,x_two,label="Día 2: {}".format(two))
        
        
        
        self.spt.axes.grid()
        self.spt.axes.legend()
        self.spt.draw()


    def downloaddata(self):
        day1 = self.dateEdit.date().toString('yyyy-MM-dd')
        day2 = self.dateEdit_2.date().toString('yyyy-MM-dd')
        data1 = GetDayDataDownload(day1)
        data2 = GetDayDataDownload(day2)
        path = os.getcwd() + "/export"
        if not os.path.exists(path):
            os.mkdir(path)
        filename = path + "/data-{}-vs-{}.csv".format(day1,day2)

        with open(filename,"w") as file:
            writer = csv.writer(file,delimiter="\t")
            writer.writerow(['id','nomask','total','date'])
            for p in data1:
                writer.writerow(p)
            for r in data2:
                writer.writerow(r)
            self.download_lbl.setText("Exportado: {}".format(filename))
