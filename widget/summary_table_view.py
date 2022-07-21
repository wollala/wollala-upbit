import csv
import io

from PySide6 import QtWidgets, QtCore, QtGui


class SummaryTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(SummaryTableView, self).__init__(parent=parent)
        self.copy_action = QtGui.QAction("복사", parent=self)
        self.copy_action.setStatusTip('선택 된 Cell의 내용을 클립보드에 복사합니다.')
        self.copy_action.triggered.connect(self.copySelection)

        self.menu = QtWidgets.QMenu(parent=self)

    def contextMenuEvent(self, event):
        self.menu.clear()
        self.menu.addAction(self.copy_action)

        if len(self.menu.actions()) > 0:
            self.menu.popup(QtGui.QCursor.pos())

    # Ctrl+C 처리
    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copySelection()

    # csv 형태로 클립보드에 복사
    @QtCore.Slot()
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
                    table[i][j] = table[i][j].replace(' %', '')
            stream = io.StringIO()
            csv.writer(stream, delimiter='\t').writerows(table)
            copy_str = stream.getvalue().replace(' KRW', '')
            copy_str = copy_str.replace(' BTC', '')
            QtWidgets.QApplication.clipboard().setText(copy_str)