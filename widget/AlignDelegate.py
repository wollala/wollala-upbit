from PySide6 import QtCore, QtWidgets


class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, align, parent=None):
        super(AlignDelegate, self).__init__(parent=parent)
        self.align = align

    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = self.align
