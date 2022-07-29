import pandas as pd
from PySide6 import QtCore, QtGui

from widget.table_view_template import TableViewTemplate


class OrderHistoryTableView(TableViewTemplate):
    meanFinished = QtCore.Signal(pd.DataFrame, pd.DataFrame, float)
    bidMinusAskFinished = QtCore.Signal(pd.DataFrame, pd.DataFrame, float)
    askMinusBidFinished = QtCore.Signal(pd.DataFrame, pd.DataFrame, float)

    def __init__(self, parent=None):
        super(OrderHistoryTableView, self).__init__(parent=parent)
        self.action_group['sum']['column_list'] = ['거래수량', '거래단가', '거래금액', '수수료', '정산금액']

        mean_action = QtGui.QAction('평균단가', parent=self)
        mean_action.setStatusTip('평균단가를 구합니다.')
        mean_action.triggered.connect(self.mean)
        self.action_group['mean'] = {
            'action': mean_action,
            'column_list': ['거래단가']
        }
        self.menu.addAction(mean_action)

        bid_minus_ask_action = QtGui.QAction('매수 - 매도', parent=self)
        bid_minus_ask_action.setStatusTip('선택 된 Cell의 값들 중 매수영역의 값과 매도영역의 값의 차를 구합니다.')
        bid_minus_ask_action.triggered.connect(self.bid_minus_ask)
        self.action_group['bid_minus_ask'] = {
            'action': bid_minus_ask_action,
            'column_list': ['거래수량']
        }
        self.menu.addAction(bid_minus_ask_action)

        ask_minus_bid_action = QtGui.QAction('매도 - 매수', parent=self)
        ask_minus_bid_action.setStatusTip('선택 된 Cell 값들 중 매도영역의 값과 매수영역의 값의 차를 구합니다.')
        ask_minus_bid_action.triggered.connect(self.ask_minus_bid)
        self.action_group['ask_minus_bid'] = {
            'action': ask_minus_bid_action,
            'column_list': ['거래금액', '정산금액']
        }
        self.menu.addAction(ask_minus_bid_action)

    @QtCore.Slot()
    def mean(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]
        trading_volume_df = df["거래수량"]
        trading_volume_df = trading_volume_df.reindex(selected_row_list)
        trading_price_df = df.reindex(selected_row_list)[header_text]

        result = (trading_volume_df * trading_price_df).sum() / trading_volume_df.sum()
        self.meanFinished.emit(trading_volume_df, trading_price_df, result)

    @QtCore.Slot()
    def bid_minus_ask(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]
        buy_df = df[df["종류"] == "매수"]
        ask_df = df[df["종류"] == "매도"]
        buy_df = buy_df.reindex(selected_row_list)[header_text]
        ask_df = ask_df.reindex(selected_row_list)[header_text]

        result = buy_df.sum() - ask_df.sum()
        self.bidMinusAskFinished.emit(buy_df, ask_df, result)

    @QtCore.Slot()
    def ask_minus_bid(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]
        buy_df = df[df["종류"] == "매수"]
        ask_df = df[df["종류"] == "매도"]
        buy_df = buy_df.reindex(selected_row_list)[header_text]
        ask_df = ask_df.reindex(selected_row_list)[header_text]

        result = ask_df.sum() - buy_df.sum()
        self.bidMinusAskFinished.emit(ask_df, buy_df, result)
