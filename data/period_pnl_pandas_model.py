import pandas as pd
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QBrush

from data.pandas_model_template import PandasModelTemplate


class PeriodPnLPandasModel(PandasModelTemplate):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(PeriodPnLPandasModel, self).__init__(dataframe, parent)
        self.plus_profit_row = self.df.index[(self.df['수익률'] >= 0)].tolist()
        self.minus_profit_row = self.df.index[(self.df['수익률'] < 0)].tolist()
        self.btc_row = self.df.index[(self.df['마켓'].str.startswith('BTC'))].tolist()
        self.krw_row = self.df.index[(self.df['마켓'].str.startswith('KRW'))].tolist()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        target_data = self.df.iloc[index.row(), index.column()]

        if role == Qt.BackgroundRole:
            if index.row() in self.plus_profit_row:
                return QBrush(self.red)
            elif index.row() in self.minus_profit_row:
                return QBrush(self.blue)
            else:
                return QBrush(self.green)

        if role == Qt.TextAlignmentRole:
            if isinstance(target_data, float):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            else:
                return Qt.AlignCenter

        if role == Qt.DisplayRole:
            if index.column() == 1:  # 총 매수 수량
                return self.balance_str(target_data)

            elif index.column() == 2:  # 총 매도 수량
                return self.balance_str(target_data)

            elif index.column() == 3:  # 미실현수량
                return self.balance_str(target_data)

            elif index.column() == 4:  # 총 매수금액
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 5:  # 총 매도금액
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 6:  # 매수 평단가
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 7:  # 매도 평단가
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 8:  # 실현손익
                if index.row() in self.krw_row:
                    return self.krw_str(target_data)
                elif index.row() in self.btc_row:
                    return self.btc_str(target_data)

            elif index.column() == 9:  # 수익률
                return self.percent_str(target_data)

            else:
                return str(target_data)

        return None
