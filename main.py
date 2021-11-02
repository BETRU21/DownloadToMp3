from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from View.mainWindow import MainWindow as Window
import ctypes
import sys
import os

if sys.platform == "win32":
    myappid = u"mycompany.myproduct.subproduct.version" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
else:
    pass

application_path = os.path.abspath("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = Window()
    win.setWindowIcon(QIcon(application_path + "{0}View{0}logo{0}logo.ico".format(os.sep)))
    win.setWindowTitle("DownloadToMp3")
    win.show()
    sys.exit(app.exec_())