import pandas as pd
from PySide6 import QtCore, QtWidgets
from pytz import timezone

from data.pnl_coin_pandas_model import PnlCoinPandasModel
from util.data_manager import DataManager
from widget.date_filter_widget import DateFilterWidget
from widget.pnl_coin_table_view import PnlCoinTableView


class PnlCoinWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PnlCoinWidget, self).__init__(parent=parent)
        self.dm = DataManager()
        self.pnl_coin_df = pd.DataFrame(
            columns=["마켓", "총 매수수량", "총 매도수량", "미실현수량", "총 매수금액", "총 매도금액", "매수 평단가", "매도 평단가",
                     "실현손익", "수익률"])
        self._from_date = QtCore.QDate.currentDate()
        self._to_date = QtCore.QDate.currentDate()

        self.date_filter_widget = DateFilterWidget()

        def set_from_date(from_date):
            self.from_date = from_date
        self.date_filter_widget.from_date_changed.connect(set_from_date)

        def set_to_date(to_date):
            self.to_date = to_date
        self.date_filter_widget.to_date_changed.connect(set_to_date)

        # 테이블
        self.pnl_coin_table_view = PnlCoinTableView()
        model = PnlCoinPandasModel(self.pnl_coin_df)
        self.pnl_coin_table_view.setModel(model)
        self.pnl_coin_table_view.verticalScrollBar().setFixedWidth(10)
        self.pnl_coin_table_view.horizontalHeader().setStretchLastSection(True)
        self.pnl_coin_table_view.setColumnWidth(0, 100)  # 마켓
        self.pnl_coin_table_view.setColumnWidth(1, 170)  # 총 매수수량
        self.pnl_coin_table_view.setColumnWidth(2, 170)  # 총 매도수량
        self.pnl_coin_table_view.setColumnWidth(3, 170)  # 총 매수금액
        self.pnl_coin_table_view.setColumnWidth(4, 170)  # 총 매도금액
        self.pnl_coin_table_view.setColumnWidth(5, 170)  # 매수 평단가
        self.pnl_coin_table_view.setColumnWidth(6, 170)  # 매도 평단가
        self.pnl_coin_table_view.setColumnWidth(7, 170)  # 미 실현손익
        self.pnl_coin_table_view.setColumnWidth(8, 170)  # 실현손익
        self.pnl_coin_table_view.setColumnWidth(9, 80)  # 수익률

        # 레이아웃
        main_layout = QtWidgets.QVBoxLayout(parent=self)
        main_layout.addWidget(self.date_filter_widget)
        main_layout.addWidget(self.pnl_coin_table_view)
        self.setLayout(main_layout)

    @property
    def from_date(self):
        return self._from_date

    @from_date.setter
    def from_date(self, value):
        self._from_date = value
        self.update_model()

    @property
    def to_date(self):
        return self._to_date

    @to_date.setter
    def to_date(self, value):
        self._to_date = value
        self.update_model()

    def filtering_df(self, df):
        result_df = df.sort_values(by='주문시간', ascending=False)

        # 날짜 필터링 님프가
        from_datetime = QtCore.QDateTime.fromString(f'{self._from_date.toString("yyyy-MM-dd")} 00:00:00',
                                                    "yyyy-MM-dd hh:mm:ss")
        to_datetime = QtCore.QDateTime.fromString(f'{self._to_date.toString("yyyy-MM-dd")} 23:59:59',
                                                  "yyyy-MM-dd hh:mm:ss")
        from_datetime = from_datetime.toPython().astimezone(timezone('Asia/Seoul'))  # noqa
        to_datetime = to_datetime.toPython().astimezone(timezone('Asia/Seoul'))  # noqa

        result_df = result_df.query(
            '@from_datetime <= 주문시간 <= @to_datetime'
        )

        # index 정리 asdf한글 이제 gm  GG adgasdgasdfasdf시발
        result_df = result_df.reset_index(drop=True)
        return result_df

    def update_model(self):
        if self.dm.order_history_df is not None:
            filterd_df = self.filtering_df(self.dm.order_history_df)
            self.dm.asset_period_pnl_df = self.dm.create_asset_period_pnl_df(filterd_df)
            model = PnlCoinPandasModel(self.dm.asset_period_pnl_df)
            self.pnl_coin_table_view.setModel(model)
