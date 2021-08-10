from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from datetime import datetime,date,timedelta

import numpy as np

from models.db.db import GetInfToday, GetTotals, GetLastData, GetInfOneDay,GetInfYesterday
from .canvas import MplCanvas

import csv

class WeekReportWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.path = os.getcwd()
        path_ui = os.path.join(self.path,r"view/week_report.ui")
        uic.loadUi(path_ui,self)

        self.move(0,0)

        self.dateEdit.setMaximumDate(datetime.now())
        self.dateEdit.setDate(datetime.now())
        self.dateEdit.dateChanged.connect(self.DateChange)

        self.spt= MplCanvas(self, width=5, height=1, dpi=100)
        self.gridLayout.addWidget(self.spt)

        self.download_button1.clicked.connect(self.downloaddata)

        self.DateChange()

    def DateChange(self):
        now = self.dateEdit.date().toString('yyyy-MM-dd')
        day = date.fromisoformat(now)
        dayminusone = day + timedelta(-1)
        dayminustwo = day + timedelta(-2)
        dayminusthree = day + timedelta(-3)
        dayminusfour = day + timedelta(-4)

        datatoday = GetInfOneDay(now)
        minusone = GetInfOneDay(str(dayminusone))
        minustwo = GetInfOneDay(str(dayminustwo))
        minusthree = GetInfOneDay(str(dayminusthree))
        minusfour = GetInfOneDay(str(dayminusfour))

        self.label_4.setText('0')
        self.label_5.setText('0')
        self.label_8.setText('0')
        self.label_10.setText('0')
        self.label_12.setText('0')

        self.spt.axes.clear()
        x = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']


        if len(datatoday) != 0:
            i1,t1,_ = GetInfYesterday(now)
            self.label_4.setText('{0:.1f}'.format((i1/t1)*100))
            xtoday = np.zeros(24,dtype=int)
            for d in datatoday:
                i = x.index(d[2])
                xtoday[i] = d[0]
            
            xt = np.arange(len(x))
            self.spt.axes.plot(x,xtoday,label="Día 1: {}".format(now))
            self.spt.axes.set_ylabel('N° Personas sin mascarilla')
            self.spt.axes.set_xlabel('Hora del día')
            self.spt.axes.set_xticklabels(x,size='xx-small')
            
            

        if len(minusone) != 0:
            i2,t2,_ = GetInfYesterday(str(dayminusone))
            self.label_5.setText('{0:.1f}'.format((i2/t2)*100))
            x_one = np.zeros(24,dtype=int)
            for d in minusone:
                i = x.index(d[2])
                x_one[i] = d[0]

            self.spt.axes.plot(x,x_one,label="Día 2: {}".format(str(dayminusone)))
        
        if len(minustwo) != 0:
            i3,t3,_ = GetInfYesterday(str(dayminustwo))
            self.label_8.setText('{0:.1f}'.format((i3/t3)*100))
            x_two = np.zeros(24,dtype=int)
            for d in minustwo:
                i = x.index(d[2])
                x_two[i] = d[0]

            self.spt.axes.plot(x,x_two,label="Día 3: {}".format(str(dayminustwo)))

        if len(minusthree) != 0:
            i4,t4,_ = GetInfYesterday(str(dayminusthree))
            self.label_10.setText('{0:.1f}'.format((i4/t4)*100))
            x_three = np.zeros(24,dtype=int)
            for d in minusthree:
                i = x.index(d[2])
                x_three[i] = d[0]

            self.spt.axes.plot(x,x_three,label="Día 4: {}".format(str(dayminusthree)))

        if len(minusfour) != 0:
            i5,t5,_ = GetInfYesterday(str(dayminusfour))
            self.label_12.setText('{0:.1f}'.format((i5/t5)*100))
            x_four = np.zeros(24,dtype=int)
            for d in minusfour:
                i = x.index(d[2])
                x_four[i] = d[0]

            self.spt.axes.plot(x,x_four,label="Día 5: {}".format(str(dayminusfour)))
        
        self.spt.axes.grid()
        self.spt.axes.legend()
        self.spt.draw()

    def downloaddata(self):
        now = self.dateEdit.date().toString('yyyy-MM-dd')
        day = date.fromisoformat(now)
        dayminusone = day + timedelta(-1)
        dayminustwo = day + timedelta(-2)
        dayminusthree = day + timedelta(-3)
        dayminusfour = day + timedelta(-4)

        data1 = GetDayDataDownload(str(dayminusfour))
        data2 = GetDayDataDownload(str(dayminusthree))
        data3 = GetDayDataDownload(str(dayminustwo))
        data4 = GetDayDataDownload(str(dayminusone))
        data5 = GetDayDataDownload(now)

        
        path = os.getcwd() + "/export"
        if not os.path.exists(path):
            os.mkdir(path)
        filename = path + "/data-{}-to-{}.csv".format(day1,day5)

        with open(filename,"w") as file:
            writer = csv.writer(file,delimiter="\t")
            writer.writerow(['id','nomask','total','date'])
            for a in data1:
                writer.writerow(a)
            for b in data2:
                writer.writerow(b)
            for c in data3:
                writer.writerow(c)
            for d in data4:
                writer.writerow(d)
            for e in data5:
                writer.writerow(e)
            self.download_lbl.setText("Exportado: {}".format(filename))
