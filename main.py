import re
import sys

import pandas as pd
from PySide6 import QtWidgets, QtGui, QtCore
from upbit.client import Upbit

from UserSetting import UserSetting
from dialog.APIKeyInputDialog import APIKeyInputDialog
from dialog.TickerSelectionDialog import TickerSelectionDialog
from widget.AccountInfoWidget import AccountInfoWidget
from widget.TransactionHistoryWidget import TransactionHistoryWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.user_setting = UserSetting()
        self.upbit_settings = self.user_setting.upbit

        upbit = Upbit()
        tickers = upbit.Market.Market_info_all()['result']
        for i in tickers:
            i['checked'] = False
        self.krw_markets = [item for item in tickers if 'KRW-' in item['market']]
        self.krw_markets = sorted(self.krw_markets, key=lambda item: item["korean_name"])
        for name in self.upbit_settings['transaction_history']['selected_krw_markets']:
            # 괄호 안의 문자 찾기 ex) 비트코인 (KRW-BTC) 에서 KRW-BTC 찾기
            ticker = re.findall('\((KRW-[^)]+|BTC-[^)]+)\)', name)[0]  # noqa
            for market in self.krw_markets:
                # currency(coin code) 추가 (ETH, BTC, XRP..)
                market["currency"] = market["market"].split('-')[1]

                if market['market'] == ticker:
                    market['checked'] = True
        self.btc_markets = [item for item in tickers if 'BTC-' in item['market']]
        self.btc_markets = sorted(self.btc_markets, key=lambda item: item["korean_name"])
        for name in self.upbit_settings['transaction_history']['selected_btc_markets']:
            # 괄호 안의 문자 찾기 ex) 비트코인 (KRW-BTC) 에서 KRW-BTC 찾기
            ticker = re.findall('\((KRW-[^)]+|BTC-[^)]+)\)', name)[0]  # noqa
            for market in self.btc_markets:
                # currency(coin code) 추가 (ETH, BTC, XRP..)
                market["currency"] = market["market"].split('-')[1]

                if market['market'] == ticker:
                    market['checked'] = True

        # Account Info Widget
        self.account_info_widget = AccountInfoWidget(self.krw_markets, self.btc_markets)

        # 거래내역 관련 Widget
        self.transaction_history_widget = TransactionHistoryWidget(self.krw_markets, self.btc_markets)

        # 계산결과 출력 Widget
        self.calculate_result_widget = QtWidgets.QTextBrowser()
        self.calculate_result_widget.setStyleSheet(
            "background-color: rgb(34, 40, 64);"
            "color: rgb(157, 159, 170)"
        )
        self.calculate_result_widget.setAcceptRichText(True)
        self.account_info_widget.account_info_tableview.sumFinished.connect(self.append_krw_sum)
        self.transaction_history_widget.order_history_tableview.sumFinished.connect(self.append_sum)
        self.transaction_history_widget.order_history_tableview.meanFinished.connect(self.append_mean)
        self.transaction_history_widget.order_history_tableview.bidMinusAskFinished.connect(self.append_bid_minus_ask)
        self.transaction_history_widget.order_history_tableview.askMinusBidFinished.connect(self.append_ask_minus_bid)

        # tabWidget
        main_widget = QtWidgets.QFrame()

        top_frame = QtWidgets.QFrame(self)
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.account_info_widget)
        top_frame.setLayout(top_layout)

        mid_frame = QtWidgets.QFrame(self)
        mid_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mid_layout = QtWidgets.QHBoxLayout()
        mid_layout.addWidget(self.transaction_history_widget)
        mid_frame.setLayout(mid_layout)

        bottom_frame = QtWidgets.QFrame(self)
        bottom_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.calculate_result_widget)
        bottom_frame.setLayout(bottom_layout)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(top_frame)
        splitter.addWidget(mid_frame)
        splitter.addWidget(bottom_frame)
        splitter.setHandleWidth(5)
        splitter.setSizes([300, 500, 200])

        main_widget_layout = QtWidgets.QHBoxLayout()
        main_widget_layout.addWidget(splitter)
        main_widget.setLayout(main_widget_layout)
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.addTab(main_widget, "투자내역")

        # menu bar
        bar = self.menuBar()

        ## 설정 메뉴
        setting_menu = bar.addMenu("설정")

        api_key_menu_action = QtGui.QAction("API key 입력", self)
        api_key_menu_action.setStatusTip("거래내역을 불러오기 위한 Upbit API key 입력")
        api_key_menu_action.triggered.connect(self.on_api_key_menu_clicked)
        setting_menu.addAction(api_key_menu_action)

        coin_select_menu_action = QtGui.QAction("코인 선택", self)
        coin_select_menu_action.setStatusTip("거래내역을 불러오고자 하는 코인 선택")
        coin_select_menu_action.triggered.connect(self.on_coin_select_menu_clicked)
        setting_menu.addAction(coin_select_menu_action)

        ## 도움말 메뉴
        help_menu = bar.addMenu("도움말")

        info_menu_action = QtGui.QAction("정보", self)
        info_menu_action.setStatusTip("Wollala Upbit 정보")
        info_menu_action.triggered.connect(self.on_info_menu_clicked)
        help_menu.addAction(info_menu_action)

        # 코인 선택 메뉴 Dialog
        self.ticker_selection_dialog = TickerSelectionDialog(self.krw_markets, self.btc_markets)
        self.ticker_selection_dialog.hide()

        # API key 입력 Dialog
        self.api_key_input_dialog = APIKeyInputDialog()
        self.api_key_input_dialog.hide()

        # 프로그램 정보 dialog
        self.program_info_dialog = QtWidgets.QMessageBox(self)
        self.program_info_dialog.setStyleSheet("* {margin-left: 0; margin-right: 15; }")
        self.program_info_dialog.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)  # noqa
        self.program_info_dialog.setWindowTitle("프로그램 정보")
        self.program_info_dialog.setText(
            "<p style='text-align: center;'><img src='qrc://Info.png' alt='' width='42' height='42'></p>"
            "<p style='text-align: center;'><strong>Wollala Upbit</strong></p>"
            "<p style='text-align: center;'>Version 0.0.1 (Beta)</p>"
            "<p style='text-align: center;'>by Wollala (<a href='mailto:wollala.zip@gmail.com'>wollala.zip@gmail.com</a>)</p>"  # noqa 
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'>이 프로그램은 어떠한 형태의 보증도 제공하지 않습니다.</p>"
            "<p style='text-align: center;'>발생하는 모든 문제에 대한 책임은 이 프로그램의 사용자에게 있습니다.</p>"
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'><b>Support</b></p>"
            "<p style='text-align: center;'>Bug report: <a href='mailto:wollala.zip@gmail.com'>wollala.zip@gmail.com</a></p>"  # noqa
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'><b>Donation</b></p>"
            "<p style='text-align: center;'><b>BTC</b>: 34EvTZBAPqT7SviBLggjn4PV9qZG4PVcFp</p>"
            "<p style='text-align: center;'><b>ETH</b>: 0xc281565c8f5fe037570aac45021db4897fd6ce19</p>"
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'>Copyright &copy; Wollala, 2021&ndash;2022. All rights reserved.</p>"
        )
        self.program_info_dialog.hide()

        self.statusBar()
        self.setCentralWidget(tab_widget)
        self.setWindowTitle('Wollala Upbit')
        self.resize(1240, 1000)

    def on_api_key_menu_clicked(self, s):
        self.api_key_input_dialog.show()

    def on_coin_select_menu_clicked(self, s):
        self.ticker_selection_dialog.show()

    def on_info_menu_clicked(self, s):
        self.program_info_dialog.show()

    def append_krw_sum(self, df, result):
        df = df.reset_index(drop=True)
        result_str = '<b><font color="#f3f3f4">' + "{0:,.0f}".format(result) + "</font></b>"
        format_str = ''

        for idx in df.index:
            if not pd.isnull(df.loc[idx]):
                format_str = format_str + ' + ' + "{0:,.0f}".format(df.loc[idx])
        format_str = format_str[3:]
        result_str = result_str + " = " + format_str
        self.calculate_result_widget.append("합 계산 결과")
        self.calculate_result_widget.append(result_str)

    def append_sum(self, df, result):
        df = df.reset_index(drop=True)
        result_str = '<b><font color="#f3f3f4">' + "{0:,.8f}".format(result) + "</font></b>"
        format_str = ''

        for idx in df.index:
            if not pd.isnull(df.loc[idx]):
                format_str = format_str + ' + ' + "{0:,.8f}".format(df.loc[idx])
        format_str = format_str[3:]
        result_str = result_str + " = " + format_str
        self.calculate_result_widget.append("합 계산 결과")
        self.calculate_result_widget.append(result_str)

    def append_mean(self, trading_volume_df, trading_price_df, result):
        trading_volume_df = trading_volume_df.reset_index(drop=True)
        trading_price_df = trading_price_df.reset_index(drop=True)
        result_str = '<b><font color="#f3f3f4">' + "{0:,.8f}".format(result) + "</font></b>"
        format_str0 = ''
        format_str1 = ''

        for i in trading_volume_df.index:
            format_str0 = format_str0 + ' + ' + "{0:,.8f}".format(trading_volume_df.loc[i]) + ' x ' + "{0:,.8f}".format(
                trading_price_df.loc[i])

        for i in trading_volume_df.index:
            format_str1 = format_str1 + ' + ' + "{0:,.8f}".format(trading_volume_df.loc[i])

        format_str0 = format_str0[3:]
        format_str1 = format_str1[3:]
        result_str = result_str + ' = ' + '<b><font color="#cecfd5">(</fond></b>' + format_str0 + \
                     '<b><font color="#cecfd5">)</fond></b>' + ' / ' + \
                     '<b><font color="#cecfd5">(</fond></b>' + \
                     format_str1 + '<b><font color="#cecfd5">)</fond></b>'

        self.calculate_result_widget.append("평단가 계산 결과")
        self.calculate_result_widget.append(result_str)

    def append_ask_minus_bid(self, ask_df, bid_df, result):
        ask_df = ask_df.reset_index(drop=True)
        bid_df = bid_df.reset_index(drop=True)
        result_str = '<b><font color="#f3f3f4">' + "{0:,.8f}".format(result) + "</font></b>"
        format_str0 = ''
        format_str1 = ''

        for idx in ask_df.index:
            if not pd.isnull(ask_df.loc[idx]):
                format_str0 = format_str0 + ' + ' + "{0:,.8f}".format(ask_df.loc[idx])
        format_str0 = format_str0[3:]
        format_str0 = '<b><font color="#cecfd5">(</fond></b>' + format_str0 + '<b><font color="#cecfd5">)</fond></b>'

        for idx in bid_df.index:
            if not pd.isnull(bid_df.loc[idx]):
                format_str1 = format_str1 + ' + ' + "{0:,.8f}".format(bid_df.loc[idx])
        format_str1 = format_str1[3:]
        format_str1 = '<b><font color="#cecfd5">(</fond></b>' + format_str1 + '<b><font color="#cecfd5">)</fond></b>'
        result_str = result_str + " = " + format_str0 + " - " + format_str1
        self.calculate_result_widget.append("매도 - 매수 계산 결과")
        self.calculate_result_widget.append(result_str)

    def append_bid_minus_ask(self, bid_df, ask_df, result):
        ask_df = ask_df.reset_index(drop=True)
        bid_df = bid_df.reset_index(drop=True)
        result_str = '<b><font color="#f3f3f4">' + "{0:,.8f}".format(result) + "</font></b>"
        format_str0 = ''
        format_str1 = ''

        for idx in ask_df.index:
            if not pd.isnull(ask_df.loc[idx]):
                format_str0 = format_str0 + ' + ' + "{0:,.8f}".format(ask_df.loc[idx])
        format_str0 = format_str0[3:]
        format_str0 = '<b><font color="#cecfd5">(</fond></b>' + format_str0 + '<b><font color="#cecfd5">)</fond></b>'

        for idx in bid_df.index:
            if not pd.isnull(bid_df.loc[idx]):
                format_str1 = format_str1 + ' + ' + "{0:,.8f}".format(bid_df.loc[idx])
        format_str1 = format_str1[3:]
        format_str1 = '<b><font color="#cecfd5">(</fond></b>' + format_str1 + '<b><font color="#cecfd5">)</fond></b>'
        result_str = result_str + " = " + format_str1 + " - " + format_str0
        self.calculate_result_widget.append("매도 - 매수 계산 결과")
        self.calculate_result_widget.append(result_str)


app = QtWidgets.QApplication([])
main_window = MainWindow()
main_window.show()

sys.exit(app.exec())
