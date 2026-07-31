import sys
import cv2

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap


class ExercisePage(QWidget):

    def __init__(self, main_window=None):
        super().__init__()

        self.main_window = main_window

        # 운동 데이터 관련 상태 변수
        self.mode = "횟수"       # "시간" 또는 "횟수"
        self.target_level = 30   # 목표 수치
        self.exercise_name = "스쿼트"
        
        self.success_count = 0
        self.fail_count = 0
        self.elapsed_seconds = 0 # 경과 시간(초)

        self.init_UI()

        # 실시간 타이머 설정 (1초마다 update_timer 실행)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def init_UI(self):
        # ChoosePage와 통일감을 주는 QSS 스타일시트
        self.setStyleSheet("""
        QWidget {
            background-color: #F5F5F5;
            font-size: 14px;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }
        QProgressBar {
            border: none;
            border-radius: 6px;
            background-color: #E0E0E0;
            text-align: center;
            color: white;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #009fe8;
            border-radius: 6px;
        }
        """)

        self.setWindowTitle("운동 진행 중")
        self.resize(800, 600)

        # ==========================================
        # 1. 상단 영역 (목표 + 프로그래스바 + 포기하기)
        # ==========================================
        self.goal_label = QLabel(f"목표 - {self.exercise_name} {self.target_level}회!", self)
        self.goal_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1976D2;
        """)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, self.target_level)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)

        # 목표 텍스트와 진행바를 담을 상단 좌측 레이아웃
        top_left_layout = QVBoxLayout()
        top_left_layout.addWidget(self.goal_label)
        top_left_layout.addWidget(self.progress_bar)

        # 포기하기 버튼
        self.btn_quit = QPushButton("포기하기", self)
        self.btn_quit.setStyleSheet("""
            QPushButton {
                background-color: #E53935;
                color: white;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
        """)
        self.btn_quit.setFixedWidth(100)
        self.btn_quit.setFixedHeight(45)

        # 상단 통합 레이아웃
        top_layout = QHBoxLayout()
        top_layout.addLayout(top_left_layout, stretch=1)
        #top_layout.addWidget(self.btn_quit)

        # ==========================================
        # 2. 메인 화면 송출 영역 (좌측 큼직한 화면)
        # ==========================================
        self.video_label = QLabel("화면 송출 공간 (웹캠/영상)", self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #212121;
                color: #FFFFFF;
                border-radius: 12px;
                font-size: 16px;
            }
        """)

        # ==========================================
        # 3. 우측 대시보드 정보 영역 (카드 형태)
        # ==========================================
        # 타이머 카드
        self.lbl_timer = self.create_info_card("00:00", "#1976D2")
        # 성공 카운트 카드
        self.lbl_success = self.create_info_card("성공: 0회", "#43A047")
        # 실패 카운트 카드
        self.lbl_fail = self.create_info_card("실패: 0회", "#E53935")
        # 총합 카드
        self.lbl_total = self.create_info_card("총합: 0회", "#424242")

        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(12)
        right_side_layout.addWidget(self.lbl_timer)
        right_side_layout.addWidget(self.lbl_success)
        right_side_layout.addWidget(self.lbl_fail)
        right_side_layout.addWidget(self.lbl_total)
        right_side_layout.addStretch() # 아래 여백 채우기
        right_side_layout.addWidget(self.btn_quit)

        # ==========================================
        # 4. 하단 레이아웃 분할 (좌: 비디오 / 우: 정보)
        # ==========================================
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.video_label, stretch=3) # 화면을 3비율로
        content_layout.addLayout(right_side_layout, stretch=1)  # 우측 카드를 1비율로

        # ==========================================
        # 5. 전체 레이아웃 조립
        # ==========================================
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(content_layout, stretch=1)

        self.setLayout(main_layout)

        # 시그널 연결
        self.btn_quit.clicked.connect(self.quit_exercise)

    def create_info_card(self, text, color):
        """카드 형태의 멋진 라벨 위젯 생성 헬퍼 함수"""
        lbl = QLabel(text, self)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFixedHeight(70)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: white;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                color: {color};
                border: 1px solid #E0E0E0;
            }}
        """)
        return lbl

    # --- 기능 및 데이터 설정 함수 ---

    def set_config(self, mode="횟수", level=30, image_idx=0):
        
        self.mode = mode
        self.target_level = level
        self.success_count = 0
        self.fail_count = 0
        self.elapsed_seconds = 0

        # UI 업데이트
        unit = "분" if mode == "시간" else "회"
        self.goal_label.setText(f"목표 - {self.exercise_name} {self.target_level}{unit}!")
        
        self.progress_bar.setRange(0, self.target_level if level > 0 else 1)
        self.progress_bar.setValue(0)
        
        self.update_counts()
        
        # 타이머 시작
        self.timer.start(1000)

    def update_frame(self, cv_img):
        """OpenCV 웹캠 프레임을 비디오 라벨에 표시하는 함수"""
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        
        q_img = QImage(rgb_img.data.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # 라벨 크기에 맞춰 비율을 유지하며 출력
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def update_timer(self):
        """1초마다 실행되는 타이머 함수"""
        self.elapsed_seconds += 1
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        self.lbl_timer.setText(f"{mins:02d}:{secs:02d}")

    def update_counts(self):
        """성공/실패 카운트 업데이트 시 호출"""
        total = self.success_count + self.fail_count
        unit = "분" if self.mode == "시간" else "회"
        
        self.lbl_success.setText(f"성공: {self.success_count}{unit}")
        self.lbl_fail.setText(f"실패: {self.fail_count}{unit}")
        self.lbl_total.setText(f"총합: {total}{unit}")
        
        # 진행률 업데이트
        self.progress_bar.setValue(self.success_count)

    def quit_exercise(self):
        """포기하기 버튼 클릭 시"""
        self.timer.stop()
        if self.main_window and hasattr(self.main_window, "show_choose_page"):
            self.main_window.show_choose_page()
        else:
            print("[단독 실행] 운동 중단 - 선택 화면으로 이동")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExercisePage()
    window.set_config(mode="횟수", level=30)
    window.show()
    sys.exit(app.exec())