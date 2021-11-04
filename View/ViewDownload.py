from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5 import uic
from Model.Download2Mp3 import Download2Mp3
from tools.ThreadWorker import Worker
import os

MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '/ui{}DownloadWindow.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)

class ViewDownload(QWidget, Ui_MainWindow):

    progressSignal = pyqtSignal(int)
    estimatedTimeSignal = pyqtSignal(str)
    rankSignal = pyqtSignal(tuple)
    errorSignal = pyqtSignal(str)
    resetIndicatorsSignal = pyqtSignal(bool)
    threadSignalFinished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connectWidgets()
        self.model = Download2Mp3(self.callableHook)
        self.listSong = []
        self.failedDownload = []

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
        self.rankSignal.connect(self.showRankOfDownload)
        self.pb_fileDL.clicked.connect(self.startListDownload)
        self.pb_file.clicked.connect(self.setFilePath)
        self.errorSignal.connect(self.errorToConsole)
        self.resetIndicatorsSignal.connect(self.resetIndicators)
        self.threadSignalFinished.connect(self.killThread)

    def killThread(self, ID):
        if ID == 0:
            self.singleSongThread.quit()
        if ID == 1:
            self.listSongThread.quit()
        else:
            pass

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
            listLen = f"{len(self.listSong)} Songs"
            self.ind_song.setText(listLen)
        except Exception as error:
            error = str(error)
            self.ind_file.setStyleSheet("QCheckBox::indicator{background-color: rgb(255,0,0);}")
            self.errorSignal.emit(error)

    def startSingleDownload(self):
        self.listSongThread.requestInterruption()
        self.singleSongThread.requestInterruption()
        self.pBar_download.setValue(0)
        print("startSingleDownload")
        self.singleSongThread.start()

    def startListDownload(self):
        self.listSongThread.requestInterruption()
        self.singleSongThread.requestInterruption()
        self.pBar_download.setValue(0)
        print("startListDownload")
        self.listSongThread.start()

    def downloadMultipleSong(self):
        print("downloadMultipleSong")
        try:
            self.failedDownload = [] # Finish this part.
            listSong = self.listSong
            lenght = len(listSong)

            rank = 0
            for url in listSong:
                try:
                    rank += 1
                    self.rankSignal.emit((rank, lenght))
                    self.model.downloadMusicFile(url)
                except Exception as e:
                    self.failedDownload.append(url)
            self.resetIndicatorsSignal.emit(True)
            self.threadSignalFinished.emit(1)
        except Exception as error:
            error = str(error)
            self.errorSignal.connect(error)
            self.resetIndicatorsSignal.emit(True)

    def downloadSingleSong(self):
        print("downloadSingleSong")
        try:
            url = self.le_link.text()
            if url == "":
                raise ValueError("url is empty.")
            self.rankSignal.emit((1,1))
            self.model.downloadMusicFile(url)
            self.threadSignalFinished.emit(0)
        except Exception as error:
            error = str(error)
            self.errorSignal.emit(error)
            self.resetIndicatorsSignal.emit(True)

    def updateProgressBar(self, downloadPercent):
        self.pBar_download.setValue(downloadPercent)

    def showEstimatedTime(self, estimatedTime):
        self.ind_count.setText(estimatedTime)

    def showRankOfDownload(self, infos):
        rank, lenght = infos
        text = f"{rank}/{lenght}"
        self.ind_download.setText(text)

    def errorToConsole(self, error):
        self.consoleView.showOnConsole(error, "red")

    def resetIndicators(self, bool):
        self.ind_download.setText("")
        self.ind_count.setText("")

    def callableHook(self, response):
        if response["status"] == "downloading":
            downloadPercent = round((response["downloaded_bytes"]*100)/response["total_bytes"],0)
            eta = response["eta"]
            if eta < 60:
                estimatedTime = f"{eta}s"
            else:
                estimatedTime = f"{eta//60}min{eta%60}s"

            self.progressSignal.emit(downloadPercent)
            self.estimatedTimeSignal.emit(estimatedTime)
