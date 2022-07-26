from PySide6 import QtWidgets


class PnlCoinTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(PnlCoinTableView, self).__init__(parent=parent)
