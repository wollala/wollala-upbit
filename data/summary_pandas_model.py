import pandas as pd
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QBrush

from data.pandas_model_template import PandasModelTemplate


class SummaryPandasModel(PandasModelTemplate):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(SummaryPandasModel, self).__init__(dataframe, parent)
        self.plus_profit_row = self.df.index[(self.df['수익률'] >= 0)].tolist()
        self.minus_profit_row = self.df.index[(self.df['수익률'] < 0)].tolist()

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
            if index.column() == 0:  # 보유KRW
                return self.krw_str(target_data)

            elif index.column() == 1:  # 총 보유자산
                return self.krw_str(target_data)

            elif index.column() == 2:  # 투자비율
                return self.percent_str(target_data)

            elif index.column() == 3:  # 총매수
                return self.krw_str(target_data)

            elif index.column() == 4:  # 총평가
                return self.krw_str(target_data)

            elif index.column() == 5:  # 평가손익
                return self.krw_str(target_data)

            elif index.column() == 6:  # 수익률
                return self.percent_str(target_data)

            else:
                return str(target_data)

        return None
