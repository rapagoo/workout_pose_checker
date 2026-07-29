from pathlib import Path

from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "yolo26n-pose.pt"


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"모델 파일을 찾을 수 없습니다: {MODEL_PATH}\n"
            "yolo26n-pose.pt 파일을 models 폴더에 넣어주세요."
        )

    model = YOLO(MODEL_PATH)

    # source=0은 기본 웹캠이며, 결과를 별도 창에 표시합니다.
    model.predict(
        source=0,
        show=True,
        conf=0.5,
        imgsz=640,
    )


if __name__ == "__main__":
    main()

