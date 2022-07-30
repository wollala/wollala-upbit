from PySide6 import QtCore, QtWidgets

from widget.calender_widget import CalenderWidget


class DateFilterWidget(QtWidgets.QGroupBox):
    from_date_changed = QtCore.Signal(QtCore.QDate)
    to_date_changed = QtCore.Signal(QtCore.QDate)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.from_date = QtCore.QDate.currentDate()
        self.to_date = QtCore.QDate.currentDate()

        self.setTitle("Date filter")
        self.setStyleSheet("QGroupBox{font-size: 12px;}")

        # 지정된 기간 선택 버튼
        self.today_btn = QtWidgets.QPushButton("오늘", parent=self)
        self.today_btn.setCheckable(True)
        self.week1_btn = QtWidgets.QPushButton("1주일", parent=self)
        self.week1_btn.setCheckable(True)
        self.week2_btn = QtWidgets.QPushButton("2주일", parent=self)
        self.week2_btn.setCheckable(True)
        self.month1_btn = QtWidgets.QPushButton("1개월", parent=self)
        self.month1_btn.setCheckable(True)
        self.month3_btn = QtWidgets.QPushButton("3개월", parent=self)
        self.month3_btn.setCheckable(True)
        self.month6_btn = QtWidgets.QPushButton("6개월", parent=self)
        self.month6_btn.setCheckable(True)
        self.month12_btn = QtWidgets.QPushButton("12개월", parent=self)
        self.month12_btn.setCheckable(True)
        self.month18_btn = QtWidgets.QPushButton("18개월", parent=self)
        self.month18_btn.setCheckable(True)
        self.month24_btn = QtWidgets.QPushButton("24개월", parent=self)
        self.month24_btn.setCheckable(True)

        self.period_btn_group = QtWidgets.QButtonGroup(parent=self)
        self.period_btn_group.addButton(self.today_btn, 0)
        self.period_btn_group.addButton(self.week1_btn, 1)
        self.period_btn_group.addButton(self.week2_btn, 2)
        self.period_btn_group.addButton(self.month1_btn, 3)
        self.period_btn_group.addButton(self.month3_btn, 4)
        self.period_btn_group.addButton(self.month6_btn, 5)
        self.period_btn_group.addButton(self.month12_btn, 6)
        self.period_btn_group.addButton(self.month18_btn, 7)
        self.period_btn_group.addButton(self.month24_btn, 8)
        self.period_btn_group.buttonClicked.connect(self.period_btn_clicked)  # noqa

        self.period_btn_layout = QtWidgets.QHBoxLayout()
        self.period_btn_layout.addWidget(self.today_btn)
        self.period_btn_layout.addWidget(self.week1_btn)
        self.period_btn_layout.addWidget(self.week2_btn)
        self.period_btn_layout.addWidget(self.month1_btn)
        self.period_btn_layout.addWidget(self.month3_btn)
        self.period_btn_layout.addWidget(self.month6_btn)
        self.period_btn_layout.addWidget(self.month12_btn)
        self.period_btn_layout.addWidget(self.month18_btn)
        self.period_btn_layout.addWidget(self.month24_btn)

        # 날짜 직접 선택 버튼
        self.from_date_btn = QtWidgets.QPushButton(
            f'{self.from_date.year()}.{self.from_date.month():02d}.{self.from_date.day():02d}',
            parent=self)
        self.from_date_btn.setCheckable(True)
        self.to_date_btn = QtWidgets.QPushButton(
            f'{self.to_date.year()}.{self.to_date.month():02d}.{self.to_date.day():02d}',
            parent=self)
        self.to_date_btn.setCheckable(True)
        self.from_date_btn.clicked.connect(self.from_btn_clicked)
        self.to_date_btn.clicked.connect(self.to_btn_clicked)

        self.date_btn_layout = QtWidgets.QGridLayout()
        self.date_btn_layout.addWidget(self.from_date_btn, 0, 0, 1, 5)
        self.date_btn_layout.addWidget(QtWidgets.QLabel(" ~ ", alignment=QtCore.Qt.AlignCenter, parent=self), 0, 5, 1,
                                       1)
        self.date_btn_layout.addWidget(self.to_date_btn, 0, 6, 1, 5)

        period_groupbox_layout = QtWidgets.QVBoxLayout()
        period_groupbox_layout.addLayout(self.period_btn_layout)
        period_groupbox_layout.addLayout(self.date_btn_layout)

        self.setLayout(period_groupbox_layout)

        # 달력위젯
        self.from_calender_widget = CalenderWidget()
        self.from_calender_widget.setMinimumWidth(400)
        self.from_calender_widget.setMinimumHeight(300)
        self.from_calender_widget.setWindowTitle("시작날짜")
        self.from_calender_widget.setDateRange(QtCore.QDate(2019, 1, 1), QtCore.QDate.currentDate())
        self.from_calender_widget.clicked.connect(self.from_date_clicked)  # noqa
        self.from_calender_widget.closed.connect(lambda: self.from_date_btn.setChecked(False))

        self.to_calender_widget = CalenderWidget()
        self.to_calender_widget.setMinimumWidth(400)
        self.to_calender_widget.setMinimumHeight(300)
        self.to_calender_widget.setWindowTitle("종료날짜")
        self.to_calender_widget.clicked.connect(self.to_date_clicked)  # noqa
        self.to_calender_widget.closed.connect(lambda: self.to_date_btn.setChecked(False))

    @QtCore.Slot(int)
    def period_btn_clicked(self, btn):
        id = self.period_btn_group.id(btn)
        self.to_date = QtCore.QDate.currentDate()
        self.to_date_btn.setChecked(False)
        self.from_date_btn.setChecked(False)
        if id == 0:
            self.from_date = QtCore.QDate.currentDate()
        elif id == 1:
            self.from_date = QtCore.QDate.currentDate().addDays(-7)
        elif id == 2:
            self.from_date = QtCore.QDate.currentDate().addDays(-14)
        elif id == 3:
            self.from_date = QtCore.QDate.currentDate().addMonths(-1)
        elif id == 4:
            self.from_date = QtCore.QDate.currentDate().addMonths(-3)
        elif id == 5:
            self.from_date = QtCore.QDate.currentDate().addMonths(-6)
        elif id == 6:
            self.from_date = QtCore.QDate.currentDate().addMonths(-12)
        elif id == 7:
            self.from_date = QtCore.QDate.currentDate().addMonths(-18)
        elif id == 8:
            self.from_date = QtCore.QDate.currentDate().addMonths(-24)

        self.from_date_btn.setText(
            f'{self.from_date.year()}.{self.from_date.month():02d}.{self.from_date.day():02d}')
        self.to_date_btn.setText(
            f'{self.to_date.year()}.{self.to_date.month():02d}.{self.to_date.day():02d}')
        self.from_date_changed.emit(self.from_date)
        self.to_date_changed.emit(self.to_date)

    @QtCore.Slot()
    def from_btn_clicked(self):
        self.unchecked_date_btn_group()
        self.to_date_btn.setChecked(False)

        self.to_calender_widget.hide()
        self.from_calender_widget.show()
        self.from_calender_widget.setSelectedDate(self.from_date)

    @QtCore.Slot()
    def to_btn_clicked(self):
        self.unchecked_date_btn_group()
        self.from_date_btn.setChecked(False)

        self.from_calender_widget.hide()
        self.to_calender_widget.show()
        self.to_calender_widget.setSelectedDate(self.to_date)

    @QtCore.Slot(QtCore.QDate)
    def from_date_clicked(self, date):
        self.from_date = date
        self.from_date_changed.emit(self.from_date)

        self.from_date_btn.setText(
            f'{self.from_date.year()}.{self.from_date.month():02d}.{self.from_date.day():02d}')
        self.from_calender_widget.hide()
        self.from_date_btn.setChecked(False)
        self.to_calender_widget.setDateRange(self.from_date, QtCore.QDate.currentDate())

    @QtCore.Slot(QtCore.QDate)
    def to_date_clicked(self, date):
        self.to_date = date
        self.to_date_changed.emit(self.to_date)

        self.to_date_btn.setText(
            f'{self.to_date.year()}.{self.to_date.month():02d}.{self.to_date.day():02d}')
        self.to_calender_widget.hide()
        self.to_date_btn.setChecked(False)
        self.from_calender_widget.setDateRange(QtCore.QDate(2019, 1, 1), self.to_date)

    def unchecked_date_btn_group(self):
        if self.period_btn_group.checkedButton():
            self.period_btn_group.setExclusive(False)
            self.period_btn_group.checkedButton().setChecked(False)
            self.period_btn_group.setExclusive(True)
