import io
import csv
import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui


class AccountInfoTableView(QtWidgets.QTableView):
    sumFinished = QtCore.Signal(pd.DataFrame, float)

    def __init__(self, parent=None):
        super(AccountInfoTableView, self).__init__(parent=parent)
        self.sum_action = QtGui.QAction('합', parent=self)
        self.sum_action.setStatusTip('선택된 Cell 값들을 더합니다.')
        self.sum_action.triggered.connect(self.sum)

        self.menu = QtWidgets.QMenu(parent=self)

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

    # Ctrl+C 처리
    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copySelection()

    # csv 형태로 클립보드에 복사
    def copySelection(self):
        selection = self.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()

            # 숫자 뒤의 KRW, BTC 문자 삭제
            for i, _v in enumerate(table):
                for j, _p in enumerate(table[i]):
                    table[i][j] = table[i][j].replace(',', '')
                    table[i][j] = table[i][j].replace(' KRW', '')
                    table[i][j] = table[i][j].replace(' BTC', '')
            stream = io.StringIO()
            csv.writer(stream).writerows(table)
            copy_str = stream.getvalue().replace(' KRW', '')
            copy_str = copy_str.replace(' BTC', '')
            QtWidgets.QApplication.clipboard().setText(copy_str)

    @QtCore.Slot(bool)
    def sum(self, checked):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]

        sum_df = df.reindex(selected_row_list)[header_text]
        result = sum_df.sum()
        self.sumFinished.emit(sum_df, result)
