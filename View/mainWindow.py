from View.ViewConsole import ViewConsole
from Model.Download2Mp3 import Download2Mp3
from View.ViewDownload import ViewDownload
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5 import uic
import os

MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '/ui{}MainWindow.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.createsComponentsAndPointers()
        self.setupWindowTabs()

    def setupWindowTabs(self):
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.tabWidget.addTab(self.downloadView, "Download")
        self.tabWidget.addTab(self.consoleView, "Console")

    def createsComponentsAndPointers(self):
        # Components
        self.modelDownload = Download2Mp3(view=True)
        self.downloadView = ViewDownload()
        self.consoleView = ViewConsole()

        # Pointers
        self.downloadView.consoleView = self.consoleView
        self.downloadView.modelDownload = self.modelDownload
        self.modelDownload.View = self.downloadView
