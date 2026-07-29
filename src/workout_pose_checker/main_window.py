import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QStackedWidget,
    QVBoxLayout
)

from pages.choose_page import ChoosePage
from pages.exercise_page import ExercisePage


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()

        self.choose_page = ChoosePage(self)
        self.exercise_page = ExercisePage(self)

        self.stack.addWidget(self.choose_page)
        self.stack.addWidget(self.exercise_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)

        self.setLayout(layout)

        # 처음 페이지
        self.stack.setCurrentWidget(self.choose_page)


    def show_exercise_page(self):
        self.stack.setCurrentWidget(self.exercise_page)



if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(680, 560)
    window.show()

    sys.exit(app.exec())