import logging

import pandas as pd
from PySide6 import QtCore
from upbit.client import Upbit

from util.singleton import Singleton


class UpbitCaller(QtCore.QObject, metaclass=Singleton):
    request_order_info_all_progress_changed = QtCore.Signal(float, pd.DataFrame)

    def __init__(self, access_key="", secret_key=""):
        super().__init__()
        self._access_key = access_key
        self._secret_key = secret_key
        self.upbit_client = Upbit(self._access_key, self._secret_key)

    @property
    def access_key(self):
        return self._access_key

    @access_key.setter
    def access_key(self, value):
        self._access_key = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    def update_upbit_client(self, access_key, secret_key):
        self._access_key = access_key
        self._secret_key = secret_key
        self.upbit_client = Upbit(self._access_key, self._secret_key)

    def api_key_test(self):
        return self.upbit_client.APIKey.APIKey_info()['response']

    def request_all_markets_ticker(self):
        market_list = self.upbit_client.Market.Market_info_all()['result']
        for market in market_list:
            market["currency"] = market["market"].split('-')[1]
        krw_markets = [item for item in market_list if 'KRW-' in item['market']]
        krw_markets = sorted(krw_markets, key=lambda item: item["korean_name"])

        btc_markets = [item for item in market_list if 'BTC-' in item['market']]
        btc_markets = sorted(btc_markets, key=lambda item: item["korean_name"])

        return {
            'krw_markets': krw_markets,
            'btc_markets': btc_markets
        }

    def request_account_info_list(self):
        account_info = self.upbit_client.Account.Account_info()
        account_info_list = account_info['result']
        return account_info_list

    def request_price_list(self, markets_string):
        return self.upbit_client.Trade.Trade_ticker(markets=markets_string)['result']

    def request_order_info(self, uuid):
        return self.upbit_client.Order.Order_info(uuid=uuid)['result']

    # 한 번에 최대요청 100개가 한계
    def request_order_info_page(self, page):
        return self.upbit_client.Order.Order_info_all(page=page, limit=100, states=["done", "cancel"])['result']

    def request_order_info_all_df(self):
        try:
            raw_order_info_all = []
            page = 1
            while True:
                orders = self.request_order_info_page(page)
                raw_order_info_all = raw_order_info_all + orders
                page += 1
                if len(orders) < 100:
                    break
            raw_order_info_all = [order for order in raw_order_info_all if order['trades_count'] > 0]

            # 개별 주문에 대한 Detailed info 요청 및 업데이트

            for i, order in enumerate(raw_order_info_all):
                detailed_order = self.request_order_info(uuid=order['uuid'])
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
                         'remaining_volume', 'reserved_fee', 'remaining_fee', 'locked'], axis=1, inplace=True,
                        errors='ignore')
                df.rename(columns={'side': '종류', 'trading_price': '거래단가', 'market': '마켓', 'created_at': '주문시간',
                                   'paid_fee': '수수료', 'fund': '거래금액', 'trading_volume': '거래수량',
                                   'executed_fund': '정산금액'}, inplace=True)
                df = df.reindex(columns=['주문시간', '마켓', '종류', '거래수량', '거래단가', '거래금액', '수수료', '정산금액'])
                df['주문시간'] = pd.to_datetime(df['주문시간'])
                df = df.astype({'수수료': float})

                # 업데이트 사항을 실시간으로 전송하기 위해 Signal의 파라미터로 return함.
                # 받는 쪽에서 아래와 같이 concat하면 됨
                # ex) order_info_all_df = pd.concat([order_info_all_df, df], ignore_index=True)
                self.request_order_info_all_progress_changed.emit((i + 1) / len(raw_order_info_all) * 100, df)
        except Exception as e:
            logging.exception(e)
