import re
from copy import deepcopy
from UserSetting import UserSetting
from PySide6 import QtCore, QtWidgets, QtGui


class TickerSelectionDialog(QtWidgets.QDialog):
    def __init__(self, krw_markets, btc_markets):
        super(TickerSelectionDialog, self).__init__()
        self.user_setting = UserSetting()
        self.upbit_settings = self.user_setting.upbit

        self.krw_markets = deepcopy(krw_markets)
        self.temp_krw_markets = deepcopy(self.krw_markets)
        self.btc_markets = deepcopy(btc_markets)
        self.temp_btc_markets = deepcopy(self.btc_markets)
        # selected_***_markets의 데이터 = ["비트코인 (KRW-BTC)", "이더리움 (KRW-ETH)"...]
        self.selected_krw_markets = deepcopy(self.upbit_settings['transaction_history'][
                                                                 'selected_krw_markets'])
        self.temp_selected_krw_markets = deepcopy(self.selected_krw_markets)
        self.selected_btc_markets = deepcopy(self.upbit_settings['transaction_history'][
                                                                 'selected_btc_markets'])
        self.temp_selected_btc_markets = deepcopy(self.selected_btc_markets)

        _market_label = QtWidgets.QLabel("SELECT MARKET")

        self.market_combobox = QtWidgets.QComboBox()
        self.market_combobox.addItems(["KRW", "BTC"])
        self.market_combobox.currentIndexChanged.connect(self.on_market_combobox_index_changed)
        _market_label.setBuddy(self.market_combobox)

        self.ticker_list_widget = QtWidgets.QListWidget()
        self.ticker_list_widget.setSortingEnabled(True)
        self.ticker_list_widget.itemChanged.connect(self.on_ticker_list_widget_item_checked_changed)
        self.ticker_list_widget.itemDoubleClicked.connect(self.on_ticker_list_widget_item_clicked)

        _selected_label = QtWidgets.QLabel("SELECED TICKERS")
        self.selected_list_widget = QtWidgets.QListWidget()
        self.selected_list_widget.setSortingEnabled(True)
        self.selected_list_widget.itemDoubleClicked.connect(self.on_selected_list_widget_item_double_clicked)

        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.on_ok_clicked)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        _top_layout = QtWidgets.QGridLayout()
        _top_layout.addWidget(_market_label, 0, 0, 0, 1)
        _top_layout.addWidget(self.market_combobox, 0, 1, 0, 2)
        _top_layout.addWidget(_selected_label, 0, 3, 0, 3, QtCore.Qt.AlignHCenter)  # noqa

        _list_layout = QtWidgets.QHBoxLayout()
        _list_layout.addWidget(self.ticker_list_widget)
        _list_layout.addWidget(self.selected_list_widget)

        _button_layout = QtWidgets.QHBoxLayout()
        _button_layout.addWidget(self.ok_button)
        _button_layout.addWidget(self.cancel_button)

        _main_layout = QtWidgets.QVBoxLayout()
        _main_layout.addLayout(_top_layout)
        _main_layout.addLayout(_list_layout)
        _main_layout.addLayout(_button_layout)
        self.setLayout(_main_layout)
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        self.setWindowTitle("코인 선택")

    @QtCore.Slot()
    def on_selected_list_widget_item_double_clicked(self, item):
        _model = None
        # 괄호 안의 문자 찾기 ex) 비트코인 (KRW-BTC)
        ticker = re.findall('\((KRW-[^)]+|BTC-[^)]+)\)', item.text())[0]  # ticker = KRW-BTC # noqa
        market = ticker.split('-')[0]  # market = KRW
        if market == 'KRW':
            _model = self.temp_krw_markets
        elif market == 'BTC':
            _model = self.temp_btc_markets

        for i in _model:
            if i['market'] == ticker:
                i['checked'] = not i['checked']
                break

        _matched_items = self.ticker_list_widget.findItems(item.text(), QtCore.Qt.MatchExactly)  # noqa
        if _matched_items:
            _matched_items[0].setCheckState(QtCore.Qt.Unchecked)

    @QtCore.Slot()
    def on_ticker_list_widget_item_checked_changed(self, item):
        _market_model = None
        _selected_model = None
        if self.market_combobox.currentIndex() == 0:
            _market_model = self.temp_krw_markets
            _selected_model = self.temp_selected_krw_markets
        elif self.market_combobox.currentIndex() == 1:
            _market_model = self.temp_btc_markets
            _selected_model = self.temp_selected_btc_markets

        if item.checkState() == QtCore.Qt.Unchecked:
            _market_model[self.ticker_list_widget.indexFromItem(item).row()]['checked'] = False
            _matched_item = self.selected_list_widget.findItems(item.text(), QtCore.Qt.MatchExactly)[0]  # noqa
            self.selected_list_widget.takeItem(self.selected_list_widget.row(_matched_item))
            _selected_model.remove(item.text())
        else:
            _market_model[self.ticker_list_widget.indexFromItem(item).row()]['checked'] = True
            _item = QtWidgets.QListWidgetItem(item.text())
            self.selected_list_widget.addItem(_item)
            _selected_model.append(item.text())

    @QtCore.Slot()
    def on_ticker_list_widget_item_clicked(self, item):
        if item.checkState() == QtCore.Qt.Unchecked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    def showEvent(self, arg__1: QtGui.QShowEvent):
        self.market_combobox.setCurrentIndex(0)
        self.refresh_list()

    @QtCore.Slot()
    def on_market_combobox_index_changed(self, index):
        self.refresh_list(temp=True)

    @QtCore.Slot()
    def on_ok_clicked(self):
        self.krw_markets = deepcopy(self.temp_krw_markets)
        self.btc_markets = deepcopy(self.temp_btc_markets)
        self.selected_krw_markets = deepcopy(self.temp_selected_krw_markets)
        self.selected_btc_markets = deepcopy(self.temp_selected_btc_markets)

        _user_setting = UserSetting()
        self.selected_krw_markets = list(set(self.selected_krw_markets))  # 중복제거
        self.selected_btc_markets = list(set(self.selected_btc_markets))  # 중복제거
        _user_setting.upbit['transaction_history']['selected_krw_markets'] = self.selected_krw_markets
        _user_setting.upbit['transaction_history']['selected_btc_markets'] = self.selected_btc_markets
        _user_setting.write_config_file()

        self.hide()

    @QtCore.Slot()
    def on_cancel_clicked(self):
        self.temp_krw_markets = deepcopy(self.krw_markets)
        self.temp_btc_markets = deepcopy(self.btc_markets)
        self.temp_selected_krw_markets = deepcopy(self.selected_krw_markets)
        self.temp_selected_btc_markets = deepcopy(self.selected_btc_markets)
        self.hide()

    def refresh_list(self, temp=False):
        self.ticker_list_widget.clear()
        self.selected_list_widget.clear()

        _market_model = None
        _selected_model = None
        if self.market_combobox.currentIndex() == 0:
            if temp is True:
                _market_model = self.temp_krw_markets
                _selected_model = self.temp_selected_krw_markets
            else:
                _market_model = self.krw_markets
                _selected_model = self.selected_krw_markets
        elif self.market_combobox.currentIndex() == 1:
            if temp is True:
                _market_model = self.temp_btc_markets
                _selected_model = self.temp_selected_btc_markets
            else:
                _market_model = self.btc_markets
                _selected_model = self.selected_btc_markets

        for i in _market_model:
            _item = QtWidgets.QListWidgetItem(f"{i['korean_name']} ({i['market']})")
            if i['checked'] is True:
                _item.setCheckState(QtCore.Qt.Checked)
            else:
                _item.setCheckState(QtCore.Qt.Unchecked)
            self.ticker_list_widget.addItem(_item)

        for i in _selected_model:
            _item = QtWidgets.QListWidgetItem(i)
            self.selected_list_widget.addItem(_item)


