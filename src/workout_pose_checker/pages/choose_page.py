import sys
from pathlib import Path
import cv2

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, 
    QButtonGroup, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

class ChoosePage(QWidget):

    def __init__(self, main_window=None):
        super().__init__()

        self.main_window = main_window

        # 상위 폴더에서 접근해서 이미지 가져오기
        current_path = Path(__file__).resolve()
        parent_path = current_path.parent.parent  # 상위 상위 폴더
        folder_path = parent_path / "images"

        # 이미지 리스트 및 인덱스
        self.image_list = []
        self.current_index = 0

        # 특정 확장자가 붙은 파일만 로드
        if folder_path.exists():
            for file in folder_path.glob("*"):
                if file.suffix.lower() in [".jpg", ".png", ".jpeg"]:
                    img = cv2.imread(str(file))
                    if img is not None:
                        self.image_list.append(img)

        # 레벨(목표치) 및 운동 모드 기본값
        self.level = 0
        self.exercise_mode = "시간"

        self.init_UI()

    def cv_to_pixmap(self, cv_img):
       
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w

        q_img = QImage(
            rgb_img.data.tobytes(),  # 메모리 안전성을 위해 tobytes() 적용
            w, h, bytes_per_line, 
            QImage.Format_RGB888
        )
        return QPixmap.fromImage(q_img)

    def init_UI(self):
        
        # 스타일시트 설정
        self.setStyleSheet("""
        QWidget {
            background-color: #F5F5F5;
            font-size: 14px;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            background-color: #009fe8;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #43A047;
        }
        QPushButton:pressed {
            background-color: #388E3C;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
            color: #666666;
        }
        QPushButton:checked {
            background-color: #170099;
        }
        """)

        self.setWindowTitle("운동 선택")
        self.resize(1000, 800)

        # 1. 운동 이미지 라벨
        self.image_label = QLabel(self)
        self.image_label.setMaximumHeight(500)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)

      

        if self.image_list:
            pixmap = self.cv_to_pixmap(self.image_list[0])
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("이미지를 찾을 수 없습니다.")

        # 2. 버튼 생성
        self.btn_prev = QPushButton("<", self)
        self.btn_start = QPushButton("운동 시작 하기", self)
        self.btn_next = QPushButton(">", self)

        # 시작 버튼 스타일
        self.btn_start.setMinimumHeight(45)
        self.btn_start.setStyleSheet("""
        QPushButton {
            background: #FF9800;
            color: white;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: #FB8C00;
        }
        """)

        # 시간/횟수 토글 버튼 & 그룹
        self.btn_time = QPushButton("시간", self)
        self.btn_count = QPushButton("횟수", self)
        self.btn_time.setCheckable(True)
        self.btn_count.setCheckable(True)
        self.btn_time.setChecked(True)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.btn_time)
        self.mode_group.addButton(self.btn_count)

        # 수치 증감 버튼 및 라벨
        self.sub_5_btn = QPushButton("-5", self)
        self.sub_1_btn = QPushButton("-1", self)
        self.temp_label = QLabel(f"{self.level} 분", self)
        self.add_1_btn = QPushButton("+1", self)
        self.add_5_btn = QPushButton("+5", self)


        
        self.name_label = QLabel("스쿼트")

        self.name_label.setFixedHeight(50)

        self.name_label.setAlignment(Qt.AlignCenter)

        self.name_label.setStyleSheet("""
        QLabel {
            font-size: 48px;
            font-weight: bold;
            color: #1976D2;
        }
        """)

        self.temp_label.setAlignment(Qt.AlignCenter)
        self.temp_label.setFixedWidth(80)
        self.temp_label.setStyleSheet("""
        font-size: 22px;
        font-weight: bold;
        color: #1976D2;
        """)

        # 초기 버튼 활성화 상태 지정
        self.btn_prev.setEnabled(False)
        if len(self.image_list) <= 1:
            self.btn_next.setEnabled(False)

        # 3. 시그널/슬롯(이벤트) 연결
        self.btn_prev.clicked.connect(self.prev)
        self.btn_start.clicked.connect(self.start_exercise)
        self.btn_next.clicked.connect(self.next)
        self.mode_group.buttonClicked.connect(self.change_mode)

        self.sub_5_btn.clicked.connect(lambda: self.change_level(-5))
        self.sub_1_btn.clicked.connect(lambda: self.change_level(-1))
        self.add_1_btn.clicked.connect(lambda: self.change_level(1))
        self.add_5_btn.clicked.connect(lambda: self.change_level(5))

        # 4. 레이아웃 배치
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_next)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.btn_time)
        mode_layout.addWidget(self.btn_count)

        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_label)

        num_layout = QHBoxLayout()
        num_layout.addWidget(self.sub_5_btn)
        num_layout.addWidget(self.sub_1_btn)
        num_layout.addWidget(self.temp_label)
        num_layout.addWidget(self.add_1_btn)
        num_layout.addWidget(self.add_5_btn)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.addWidget(self.image_label)
        main_layout.addLayout(name_layout)
        main_layout.addLayout(mode_layout)
        main_layout.addLayout(num_layout)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    # --- 기능 메서드 ---
    def change_img(self):
        if self.image_list:
            pixmap = self.cv_to_pixmap(self.image_list[self.current_index])
            self.image_label.setPixmap(pixmap)
        if  self.current_index == 0:
            self.name_label.setText("스쿼트" )
        elif  self.current_index  == 1:         
            self.name_label.setText("팔굽혀펴기")
    def prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.change_img()

        if self.current_index == 0:
            self.btn_prev.setEnabled(False)

        self.btn_next.setEnabled(True)

    def next(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.change_img()

        if self.current_index == len(self.image_list) - 1:
            self.btn_next.setEnabled(False)

        self.btn_prev.setEnabled(True)

    def start_exercise(self):
        if self.main_window and hasattr(self.main_window, "show_exercise_page"):
            self.main_window.show_exercise_page()
        else:
            print(f"[단독 실행] 운동 시작 - 모드: {self.exercise_mode}, 목표: {self.level}")

    def change_mode(self, button):
        self.exercise_mode = button.text()
        self.update_label()

    def change_level(self, value):
        self.level += value
        if self.level < 0:
            self.level = 0
        self.update_label()

    def update_label(self):
        unit = "분" if self.exercise_mode == "시간" else "회"
        self.temp_label.setText(f"{self.level} {unit}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChoosePage()
    window.show()
    sys.exit(app.exec())