import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui


class AccountInfoTableView(QtWidgets.QTableView):
    sumFinished = QtCore.Signal(pd.DataFrame, float)

    def __init__(self):
        super(AccountInfoTableView, self).__init__()
        self.sum_action = QtGui.QAction('합', self)
        self.sum_action.setStatusTip('선택된 Cell 값들을 더합니다.')
        self.sum_action.triggered.connect(self.sum)

        self.menu = QtWidgets.QMenu(self)

    def contextMenuEvent(self, event):
        self.menu.clear()

        selected_haeder_set = set(
            map(lambda i: i.model().headerData(i.column(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole),
                self.selectedIndexes()))

        # 같은 Column 선택 & 선택 cell 1개 이상
        if len(selected_haeder_set) == 1 and len(self.selectedIndexes()) > 1:
            if "매수금액" in selected_haeder_set:
                self.menu.addAction(self.sum_action)
            if "평가금액" in selected_haeder_set:
                self.menu.addAction(self.sum_action)
            if "평가손익" in selected_haeder_set:
                self.menu.addAction(self.sum_action)

        if len(self.menu.actions()) > 0:
            self.menu.popup(QtGui.QCursor.pos())

    @QtCore.Slot(bool)
    def sum(self, checked):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]

        sum_df = df.reindex(selected_row_list)[header_text]
        result = sum_df.sum()
        self.sumFinished.emit(sum_df, result)
