from pathlib import Path

import cv2

from .pose_service import PoseService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "yolo26n-pose.pt"
WINDOW_NAME = "Workout Pose Checker"
EXERCISE = "squat"

POSE_CONNECTIONS = (
    (5, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16),
)
DRAW_CONFIDENCE = 0.5


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


def draw_pose(frame, keypoints):
    visible = {
        point["index"]: (
            int(point["x"]),
            int(point["y"]),
        )
        for point in keypoints
        if point["confidence"] >= DRAW_CONFIDENCE
    }

    for start, end in POSE_CONNECTIONS:
        if start in visible and end in visible:
            cv2.line(
                frame,
                visible[start],
                visible[end],
                (0, 255, 0),
                2,
            )

    for position in visible.values():
        cv2.circle(frame, position, 4, (0, 0, 255), -1)


def draw_analysis(frame, analysis):
    draw_pose(frame, analysis["keypoints"])
    metrics = analysis["metrics"]

    if analysis["side"] is not None:
        draw_text(frame, f'Side: {analysis["side"]}', 40)
        draw_text(
            frame,
            f'Hip angle: {metrics["hip_angle"]:.1f}',
            70,
            (0, 255, 255),
        )
        draw_text(
            frame,
            f'Knee angle: {metrics["knee_angle"]:.1f}',
            100,
            (0, 255, 255),
        )
        draw_text(
            frame,
            f'Hip depth: {metrics["hip_depth"]:.2f}',
            130,
            (0, 255, 255),
        )

    draw_text(
        frame,
        f'Status: {analysis["status"]}',
        170,
        (0, 255, 0),
    )
    draw_text(
        frame,
        f'Success: {analysis["success_count"]}',
        200,
    )
    draw_text(
        frame,
        f'Fail: {analysis["failure_count"]}',
        230,
    )


def main():
    service = PoseService(
        model_path=MODEL_PATH,
        device="cuda:0",
    )
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("웹캠을 열 수 없습니다.")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("웹캠 프레임을 읽을 수 없습니다.")

            analysis = service.analyze_frame(frame, EXERCISE)
            draw_analysis(frame, analysis)
            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
