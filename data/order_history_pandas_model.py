import pandas as pd
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QBrush

from data.pandas_model_template import PandasModelTemplate


class OrderHistoryPandasModel(PandasModelTemplate):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(OrderHistoryPandasModel, self).__init__(dataframe, parent)
        self.sell_row = self.df.index[(self.df['종류'] == '매도')].tolist()
        self.buy_row = self.df.index[(self.df['종류'] == '매수')].tolist()
        self.btc_row = self.df.index[(self.df['마켓'].str.startswith('BTC'))].tolist()
        self.krw_row = self.df.index[(self.df['마켓'].str.startswith('KRW'))].tolist()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        target_data = self.df.iloc[index.row(), index.column()]

        if role == Qt.BackgroundRole:
            if index.row() in self.buy_row:
                return QBrush(self.red)
            elif index.row() in self.sell_row:
                return QBrush(self.blue)
            else:
                return QBrush(self.white)

        if role == Qt.TextAlignmentRole:
            if isinstance(target_data, float):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            else:
                return Qt.AlignCenter

        if role == Qt.DisplayRole:
            if index.column() == 0:  # 주문시간
                return self.datetime_str(target_data)

            elif index.column() == 3:  # 거래수량
                return self.balance_str(target_data)

            elif index.column() == 4:  # 거래단가
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 5:  # 거래금액
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 6:  # 수수료
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 7:  # 정산금액
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            else:
                return str(target_data)

        return None
