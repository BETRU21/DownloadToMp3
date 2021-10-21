from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from View.mainWindow import MainWindow as Window
import ctypes
import sys
import os

appID = "DownloadToMp3"
if os.name == 'nt':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)
elif os.name == 'posix':
    pass

applicationPath = os.path.abspath("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    MainWindow = QMainWindow()
    win = Window()
    win.setWindowIcon(QIcon(applicationPath + "{0}View{0}logo{0}logo.ico".format(os.sep)))
    win.setWindowTitle("DownloadToMp3")
    win.show()
    sys.exit(app.exec())
