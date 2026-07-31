import sys

from PySide6.QtWidgets import QApplication, QStackedWidget, QVBoxLayout, QWidget
from pages.choose_page import ChoosePage
from pages.exercise_page import ExercisePage


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("운동 자세 AI 보정 도우미")

        
        self.stack = QStackedWidget()

        # 페이지 인스턴스 생성 (self를 전달하여 MainWindow 조작 가능하게 함)
        self.choose_page = ChoosePage(self)
        self.exercise_page = ExercisePage(self)

        self.stack.addWidget(self.choose_page)
        self.stack.addWidget(self.exercise_page)

        # 메인 레이아웃 설정 (여백 제거)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        self.setLayout(layout)

        # 초기 페이지 설정
        self.show_choose_page()

    def show_exercise_page(self):
        
        # ChoosePage에서 현재 설정된 상태 가져오기
        selected_mode = self.choose_page.exercise_mode  # "시간" 또는 "횟수"
        selected_level = self.choose_page.level  # 설정한 목표 수치
        current_img_index = self.choose_page.current_index  # 선택된 운동 이미지 인덱스

        # ExercisePage에 데이터 전달
        if hasattr(self.exercise_page, "set_config"):
            self.exercise_page.set_config(
                mode=selected_mode,
                level=selected_level,
                image_idx=current_img_index,
            )

        # 화면 전환
        self.stack.setCurrentWidget(self.exercise_page)

    def show_choose_page(self):
        
        self.stack.setCurrentWidget(self.choose_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(800, 600)  # ChoosePage 권장 크기인 800x600에 맞춤
    window.show()

    sys.exit(app.exec())