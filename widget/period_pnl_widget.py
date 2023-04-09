import pandas as pd
from PySide6 import QtCore, QtWidgets
from pytz import timezone

from data.period_pnl_pandas_model import PeriodPnLPandasModel
from util.data_manager import DataManager
from widget.date_filter_widget import DateFilterWidget
from widget.period_pnl_table_view import PeriodPnLTableView


class PeriodPnLWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PeriodPnLWidget, self).__init__(parent=parent)
        self.dm = DataManager()
        self.period_pnl_df = pd.DataFrame(
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
        self.period_pnl_table_view = PeriodPnLTableView()
        model = PeriodPnLPandasModel(self.period_pnl_df)
        self.period_pnl_table_view.setModel(model)
        self.period_pnl_table_view.horizontalHeader().setStretchLastSection(True)
        self.period_pnl_table_view.setColumnWidth(0, 100)  # 마켓
        self.period_pnl_table_view.setColumnWidth(1, 150)  # 총 매수수량
        self.period_pnl_table_view.setColumnWidth(2, 150)  # 총 매도수량
        self.period_pnl_table_view.setColumnWidth(3, 150)  # 총 매수금액
        self.period_pnl_table_view.setColumnWidth(4, 150)  # 총 매도금액
        self.period_pnl_table_view.setColumnWidth(5, 150)  # 매수 평단가
        self.period_pnl_table_view.setColumnWidth(6, 150)  # 매도 평단가
        self.period_pnl_table_view.setColumnWidth(7, 150)  # 미 실현손익
        self.period_pnl_table_view.setColumnWidth(8, 150)  # 실현손익
        self.period_pnl_table_view.setColumnWidth(9, 70)  # 수익률

        self.pnl_title = QtWidgets.QLabel("[PNL]")
        self.pnl_since = QtWidgets.QLabel("SINCE: ")
        self.pnl_krw_layout = QtWidgets.QLabel("KRW: " + str(0), self)
        self.pnl_btc_layout = QtWidgets.QLabel("BTC: " + str(0), self)

        # 레이아웃
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.date_filter_widget)
        self.main_layout.addWidget(self.period_pnl_table_view)
        self.main_layout.addWidget(self.pnl_title)
        self.main_layout.addWidget(self.pnl_since)
        self.main_layout.addWidget(self.pnl_krw_layout)
        self.main_layout.addWidget(self.pnl_btc_layout)
        self.setLayout(self.main_layout)

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
        result_df = df.sort_values(by="주문시간", ascending=False)

        from_datetime = QtCore.QDateTime.fromString(f"{self._from_date.toString('yyyy-MM-dd')} 00:00:00",
                                                    "yyyy-MM-dd hh:mm:ss")
        to_datetime = QtCore.QDateTime.fromString(f"{self._to_date.toString('yyyy-MM-dd')} 23:59:59",
                                                  "yyyy-MM-dd hh:mm:ss")
        from_datetime = from_datetime.toPython().astimezone(timezone("Asia/Seoul"))  # noqa
        to_datetime = to_datetime.toPython().astimezone(timezone("Asia/Seoul"))  # noqa

        result_df = result_df.query(
            "@from_datetime <= 주문시간 <= @to_datetime"
        )

        result_df = result_df.reset_index(drop=True)
        return result_df

    def update_model(self):
        if self.dm.order_history_df is not None:
            filterd_df = self.filtering_df(self.dm.order_history_df)
            self.dm.asset_period_pnl_df, since, pnl_krw, pnl_btc = self.dm.create_asset_period_pnl_df(filterd_df)

            self.pnl_since.setText("SINCE: " + str(since))
            self.pnl_krw_layout.setText("KRW: " + "{:,}".format(pnl_krw))
            self.pnl_btc_layout.setText("BTC: " + "{:,}".format(pnl_btc))

            model = PeriodPnLPandasModel(self.dm.asset_period_pnl_df)
            self.period_pnl_table_view.setModel(model)
