from PySide6 import QtCore, QtWidgets


class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, align):
        super(AlignDelegate, self).__init__()
        self.align = align

    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = self.align
