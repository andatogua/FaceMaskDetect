from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from datetime import datetime,date,timedelta
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import random

from models.db.db import GetInfToday, GetTotals, GetLastData

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class ReportWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.path = os.getcwd()
        path_ui = os.path.join(self.path,r"view/report.ui")
        uic.loadUi(path_ui,self)
        self.week_radio.setChecked(True)
        self.today_radio.toggled.connect(lambda:self.radiostate(self.today_radio))
        self.week_radio.toggled.connect(lambda:self.radiostate(self.week_radio))
        self.month_radio.toggled.connect(lambda:self.radiostate(self.month_radio))

        self.sbt = MplCanvas(self, width=5, height=3, dpi=100)
        self.spt = MplCanvas(self, width=5, height=3, dpi=100)

        self.sbw = MplCanvas(self, width=5, height=3, dpi=100)
        self.spw = MplCanvas(self, width=5, height=3, dpi=100)

        self.sbm = MplCanvas(self, width=5, height=3, dpi=100)
        self.spm = MplCanvas(self, width=5, height=3, dpi=100)

        self.LoadData()
        self.radiostate(self.today_radio)
    
    def radiostate(self,radio):
        if self.week_radio.isChecked():
            self.sbm.hide()
            self.spm.hide()
            self.sbw.show()
            self.spw.show()
        elif self.month_radio.isChecked():
            self.sbw.hide()
            self.spw.hide()
            self.sbm.show()
            self.spm.show()
        

    def LoadData(self):
        now = date.today()
        _,nomask,__ = GetInfToday(str(now))
        total_inf,nomask_inf = GetTotals()
        _mask = total_inf - nomask_inf
        self.today_lbl.setText(str(nomask))

        #----------- week ------------------


        lastweek = now + timedelta(-7)
        lastmonth = now + timedelta(-30)
        dataweek = GetLastData(str(lastweek))
        datamonth = GetLastData(str(lastmonth))
        totalweek = 0
        for t in dataweek:
            totalweek += t[0]
        self.week_lbl.setText(str(totalweek))
        w=[]
        for i in range(-6,1,1):
            w.append(str(now + timedelta(i)))
        
        valuesnomask = np.zeros(len(w),dtype=int)
        valuesmask = np.zeros(len(w),dtype=int)

        for day in dataweek:
            i = w.index(day[2])
            valuesnomask[i] = day[0]
            valuesmask[i] = day[1]-day[0]

        
        self.sbw.axes.bar(w,valuesnomask,0.3,label='No mask')
        self.sbw.axes.bar(w,valuesmask,0.3,bottom=valuesnomask,label='Mask')
        self.sbw.axes.set_xticklabels(w,rotation='vertical',size='xx-small')
        self.sbw.axes.grid()
        self.sbw.axes.legend()

        
        self.spw.axes.plot(w,valuesnomask)
        
        prom = np.mean(valuesnomask)
        xprom = np.zeros(len(w))
        for (d,_) in enumerate(xprom):
            xprom[d] = prom

        self.spw.axes.plot(w,xprom,label='Promedio: {0:.0f}'.format(prom))
        self.spw.axes.set_xticklabels(w,rotation='vertical',size='xx-small')
        self.spw.axes.legend()
        self.spw.axes.grid()
        

        self.verticalLayout_5.addWidget(self.sbw)
        self.verticalLayout_5.addWidget(self.spw)

        #--------------month--------------
        lastmonth = now + timedelta(-30)
        datamonth = GetLastData(str(lastmonth))
        totalmonth = 0
        for t in datamonth:
            totalmonth += t[0]
        self.month_lbl.setText(str(totalmonth))

        m=[]

        for i in range(-29,1,1):
            m.append(str(now + timedelta(i)))

        valmonthmask = np.zeros(len(m), dtype=int)
        valmonthnomask = np.zeros(len(m), dtype=int)
        
        for day in datamonth:
            i = m.index(day[2])
            valmonthnomask[i]=day[0]
            valmonthmask[i]=day[1]-day[0]


        mx=np.arange(len(m))
        self.sbm.axes.bar(mx-0.15,valmonthnomask,0.3,label='No mask')
        #self.sbm.axes.bar(m,valmonthmask,0.3,bottom=valmonthnomask,label='Mask')
        self.sbm.axes.bar(mx+0.15,valmonthmask,0.3,label='Mask')
        self.sbm.axes.set_xticks(mx)
        self.sbm.axes.set_xticklabels(m,rotation='vertical',size='xx-small')
        self.sbm.axes.grid()
        self.sbm.axes.legend()

        
        self.spm.axes.plot(m,valmonthnomask)
        
        promm = np.mean(valmonthnomask)
        xpromm = np.zeros(len(m))
        for (d,_) in enumerate(xpromm):
            xpromm[d] = promm

        self.spm.axes.plot(m,xpromm,label='Promedio: {0:.0f}'.format(promm))
        self.spm.axes.set_xticklabels(m,rotation='vertical',size='xx-small')
        self.spm.axes.grid()
        self.spm.axes.legend()
        

        self.verticalLayout_5.addWidget(self.sbm)
        self.verticalLayout_5.addWidget(self.spm)



        sc = MplCanvas(self, width=5, height=4, dpi=100)
        explode = (0,0.3)
        labels = 'Con Masc', 'Sin Masc'
        fracs = [_mask,nomask_inf]


        sc.axes.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
        self.gridLayout.addWidget(sc)
        self.with_lbl.setText(str(_mask))
        self.without_lbl.setText(str(nomask_inf))
        self.total_lbl.setText(str(total_inf))

        