import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QStackedWidget, QVBoxLayout, QWidget

# Support launching this file directly from the project root.
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from workout_pose_checker.pages.choose_page import ChoosePage
from workout_pose_checker.pages.exercise_page import ExercisePage
from workout_pose_checker.pages.result_page import ResultPage
from workout_pose_checker.mock_pose_service import MockPoseService
from workout_pose_checker.pose_service import PoseService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "yolo26n-pose.pt"
USE_MOCK_POSE_SERVICE = True


def create_pose_service():
    """테스트 모드에 맞는 포즈 평가 서비스를 생성한다."""
    if USE_MOCK_POSE_SERVICE:
        return MockPoseService(frames_per_status=30)

    return PoseService(model_path=MODEL_PATH)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        mode_label = " [Mock]" if USE_MOCK_POSE_SERVICE else ""
        self.setWindowTitle(f"운동 자세 AI 보정 도우미{mode_label}")

        
        self.stack = QStackedWidget()

        # 페이지 인스턴스 생성 (self를 전달하여 MainWindow 조작 가능하게 함)
        self.choose_page = ChoosePage(self)
        self.pose_service = create_pose_service()
        self.exercise_page = ExercisePage(self, pose_service=self.pose_service)
        self.result_page = ResultPage(self)

        self.success_count = 0
        self.fail_count = 0

        self.stack.addWidget(self.choose_page)
        self.stack.addWidget(self.exercise_page)
        self.stack.addWidget(self.result_page)

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

    def show_result_page(self, success, fail, time):

        self.result_page.set_result(
            success,
            fail,
            time
        )

        self.stack.setCurrentWidget(
            self.result_page
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(800, 600)  # ChoosePage 권장 크기인 800x600에 맞춤
    window.show()

    sys.exit(app.exec())
