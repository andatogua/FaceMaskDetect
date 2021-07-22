from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from datetime import datetime,date,timedelta

import numpy as np

from models.db.db import GetInfToday, GetTotals, GetLastData, GetInfOneDay
from .canvas import MplCanvas

class ReportWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.path = os.getcwd()
        path_ui = os.path.join(self.path,r"view/report.ui")
        uic.loadUi(path_ui,self)

        self.dateEdit.setMaximumDate(datetime.now())
        self.dateEdit.setDate(datetime.now())
        self.dateEdit.dateChanged.connect(self.DateChange)

        self.sbt = MplCanvas(self, width=5, height=1, dpi=100)
        self.spt = MplCanvas(self, width=5, height=1, dpi=100)
        self.verticalLayout_5.addWidget(self.sbt)
        self.verticalLayout_6.addWidget(self.spt)

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.gridLayout.addWidget(self.sc)


        self.DateChange()

    def DateChange(self):
        now = self.dateEdit.date().toString('yyyy-MM-dd')
        self.LoadData(now)

    def LoadData(self,now):
        _,nomask,_totaltoday = GetInfToday(now)
        if nomask != None and nomask != '':
            _mask = _totaltoday - nomask
        else:
            _mask = 0
            _totaltoday = 0
            nomask = 0
        self.with_lbl.setText(str(_mask))
        self.without_lbl.setText(str(nomask))
        self.total_lbl.setText(str(_totaltoday))

        self.today_lbl.setText(str(nomask))

        #---------------today-------------------
        datatoday = GetInfOneDay(now)
        self.sbt.axes.clear()
        self.spt.axes.clear()
        if len(datatoday) != 0:
            xtoday = np.zeros(24,dtype=int)
            x1today = np.zeros(24,dtype=int)
            x2today = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
            for d in datatoday:
                i = x2today.index(d[2])
                xtoday[i] = d[0]
                x1today[i] = d[1]

            xt = np.arange(len(x2today))
            self.sbt.axes.bar(xt-0.15,x1today,0.3,label='Total')
            self.sbt.axes.bar(xt+0.15,xtoday,0.3,label='Infractores')
            self.sbt.axes.set_ylabel('N° Personas sin mascarilla')
            self.sbt.axes.set_xlabel('Hora del día')
            self.sbt.axes.set_xticks(xt)
            self.sbt.axes.set_xticklabels(x2today,size='xx-small')
            self.sbt.axes.grid()
            self.sbt.axes.legend()

            self.spt.axes.plot(x2today,xtoday)
            self.spt.axes.set_ylabel('N° Personas sin mascarilla')
            self.spt.axes.set_xlabel('Hora del día')
            self.spt.axes.set_xticks(xt)
            self.spt.axes.set_xticklabels(x2today,size='xx-small')
            self.spt.axes.grid()
            self.spt.axes.legend()
        
        self.sbt.draw()
        self.spt.draw()



        #--------------------------------------

        explode = (0,0.3)
        labels = 'Infractores', 'Responsables'
        fracs = [nomask,_mask]
        self.sc.axes.clear()
        if nomask != '' and _totaltoday != '':
            self.sc.axes.pie(fracs, explode=explode, labels=labels,  shadow=True, startangle=90, autopct='%1.1f%%')
        self.sc.draw()
        

        