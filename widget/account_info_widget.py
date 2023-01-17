import logging

import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui, QtCharts

from data.account_info_pandas_model import AccountInfoPandasModel
from data.summary_pandas_model import SummaryPandasModel
from util.data_manager import DataManager
from util.upbit_caller import UpbitCaller
from widget.account_info_table_view import AccountInfoTableView
from widget.summary_table_view import SummaryTableView
from widget.waiting_spinner import WaitingSpinner


class AccountInfoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AccountInfoWidget, self).__init__(parent=parent)
        self.upbit = UpbitCaller()
        self.dm = DataManager()
        # self.krw_markets = krw_markets
        # self.btc_markets = btc_markets
        self.account_info_df = None
        self.summary_df = None

        # Loading Spinner
        self.spinner = WaitingSpinner(self)

        # 새로고침 버튼
        self.refresh_btn = QtWidgets.QPushButton(u"\u21BB", parent=self)
        self.refresh_btn.setStyleSheet("font-size: 20px;")
        self.refresh_btn.setFixedHeight(58)
        self.refresh_btn.clicked.connect(self.refresh_btn_clicked)

        # TableView
        self.summary_tableview = SummaryTableView()
        summary_header_model = QtGui.QStandardItemModel(parent=self)
        summary_header_model.setHorizontalHeaderLabels(['보유KRW', '총매수', '투자비율', '총 보유자산', '총평가', '평가손익', '수익률'])
        self.summary_tableview.verticalHeader().setHidden(True)
        self.summary_tableview.setModel(summary_header_model)
        self.summary_tableview.horizontalHeader().setStretchLastSection(True)
        self.summary_tableview.setColumnWidth(0, 210)  # 보유KRW
        self.summary_tableview.setColumnWidth(1, 130)  # 총매수
        self.summary_tableview.setColumnWidth(2, 130)  # 투자비율
        self.summary_tableview.setColumnWidth(3, 130)  # 총 보유자산
        self.summary_tableview.setColumnWidth(4, 130)  # 총평가
        self.summary_tableview.setColumnWidth(5, 130)  # 평가손익
        self.summary_tableview.setColumnWidth(6, 70)  # 수익률
        self.summary_tableview.setFixedHeight(58)

        # TableView
        self.account_info_tableview = AccountInfoTableView()
        account_info_header_model = QtGui.QStandardItemModel(parent=self)
        account_info_header_model.setHorizontalHeaderLabels(
            ['화폐종류', '보유수량', '매수평균가', '현재가', '매수금액', '평가금액', '평가손익', '수익률'])
        self.account_info_tableview.verticalHeader().setHidden(True)
        self.account_info_tableview.setModel(account_info_header_model)
        self.account_info_tableview.horizontalHeader().setStretchLastSection(True)
        self.account_info_tableview.setColumnWidth(0, 80)  # 화폐종류
        self.account_info_tableview.setColumnWidth(1, 130)  # 보유수량
        self.account_info_tableview.setColumnWidth(2, 130)  # 매수평균가
        self.account_info_tableview.setColumnWidth(3, 130)  # 현재가
        self.account_info_tableview.setColumnWidth(4, 130)  # 매수금액
        self.account_info_tableview.setColumnWidth(5, 130)  # 평가금액
        self.account_info_tableview.setColumnWidth(6, 130)  # 평가손익
        self.account_info_tableview.setColumnWidth(7, 70)  # 수익률

        # PieChart
        def on_hovered(slice, state):
            if state:
                slice.setExploded()
                slice.setLabelVisible()
            else:
                slice.setExploded(False)
                slice.setLabelVisible(False)

        self.chart = QtCharts.QChart()
        self.chart.setTheme(QtCharts.QChart.ChartThemeBlueCerulean)
        self.series = QtCharts.QPieSeries()
        self.series.hovered.connect(on_hovered)
        self.chart.addSeries(self.series)
        self.chart.setTitle('보유자산 포트폴리오')
        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)  # noqa
        self.chart.legend().setAlignment(QtCore.Qt.AlignRight)

        self.chart_view = QtCharts.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

        # Layout
        left_frame = QtWidgets.QFrame(parent=self)
        left_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_left_layout = QtWidgets.QGridLayout()
        top_left_layout.addWidget(self.summary_tableview, 0, 0, 1, 14)
        top_left_layout.addWidget(self.refresh_btn, 0, 14, 1, 1)
        top_left_layout.addWidget(self.account_info_tableview, 1, 0, 1, 15)
        left_frame.setLayout(top_left_layout)

        right_frame = QtWidgets.QFrame(parent=self)
        right_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_right_layout = QtWidgets.QGridLayout()
        top_right_layout.addWidget(self.chart_view)
        right_frame.setLayout(top_right_layout)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, parent=self)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setHandleWidth(5)
        splitter.setSizes([1100, 500])

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def refresh_btn_clicked(self):
        self.play_spinner()

    def updated_asset_df(self):
        # for pie chart
        try:
            self.series.clear()
            for index, row in self.dm.asset_df.iterrows():
                if row['화폐종류'] and row['화폐종류'] == 'KRW':
                    self.series.append(row['화폐종류'], row['보유수량'])
                elif row['평가금액'] and not pd.isna(row['평가금액']):
                    self.series.append(row['화폐종류'], row['평가금액'])

            for s in self.series.slices():
                s.setBorderColor("black")
                s.setLabel(f'{s.label()} {100 * s.percentage():.2f} %')

            self.summary_tableview.setModel(SummaryPandasModel(self.dm.asset_summary_df))
            self.account_info_tableview.setModel(AccountInfoPandasModel(self.dm.asset_df))
            self.stop_spinner()
        except Exception as e:
            logging.exception(e)

    def play_spinner(self):
        self.setEnabled(False)
        self.spinner.show()
        self.spinner.raise_()
        self.spinner.start()

    def stop_spinner(self):
        self.setEnabled(True)
        self.spinner.stop()
