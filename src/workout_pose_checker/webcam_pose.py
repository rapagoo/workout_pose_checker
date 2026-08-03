"""웹캠 입력으로 포즈 평가 기능을 확인하는 간단한 실행 프로그램."""

import argparse

import cv2

from .app_paths import get_model_path
from .pose_service import PoseService
from .pose_renderer import draw_pose

WINDOW_NAME = "Workout Pose Checker"
EXERCISE = "squat"

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


def draw_analysis(frame, analysis):
    """서비스 결과의 관절, 측정값, 상태와 성공 횟수를 화면에 표시한다."""
    draw_pose(frame, analysis["keypoints"])
    metrics = analysis["metrics"]

    if analysis["side"] is not None:
        draw_text(frame, f'Side: {analysis["side"]}', 40)
        if analysis["exercise"] == "squat":
            hip_angle = metrics["hip_angle"]
            knee_angle = metrics["knee_angle"]
            hip_depth = metrics["hip_depth"]
            if hip_angle is not None:
                draw_text(
                    frame,
                    f"Hip angle: {hip_angle:.1f}",
                    70,
                    (0, 255, 255),
                )
            if knee_angle is not None:
                draw_text(
                    frame,
                    f"Knee angle: {knee_angle:.1f}",
                    100,
                    (0, 255, 255),
                )
            if hip_depth is not None:
                draw_text(
                    frame,
                    f"Hip depth: {hip_depth:.2f}",
                    130,
                    (0, 255, 255),
                )
        elif analysis["exercise"] == "pushup":
            elbow_angle = metrics["elbow_angle"]
            if elbow_angle is not None:
                draw_text(
                    frame,
                    f"Elbow angle: {elbow_angle:.1f}",
                    70,
                    (0, 255, 255),
                )

            left_elbow_angle = metrics["left_elbow_angle"]
            right_elbow_angle = metrics["right_elbow_angle"]
            front_view_ratio = metrics["front_view_ratio"]
            if (
                analysis["side"] == "FRONT"
                and left_elbow_angle is not None
                and right_elbow_angle is not None
                and front_view_ratio is not None
            ):
                draw_text(
                    frame,
                    (
                        f"L/R elbow: {left_elbow_angle:.1f}"
                        f" / {right_elbow_angle:.1f}"
                    ),
                    100,
                    (0, 255, 255),
                )
                draw_text(
                    frame,
                    f"Front ratio: {front_view_ratio:.2f}",
                    130,
                    (0, 255, 255),
                )
            elif metrics["body_angle"] is not None:
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
    service = PoseService(model_path=get_model_path())

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
