from pathlib import Path

import cv2
from ultralytics import YOLO

from .pose_utils import calculate_angle, select_visible_side


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "yolo26n-pose.pt"

KEYPOINT_CONFIDENCE = 0.5
STANDING_HIP_ANGLE = 155
STANDING_KNEE_ANGLE = 160
START_HIP_ANGLE = 145
START_KNEE_ANGLE = 150
BOTTOM_HIP_ANGLE = 100
BOTTOM_KNEE_ANGLE = 110
BOTTOM_HIP_DEPTH = -0.6
CONFIRM_FRAMES = 3
SQUAT_SIDE_INDEXES = {
    "L": (5, 11, 13, 15),
    "R": (6, 12, 14, 16),
}


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
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("웹캠을 열 수 없습니다.")

    success_count = 0
    failure_count = 0
    rep_in_progress = False
    reached_bottom = False
    bottom_frames = 0
    standing_frames = 0
    status = "READY"

    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("웹캠 프레임을 읽을 수 없습니다.")

            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

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
                side = select_visible_side(
                    scores,
                    SQUAT_SIDE_INDEXES,
                    KEYPOINT_CONFIDENCE,
                )

                if side is None:
                    status = "JOINTS_NOT_VISIBLE"
                else:
                    indexes = SQUAT_SIDE_INDEXES[side]
                    shoulder_index, hip_index, knee_index, ankle_index = indexes

                    shoulder = points[shoulder_index]
                    hip = points[hip_index]
                    knee = points[knee_index]
                    ankle = points[ankle_index]

                    hip_angle = calculate_angle(shoulder, hip, knee)
                    knee_angle = calculate_angle(hip, knee, ankle)
                    lower_leg_length = max(abs(ankle[1] - knee[1]), 1)
                    hip_depth = (hip[1] - knee[1]) / lower_leg_length

                    is_standing = (
                        hip_angle >= STANDING_HIP_ANGLE
                        and knee_angle >= STANDING_KNEE_ANGLE
                    )
                    has_started = (
                        hip_angle <= START_HIP_ANGLE
                        or knee_angle <= START_KNEE_ANGLE
                    )
                    is_bottom = (
                        hip_angle <= BOTTOM_HIP_ANGLE
                        and knee_angle <= BOTTOM_KNEE_ANGLE
                        and hip_depth >= BOTTOM_HIP_DEPTH
                    )

                    if has_started and not rep_in_progress:
                        rep_in_progress = True
                        reached_bottom = False
                        status = "MOVING"

                    if rep_in_progress:
                        bottom_frames = (
                            bottom_frames + 1 if is_bottom else 0
                        )
                        standing_frames = (
                            standing_frames + 1 if is_standing else 0
                        )

                        if bottom_frames >= CONFIRM_FRAMES:
                            reached_bottom = True
                            status = "BOTTOM"

                        if standing_frames >= CONFIRM_FRAMES:
                            if reached_bottom:
                                success_count += 1
                                status = "SUCCESS"
                            else:
                                failure_count += 1
                                status = "FAIL"

                            rep_in_progress = False
                            reached_bottom = False
                            bottom_frames = 0
                            standing_frames = 0
                    elif is_standing:
                        status = "READY"

                    draw_text(annotated_frame, f"Side: {side}", 40)
                    draw_text(
                        annotated_frame,
                        f"Hip angle: {hip_angle:.1f}",
                        70,
                        (0, 255, 255),
                    )
                    draw_text(
                        annotated_frame,
                        f"Knee angle: {knee_angle:.1f}",
                        100,
                        (0, 255, 255),
                    )
                    draw_text(
                        annotated_frame,
                        f"Hip depth: {hip_depth:.2f}",
                        130,
                        (0, 255, 255),
                    )
            else:
                status = "PERSON_NOT_FOUND"

            draw_text(annotated_frame, f"Status: {status}", 170, (0, 255, 0))
            draw_text(annotated_frame, f"Success: {success_count}", 200)
            draw_text(annotated_frame, f"Fail: {failure_count}", 230)

            cv2.imshow("Workout Pose Checker", annotated_frame)

            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
