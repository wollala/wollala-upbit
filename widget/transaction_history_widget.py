import re

import pandas as pd
from PySide6 import QtCore, QtWidgets
from pytz import timezone

from data.order_history_pandas_model import OrderHistoryPandasModel
from util.data_manager import DataManager
from util.upbit_caller import UpbitCaller
from widget.date_filter_widget import DateFilterWidget
from widget.order_history_table_view import OrderHistoryTableView
from widget.waiting_spinner import WaitingSpinner


class TransactionHistoryWidget(QtWidgets.QWidget):
    loading_progress_order_history_changed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.upbit = UpbitCaller()
        self.dm = DataManager()

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
        model = OrderHistoryPandasModel(self.dm.order_history_df)
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

    @property
    def loading_progress_order_history(self):
        return self._loading_progress_order_history

    @loading_progress_order_history.setter
    def loading_progress_order_history(self, value):
        self._loading_progress_order_history = value
        self.loading_progress_order_history_changed.emit(value)  # noqa

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
            self.date_filter_widget.to_date_btn.setText(
                f'{self.to_date.year()}.{self.to_date.month():02d}.{self.to_date.day():02d}')
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
        self.update_model()

    @QtCore.Slot()
    def refresh_btn_clicked(self):
        self.dm.order_history_df = pd.DataFrame(
            columns=["주문시간", "마켓", "종류", "거래수량", "거래단가", "거래금액", "수수료", "정산금액"])
        self.play_spinner()

    @QtCore.Slot(int)
    def side_btn_clicked(self, btn):  # noqa
        self.update_model()

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
            items_list = [f"{i['korean_name']} ({i['market']})" for i in self.dm.krw_markets]
            self.ticker_filter_combobox.addItem("KRW 전체")
            self.ticker_filter_combobox.addItems(items_list)
        elif id == 2:
            self.ticker_filter_combobox.setEnabled(True)
            self.ticker_filter_combobox.clear()
            items_list = [f"{i['korean_name']} ({i['market']})" for i in self.dm.btc_markets]
            self.ticker_filter_combobox.addItem("BTC 전체")
            self.ticker_filter_combobox.addItems(items_list)

        self.update_model()

    def updated_order_history_df(self, progress_value, df):
        self.loading_progress_order_history = progress_value
        self.dm.order_history_df = pd.concat([self.dm.order_history_df, df], ignore_index=True)

    def update_model(self):
        if self.dm.order_history_df is not None:
            df_for_model = self.filtering_df(self.dm.order_history_df)
            model = OrderHistoryPandasModel(df_for_model)
            self.order_history_tableview.setModel(model)

    def play_spinner(self):
        self.refresh_btn.setEnabled(False)
        self.spinner.show()
        self.spinner.raise_()
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.stop()
        self.refresh_btn.setEnabled(True)

    def filtering_df(self, df):
        result_df = df.sort_values(by='주문시간', ascending=False)

        # 날짜 필터링
        from_datetime = QtCore.QDateTime.fromString(f'{self._from_date.toString("yyyy-MM-dd")} 00:00:00',
                                                    "yyyy-MM-dd hh:mm:ss")
        to_datetime = QtCore.QDateTime.fromString(f'{self._to_date.toString("yyyy-MM-dd")} 23:59:59',
                                                  "yyyy-MM-dd hh:mm:ss")
        from_datetime = from_datetime.toPython().astimezone(timezone('Asia/Seoul'))  # noqa
        to_datetime = to_datetime.toPython().astimezone(timezone('Asia/Seoul'))  # noqa

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
