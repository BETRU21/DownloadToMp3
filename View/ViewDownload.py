from Model.Download2Mp3 import Download2Mp3
from tools.threadWorker import Worker
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5 import uic
import sys
import os
from threading import *

MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '/ui{}DownloadWindow.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)


class ViewDownload(QWidget, Ui_MainWindow):

    progressSignal = pyqtSignal(int)
    estimatedTimeSignal = pyqtSignal(str)

    def __init__(self):
        super(ViewDownload, self).__init__()
        self.model = Download2Mp3(self.callableHook)
        self.setupUi(self)
        self.connectWidgets()
        self.listSong = []

        self.singleSongWorker = Worker(self.downloadSingleSong)
        self.singleSongThread = QThread()

        self.listSongWorker = Worker(self.downloadMultipleSong)
        self.listSongThread = QThread()

        self.create_threads()

    def create_threads(self):
        self.singleSongWorker.moveToThread(self.singleSongThread)
        self.singleSongThread.started.connect(self.singleSongWorker.run)

        self.listSongWorker.moveToThread(self.listSongThread)
        self.listSongThread.started.connect(self.listSongWorker.run)

    def connectWidgets(self):
        self.pb_linkDL.clicked.connect(self.downloadSingleSong)
        self.progressSignal.connect(self.updateProgressBar)
        self.estimatedTimeSignal.connect(self.showEstimatedTime)
        # self.pb_listDL.clicked.connect()
        # self.pb_file.clicked.connect()
        # self.ind_file
        # self.ind_count
        # self.le_link

    def startSingleDownload(self):
        self.pBar_download.setValue(0)
        self.singleSongThread.start()

    def startListDownload(self):
        self.pBar_download.setValue(0)
        self.listSongThread.start()

    def downloadMultipleSong(self):
        listSong = self.listSong
        for url in listSong:
            try:
                self.model.downloadMusicFile(url)
            except Exception as e:
                e = str(e)
                self.consoleView.showOnConsole(e, "red")

    def downloadSingleSong(self):
        url = self.le_link.text()
        try:
            self.model.downloadMusicFile(url)
        except Exception as e:
            e = str(e)
            self.consoleView.showOnConsole(e, "red")

    def updateProgressBar(self, downloadPercent):
        self.pBar_download.setValue(downloadPercent)

    def showEstimatedTime(self, estimatedTime):
        self.ind_count.setText(estimatedTime)

    def callableHook(self, response):
        if response["status"] == "downloading":
            downloadPercent = round((response["downloaded_bytes"]*100)/response["total_bytes"],0)
            eta = response["eta"]
            estimatedTime = f"{eta}s"

            self.progressSignal.emit(downloadPercent)
            self.estimatedTimeSignal.emit(estimatedTime)

