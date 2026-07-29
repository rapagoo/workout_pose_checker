"""웹캠 입력으로 포즈 평가 기능을 확인하는 간단한 실행 프로그램."""

import argparse
from pathlib import Path

import cv2

# 실제 모델 테스트
# from .pose_service import PoseService

# Mock 테스트
from .mock_pose_service import MockPoseService


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
    """프레임 왼쪽의 지정된 높이에 상태 문구를 그린다."""
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
    """신뢰도 기준을 통과한 관절과 연결선을 프레임에 그린다."""
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
    """서비스 결과의 관절, 측정값, 상태와 성공 횟수를 화면에 표시한다."""
    draw_pose(frame, analysis["keypoints"])
    metrics = analysis["metrics"]

    if analysis["side"] is not None:
        draw_text(frame, f'Side: {analysis["side"]}', 40)
        if analysis["exercise"] == "squat":
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
        elif analysis["exercise"] == "pushup":
            draw_text(
                frame,
                f'Elbow angle: {metrics["elbow_angle"]:.1f}',
                70,
                (0, 255, 255),
            )
            draw_text(
                frame,
                f'Body angle: {metrics["body_angle"]:.1f}',
                100,
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


def main(exercise=EXERCISE):
    """웹캠 프레임을 반복 분석하며 q 또는 Esc 입력 전까지 결과를 보여준다."""
    # 실제 모델
    # service = PoseService(model_path=MODEL_PATH)

    # Mock 모델
    service = MockPoseService(frames_per_status=30)

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("웹캠을 열 수 없습니다.")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("웹캠 프레임을 읽을 수 없습니다.")

            # PoseService가 UI와 모델 사이의 유일한 연동 지점이다.
            analysis = service.analyze_frame(frame, exercise)
            draw_analysis(frame, analysis)
            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exercise",
        choices=("squat", "pushup"),
        default=EXERCISE,
    )
    args = parser.parse_args()
    main(exercise=args.exercise)
