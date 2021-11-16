from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSignal, QThread, QMutex
from PyQt5 import uic
from Model.Download2Mp3 import Download2Mp3
from tools.ThreadWorker import Worker
import os

applicationPath = os.path.abspath("")

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
        self.language = "english"
        self.mutex = QMutex()
        self.createLanguageDict()
        self.listSong = []
        self.failedDownload = []

        self.singleSongWorker = Worker(self.downloadSingleSong)
        self.singleSongThread = QThread()

        self.listSongWorker = Worker(self.downloadMultipleSong)
        self.listSongThread = QThread()

        self.createThreads()

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

    # Thread Section

    def createThreads(self):
        self.singleSongWorker.moveToThread(self.singleSongThread)
        self.singleSongThread.started.connect(self.singleSongWorker.run)

        self.listSongWorker.moveToThread(self.listSongThread)
        self.listSongThread.started.connect(self.listSongWorker.run)

    def startSingleDownload(self):
        thread1Running = self.listSongThread.isRunning()
        thread2Running = self.singleSongThread.isRunning()
        if thread1Running == False:
            if thread2Running == False:
                self.pBar_download.setValue(0)
                self.singleSongThread.start()

    def startListDownload(self):
        thread1Running = self.listSongThread.isRunning()
        thread2Running = self.singleSongThread.isRunning()
        if thread1Running == False:
            if thread2Running == False:
                self.pBar_download.setValue(0)
                self.listSongThread.start()

    def killThread(self, ID):
        if ID == 0:
            self.singleSongThread.quit()
        elif ID == 1:
            self.listSongThread.quit()
        else:
            pass

    # Download Section

    def downloadSingleSong(self):
        try:
            language = self.currentLanguage()
            if language == "english":
                self.actionSignal.emit("Start single download")
            else:
                self.actionSignal.emit("Lancement du téléchargement avec url")
            url = self.le_link.text()
            if url == "":
                language = self.currentLanguage()
                if language == "english":
                    raise ValueError("url is empty")
                else:
                    raise ValueError("L'url est vide")
            self.failedDownload = []
            self.rankSignal.emit((1,1))
            self.model.downloadMusicFile(url)
            self.createfailDownloadFile()
            self.resetIndicatorsSignal.emit(True)
            language = self.currentLanguage()
            if language == "english":
                self.actionSignal.emit("Single download complete")
            else:
                self.actionSignal.emit("Téléchargement avec url complété")
            self.threadSignalFinished.emit(0)
        except Exception as error:
            error = str(error)
            language = self.currentLanguage()
            if language == "english":
                self.errorSignal.emit("Single download interrupted")
            else:
                self.errorSignal.emit("Téléchargement avec url interrompu")
            self.errorSignal.emit(error)
            self.resetIndicatorsSignal.emit(True)
            self.threadSignalFinished.emit(0)

    def downloadMultipleSong(self):
        try:
            language = self.currentLanguage()
            if language == "english":
                self.actionSignal.emit("Start list download")
            else:
                self.actionSignal.emit("Lancement du téléchargement avec la liste")

            self.failedDownload = []
            listSong = self.listSong
            lenght = len(listSong)

            for rank, url in enumerate(listSong):
                try:
                    rank = rank + 1
                    self.rankSignal.emit((rank, lenght))
                    self.model.downloadMusicFile(url)
                    language = self.currentLanguage()
                    if language == "english":
                        self.actionSignal.emit(f"Download {rank}/{lenght} complete")
                    else:
                        self.actionSignal.emit(f"Téléchargement {rank}/{lenght} complété")
                except Exception as error:
                    error = str(error)
                    language = self.currentLanguage()
                    if language == "english":
                        self.errorSignal.emit(f"Download {rank}/{lenght} failed")
                    else:
                        self.errorSignal.emit(f"Téléchargement {rank}/{lenght} interrompu")
                    self.errorSignal.emit(error)
                    self.failedDownload.append(url)

            self.createfailDownloadFile()
            self.resetIndicatorsSignal.emit(True)
            language = self.currentLanguage()
            if language == "english":
                self.actionSignal.emit("List download complete")
            else:
                self.actionSignal.emit("Téléchargement de la liste terminé")
            self.threadSignalFinished.emit(1)
        except Exception as error:
            error = str(error)
            language = self.currentLanguage()
            if language == "english":
                self.errorSignal.emit("List download interrupted")
            else:
                self.errorSignal.emit("Téléchargement de la liste interrompu")
            self.errorSignal.connect(error)
            self.resetIndicatorsSignal.emit(True)
            self.threadSignalFinished.emit(1)

    # File Section

    def setFilePath(self):
        try:
            self.filePath = QFileDialog.getOpenFileName(self, "Select File")[0]
            if self.filePath == "":
                raise ValueError("filePath is empty")
            self.listSong = self.getUrl(self.filePath)
            self.ind_file.setStyleSheet("QCheckBox::indicator{background-color: rgb(0,255,0);}")
            listLen = len(self.listSong)
            text = f"{listLen} url"
            self.ind_song.setText(text)

            language = self.currentLanguage()
            if language == "english":
                self.actionSignal.emit(f"{listLen} url loaded")
            else:
                self.actionSignal.emit(f"{listLen} url enregistré")

        except Exception as error:
            error = str(error)
            self.ind_file.setStyleSheet("QCheckBox::indicator{background-color: rgb(255,0,0);}")
            self.errorSignal.emit(error)

    

    def createfailDownloadFile(self):
        if self.failedDownload != []:
            folder = applicationPath + "/failedDownloadFile"
            path = os.path.join(folder, f"failedDownload")
            with open(path + ".txt", "w+") as f:
                for i, link in enumerate(self.failedDownload):
                    lenn = len(self.failedDownload)
                    if (i + 1) == lenn:
                        f.wrote(f"{link}")
                    else:
                        f.write(f"{link}\n")
                f.close()
            language = self.currentLanguage()
            if language == "english":
                self.actionSignal.emit("failedDownload file create at :")
            else:
                self.actionSignal.emit("Fichier failedDownload créer à l'emplacement :")
            self.actionSignal.emit(folder)

    def getUrl(self, path):
        fich = open(path, "r")
        fich_str = list(fich)
        fich.close()
        url = []
        for i in fich_str:
            elem = i.replace("\n", "")
            if elem.find("https://www.youtube.com/watch?v=") > -1:
                url.append(elem)
        return url

    # Signals Section

    def updateProgressBar(self, downloadPercent):
        self.pBar_download.setValue(downloadPercent)

    def showEstimatedTime(self, estimatedTime):
        self.ind_count.setText(estimatedTime)

    def showRankOfDownload(self, infos):
        rank, lenght = infos
        text = f"{rank}/{lenght}"
        self.ind_download.setText(text)

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

    # Language/Console Section

    def errorToConsole(self, error):
        self.consoleView.showOnConsole(error, "red")

    def actionsToConsole(self, action):
        self.consoleView.showOnConsole(action, "green")

    def currentLanguage(self):
        self.mutex.lock()
        language = self.language
        self.mutex.unlock()
        return language

    def changeLanguage(self, language):
        self.mutex.lock()
        self.language = language
        self.mutex.unlock()
        self.gb_link.setTitle(self.widgetLabel.get(language).get("gb_link"))
        self.gb_list.setTitle(self.widgetLabel.get(language).get("gb_list"))
        self.pb_linkDL.setText(self.widgetLabel.get(language).get("pb_linkDL"))
        self.pb_file.setText(self.widgetLabel.get(language).get("pb_file"))
        self.pb_fileDL.setText(self.widgetLabel.get(language).get("pb_fileDL"))

    def createLanguageDict(self):
        self.widgetLabel = {"french": {}, "english": {}}

        self.widgetLabel["french"]["gb_link"] = "Téléchargement avec un lien"
        self.widgetLabel["english"]["gb_link"] = "Link Download"
        self.widgetLabel["french"]["gb_list"] = "Téléchargement avec une liste"
        self.widgetLabel["english"]["gb_list"] = "List Download"
        self.widgetLabel["french"]["pb_linkDL"] = "Télécharger"
        self.widgetLabel["english"]["pb_linkDL"] = "Start Download"
        self.widgetLabel["french"]["pb_file"] = "Sélectionner un fichier"
        self.widgetLabel["english"]["pb_file"] = "Select File"
        self.widgetLabel["french"]["pb_fileDL"] = "Télécharger"
        self.widgetLabel["english"]["pb_fileDL"] = "Start Download"
