import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QBrush, QColor, QFont


class AccountInfoPandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.df = dataframe.round(9)
        self.df = self.df.reset_index(drop=True)
        self.krw_row = self.df[self.df["화폐종류"].str.contains("KRW")].index
        self.plus_profit_row = self.df.index[(self.df['수익률'] >= 0)].tolist()
        self.minus_profit_row = self.df.index[(self.df['수익률'] < 0)].tolist()

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self.df)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self.df.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None
        elif role == Qt.BackgroundRole:
            red = QColor(238, 64, 53, 200)
            blue = QColor(3, 146, 207, 200)
            gray = QColor(116, 109, 105, 70)
            green = QColor("#5F7161")
            if index.row() in self.krw_row:
                return QBrush(green)
            elif index.row() in self.plus_profit_row:
                return QBrush(red)
            elif index.row() in self.minus_profit_row:
                return QBrush(blue)
            else:
                return QBrush(gray)
        elif role == Qt.TextAlignmentRole:
            target_data = self.df.iloc[index.row(), index.column()]
            if isinstance(target_data, float):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            else:
                return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            target_data = self.df.iloc[index.row(), index.column()]
            if index.column() == 1:  # 보유수량
                # KRW 이거나 소수점이 없으면 소수점 자리수 출력 안함
                if self.df.iloc[index.row(), 0].startswith("KRW") or self.df.iloc[index.row(), 1] % 1 == 0:
                    return "{0:,.0f}".format(target_data)
                else:
                    return "{0:,.8f}".format(target_data)
            elif index.column() == 2:  # 매수평균가
                return "{0:,.0f} KRW".format(target_data)
            elif index.column() == 3:  # 현재가
                if pd.isnull(target_data):
                    return ""
                else:
                    return "{0:,.0f} KRW".format(target_data)
            elif index.column() == 4:  # 매수금액
                return "{0:,.0f} KRW".format(target_data)
            elif index.column() == 5:  # 평가금액
                if pd.isnull(target_data):
                    return ""
                else:
                    return "{0:,.0f} KRW".format(target_data)
            elif index.column() == 6:  # 평가손익
                if pd.isnull(target_data):
                    return ""
                else:
                    return "{0:,.0f} KRW".format(target_data)
            elif index.column() == 7:  # 수익률
                if pd.isnull(target_data):
                    return ""
                else:
                    return "{0:,.2f} %".format(target_data)

            return str(target_data)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])

        return None
