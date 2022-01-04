from PySide6 import QtCore, QtWidgets

from UserSetting import UserSetting


class APIKeyInputDialog(QtWidgets.QDialog):
    def __init__(self):
        super(APIKeyInputDialog, self).__init__()
        self.setWindowTitle("API key 입력")
        self.user_setting = UserSetting()
        self.upbit_settings = self.user_setting.upbit
        self.api_access_key = self.upbit_settings["access_key"]
        self.api_secret_key = self.upbit_settings["secret_key"]

        _api_access_key_label = QtWidgets.QLabel("Access key")
        _api_secret_key_label = QtWidgets.QLabel("Secret key")

        self.api_access_key_edit = QtWidgets.QLineEdit(self.api_access_key)
        self.api_secret_key_edit = QtWidgets.QLineEdit(self.api_secret_key)
        _api_access_key_label.setBuddy(self.api_access_key_edit)
        _api_secret_key_label.setBuddy(self.api_secret_key_edit)

        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.on_ok_clicked)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        _grid_layout = QtWidgets.QGridLayout()
        _grid_layout.addWidget(_api_access_key_label, 0, 0)
        _grid_layout.addWidget(self.api_access_key_edit, 0, 1)
        _grid_layout.addWidget(_api_secret_key_label, 1, 0)
        _grid_layout.addWidget(self.api_secret_key_edit, 1, 1)

        _button_layout = QtWidgets.QHBoxLayout()
        _button_layout.addWidget(self.ok_button)
        _button_layout.addWidget(self.cancel_button)

        _main_layout = QtWidgets.QVBoxLayout()
        _main_layout.addLayout(_grid_layout)
        _main_layout.addLayout(_button_layout)
        self.setLayout(_main_layout)
        self.setFixedSize(480, 150)

    @QtCore.Slot()
    def on_ok_clicked(self):
        self.api_access_key = self.api_access_key_edit.text()
        self.api_secret_key = self.api_secret_key_edit.text()

        _user_setting = UserSetting()
        _user_setting.upbit['access_key'] = self.api_access_key
        _user_setting.upbit['secret_key'] = self.api_secret_key
        _user_setting.write_config_file()

        self.hide()

    @QtCore.Slot()
    def on_cancel_clicked(self):
        self.hide()
