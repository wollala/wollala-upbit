import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui
from upbit.client import Upbit

from UserSetting import UserSetting
from data.AccountInfoPandasModel import AccountInfoPandasModel
from data.SummaryPandasModel import PandasModel
from util.Thread import Worker
from widget.WaitingSpinner import WaitingSpinner
from widget.AccountInfoTableView import AccountInfoTableView


class AccountInfoWidget(QtWidgets.QWidget):
    def __init__(self, krw_markets, btc_markets):
        super(AccountInfoWidget, self).__init__()
        self.krw_markets = krw_markets
        self.btc_markets = btc_markets
        self.account_info_df = None
        self.summary_df = None
        # Thread
        self.thread_pool = QtCore.QThreadPool.globalInstance()

        # Loading Spinner
        self.spinner = WaitingSpinner(self)

        # 새로고침 버튼
        self.refresh_btn = QtWidgets.QPushButton(u"\u21BB")
        self.refresh_btn.setStyleSheet("font-size: 20px;")
        self.refresh_btn.setFixedHeight(58)
        self.refresh_btn.clicked.connect(self.refresh_btn_clicked)

        # TableView
        self.summary_tableview = QtWidgets.QTableView()
        summary_header_model = QtGui.QStandardItemModel()
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

        top_layout = QtWidgets.QGridLayout()
        top_layout.addWidget(self.summary_tableview, 0, 0, 0, 18, alignment=QtCore.Qt.AlignTop)
        top_layout.addWidget(self.refresh_btn, 0, 19, 0, 1, alignment=QtCore.Qt.AlignBottom)

        # TableView
        self.account_info_tableview = AccountInfoTableView()
        account_info_header_model = QtGui.QStandardItemModel()
        account_info_header_model.setHorizontalHeaderLabels(['화폐종류', '보유수량', '매수평균가', '현재가', '매수금액', '평가금액', '평가손익', '수익률'])
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

        # Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.account_info_tableview)
        self.setLayout(main_layout)

        # Get data
        self.refresh_btn_clicked()

    def refresh_btn_clicked(self):
        def worker_fn():
            user_setting = UserSetting()
            upbit = Upbit(user_setting.upbit['access_key'], user_setting.upbit['secret_key'])
            account_info = upbit.Account.Account_info()
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
            krw_price_list = upbit.Trade.Trade_ticker(markets=krw_markets_string)['result']
            btc_price_list = upbit.Trade.Trade_ticker(markets=btc_markets_string)['result']
            krw_price_df = pd.DataFrame(krw_price_list, columns={'market', 'trade_price'})
            btc_price_df = pd.DataFrame(btc_price_list, columns={'market', 'trade_price'})
            btc_price = krw_price_df[krw_price_df['market'] == 'KRW-BTC']['trade_price']  # 코인의 btc가격 * btc의 krw가격
            # KRW 마켓코인: trade_price = 코인의 krw가격
            # BTC 마켓코인: trade_price = 코인의 btc가격 * btc의 krw가격
            btc_price_df['trade_price'] = btc_price_df.loc[:, 'trade_price'] * btc_price
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

        def result_fn(df):
            self.account_info_df = df

        def finish_fn():
            self.summary_df = pd.DataFrame()
            self.summary_df["보유KRW"] = self.account_info_df[self.account_info_df["화폐종류"] == "KRW"]["보유수량"]
            self.summary_df["총 보유자산"] = self.summary_df["보유KRW"] + self.account_info_df["평가금액"].sum()
            self.summary_df["총매수"] = self.account_info_df["매수금액"].sum()
            self.summary_df["투자비율"] = self.summary_df["총매수"] / (self.summary_df["보유KRW"] + self.summary_df["총매수"]) * 100
            self.summary_df["총평가"] = self.account_info_df["평가금액"].sum()
            self.summary_df["평가손익"] = self.summary_df["총평가"] - self.summary_df["총매수"]
            self.summary_df['수익률'] = self.summary_df["평가손익"] / self.summary_df["총매수"] * 100
            self.summary_df = self.summary_df.reindex(
                columns=['보유KRW', '총매수', '투자비율', '총 보유자산', '총평가', '평가손익', '수익률'])
            self.summary_tableview.setModel(PandasModel(self.summary_df))
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