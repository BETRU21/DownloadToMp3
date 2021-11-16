from View.ViewConsole import ViewConsole
from View.ViewDownload import ViewDownload
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QAction, QLabel, QMenu
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
        self.setupMenuBar()
        self.connectButton()

    def connectButton(self):
        self.englishLanguage.triggered.connect(self.changeLanguageEnglish)
        self.frenchLanguage.triggered.connect(self.changeLanguageFrench)

    def changeLanguageEnglish(self):
        language = self.downloadView.currentLanguage()
        if language == "english":
            pass
        else:
            self.tabWidget.setTabText(0,"Download")
            self.downloadView.changeLanguage("english")

    def changeLanguageFrench(self):
        language = self.downloadView.currentLanguage()
        if language == "french":
            pass
        else:
            self.tabWidget.setTabText(0,"Téléchargement")
            self.downloadView.changeLanguage("french")

    def setupWindowTabs(self):
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.tabWidget.addTab(self.downloadView, "Download")
        self.tabWidget.addTab(self.consoleView, "Console")

    def createsComponentsAndPointers(self):
        # Components
        self.downloadView = ViewDownload()
        self.consoleView = ViewConsole()

        # Pointers
        self.downloadView.consoleView = self.consoleView
        self.consoleView.downloadView = self.downloadView

    def setupMenuBar(self):
        self.languageMenu = self.menubar.addMenu("Language")
        self.englishLanguage = QAction("English", self)
        self.frenchLanguage = QAction("Français", self)
        self.languageMenu.addAction(self.englishLanguage)
        self.languageMenu.addAction(self.frenchLanguage)
