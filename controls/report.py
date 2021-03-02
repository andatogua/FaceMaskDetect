from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from datetime import datetime
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import random

from models.db.db import GetInfToday, GetTotals

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
        date = str(datetime.now())
        now = date[8:10]
        today = GetInfToday(now)
        total_inf,nomask_inf = GetTotals()
        _mask = total_inf - nomask_inf
        self.today_lbl.setText(str(today))

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