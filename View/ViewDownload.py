from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import uic
from Model.Download2Mp3 import Download2Mp3
from tools.ThreadWorker import Worker
import os

MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '/ui{}DownloadWindow.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)

class ViewDownload(QWidget, Ui_MainWindow):

    progressSignal = pyqtSignal(int)
    estimatedTimeSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connectWidgets()
        self.model = Download2Mp3(self.callableHook)
        self.listSong = []
        self.filePath = ""

        self.singleSongWorker = Worker(self.downloadSingleSong)
        self.singleSongThread = QThread()

        self.listSongWorker = Worker(self.downloadMultipleSong)
        self.listSongThread = QThread()

        self.createThreads()

    def createThreads(self):
        self.singleSongWorker.moveToThread(self.singleSongThread)
        self.singleSongThread.started.connect(self.singleSongWorker.run)

        self.listSongWorker.moveToThread(self.listSongThread)
        self.listSongThread.started.connect(self.listSongWorker.run)

    def connectWidgets(self):
        self.pb_linkDL.clicked.connect(self.startSingleDownload)
        self.progressSignal.connect(self.updateProgressBar)
        self.estimatedTimeSignal.connect(self.showEstimatedTime)
        self.pb_fileDL.clicked.connect(self.startListDownload)
        self.pb_file.clicked.connect(self.setFilePath)

    def setFilePath(self):
        try:
            self.filePath = QFileDialog.getOpenFileName(self, "Select File")[0]
            if self.filePath == "":
                raise ValueError("filePath is empty.")
            fich = open(self.filePath, "r")
            musicList = list(fich)
            fich.close()
            self.listSong = []
            for j in musicList:
                elem = j.replace("\n", "")
                self.listSong.append(str(elem))
            self.consoleView.showOnConsole("filePath found !", "green")
            self.ind_file.setStyleSheet("QCheckBox::indicator{background-color: rgb(0,255,0);}")
        except Exception as e:
            e = str(e)
            self.ind_file.setStyleSheet("QCheckBox::indicator{background-color: rgb(255,0,0);}")
            self.consoleView.showOnConsole(e, "red")

    def startSingleDownload(self):
        self.pBar_download.setValue(0)
        self.singleSongThread.start()

    def startListDownload(self):
        self.pBar_download.setValue(0)
        self.listSongThread.start()

    def downloadMultipleSong(self):
        print("allo")
        listSong = self.listSong
        for url in listSong:
            try:
                self.model.downloadMusicFile(url)
            except Exception as e:
                e = str(e)

    def downloadSingleSong(self):
        url = self.le_link.text()
        self.model.downloadMusicFile(url)

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
