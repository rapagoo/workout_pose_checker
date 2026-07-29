from pathlib import Path

import cv2
from ultralytics import YOLO

from .analyzers import SquatAnalyzer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "yolo26n-pose.pt"


def draw_text(frame, text, y, color=(255, 255, 255)):
    cv2.putText(
        frame,
        text,
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2,
    )


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"모델 파일을 찾을 수 없습니다: {MODEL_PATH}\n"
            "yolo26n-pose.pt 파일을 models 폴더에 넣어주세요."
        )

    model = YOLO(MODEL_PATH)
    analyzer = SquatAnalyzer()
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("웹캠을 열 수 없습니다.")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("웹캠 프레임을 읽을 수 없습니다.")

            # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            result = model.predict(
                source=frame,
                conf=0.5,
                imgsz=640,
                device="cuda:0",
                verbose=False,
            )[0]
            annotated_frame = result.plot()

            if (
                result.keypoints is not None
                and result.keypoints.conf is not None
                and len(result.keypoints.xy) > 0
            ):
                points = result.keypoints.xy[0].cpu().numpy()
                scores = result.keypoints.conf[0].cpu().numpy()
                analysis = analyzer.analyze(points, scores)
            else:
                analysis = analyzer.person_not_found()

            metrics = analysis["metrics"]
            if analysis["side"] is not None:
                draw_text(
                    annotated_frame,
                    f'Side: {analysis["side"]}',
                    40,
                )
                draw_text(
                    annotated_frame,
                    f'Hip angle: {metrics["hip_angle"]:.1f}',
                    70,
                    (0, 255, 255),
                )
                draw_text(
                    annotated_frame,
                    f'Knee angle: {metrics["knee_angle"]:.1f}',
                    100,
                    (0, 255, 255),
                )
                draw_text(
                    annotated_frame,
                    f'Hip depth: {metrics["hip_depth"]:.2f}',
                    130,
                    (0, 255, 255),
                )

            draw_text(
                annotated_frame,
                f'Status: {analysis["status"]}',
                170,
                (0, 255, 0),
            )
            draw_text(
                annotated_frame,
                f'Success: {analysis["success_count"]}',
                200,
            )
            draw_text(
                annotated_frame,
                f'Fail: {analysis["failure_count"]}',
                230,
            )

            cv2.imshow("Workout Pose Checker", annotated_frame)

            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
