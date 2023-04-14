import sys

import pandas as pd
from PySide6 import QtWidgets, QtGui, QtCore

from dialog.apikey_input_dialog import APIKeyInputDialog
from dialog.program_info_dialog import ProgramInfoDialog
from user_setting import UserSetting
from util.data_manager import DataManager
from util.thread import Worker
from util.upbit_caller import UpbitCaller
from widget.account_info_widget import AccountInfoWidget
from widget.period_pnl_widget import PeriodPnLWidget
from widget.transaction_history_widget import TransactionHistoryWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        upbit_config = UserSetting().upbit
        self.dm = DataManager()
        self.upbit = UpbitCaller(upbit_config["access_key"], upbit_config["secret_key"])

        # Thread workers
        self.asset_thread_worker = Worker(run_func=self.asset_thread_worker_fn, parent=self)
        self.orders_thread_worker = Worker(run_func=self.orders_thread_worker_fn, parent=self)

        api_key_test_response = self.upbit.api_key_test()
        if not api_key_test_response:
            QtWidgets.QMessageBox.information(self, 'wollala-upbit 메시지',
                                              f'Upbit 서버의 응답이 없습니다.\n'
                                              f'처음 사용자라면, API key를 등록 후 사용해주세요.\n')
        elif not api_key_test_response['ok']:
            QtWidgets.QMessageBox.information(self, 'wollala-upbit 메시지',
                                              f'upbit 서버와 API key 인증과정에서 문제가 생겼습니다.\n'
                                              f'처음 사용자라면, API key를 등록 후 사용해주세요.\n'
                                              f'{api_key_test_response["reason"]}')

        all_markets_ticker = self.upbit.request_all_markets_ticker()
        self.dm.krw_markets = all_markets_ticker['krw_markets']
        self.dm.btc_markets = all_markets_ticker['btc_markets']

        # Create Tab members
        self.main_tab0_widget = self.create_main_tab0()

        # Tab widget
        tab_widget = QtWidgets.QTabWidget(parent=self)
        tab_widget.addTab(self.main_tab0_widget, "투자내역")

        # Progress Bar
        self.progressbar = QtWidgets.QProgressBar(parent=self)
        self.progressbar.setTextVisible(True)
        self.progressbar.setAlignment(QtCore.Qt.AlignCenter)  # noqa
        self.progressbar.setMaximumWidth(500)
        self.statusBar().addPermanentWidget(self.progressbar)
        self.transaction_history_widget.loading_progress_order_history_changed.connect(self.update_progressbar)

        # menu bar
        bar = self.menuBar()

        # 설정 메뉴
        setting_menu = bar.addMenu("설정")

        api_key_menu_action = QtGui.QAction("API key 입력", parent=self)
        api_key_menu_action.setStatusTip("거래내역을 불러오기 위한 Upbit API key 입력")
        api_key_menu_action.triggered.connect(self.api_key_menu_clicked)
        setting_menu.addAction(api_key_menu_action)

        # 도움말 메뉴
        help_menu = bar.addMenu("도움말")

        info_menu_action = QtGui.QAction("정보", parent=self)
        info_menu_action.setStatusTip("wollala-upbit 정보")
        info_menu_action.triggered.connect(self.info_menu_clicked)
        help_menu.addAction(info_menu_action)

        # API key 입력 dialog
        self.apikey_input_dialog = APIKeyInputDialog(parent=self)
        self.apikey_input_dialog.upbit_client_updated.connect(self.updated_upbit_client)
        self.apikey_input_dialog.hide()

        # 프로그램 정보 dialog
        self.program_info_dialog = ProgramInfoDialog(parent=self)

        self.statusBar()
        self.setCentralWidget(tab_widget)
        self.setWindowTitle('wollala-upbit')
        self.resize(1600, 1000)

    @QtCore.Slot()
    def api_key_menu_clicked(self, s):  # noqa
        self.apikey_input_dialog.show()

    @QtCore.Slot()
    def info_menu_clicked(self, s):  # noqa
        self.program_info_dialog.show()

    @QtCore.Slot()
    def model_Updated(self, first_order_day, last_order_day, pnl_krw, pnl_btc):
        self.calculate_console_widget.append("========  수익률  ========")
        self.calculate_console_widget.append(f'기간 : <b><font color="#f3f3f4">{first_order_day.strftime("%Y-%m-%d %H:%M:%S")}</font></b> ~ <b><font color="#f3f3f4">{last_order_day.strftime("%Y-%m-%d %H:%M:%S")}</font></b>'
                                             f' ({last_order_day - first_order_day})')
        self.calculate_console_widget.append(f'KRW   : <b><font color="#f3f3f4">{pnl_krw:>,.0f}</font></b> ￦')
        self.calculate_console_widget.append(f'BTC   : <b><font color="#f3f3f4">{pnl_btc:>,.8f}</font></b> btc')

    @QtCore.Slot()
    def krw_sum_finished(self, df, result):
        df = df.reset_index(drop=True)
        result = f'{result:,.0f}' if result % 1 == 0 else f'{result:,.8f}'
        result_str = f'<b><font color="#f3f3f4">{result}</font></b>'
        format_str = ''

        for idx in df.index:
            if not pd.isnull(df.loc[idx]):
                format_str = f'{format_str} + {df.loc[idx]:,.0f}'
        format_str = format_str[3:]
        result_str = f'{result_str} = {format_str}'
        self.calculate_console_widget.append("합 계산 결과")
        self.calculate_console_widget.append(result_str)

    @QtCore.Slot()
    def sum_finished(self, df, result):
        df = df.reset_index(drop=True)
        result = f'{result:,.0f}' if result % 1 == 0 else f'{result:,.8f}'
        result_str = f'<b><font color="#f3f3f4">{result}</font></b>'
        format_str = ''

        for idx in df.index:
            if not pd.isnull(df.loc[idx]):
                if df.loc[idx] % 1 == 0:
                    format_str = f'{format_str} + {df.loc[idx]:,.0f}'
                else:
                    format_str = f'{format_str} + {df.loc[idx]:,.8f}'
        format_str = format_str[3:]
        result_str = f'{result_str} = {format_str}'
        self.calculate_console_widget.append("합 계산 결과")
        self.calculate_console_widget.append(result_str)

    @QtCore.Slot()
    def mean_finished(self, trading_volume_df, trading_price_df, result):
        trading_volume_df = trading_volume_df.reset_index(drop=True)
        trading_price_df = trading_price_df.reset_index(drop=True)
        result = f'{result:,.0f}' if result % 1 == 0 else f'{result:,.8f}'
        result_str = f'<b><font color="#f3f3f4">{result}</font></b>'
        format_str0 = ''
        format_str1 = ''

        for i in trading_volume_df.index:
            format_str0 = f'{format_str0} + {trading_volume_df.loc[i]:,.8f} x {trading_price_df.loc[i]:,.8f}'

        for i in trading_volume_df.index:
            format_str1 = f'{format_str1} + {trading_volume_df.loc[i]:,.8f}'

        format_str0 = format_str0[3:]
        format_str1 = format_str1[3:]
        result_str = f'{result_str} =' \
                     f'<b><font color="#cecfd5">(</fond></b>{format_str0}<b><font color="#cecfd5">)</fond></b> / ' \
                     f'<b><font color="#cecfd5">(</fond></b>{format_str1}<b><font color="#cecfd5">)</fond></b>'

        self.calculate_console_widget.append("평단가 계산 결과")
        self.calculate_console_widget.append(result_str)

    @QtCore.Slot()
    def ask_minus_bid_finished(self, ask_df, bid_df, result):
        ask_df = ask_df.reset_index(drop=True)
        bid_df = bid_df.reset_index(drop=True)
        result = f'{result:,.0f}' if result % 1 == 0 else f'{result:,.8f}'
        result_str = f'<b><font color="#f3f3f4">{result}</font></b>'
        format_str0 = ''
        format_str1 = ''

        for idx in ask_df.index:
            if not pd.isnull(ask_df.loc[idx]):
                format_str0 = f'{format_str0} + {ask_df.loc[idx]:,.8f}'
        format_str0 = format_str0[3:]
        format_str0 = f'<b><font color="#cecfd5">(</fond></b>{format_str0}<b><font color="#cecfd5">)</fond></b>'

        for idx in bid_df.index:
            if not pd.isnull(bid_df.loc[idx]):
                format_str1 = f'{format_str1} + {bid_df.loc[idx]:,.8f}'
        format_str1 = format_str1[3:]
        format_str1 = f'<b><font color="#cecfd5">(</fond></b>{format_str1}<b><font color="#cecfd5">)</fond></b>'
        result_str = f'{result_str} = {format_str0} - {format_str1}'
        self.calculate_console_widget.append("매도 - 매수 계산 결과")
        self.calculate_console_widget.append(result_str)

    @QtCore.Slot()
    def bid_minus_ask_finished(self, bid_df, ask_df, result):
        ask_df = ask_df.reset_index(drop=True)
        bid_df = bid_df.reset_index(drop=True)
        result = f'{result:,.0f}' if result % 1 == 0 else f'{result:,.8f}'
        result_str = f'<b><font color="#f3f3f4">{result}</font></b>'
        format_str0 = ''
        format_str1 = ''

        for idx in ask_df.index:
            if not pd.isnull(ask_df.loc[idx]):
                format_str0 = f'{format_str0} + {ask_df.loc[idx]:,.8f}'
        format_str0 = format_str0[3:]
        format_str0 = f'<b><font color="#cecfd5">(</fond></b>{format_str0}<b><font color="#cecfd5">)</fond></b>'

        for idx in bid_df.index:
            if not pd.isnull(bid_df.loc[idx]):
                format_str1 = f'{format_str1} + {bid_df.loc[idx]:,.8f}'
        format_str1 = format_str1[3:]
        format_str1 = f'<b><font color="#cecfd5">(</fond></b>{format_str1}<b><font color="#cecfd5">)</fond></b>'
        result_str = f'{result_str} = {format_str1} - {format_str0}'
        self.calculate_console_widget.append("매도 - 매수 계산 결과")
        self.calculate_console_widget.append(result_str)

    @QtCore.Slot()
    def update_progressbar(self, v):
        if v == 100:
            self.progressbar.setValue(v)
            self.progressbar.setFormat(f'거래내역을 모두 가져왔어요!')
            self.progressbar.setEnabled(False)
        else:
            self.progressbar.setEnabled(True)
            self.progressbar.setValue(v)
            self.progressbar.setFormat(f'거래내역을 가져오는 중..({self.progressbar.value()} %)')

    @QtCore.Slot()
    def updated_upbit_client(self):
        all_markets_ticker = self.upbit.request_all_markets_ticker()
        self.dm.krw_markets = all_markets_ticker['krw_markets']
        self.dm.btc_markets = all_markets_ticker['btc_markets']
        self.asset_thread_worker.start()
        self.orders_thread_worker.start()

    def create_main_tab0(self):
        # Top widget
        # Account Info Widget
        self.account_info_widget = AccountInfoWidget(parent=self)
        self.account_info_widget.account_info_tableview.sumFinished.connect(self.krw_sum_finished)
        self.account_info_widget.refresh_btn.clicked.connect(self.asset_thread_worker.start)
        self.asset_thread_worker.finished.connect(self.account_info_widget.updated_asset_df)
        self.asset_thread_worker.start()

        top_frame = QtWidgets.QFrame(parent=self)
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.account_info_widget)
        top_frame.setLayout(top_layout)

        # Mid widget. Mid has 2 tabs
        # 거래내역 관련 Widget
        self.transaction_history_widget = TransactionHistoryWidget(parent=self)
        self.transaction_history_widget.order_history_tableview.sumFinished.connect(self.sum_finished)
        self.transaction_history_widget.order_history_tableview.meanFinished.connect(self.mean_finished)
        self.transaction_history_widget.order_history_tableview.bidMinusAskFinished.connect(self.bid_minus_ask_finished)
        self.transaction_history_widget.order_history_tableview.askMinusBidFinished.connect(self.ask_minus_bid_finished)
        self.transaction_history_widget.refresh_btn.clicked.connect(self.orders_thread_worker.start)
        self.orders_thread_worker.finished.connect(self.transaction_history_widget.stop_spinner)
        self.orders_thread_worker.start()
        self.upbit.request_order_info_all_progress_changed.connect(
            self.transaction_history_widget.updated_order_history_df)

        # 코인별 수익률 Widget
        self.period_pnl_widget = PeriodPnLWidget(parent=self)
        self.period_pnl_widget.period_pnl_table_view.sumFinished.connect(self.sum_finished)
        self.period_pnl_widget.modelUpdated.connect(self.model_Updated)

        # Layout
        mid_tab_widget = QtWidgets.QTabWidget(parent=self)

        mid_tab0_frame = QtWidgets.QFrame(parent=self)
        mid_tab0_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mid_tab0_layout = QtWidgets.QHBoxLayout()
        mid_tab0_layout.addWidget(self.transaction_history_widget)
        mid_tab0_frame.setLayout(mid_tab0_layout)

        mid_tab1_frame = QtWidgets.QFrame(parent=self)
        mid_tab1_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mid_tab1_layout = QtWidgets.QHBoxLayout()
        mid_tab1_layout.addWidget(self.period_pnl_widget)
        mid_tab1_frame.setLayout(mid_tab1_layout)

        mid_tab_widget.addTab(mid_tab0_frame, "거래내역")
        mid_tab_widget.addTab(mid_tab1_frame, "기간손익")
        # Bottom widget.
        # 계산결과 출력 Widget
        self.calculate_console_widget = QtWidgets.QTextBrowser(parent=self)
        self.calculate_console_widget.setStyleSheet(
            "background-color: rgb(34, 40, 64);"
            "color: rgb(157, 159, 170)"
        )
        self.calculate_console_widget.setFont(QtGui.QFont('Consolas', 11))
        self.calculate_console_widget.setAcceptRichText(True)
        bottom_frame = QtWidgets.QFrame(parent=self)
        bottom_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.calculate_console_widget)
        bottom_frame.setLayout(bottom_layout)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, parent=self)
        splitter.addWidget(top_frame)
        splitter.addWidget(mid_tab_widget)
        splitter.addWidget(bottom_frame)
        splitter.setHandleWidth(5)
        splitter.setSizes([300, 600, 125])

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(splitter)
        widget = QtWidgets.QFrame(parent=self)
        widget.setLayout(layout)

        return widget

    def closeEvent(self, e):
        # for thread terminate
        self.asset_thread_worker.stop()
        self.orders_thread_worker.stop()

    def asset_thread_worker_fn(self):
        account_info_list = self.upbit.request_account_info_list()
        markets_string = self.dm.extract_markets_string_in_asset(account_info_list)
        krw_price_list = None
        btc_price_list = None
        if markets_string['krw_markets_string']:
            krw_price_list = self.upbit.request_price_list(markets_string['krw_markets_string'])
        if markets_string['btc_markets_string']:
            btc_price_list = self.upbit.request_price_list(markets_string['btc_markets_string'])
        self.dm.asset_coins_price_df = self.dm.create_asset_coins_price_df(krw_price_list, btc_price_list)
        self.dm.asset_df = self.dm.create_asset_df(account_info_list, self.dm.asset_coins_price_df)
        self.dm.asset_summary_df = self.dm.create_asset_summary_df(self.dm.asset_df)

    def orders_thread_worker_fn(self):
        self.upbit.request_order_info_all_df()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
