from PySide6 import QtWidgets, QtCore


class ProgramInfoDialog(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(ProgramInfoDialog, self).__init__(parent=parent)

        self.setStyleSheet("* {margin-left: 0; margin-right: 15; }")
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)  # noqa
        self.setWindowTitle("프로그램 정보")
        self.setText(
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'><img src=':/resource/wollala-upbit_icon.png' alt='' width='64' height='64'></p>"
            "<p style='text-align: center; font-size: 28px;'><strong>wollala-upbit</strong></p>"
            "<p style='text-align: center;'>Version 1.1.0</p>"
            "<p style='text-align: center;'>by wollala (<a href='mailto:wollala.zip@gmail.com'>wollala.zip@gmail.com</a>)</p>"  # noqa 
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'>이 프로그램은 어떠한 형태의 보증도 제공하지 않습니다.</p>"
            "<p style='text-align: center;'>발생하는 모든 문제에 대한 책임은 이 프로그램의 사용자에게 있습니다.</p>"
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'><b>Support</b></p>"
            "<p style='text-align: center;'><b>GitHub</b>: <a href='https://github.com/Wollala/wollala-upbit'>https://github.com/Wollala/wollala-upbit</a></p>"  # noqa
            "<p style='text-align: center;'><b>Release page</b>: <a href='https://github.com/Wollala/wollala-upbit/releases'>https://github.com/Wollala/wollala-upbit/releases</a></p>"  # noqa
            "<p style='text-align: center;'><b>Bug 제보 및 제안</b>: <a href='https://github.com/Wollala/wollala-upbit/issues'>https://github.com/Wollala/wollala-upbit/issues</a></p>"  # noqa
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'><b>Donation</b></p>"
            "<p style='text-align: center;'><b>BTC</b>: 34EvTZBAPqT7SviBLggjn4PV9qZG4PVcFp</p>"
            "<p style='text-align: center;'><b>ETH</b>: 0xc281565c8f5fe037570aac45021db4897fd6ce19</p>"
            "<p style='text-align: center;'>&nbsp;</p>"
            "<p style='text-align: center;'>Thanks for hannah, ahram</p>"
            "<p style='text-align: center;'>Copyright &copy; Wollala, 2021&ndash;2022. All rights reserved.</p>"
        )
        self.hide()
