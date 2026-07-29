import sys
import cv2

from PySide6.QtWidgets import (
    QApplication, QWidget,
    QLabel, QPushButton, QButtonGroup,
    QVBoxLayout, QHBoxLayout
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from pathlib import Path

class ChoosePage(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
    
        # 상위 폴더에서 접근해서 이미지 가져오기
        current_path = Path(__file__).resolve()
        parent_path = current_path.parent.parent #상위 상위 폴더
        folder_path = parent_path / "images"

        # 이미지 리스트
        self.image_list = []
         # 이미지 인덱스
        self.current_index = 0

        # 특정 확장자가 붇은 것만 가져오기
        for file in folder_path.glob("*"):
            print("check1")
            if file.suffix.lower() in [".jpg", ".png", ".jpeg"]:
                img = cv2.imread(str(file))
                self.image_list.append(img)
                print("check2")
       

        # 레벨 인덱스
        self.level = 0
        self.exercise_mode = "시간"

        self.init_UI()


    # OpenCV 이미지를 픽셀 앱으로 변환하는 함수
    def cv_to_pixmap(self, cv_img):

        """OpenCV 이미지를 QPixmap으로 변환"""
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w

        q_img = QImage(
            rgb_img.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        return QPixmap.fromImage(q_img)

    # UI 를 구혀하는 함수
    def init_UI(self):
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

        self.setWindowTitle("")
        self.resize(800, 600)

        # 운동 이미지가 들어갈 라벨 설정
        self.image_label = QLabel(self)
        self.image_label.setMaximumHeight(350)
        self.image_label.setAlignment(Qt.AlignCenter)

        #이미지 불러오기
        if self.image_list:
            pixmap = self.cv_to_pixmap(self.image_list[0])
            self.image_label.setPixmap(pixmap)


        #운동 선택 버튼 
        self.btn_prev = QPushButton("<", self)
        self.btn_start = QPushButton("운동 시작 하기", self)
        self.btn_next = QPushButton(">", self)

        #시간/횟수 토글 버튼 
        self.btn_time = QPushButton("시간")
        self.btn_count = QPushButton("횟수")

        #버튼 그룹으로 토글 버튼 만들기
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.btn_time)
        self.mode_group.addButton(self.btn_count)


        # 횟수/분 설정 버튼
        self.sub_5_btn = QPushButton("-5",self)
        self.sub_1_btn = QPushButton("-1",self)
        self.temp_label = QLabel(f"{self.level} 분", self)
        self.add_1_btn = QPushButton("+1",self)
        self.add_5_btn = QPushButton("+5",self)


        self.temp_label.setAlignment(Qt.AlignCenter)
        self.temp_label.setFixedWidth(60)
        self.temp_label.setStyleSheet("""
        font-size: 22px;
        font-weight: bold;
        color: #1976D2;
        """)
        
        # self.mode_label.setStyleSheet("""
        # font-size:18px;
        # font-weight:bold;
        # """)

        self.btn_start.setMinimumHeight(45)
        self.btn_start.setStyleSheet("""
        QPushButton{
            background:#FF9800;
            color:white;
            border-radius:10px;
            font-size:16px;
            font-weight:bold;
        }
        QPushButton:hover{
            background:#FB8C00;
        }
        """)

        # 기본 활성/비활성 상태 정하기
        self.btn_prev.setEnabled(False)

        self.btn_time.setCheckable(True)
        self.btn_count.setCheckable(True)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)

        self.mode_group.addButton(self.btn_time)
        self.mode_group.addButton(self.btn_count)

        self.btn_time.setChecked(True)

        
        # 버튼에 이벤트 함수를 연결하기
        self.btn_prev.clicked.connect(self.prev)
        self.btn_start.clicked.connect(self.start_exercise)
        self.btn_next.clicked.connect(self.next)
        self.mode_group.buttonClicked.connect(self.change_mode)

        self.sub_5_btn.clicked.connect(lambda: self.change_level(-5))
        self.sub_1_btn.clicked.connect(lambda: self.change_level(-1))
        self.add_1_btn.clicked.connect(lambda: self.change_level(1))
        self.add_5_btn.clicked.connect(lambda: self.change_level(5))

        # 수평 레이아웃
        btn_layout = QHBoxLayout() # 이미지 전환 레이아웃
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_next)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.btn_time)
        mode_layout.addWidget(self.btn_count)
        
        num_layout = QHBoxLayout()
        num_layout.addWidget(self.sub_5_btn)
        num_layout.addWidget(self.sub_1_btn)


        num_layout.addWidget(self.temp_label)
    

        num_layout.addWidget(self.add_1_btn)
        num_layout.addWidget(self.add_5_btn)

        #수직 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)          # 위젯 사이 간격
        main_layout.setContentsMargins(20, 20, 20, 20)   # 바깥 여백

        main_layout.addWidget(self.image_label)
        main_layout.addLayout(mode_layout)
        main_layout.addLayout(num_layout)
        main_layout.addLayout(btn_layout)

        # 메인 레이아웃 설정
        self.setLayout(main_layout)


        self.flag = 0

    # 이미지 변환하는 함수
    def change_img(self):
        pixmap = self.cv_to_pixmap(self.image_list[self.current_index])
        self.image_label.setPixmap(pixmap)

    # 이전 이미지로 돌아가기 버튼 이벤트 함수
    def prev(self):

        if self.current_index > 0:
            self.current_index -= 1

        self.change_img()

        # 첫 이미지면 이전 버튼 비활성화
        if self.current_index == 0:
            self.btn_prev.setEnabled(False)

        self.btn_next.setEnabled(True)

    # 운동시작하기 버튼 이벤트 함수
    def start_exercise(self):

        self.main_window.show_exercise_page()

    # 다음 이미지로 전환하는 버튼 이벤트 함수
    def next(self):

        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1

        self.change_img()

        # 마지막 이미지면 다음 버튼 비활성화
        if self.current_index == len(self.image_list) - 1:
            self.btn_next.setEnabled(False)

        self.btn_prev.setEnabled(True)   

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