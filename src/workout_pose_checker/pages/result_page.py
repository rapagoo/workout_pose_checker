from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)

from PySide6.QtCore import Qt


class ResultPage(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.init_UI()


    def init_UI(self):

        self.setStyleSheet("""
        QWidget {
            background-color: #F5F5F5;
        }

        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #333333;
        }

        QPushButton {
            background-color: #1976D2;
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1565C0;
        }
        """)


        title = QLabel("운동 결과")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            color: #1976D2;
        """)


        self.lbl_success = QLabel("성공: 0회")
        self.lbl_fail = QLabel("실패: 0회")
        self.lbl_total = QLabel("총합: 0회")
        self.lbl_time = QLabel("운동 시간: 00:00")


        for lbl in [
            self.lbl_success,
            self.lbl_fail,
            self.lbl_total,
            self.lbl_time
        ]:
            lbl.setAlignment(Qt.AlignCenter)


        self.btn_home = QPushButton("처음 화면으로")

        self.btn_home.clicked.connect(
            self.go_home
        )


        layout = QVBoxLayout()

        layout.addWidget(title)
        layout.addSpacing(30)

        layout.addWidget(self.lbl_success)
        layout.addWidget(self.lbl_fail)
        layout.addWidget(self.lbl_total)
        layout.addWidget(self.lbl_time)

        layout.addSpacing(30)

        layout.addWidget(self.btn_home)


        self.setLayout(layout)


    def set_result(self, success, fail, time):

        total = success + fail

        mins = time // 60
        secs = time % 60


        self.lbl_success.setText(
            f"성공: {success}회"
        )

        self.lbl_fail.setText(
            f"실패: {fail}회"
        )

        self.lbl_total.setText(
            f"총합: {total}회"
        )

        self.lbl_time.setText(
            f"운동 시간: {mins:02d}:{secs:02d}"
        )


    def go_home(self):

        if self.main_window:

            self.main_window.show_choose_page()