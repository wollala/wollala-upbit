import pandas as pd
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QBrush

from data.pandas_model_template import PandasModelTemplate


class AccountInfoPandasModel(PandasModelTemplate):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(AccountInfoPandasModel, self).__init__(dataframe, parent)
        self.krw_row = self.df[self.df["화폐종류"].str.contains("KRW")].index
        self.plus_profit_row = self.df.index[(self.df['수익률'] >= 0)].tolist()
        self.minus_profit_row = self.df.index[(self.df['수익률'] < 0)].tolist()
        self.krw_row = self.df.index[(self.df['화폐종류'] == 'KRW')].tolist()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        target_data = self.df.iloc[index.row(), index.column()]

        if role == Qt.TextAlignmentRole:
            if isinstance(target_data, float):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            else:
                return Qt.AlignCenter

        if role == Qt.BackgroundRole:
            if index.row() in self.krw_row:
                return QBrush(self.sky)
            elif index.row() in self.plus_profit_row:
                return QBrush(self.red)
            elif index.row() in self.minus_profit_row:
                return QBrush(self.blue)
            else:
                return QBrush(self.white)

        if role == Qt.DisplayRole:
            if index.column() == 1:  # 보유수량
                if index.row() in self.krw_row:
                    return f'{target_data:,.0f}'
                else:
                    return self.balance_str(target_data)

            elif index.column() == 2:  # 매수평균가
                return self.krw_str(target_data)

            elif index.column() == 3:  # 현재가
                return self.krw_str(target_data)

            elif index.column() == 4:  # 매수금액
                return self.krw_str(target_data)

            elif index.column() == 5:  # 평가금액
                return self.krw_str(target_data)

            elif index.column() == 6:  # 평가손익
                return self.krw_str(target_data)

            elif index.column() == 7:  # 수익률
                return self.percent_str(target_data)

            return str(target_data)

        return None
