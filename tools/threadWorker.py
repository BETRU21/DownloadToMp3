from PyQt5.QtCore import *


class Worker(QObject):
    def __init__(self, workerFunction, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = workerFunction
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            print("ERROR: ", e)
