import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor


class PandasModelTemplate(QAbstractTableModel):
    # Bootstrap Colors Color Palette
    red = QColor("#d2d9534f")
    white = QColor("#f9f9f9")
    sky = QColor("#5bc0de")
    green = QColor("#d25cb85c")
    blue = QColor("#d2428bca")

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.df = dataframe.round(9)
        self.df = self.df.reset_index(drop=True)

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self.df)
        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self.df.columns)
        return 0

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])
        return None

    def krw_str(self, num):
        if pd.isnull(num):
            return ''
        else:
            return f'{num:,.0f} KRW'

    def btc_str(self, num):
        if pd.isnull(num):
            return ''
        else:
            return f'{num:,.8f} BTC'

    def balance_str(self, num):
        if pd.isnull(num):
            return ''
        elif num % 1 == 0:
            return f'{num:,.0f}'
        else:
            return f'{num:,.8f}'

    def percent_str(self, num):
        if pd.isnull(num):
            return ''
        else:
            return f'{num:,.2f} %'

    def datetime_str(self, datetime):
        return datetime.strftime("%Y/%m/%d %H:%M:%S")
