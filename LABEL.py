# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LABEL.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

# from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(878, 545)
        self.centralwidget = PyQt5.QtWidgets.QWidget(MainWindow)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")
        self.splitter_3 =  PyQt5.QtWidgets.QSplitter(self.centralwidget)
        self.splitter_3.setGeometry( PyQt5.QtCore.QRect(0, 180, 731, 331))
        self.splitter_3.setOrientation( PyQt5.QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.graphicsView = PlotWidget(self.splitter_3)
        brush =  PyQt5.QtGui.QBrush( PyQt5.QtGui.QColor(0, 0, 0))
        brush.setStyle(PyQt5.QtCore.Qt.SolidPattern)
        self.graphicsView.setBackgroundBrush(brush)
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView_2 = PlotWidget(self.splitter_3)
        brush = PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(0, 0, 0))
        brush.setStyle(PyQt5.QtCore.Qt.SolidPattern)
        self.graphicsView_2.setBackgroundBrush(brush)
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.splitter_4 = PyQt5.QtWidgets.QSplitter(self.centralwidget)
        self.splitter_4.setGeometry(PyQt5.QtCore.QRect(740, 10, 121, 81))
        self.splitter_4.setOrientation(PyQt5.QtCore.Qt.Vertical)
        self.splitter_4.setObjectName("splitter_4")
        self.label_3 = PyQt5.QtWidgets.QLabel(self.splitter_4)
        font = PyQt5.QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setScaledContents(False)
        self.label_3.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.label_3.setWordWrap(False)
        self.label_3.setObjectName("label_3")
        self.lcdNumber_3 = PyQt5.QtWidgets.QLCDNumber(self.splitter_4)
        self.lcdNumber_3.setAutoFillBackground(True)
        self.lcdNumber_3.setSegmentStyle(PyQt5.QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_3.setObjectName("lcdNumber_3")
        self.splitter = PyQt5.QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(PyQt5.QtCore.QRect(0, 10, 361, 161))
        self.splitter.setOrientation(PyQt5.QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.label = PyQt5.QtWidgets.QLabel(self.splitter)
        font = PyQt5.QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setScaledContents(False)
        self.label.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.lcdNumber_2 = PyQt5.QtWidgets.QLCDNumber(self.splitter)
        self.lcdNumber_2.setAutoFillBackground(True)
        self.lcdNumber_2.setSmallDecimalPoint(False)
        self.lcdNumber_2.setSegmentStyle(PyQt5.QtWidgets.QLCDNumber.Flat)
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.splitter_2 = PyQt5.QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(PyQt5.QtCore.QRect(370, 10, 361, 161))
        self.splitter_2.setOrientation(PyQt5.QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.label_2 = PyQt5.QtWidgets.QLabel(self.splitter_2)
        font = PyQt5.QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.lcdNumber = PyQt5.QtWidgets.QLCDNumber(self.splitter_2)
        font = PyQt5.QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lcdNumber.setFont(font)
        self.lcdNumber.setAutoFillBackground(True)
        self.lcdNumber.setSegmentStyle(PyQt5.QtWidgets.QLCDNumber.Flat)
        self.lcdNumber.setObjectName("lcdNumber")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = PyQt5.QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(PyQt5.QtCore.QRect(0, 0, 878, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = PyQt5.QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        PyQt5.QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = PyQt5.QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_3.setText(_translate("MainWindow", "Frames"))
        self.label.setText(_translate("MainWindow", "Breathing Rate"))
        self.label_2.setText(_translate("MainWindow", "Heart Rate"))

from pyqtgraph import PlotWidget
