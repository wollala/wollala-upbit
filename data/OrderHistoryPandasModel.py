import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QBrush, QColor


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.df = dataframe
        self.sellRow = self.df.index[(self.df['종류'] == '매도')].tolist()
        self.buyRow = self.df.index[(self.df['종류'] == '매수')].tolist()

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
            if index.row() in self.buyRow:
                return QBrush(red)
            elif index.row() in self.sellRow:
                return QBrush(blue)
        elif role == Qt.TextAlignmentRole:
            target_data = self.df.iloc[index.row(), index.column()]
            if isinstance(target_data, float):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            else:
                return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            target_data = self.df.iloc[index.row(), index.column()]

            if index.column() == 0:  # 날짜
                return target_data.strftime("%Y/%m/%d %H:%M:%S")
            elif index.column() == 3:  # 거래수량
                return "{0:,.8f}".format(target_data)
            elif index.column() == 4:  # 거래단가
                if self.df.iloc[index.row(), 1].startswith("KRW"):
                    return "{0:,.0f} KRW".format(target_data)
                elif self.df.iloc[index.row(), 1].startswith("BTC"):
                    return "{0:,.8f} BTC".format(target_data)
            elif index.column() == 5:  # 거래금액
                if self.df.iloc[index.row(), 1].startswith("KRW"):
                    return "{0:,.0f} KRW".format(target_data)
                elif self.df.iloc[index.row(), 1].startswith("BTC"):
                    return "{0:,.8f} BTC".format(target_data)
            elif index.column() == 6:  # 수수료
                if self.df.iloc[index.row(), 1].startswith("KRW"):
                    return "{0:,.0f} KRW".format(target_data)
                elif self.df.iloc[index.row(), 1].startswith("BTC"):
                    return "{0:,.8f} BTC".format(target_data)
            elif index.column() == 7:  # 정산금액
                if self.df.iloc[index.row(), 1].startswith("KRW"):
                    return "{0:,.0f} KRW".format(target_data)
                elif self.df.iloc[index.row(), 1].startswith("BTC"):
                    return "{0:,.8f} BTC".format(target_data)
            else:
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
