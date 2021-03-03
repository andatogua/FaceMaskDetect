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
        self.LoadData()
    

    def LoadData(self):
        now = date.today()
        _,nomask,__ = GetInfToday(str(now))
        total_inf,nomask_inf = GetTotals()
        _mask = total_inf - nomask_inf
        self.today_lbl.setText(str(nomask))

        #-----------------------------
        lastweek = now + timedelta(-7)
        dataweek = GetLastData(str(lastweek))
        totalweek = 0
        for t in dataweek:
            totalweek += t[0]
        self.week_lbl.setText(str(totalweek))
        w=[]
        dw=[]
        dww=[]
        for i in range(-6,1,1):
            w.append(str(now + timedelta(i)))
        
        valuesnomask = np.zeros(len(w),dtype=int)
        valuesmask = np.zeros(len(w),dtype=int)

        for day in dataweek:
            i = w.index(day[2])
            valuesnomask[i] = day[0]
            valuesmask[i] = day[1]-day[0]

        #----------------------------
        lastmonth = now + timedelta(-30)
        datamonth = GetLastData(str(lastmonth))
        totalmonth = 0
        for t in datamonth:
            totalmonth += t[0]
        self.month_lbl.setText(str(totalmonth))



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

        sb = MplCanvas(self, width=5, height=3, dpi=100)
        sb.axes.bar(w,valuesnomask,0.3,label='No mask')
        sb.axes.bar(w,valuesmask,0.3,bottom=valuesnomask,label='Mask')
        sb.axes.set_xticklabels(w,rotation='vertical',size='xx-small')
        sb.axes.legend()

        sp = MplCanvas(self, width=5, height=3, dpi=100)
        sp.axes.plot(w,valuesnomask)
        
        prom = np.mean(valuesnomask)
        xprom = np.zeros(len(w))
        for (d,_) in enumerate(xprom):
            xprom[d] = prom

        sp.axes.plot(w,xprom,label='Promedio: {}'.format(prom))
        sp.axes.legend()

        self.verticalLayout_5.addWidget(sb)
        self.verticalLayout_5.addWidget(sp)