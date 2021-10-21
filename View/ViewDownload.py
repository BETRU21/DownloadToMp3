from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import sys
import os

MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '/ui{}DownloadWindow.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)

class ViewDownload(QWidget, Ui_MainWindow):
    def __init__(self, modelDownload):
        super(ViewDownload, self).__init__()
        self.setupUi(self)
        self.modelDownload = modelDownload
        self.setupWidgets()
        self.connectWidgets()

    def connectWidgets(self):
        pass

    def setupWidgets(self):
        pass
