from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class ExercisePage(QWidget):

    def __init__(self, main_window):
        super().__init__()

        label = QLabel("운동 진행 화면")

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)