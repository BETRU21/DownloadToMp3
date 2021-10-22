from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import sys
import os

MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '/ui{}DownloadWindow.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)

class ViewDownload(QWidget, Ui_MainWindow):
    def __init__(self):
        super(ViewDownload, self).__init__()
        self.setupUi(self)
        self.connectWidgets()

    def connectWidgets(self):
        self.pb_linkDL.clicked.connect(self.downloadSingleSong)
        # self.pb_listDL.clicked.connect()
        # self.pb_file.clicked.connect()
        # self.ind_file
        # self.ind_count
        # self.le_link
        # self.pBar_download
        pass

    def downloadSingleSong(self):
        url = self.le_link.text()
        self.modelDownload.downloadMusicFile(url)

    def downloadStatus(self, downloadPercent, estimatedTime):
        pass

