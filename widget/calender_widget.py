from PySide6 import QtCore, QtWidgets, QtGui


class CalenderWidget(QtWidgets.QCalendarWidget):
    closed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.closed.emit()
