"""포즈 키포인트를 OpenCV 프레임에 표시하는 공용 렌더러."""

import cv2


# YOLO Pose가 사용하는 COCO 17개 키포인트의 연결 구조다.
POSE_CONNECTIONS = (
    (0, 1),
    (0, 2),
    (1, 2),
    (1, 3),
    (2, 4),
    (3, 5),
    (4, 6),
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
KEYPOINT_COLOR = (0, 0, 255)
CONNECTION_COLOR = (0, 255, 0)


def draw_pose(frame, keypoints, confidence=DRAW_CONFIDENCE):
    """신뢰도 기준을 통과한 관절점과 연결선을 프레임에 그린다."""
    visible = {
        point["index"]: (
            int(point["x"]),
            int(point["y"]),
        )
        for point in keypoints
        if point["confidence"] >= confidence
    }

    for start, end in POSE_CONNECTIONS:
        if start in visible and end in visible:
            cv2.line(
                frame,
                visible[start],
                visible[end],
                CONNECTION_COLOR,
                2,
            )

    for position in visible.values():
        cv2.circle(frame, position, 4, KEYPOINT_COLOR, -1)

    return frame
