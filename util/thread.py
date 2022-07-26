from PySide6.QtCore import QThread


class Worker(QThread):
    def __init__(self, run_func, parent=None):
        QThread.__init__(self, parent)
        self.run_func = run_func

    def run(self):
        self.run_func()

    def stop(self):
        self.terminate()
        self.wait(3000)
