import logging

import numpy as np
import pandas as pd
from PySide6 import QtCore

from util.singleton import Singleton


class DataManager(QtCore.QObject, metaclass=Singleton):
    asset_summary_df_changed = QtCore.Signal(pd.DataFrame)
    asset_df_changed = QtCore.Signal(pd.DataFrame)
    order_history_df_changed = QtCore.Signal(pd.DataFrame)
    asset_coins_price_df_changed = QtCore.Signal(pd.DataFrame)
    asset_period_pnl_df_changed = QtCore.Signal(pd.DataFrame)

    def __init__(self):
        super().__init__()
        self._asset_summary_df = pd.DataFrame(
            columns=['보유KRW', '총매수', '투자비율', '총 보유자산', '총평가', '평가손익', '수익률'])
        self._asset_df = pd.DataFrame(
            columns=['화폐종류', '보유수량', '매수평균가', '현재가', '매수금액', '평가금액', '평가손익', '수익률'])
        self._order_history_df = pd.DataFrame(
            columns=["주문시간", "마켓", "종류", "거래수량", "거래단가", "거래금액", "수수료", "정산금액"])
        self._asset_coins_price_df = pd.DataFrame(
            columns=['market', 'trade_krw_price', 'trade_btc_price'])
        self._asset_period_pnl_df = pd.DataFrame(
            columns=["마켓", "총 매수수량", "총 매도수량", "미실현수량", "총 매수금액", "총 매도금액", "매수 평단가", "매도 평단가",
                     "실현손익", "수익률"])

        self.krw_markets = None
        self.btc_markets = None

    @property
    def asset_summary_df(self):
        return self._asset_summary_df

    @asset_summary_df.setter
    def asset_summary_df(self, value):
        self._asset_summary_df = value
        self.asset_summary_df_changed.emit(value)

    @property
    def asset_df(self):
        return self._asset_df

    @asset_df.setter
    def asset_df(self, value):
        self._asset_df = value
        self.asset_df_changed.emit(value)

    @property
    def order_history_df(self):
        return self._order_history_df

    @order_history_df.setter
    def order_history_df(self, value):
        self._order_history_df = value
        self.order_history_df_changed.emit(value)

    @property
    def asset_coins_price_df(self):
        return self._asset_coins_price_df

    @asset_coins_price_df.setter
    def asset_coins_price_df(self, value):
        self._asset_coins_price_df = value
        self.asset_coins_price_df_changed.emit(value)

    @property
    def asset_period_pnl_df(self):
        return self._asset_period_pnl_df

    @asset_period_pnl_df.setter
    def asset_period_pnl_df(self, value):
        self._asset_period_pnl_df = value
        self.asset_period_pnl_df_changed.emit(value)

    # account_info_list는 upbit_caller.request_account_info_list()의 반환값.
    def extract_markets_string_in_asset(self, account_info_list):
        result = {
            'krw_markets_string': "",
            'btc_markets_string': ""
        }
        try:
            coin_base_krw_market = ['KRW-BTC']
            coin_base_btc_market = []
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
            result['krw_markets_string'] = krw_markets_string
            result['btc_markets_string'] = btc_markets_string
        except Exception as e:
            logging.exception(e)
        finally:
            return result

    # krw_price_list는 upbit_caller.request_price_list()의 반환값
    # btc_price_list는 upbit_caller.request_price_list()의 반환값
    def create_asset_coins_price_df(self, krw_price_list, btc_price_list):
        df = pd.DataFrame()
        krw_price_df = None
        btc_price_df = None
        try:
            if krw_price_list:
                krw_price_df = pd.DataFrame(krw_price_list, columns=['market', 'trade_price'])  # trade_price = krw 가격
                krw_price_df.rename(columns={'trade_price': 'trade_krw_price'}, inplace=True)
                btc_price = krw_price_df.loc[krw_price_df['market'] == 'KRW-BTC']['trade_krw_price'].reset_index(
                    drop=True)
            if btc_price_list:
                btc_price_df = pd.DataFrame(btc_price_list, columns=['market', 'trade_price'])  # trade_price = btc 가격
                btc_price_df.rename(columns={'trade_price': 'trade_btc_price'}, inplace=True)
                # KRW 마켓코인: trade_krw_price = 코인의 krw가격
                # BTC 마켓코인: trade_krw_price = 코인의 btc가격(trade_btc_price) * btc의 krw가격
                btc_price_df['trade_krw_price'] = btc_price_df.loc[:, 'trade_btc_price'] * btc_price[0]

            df = pd.concat([krw_price_df, btc_price_df], axis=0)
            df = df.reset_index()

            columns = []
            if 'market' in df.columns:
                columns.append('market')
            if 'trade_krw_price' in df.columns:
                columns.append('trade_krw_price')
            if 'trade_btc_price' in df.columns:
                columns.append('trade_btc_price')

            df = df[columns]
        except Exception as e:
            logging.exception(e)
        finally:
            return df

    # account_info_list는 upbit_caller.request_account_info_list()의 반환값.
    # account_info_list는 create_asset_coins_price_df()의 반환값.
    def create_asset_df(self, account_info_list, asset_coins_price_df):
        df = pd.DataFrame(account_info_list)
        try:
            if 'market' in df.columns and 'market' in asset_coins_price_df:
                df = pd.merge(df, asset_coins_price_df, how='left', on='market')
            else:
                df['trade_krw_price'] = 0.0
                df['market'] = None

            df = df.astype({
                'locked': float,
                'balance': float,
                'avg_buy_price': float,
                'trade_krw_price': float
            })
            df.rename(
                columns={'balance': '보유수량', 'avg_buy_price': '매수평균가', 'currency': '화폐종류', 'trade_krw_price': '현재가'},
                inplace=True)
            df['보유수량'] = df['보유수량'] + df['locked']
            df.drop(['locked', 'avg_buy_price_modified', 'unit_currency', 'market'], axis=1, inplace=True)

            df['매수금액'] = df['보유수량'] * df['매수평균가']
            df['평가금액'] = df['보유수량'] * df['현재가']
            df['평가손익'] = df['평가금액'] - df['매수금액']
            df['수익률'] = df['평가손익'] / df['매수금액'] * 100

            df = df.reindex(
                columns=['화폐종류', '보유수량', '매수평균가', '현재가', '매수금액', '평가금액', '평가손익', '수익률'])
            df['평가금액'] = np.where(df['화폐종류'] == 'KRW', df['보유수량'], df['평가금액'])
            df = df.sort_values(by="평가금액", ascending=False)
        except Exception as e:
            logging.exception(e)
        finally:
            return df

    def create_asset_summary_df(self, asset_df):
        df = pd.DataFrame()
        try:
            df["보유KRW"] = asset_df[asset_df["화폐종류"] == "KRW"]["보유수량"]
            df["총 보유자산"] = asset_df["평가금액"].sum()
            df["총매수"] = asset_df["매수금액"].sum()
            df["투자비율"] = df["총매수"] / (df["보유KRW"] + df["총매수"]) * 100
            df["총평가"] = asset_df["평가금액"].sum() - df["보유KRW"]
            df["평가손익"] = df["총평가"] - df["총매수"]
            df['수익률'] = df["평가손익"] / df["총매수"] * 100
            df = df.reindex(
                columns=['보유KRW', '총매수', '투자비율', '총 보유자산', '총평가', '평가손익', '수익률'])
            df = df.reset_index(drop=True)
        except Exception as e:
            logging.exception(e)
        finally:
            return df

    def create_asset_period_pnl_df(self, filterd_order_history_df):
        pnl = 0
        result_df = pd.DataFrame(
            columns=["마켓", "총 매수수량", "총 매도수량", "미실현수량", "총 매수금액", "총 매도금액", "매수 평단가", "매도 평단가",
                     "실현손익", "수익률"])
        try:
            df = filterd_order_history_df.groupby(['마켓', '종류'])[['정산금액', '거래수량']].sum().unstack()

            result_df['마켓'] = df.index
            df = df.reset_index()
            if ('거래수량', '매수') in df.columns:
                result_df['총 매수수량'] = df['거래수량', '매수']
            if ('거래수량', '매도') in df.columns:
                result_df['총 매도수량'] = df['거래수량', '매도']
            if ('정산금액', '매수') in df.columns:
                result_df['총 매수금액'] = df['정산금액', '매수']
            if ('정산금액', '매도') in df.columns:
                result_df['총 매도금액'] = df['정산금액', '매도']
            result_df = result_df.fillna(0)
            result_df['미실현수량'] = result_df['총 매수수량'] - result_df['총 매도수량']
            result_df['매수 평단가'] = result_df['총 매수금액'] / result_df["총 매수수량"]
            result_df['매도 평단가'] = result_df['총 매도금액'] / result_df["총 매도수량"]
            result_df['실현손익'] = (result_df['매도 평단가'] * result_df['총 매도수량']) - (
                    result_df['매수 평단가'] * result_df['총 매도수량'])
            result_df['수익률'] = (result_df['매도 평단가'] - result_df['매수 평단가']) / result_df['매수 평단가'] * 100
            result_df = result_df.sort_values(by="총 매수금액", ascending=False)

            pnl = result_df['실현손익'].sum()
        except Exception as e:
            logging.exception(e)
        finally:
            return result_df, pnl
