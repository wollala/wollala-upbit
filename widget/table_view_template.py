import csv
import io

import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui


# 우클릭 메뉴 sum, copy를 기본으로 지원
class TableViewTemplate(QtWidgets.QTableView):
    sumFinished = QtCore.Signal(pd.DataFrame, float)

    def __init__(self, parent=None):
        super(TableViewTemplate, self).__init__(parent=parent)

        self.action_group = {
            # "sum": {
            #         "action": sum_action, // action object
            #         "column_list": [column_name..] // 활성되는 Column 이름 List
            # }
            # "copy": {
            #         "action": copy_action
            #         "column_list": [column_name..]
            # }
        }
        self.menu = QtWidgets.QMenu(parent=self)

        sum_action = QtGui.QAction('더하기', parent=self)
        sum_action.setStatusTip('선택 된 Cell의 값들을 더합니다.')
        sum_action.triggered.connect(self.sum)
        self.action_group['sum'] = {
            'action': sum_action,
            'column_list': []
        }
        self.menu.addAction(sum_action)

        copy_action = QtGui.QAction("복사", parent=self)
        copy_action.setStatusTip('선택 된 Cell의 값들을 클립보드에 복사합니다.')
        copy_action.triggered.connect(self.copySelection)
        self.action_group['copy'] = {
            'action': copy_action,
            'column_list': []
        }
        self.menu.addAction(copy_action)

    def contextMenuEvent(self, event):
        selected_haeder_list = list(set(  # 중복제거를 위한 set
            map(lambda i: i.model().headerData(i.column(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole),
                self.selectedIndexes())))

        for v in self.action_group.values():
            if len(v['column_list']) == 0:  # 비어있으면 항상 활성화
                v['action'].setEnabled(True)
            else:
                v['action'].setEnabled(False)
                
            if len(selected_haeder_list) == 1 and len(self.selectedIndexes()) > 1:
                if selected_haeder_list[0] in v['column_list']:
                    v['action'].setEnabled(True)
                else:
                    v['action'].setEnabled(False)

        if len(self.menu.actions()) > 0:
            self.menu.popup(QtGui.QCursor.pos())

    def keyPressEvent(self, event):
        # Ctrl+C 처리
        if event.matches(QtGui.QKeySequence.Copy):
            self.copySelection()

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

            # 숫자 뒤의 'KRW', 'BTC', '%', ',' 문자 삭제
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

    @QtCore.Slot()
    def sum(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]

        sum_df = df.reindex(selected_row_list)[header_text]
        result = sum_df.sum()
        self.sumFinished.emit(sum_df, result)
