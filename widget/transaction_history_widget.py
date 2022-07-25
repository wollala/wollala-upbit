import re

import pandas as pd
from PySide6 import QtCore, QtWidgets
from pytz import timezone

from data.order_history_pandas_model import OrderHistoryPandasModel
from widget.date_filter_widget import DateFilterWidget
from util.thread import Worker
from widget.calender_widget import CalenderWidget
from widget.order_history_table_view import OrderHistoryTableView
from widget.waiting_spinner import WaitingSpinner


class TransactionHistoryWidget(QtWidgets.QWidget):
    @property
    def from_date(self):
        return self._from_date

    @from_date.setter
    def from_date(self, value):
        self._from_date = value
        if self.order_history_df is not None:
            df_for_model = self.filtering_df(self.order_history_df)
            model = OrderHistoryPandasModel(df_for_model)
            self.order_history_tableview.setModel(model)

    @property
    def to_date(self):
        return self._to_date

    @to_date.setter
    def to_date(self, value):
        self._to_date = value
        if self.order_history_df is not None:
            df_for_model = self.filtering_df(self.order_history_df)
            model = OrderHistoryPandasModel(df_for_model)
            self.order_history_tableview.setModel(model)

    @property
    def loading_progress_order_history(self):
        return self._loading_progress_order_history

    @loading_progress_order_history.setter
    def loading_progress_order_history(self, value):
        self._loading_progress_order_history = value
        self.loading_progress_order_history_changed.emit(value)  # noqa

    @property
    def order_history_df(self):
        return self._order_history_df

    @order_history_df.setter
    def order_history_df(self, value):
        self._order_history_df = value
        self.order_history_df_changed.emit()  # noqa

    order_history_df_changed = QtCore.Signal()
    loading_progress_order_history_changed = QtCore.Signal(int)

    def __init__(self, upbit_client, krw_markets, btc_markets, parent=None):
        super().__init__(parent=parent)
        self.upbit_client = upbit_client
        self.krw_markets = krw_markets
        self.btc_markets = btc_markets

        self._order_history_df = pd.DataFrame(columns=["주문시간", "마켓", "종류", "거래수량", "거래단가", "거래금액", "수수료", "정산금액"])
        self._from_date = QtCore.QDate.currentDate()
        self._to_date = QtCore.QDate.currentDate()
        self._loading_progress_order_history = 0.0

        self._filteringed = False
        self._prev_double_clicked_text = None
        self._prev_from_date = self._from_date
        self._prev_to_date = self._to_date
        self._prev_ticker_text = ""
        self._prev_side_text = "전체"

        # Thread
        self.thread_pool = QtCore.QThreadPool.globalInstance()

        # Loading Spinner
        self.spinner = WaitingSpinner(self)

        # 새로고침 버튼
        self.refresh_btn = QtWidgets.QPushButton(u"\u21BB", parent=self)
        self.refresh_btn.setStyleSheet("font-size: 20px;")
        self.refresh_btn.setFixedHeight(58)
        self.refresh_btn.clicked.connect(self.refresh_btn_clicked)

        # Ticker Filter
        self.all_ticker_btn = QtWidgets.QPushButton("전체", parent=self)
        self.all_ticker_btn.setFixedHeight(25)
        self.all_ticker_btn.setCheckable(True)
        self.krw_ticker_btn = QtWidgets.QPushButton("KRW", parent=self)
        self.krw_ticker_btn.setFixedHeight(25)
        self.krw_ticker_btn.setCheckable(True)
        self.btc_ticker_btn = QtWidgets.QPushButton("BTC", parent=self)
        self.btc_ticker_btn.setFixedHeight(25)
        self.btc_ticker_btn.setCheckable(True)

        self.ticker_btn_group = QtWidgets.QButtonGroup(parent=self)
        self.ticker_btn_group.addButton(self.all_ticker_btn, 0)
        self.ticker_btn_group.addButton(self.krw_ticker_btn, 1)
        self.ticker_btn_group.addButton(self.btc_ticker_btn, 2)
        self.ticker_btn_group.buttonClicked.connect(self.ticker_btn_clicked)  # noqa

        self.ticker_filter_combobox = QtWidgets.QComboBox(parent=self)
        self.ticker_filter_combobox.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.ticker_filter_combobox.currentIndexChanged.connect(
            self.ticker_filter_combobox_currentIndex_changed)  # noqa

        ticker_groupbox_layout = QtWidgets.QGridLayout()
        ticker_groupbox_layout.addWidget(self.all_ticker_btn, 0, 0, 0, 1)
        ticker_groupbox_layout.addWidget(self.krw_ticker_btn, 0, 1, 0, 1)
        ticker_groupbox_layout.addWidget(self.btc_ticker_btn, 0, 2, 0, 1)
        ticker_groupbox_layout.addWidget(self.ticker_filter_combobox, 0, 3, 0, 7)
        ticker_groupbox = QtWidgets.QGroupBox("Tiker filter", parent=self)
        ticker_groupbox.setStyleSheet("QGroupBox{font-size: 12px;}")
        ticker_groupbox.setLayout(ticker_groupbox_layout)

        # 매수/매도 필터
        self.all_side_btn = QtWidgets.QPushButton("전체", parent=self)
        self.all_side_btn.setFixedHeight(25)
        self.all_side_btn.setCheckable(True)
        self.buy_side_btn = QtWidgets.QPushButton("매수", parent=self)
        self.buy_side_btn.setFixedHeight(25)
        self.buy_side_btn.setCheckable(True)
        self.sell_side_btn = QtWidgets.QPushButton("매도", parent=self)
        self.sell_side_btn.setFixedHeight(25)
        self.sell_side_btn.setCheckable(True)

        self.side_btn_group = QtWidgets.QButtonGroup(parent=self)
        self.side_btn_group.addButton(self.all_side_btn, 0)
        self.side_btn_group.addButton(self.buy_side_btn, 1)
        self.side_btn_group.addButton(self.sell_side_btn, 2)
        self.side_btn_group.buttonClicked.connect(self.side_btn_clicked)  # noqa

        side_groupbox_layout = QtWidgets.QGridLayout()
        side_groupbox_layout.addWidget(self.all_side_btn, 0, 0, 0, 1)
        side_groupbox_layout.addWidget(self.buy_side_btn, 0, 1, 0, 1)
        side_groupbox_layout.addWidget(self.sell_side_btn, 0, 2, 0, 1)
        side_groupbox = QtWidgets.QGroupBox("Side filter", parent=self)
        side_groupbox.setStyleSheet("QGroupBox{font-size: 12px;}")
        side_groupbox.setLayout(side_groupbox_layout)

        top_btn_layout = QtWidgets.QGridLayout()
        top_btn_layout.addWidget(ticker_groupbox, 0, 0, 0, 10)
        top_btn_layout.addWidget(side_groupbox, 0, 10, 0, 6)
        top_btn_layout.addWidget(QtWidgets.QWidget(parent=self), 0, 16, 0, 3)
        top_btn_layout.addWidget(self.refresh_btn, 0, 19, 0, 1, alignment=QtCore.Qt.AlignBottom)  # noqa

        self.date_filter_widget = DateFilterWidget()

        def set_from_date(from_date):
            self.from_date = from_date
        self.date_filter_widget.from_date_changed.connect(set_from_date)

        def set_to_date(to_date):
            self.to_date = to_date
        self.date_filter_widget.to_date_changed.connect(set_to_date)

        # 테이블
        self.order_history_tableview = OrderHistoryTableView()
        self.order_history_tableview.verticalScrollBar().setFixedWidth(10)
        model = OrderHistoryPandasModel(self.order_history_df)
        self.order_history_tableview.setModel(model)
        self.order_history_tableview.horizontalHeader().setStretchLastSection(True)
        self.order_history_tableview.setColumnWidth(0, 170)  # 주문시간
        self.order_history_tableview.setColumnWidth(1, 100)  # 마켓
        self.order_history_tableview.setColumnWidth(2, 60)  # 종류
        self.order_history_tableview.setColumnWidth(3, 170)  # 거래수량
        self.order_history_tableview.setColumnWidth(4, 170)  # 거래단가
        self.order_history_tableview.setColumnWidth(5, 170)  # 거래금액
        self.order_history_tableview.setColumnWidth(6, 140)  # 수수료
        self.order_history_tableview.setColumnWidth(7, 170)  # 정산금
        self.order_history_tableview.doubleClicked.connect(self.table_double_clicked)  # noqa

        self.table_layout = QtWidgets.QHBoxLayout()
        self.table_layout.addWidget(self.order_history_tableview)

        # 레이아웃
        main_layout = QtWidgets.QVBoxLayout(parent=self)
        main_layout.addLayout(top_btn_layout)
        main_layout.addWidget(self.date_filter_widget)
        main_layout.addLayout(self.table_layout)
        self.setLayout(main_layout)

        self.all_ticker_btn.setChecked(True)
        self.ticker_btn_clicked(self.all_ticker_btn)
        self.all_side_btn.setChecked(True)
        self.ticker_btn_clicked(self.all_side_btn)
        self.date_filter_widget.today_btn.setChecked(True)
        self.date_filter_widget.period_btn_clicked(self.date_filter_widget.today_btn)
        self.refresh_btn_clicked()

    @QtCore.Slot()
    def table_double_clicked(self, qmodel_index):
        col = qmodel_index.column()
        header_text = qmodel_index.model().headerData(col, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        cell_text = qmodel_index.data()
        if header_text == "주문시간":
            cell_text = cell_text.split(' ')[0]

        # 클릭했던 것을 다시 클릭하면 이전 상태로 복구함.
        if self._prev_double_clicked_text == cell_text and self._filteringed:
            self._filteringed = False
            if header_text == "주문시간":
                self.from_date = self._prev_from_date
                self.to_date = self._prev_to_date
                self.date_filter_widget.from_date_btn.setText(
                    f'{self._prev_from_date.year()}.{self._prev_from_date.month():02d}.{self._prev_from_date.day():02d}')
                self.date_filter_widget.to_date_btn.setText(
                    f'{self._prev_to_date.year()}.{self._prev_to_date.month():02d}.{self._prev_to_date.day():02d}')
            elif header_text == "마켓":
                if self._prev_ticker_text.startswith('KRW-') or self._prev_ticker_text.startswith('KRW 전체'):
                    self.krw_ticker_btn.setChecked(True)
                    self.ticker_btn_clicked(self.krw_ticker_btn)
                    index = self.ticker_filter_combobox.findText(self._prev_ticker_text,
                                                                 QtCore.Qt.MatchContains)  # noqa
                    if index >= 0:
                        self.ticker_filter_combobox.setCurrentIndex(index)
                elif self._prev_ticker_text.startswith('BTC-') or self._prev_ticker_text.startswith('BTC 전체'):
                    self.btc_ticker_btn.setChecked(True)
                    self.ticker_btn_clicked(self.btc_ticker_btn)
                    index = self.ticker_filter_combobox.findText(self._prev_ticker_text,
                                                                 QtCore.Qt.MatchContains)  # noqa
                    if index >= 0:
                        self.ticker_filter_combobox.setCurrentIndex(index)
                elif self._prev_ticker_text == 'KRW/BTC 전체':
                    self.all_ticker_btn.setChecked(True)
                    self.ticker_btn_clicked(self.all_ticker_btn)
            elif header_text == "종류":
                if self._prev_side_text == "매수":
                    self.buy_side_btn.setChecked(True)
                    self.side_btn_clicked(self.buy_side_btn)
                elif self._prev_side_text == "매도":
                    self.sell_side_btn.setChecked(True)
                    self.side_btn_clicked(self.sell_side_btn)
                elif self._prev_side_text == "전체":
                    self.all_side_btn.setChecked(True)
                    self.side_btn_clicked(self.all_side_btn)
            return
        else:  # 이전 상태 복구를 위한 데이터 저장
            self._filteringed = True
            if header_text == "주문시간":
                self._prev_double_clicked_text = cell_text.split(' ')[0]
            else:
                self._prev_double_clicked_text = cell_text
            self._prev_from_date = self._from_date
            self._prev_to_date = self._to_date
            self._prev_ticker_text = self.ticker_filter_combobox.currentText()
            if self.buy_side_btn.isChecked():
                self._prev_side_text = "매수"
            elif self.sell_side_btn.isChecked():
                self._prev_side_text = "매도"
            else:
                self._prev_side_text = "전체"

        # 필터링
        if header_text == "주문시간":
            self.date_filter_widget.unchecked_date_btn_group()
            self.from_date = QtCore.QDate.fromString(cell_text, "yyyy/MM/dd")
            self.to_date = QtCore.QDate.fromString(cell_text, "yyyy/MM/dd")
            self.date_filter_widget.from_date_btn.setText(
                f'{self.from_date.year()}.{self.from_date.month():02d}.{self.from_date.day():02d}')
            self.date_filter_widget.to_date_btn.setText(f'{self.to_date.year()}.{self.to_date.month():02d}.{self.to_date.day():02d}')
        elif header_text == "마켓":
            if cell_text.startswith('KRW-'):
                self.krw_ticker_btn.setChecked(True)
                self.ticker_btn_clicked(self.krw_ticker_btn)
            elif cell_text.startswith('BTC-'):
                self.btc_ticker_btn.setChecked(True)
                self.ticker_btn_clicked(self.btc_ticker_btn)
            index = self.ticker_filter_combobox.findText(cell_text, QtCore.Qt.MatchContains)  # noqa
            if index >= 0:
                self.ticker_filter_combobox.setCurrentIndex(index)
        elif header_text == "종류":
            if cell_text == "매수":
                self.buy_side_btn.setChecked(True)
                self.side_btn_clicked(self.buy_side_btn)
            elif cell_text == "매도":
                self.sell_side_btn.setChecked(True)
                self.side_btn_clicked(self.sell_side_btn)

    @QtCore.Slot()
    def ticker_filter_combobox_currentIndex_changed(self):  # noqa
        if self.order_history_df is not None:
            df_for_model = self.filtering_df(self.order_history_df)
            model = OrderHistoryPandasModel(df_for_model)
            self.order_history_tableview.setModel(model)

    @QtCore.Slot()
    def refresh_btn_clicked(self):
        def worker_fn():
            self.get_all_orders_by_upbit()

        def finish_fn():
            self.stop_spinner()

        self.play_spinner()
        worker = Worker(worker_fn)
        worker.signals.finished.connect(finish_fn)
        self.thread_pool.start(worker)

    @QtCore.Slot(int)
    def side_btn_clicked(self, btn):  # noqa
        if self.order_history_df is not None:
            df_for_model = self.filtering_df(self.order_history_df)
            model = OrderHistoryPandasModel(df_for_model)
            self.order_history_tableview.setModel(model)

    @QtCore.Slot(int)
    def ticker_btn_clicked(self, btn):
        id = self.ticker_btn_group.id(btn)
        if id == 0:
            self.ticker_filter_combobox.setEnabled(False)
            self.ticker_filter_combobox.clear()
            self.ticker_filter_combobox.addItem("KRW/BTC 전체")
        elif id == 1:
            self.ticker_filter_combobox.setEnabled(True)
            self.ticker_filter_combobox.clear()
            items_list = [f"{i['korean_name']} ({i['market']})" for i in self.krw_markets]
            self.ticker_filter_combobox.addItem("KRW 전체")
            self.ticker_filter_combobox.addItems(items_list)
        elif id == 2:
            self.ticker_filter_combobox.setEnabled(True)
            self.ticker_filter_combobox.clear()
            items_list = [f"{i['korean_name']} ({i['market']})" for i in self.btc_markets]
            self.ticker_filter_combobox.addItem("BTC 전체")
            self.ticker_filter_combobox.addItems(items_list)

        if self.order_history_df is not None:
            df_for_model = self.filtering_df(self.order_history_df)
            model = OrderHistoryPandasModel(df_for_model)
            self.order_history_tableview.setModel(model)

    def get_all_orders_by_upbit(self):
        # 전체 주문 History 요청
        _order_info_all = []
        page = 1
        while True:
            orders = self.upbit_client.Order.Order_info_all(page=page, limit=100, states=["done", "cancel"])['result']
            _order_info_all = _order_info_all + orders
            page += 1
            if len(orders) < 100:
                break
        _order_info_all = [order for order in _order_info_all if order['trades_count'] > 0]

        # 개별 주문에 대한 Detailed info 요청 및 업데이트
        for i, order in enumerate(_order_info_all):
            detailed_order = self.upbit_client.Order.Order_info(uuid=order['uuid'])['result']
            if 'trades' in detailed_order and detailed_order['trades']:
                df_trades = pd.DataFrame(detailed_order['trades'])
                df_trades = df_trades.astype({'funds': float,
                                              'price': float,
                                              'volume': float})
                fund = df_trades['funds'].sum()
                trading_price = df_trades['price'].sum() / detailed_order['trades_count']
                trading_volume = df_trades['volume'].sum()
                order['fund'] = fund
                order['trading_price'] = trading_price
                order['trading_volume'] = trading_volume
                if order['side'] == 'ask':  # 매도시 최종금액 = 정산금액 - 수수료
                    order['executed_fund'] = order['fund'] - float(order['paid_fee'])
                else:  # 매수시 최종금액 = 정산금액 + 수수료
                    order['executed_fund'] = order['fund'] + float(order['paid_fee'])
            # single dict to df로 변환
            df = pd.DataFrame([order])
            df.loc[(df.side == 'bid'), 'side'] = '매수'
            df.loc[(df.side == 'ask'), 'side'] = '매도'

            df.drop(['uuid', 'ord_type', 'price', 'state', 'trades_count', 'volume', 'executed_volume',
                     'remaining_volume', 'reserved_fee', 'remaining_fee', 'locked'], axis=1, inplace=True, errors='ignore')
            df.rename(columns={'side': '종류', 'trading_price': '거래단가', 'market': '마켓', 'created_at': '주문시간',
                               'paid_fee': '수수료', 'fund': '거래금액', 'trading_volume': '거래수량',
                               'executed_fund': '정산금액'}, inplace=True)
            df = df.reindex(columns=['주문시간', '마켓', '종류', '거래수량', '거래단가', '거래금액', '수수료', '정산금액'])
            df['주문시간'] = pd.to_datetime(df['주문시간'])
            df = df.astype({'수수료': float})

            # update progress bar in main
            self.loading_progress_order_history = (i + 1) / len(_order_info_all) * 100
            # 저장
            self.order_history_df = pd.concat([self.order_history_df, df], ignore_index=True)
            self.order_history_df_changed.emit()  # noqa

    def play_spinner(self):
        self.refresh_btn.setEnabled(False)
        self.spinner.show()
        self.spinner.raise_()
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.stop()
        self.refresh_btn.setEnabled(True)

    def update_table_model(self):
        df_for_model = self.filtering_df(self.order_history_df)
        model = OrderHistoryPandasModel(df_for_model)
        self.order_history_tableview.setModel(model)

    def filtering_df(self, df):
        result_df = df.sort_values(by='주문시간', ascending=False)

        # 날짜 필터링
        from_datetime = QtCore.QDateTime.fromString(f'{self._from_date.toString("yyyy-MM-dd")} 00:00:00',
                                                    "yyyy-MM-dd hh:mm:ss")
        to_datetime = QtCore.QDateTime.fromString(f'{self._to_date.toString("yyyy-MM-dd")} 23:59:59',
                                                  "yyyy-MM-dd hh:mm:ss")
        from_datetime = from_datetime.toPython().astimezone(timezone('Asia/Seoul'))
        to_datetime = to_datetime.toPython().astimezone(timezone('Asia/Seoul'))

        result_df = result_df.query(
            '@from_datetime <= 주문시간 <= @to_datetime'
        )

        # 매수 매도 필터링
        side_btn_id = self.side_btn_group.checkedId()
        if side_btn_id == 0:  # 전체
            pass
        elif side_btn_id == 1:  # 매수
            result_df = result_df.query('종류.str.contains("매수")')
        elif side_btn_id == 2:  # 매도
            result_df = result_df.query('종류.str.contains("매도")')

        # 코인 필터링
        if self.ticker_filter_combobox.currentText() == "KRW/BTC 전체":
            pass
        elif self.ticker_filter_combobox.currentText() == "KRW 전체":
            result_df = result_df.query('마켓.str.contains("KRW-")')
        elif self.ticker_filter_combobox.currentText() == "BTC 전체":
            result_df = result_df.query('마켓.str.contains("BTC-")')
        else:  # 일반 코인 선택
            temp_list = re.findall('\((KRW-[^)]+|BTC-[^)]+)\)', self.ticker_filter_combobox.currentText())  # noqa
            if temp_list:
                target_ticker = temp_list[0]  # noqa
                result_df = result_df.query('마켓.str.contains(@target_ticker)')
            else:
                return result_df.dropna()

        # index 정리
        result_df = result_df.reset_index(drop=True)
        return result_df
