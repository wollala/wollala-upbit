import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui, QtCharts

from data.account_info_pandas_model import AccountInfoPandasModel
from data.summary_pandas_model import SummaryPandasModel
from util.thread import Worker
from widget.account_info_table_view import AccountInfoTableView
from widget.summary_table_view import SummaryTableView
from widget.waiting_spinner import WaitingSpinner


class AccountInfoWidget(QtWidgets.QWidget):
    def __init__(self, upbit_client, krw_markets, btc_markets, parent=None):
        super(AccountInfoWidget, self).__init__(parent=parent)
        self.upbit_client = upbit_client
        self.krw_markets = krw_markets
        self.btc_markets = btc_markets
        self.account_info_df = None
        self.summary_df = None
        # Thread
        self.thread_pool = QtCore.QThreadPool.globalInstance()

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
        self.summary_tableview.setColumnWidth(0, 180)  # 보유KRW
        self.summary_tableview.setColumnWidth(1, 180)  # 총매수
        self.summary_tableview.setColumnWidth(2, 80)  # 투자비율
        self.summary_tableview.setColumnWidth(3, 180)  # 총 보유자산
        self.summary_tableview.setColumnWidth(4, 180)  # 총평가
        self.summary_tableview.setColumnWidth(5, 180)  # 평가손익
        self.summary_tableview.setColumnWidth(6, 80)  # 수익률
        self.summary_tableview.setFixedHeight(58)

        # TableView
        self.account_info_tableview = AccountInfoTableView()
        account_info_header_model = QtGui.QStandardItemModel(parent=self)
        account_info_header_model.setHorizontalHeaderLabels(
            ['화폐종류', '보유수량', '매수평균가', '현재가', '매수금액', '평가금액', '평가손익', '수익률'])
        self.account_info_tableview.verticalHeader().setHidden(True)
        self.account_info_tableview.setModel(account_info_header_model)
        self.account_info_tableview.horizontalHeader().setStretchLastSection(True)
        self.account_info_tableview.setColumnWidth(0, 60)  # 화폐종류
        self.account_info_tableview.setColumnWidth(1, 170)  # 보유수량
        self.account_info_tableview.setColumnWidth(2, 170)  # 매수평균가
        self.account_info_tableview.setColumnWidth(3, 170)  # 현재가
        self.account_info_tableview.setColumnWidth(4, 170)  # 매수금액
        self.account_info_tableview.setColumnWidth(5, 170)  # 평가금액
        self.account_info_tableview.setColumnWidth(6, 170)  # 평가손익
        self.account_info_tableview.setColumnWidth(7, 80)  # 수익률

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
        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
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
        splitter.setSizes([500, 200])

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Get data
        self.refresh_btn_clicked()

    def refresh_btn_clicked(self):
        def worker_fn():
            account_info = None
            try:
                account_info = self.upbit_client.Account.Account_info()
                account_info_list = account_info['result']

                coin_base_krw_market = ['KRW-BTC']
                coin_base_btc_market = []

                # 각 코인의 market을 찾는다.
                # KRW에 있는면 KRW로 BTC에만 있으면 BTC로..
                for i in account_info_list:
                    if i['currency'] in [i['currency'] for i in self.krw_markets]:
                        market_string = f'KRW-{i["currency"]}'
                        i['market'] = market_string
                        coin_base_krw_market.append(market_string)
                    elif i['currency'] in [i['currency'] for i in self.btc_markets]:
                        market_string = f'BTC-{i["currency"]}'
                        i['market'] = market_string
                        coin_base_btc_market.append(market_string)
                krw_markets_string = ','.join(set(coin_base_krw_market))
                btc_markets_string = ','.join(set(coin_base_btc_market))
                krw_price_list = self.upbit_client.Trade.Trade_ticker(markets=krw_markets_string)['result']
                btc_price_list = self.upbit_client.Trade.Trade_ticker(markets=btc_markets_string)['result']
                krw_price_df = pd.DataFrame(krw_price_list, columns={'market', 'trade_price'})
                btc_price_df = pd.DataFrame(btc_price_list, columns={'market', 'trade_price'})
                btc_price = krw_price_df.loc[krw_price_df['market'] == 'KRW-BTC']['trade_price'].reset_index(drop=True)

                # KRW 마켓코인: trade_price = 코인의 krw가격
                # BTC 마켓코인: trade_price = 코인의 btc가격 * btc의 krw가격
                btc_price_df['trade_price'] = btc_price_df.loc[:, 'trade_price'] * btc_price[0]
                price_df = pd.concat([krw_price_df, btc_price_df], axis=0)

                account_info_df = pd.DataFrame(account_info_list)
                account_info_df = pd.merge(account_info_df, price_df, how='left', on='market')
                account_info_df = account_info_df.astype({
                    'locked': float,
                    'balance': float,
                    'avg_buy_price': float,
                    'trade_price': float
                })
                account_info_df['balance'] = account_info_df['balance'] + account_info_df['locked']

                account_info_df.drop(['locked', 'avg_buy_price_modified', 'unit_currency', 'market'], axis=1, inplace=True)
                account_info_df.rename(
                    columns={'balance': '보유수량', 'avg_buy_price': '매수평균가', 'currency': '화폐종류', 'trade_price': '현재가'},
                    inplace=True)

                account_info_df['매수금액'] = account_info_df['보유수량'] * account_info_df['매수평균가']
                account_info_df['평가금액'] = account_info_df['보유수량'] * account_info_df['현재가']
                account_info_df['평가손익'] = account_info_df['평가금액'] - account_info_df['매수금액']
                account_info_df['수익률'] = account_info_df['평가손익'] / account_info_df['매수금액'] * 100

                account_info_df = account_info_df.reindex(
                    columns=['화폐종류', '보유수량', '매수평균가', '현재가', '매수금액', '평가금액', '평가손익', '수익률'])
                return account_info_df
            except Exception as e:
                return pd.DataFrame(columns=['화폐종류', '보유수량', '매수평균가', '현재가', '매수금액', '평가금액', '평가손익', '수익률'])

        def result_fn(df):
            # for table
            import numpy as np
            df['평가금액'] = np.where(df['화폐종류'] == 'KRW', df['보유수량'], df['평가금액'])
            df = df.sort_values(by="평가금액", ascending=False)
            self.account_info_df = df

            # for pie chart
            self.series.clear()
            for index, row in df.iterrows():
                if row['화폐종류'] == 'KRW':
                    self.series.append(row['화폐종류'], row['보유수량'])
                elif row['평가금액'] and not pd.isna(row['평가금액']):
                    self.series.append(row['화폐종류'], row['평가금액'])

            for s in self.series.slices():
                s.setBorderColor("black")
                s.setLabel(f'{s.label()} {100 * s.percentage():.2f} %')

        def finish_fn():
            self.summary_df = pd.DataFrame()
            self.summary_df["보유KRW"] = self.account_info_df[self.account_info_df["화폐종류"] == "KRW"]["보유수량"]
            self.summary_df["총 보유자산"] = self.account_info_df["평가금액"].sum()
            self.summary_df["총매수"] = self.account_info_df["매수금액"].sum()
            self.summary_df["투자비율"] = self.summary_df["총매수"] / (self.summary_df["보유KRW"] + self.summary_df["총매수"]) * 100
            self.summary_df["총평가"] = self.account_info_df["평가금액"].sum() - self.summary_df["보유KRW"]
            self.summary_df["평가손익"] = self.summary_df["총평가"] - self.summary_df["총매수"]
            self.summary_df['수익률'] = self.summary_df["평가손익"] / self.summary_df["총매수"] * 100
            self.summary_df = self.summary_df.reindex(
                columns=['보유KRW', '총매수', '투자비율', '총 보유자산', '총평가', '평가손익', '수익률'])
            self.summary_df = self.summary_df.reset_index(drop=True)
            self.summary_tableview.setModel(SummaryPandasModel(self.summary_df))
            self.account_info_tableview.setModel(AccountInfoPandasModel(self.account_info_df))

            self.stop_spinner()

        self.play_spinner()
        worker = Worker(worker_fn)
        worker.signals.result.connect(result_fn)
        worker.signals.finished.connect(finish_fn)
        self.thread_pool.start(worker)

    def play_spinner(self):
        self.setEnabled(False)
        self.spinner.show()
        self.spinner.raise_()
        self.spinner.start()

    def stop_spinner(self):
        self.setEnabled(True)
        self.spinner.stop()
