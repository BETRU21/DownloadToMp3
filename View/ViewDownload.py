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
    actionSignal = pyqtSignal(str)
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
        self.pb_fileDL.clicked.connect(self.startListDownload)
        self.pb_file.clicked.connect(self.setFilePath) 

        self.actionSignal.connect(self.actionsToConsole)
        self.estimatedTimeSignal.connect(self.showEstimatedTime)
        self.errorSignal.connect(self.errorToConsole)
        self.progressSignal.connect(self.updateProgressBar)
        self.rankSignal.connect(self.showRankOfDownload)
        self.resetIndicatorsSignal.connect(self.resetIndicators)
        self.threadSignalFinished.connect(self.killThread)

    def killThread(self, ID):
        if ID == 0:
            self.singleSongThread.quit()
        elif ID == 1:
            self.listSongThread.quit()
        else:
            pass

    def setFilePath(self):
        try:
            self.filePath = QFileDialog.getOpenFileName(self, "Select File")[0]
            if self.filePath == "":
                raise ValueError("filePath is empty")
            self.listSong = self.getUrl(self.filePath)
            self.ind_file.setStyleSheet("QCheckBox::indicator{background-color: rgb(0,255,0);}")
            listLen = len(self.listSong)
            text = f"{listLen} songs"
            self.ind_song.setText(text)
            self.actionSignal.emit(f"{listLen} url loaded")
        except Exception as error:
            error = str(error)
            self.ind_file.setStyleSheet("QCheckBox::indicator{background-color: rgb(255,0,0);}")
            self.errorSignal.emit(error)

    def startSingleDownload(self):
        self.listSongThread.requestInterruption()
        self.singleSongThread.requestInterruption()
        self.pBar_download.setValue(0)
        self.singleSongThread.start()

    def startListDownload(self):
        self.listSongThread.requestInterruption()
        self.singleSongThread.requestInterruption()
        self.pBar_download.setValue(0)
        self.listSongThread.start()

    def downloadMultipleSong(self):
        try:
            self.actionSignal.emit("Start list download")
            self.failedDownload = []
            listSong = self.listSong
            lenght = len(listSong)

            for rank, url in enumerate(listSong):
                try:
                    rank = rank + 1
                    self.rankSignal.emit((rank, lenght))
                    self.model.downloadMusicFile(url)
                    self.actionSignal.emit(f"Download {rank}/{lenght} complete")
                except Exception as error:
                    error = str(error)
                    self.errorSignal.emit(f"Download {rank}/{lenght} failed")
                    self.errorSignal.emit(error)
                    self.failedDownload.append(url)
            # TODO Create file with failedDownload url in.
            self.resetIndicatorsSignal.emit(True)
            self.threadSignalFinished.emit(1)
            self.actionSignal.emit("List download complete")
        except Exception as error:
            error = str(error)
            self.errorSignal.connect(error)
            self.resetIndicatorsSignal.emit(True)

    def downloadSingleSong(self):
        try:
            self.actionSignal.emit("Start single download")
            url = self.le_link.text()
            if url == "":
                raise ValueError("url is empty")
            self.rankSignal.emit((1,1))
            self.model.downloadMusicFile(url)
            self.threadSignalFinished.emit(0)
            self.actionSignal.emit("Single download complete")
        except Exception as error:
            error = str(error)
            self.actionSignal.emit("Single download interrupted")
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

    def actionsToConsole(self, action):
        self.consoleView.showOnConsole(action, "green")

    def resetIndicators(self, bool):
        self.ind_download.setText("")
        self.ind_count.setText("")

    def callableHook(self, response):
        if response["status"] == "downloading":
            downloadPercent = round((response["downloaded_bytes"]*100)/response["total_bytes"],0)
            time = response["eta"]
            if time < 60:
                estimatedTime = f"{time}s"
            elif time < 3600:
                estimatedTime = f"{time//60}min{time%60}s"
            else:
                estimatedTime = f"{time//3600}h{time//60}min{time%60}s"

            self.progressSignal.emit(downloadPercent)
            self.estimatedTimeSignal.emit(estimatedTime)

    def getUrl(self, path):
        if type(path) is not str:
            raise TypeError("path argument is not a string")

        fich = open(path, "r")
        fich_str = list(fich)
        fich.close()
        url = []
        for i in fich_str:
            elem = i.replace("\n", "")
            if elem.find("https://www.youtube.com/watch?v=") > -1:
                url.append(elem)
        return url
