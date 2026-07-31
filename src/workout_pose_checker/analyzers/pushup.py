"""팔굽혀펴기 자세의 단계와 성공 횟수를 판정한다."""

import math

from ..pose_utils import calculate_angle, select_visible_side


# COCO 관절 번호: 어깨, 팔꿈치, 손목, 엉덩이, 발목 순서이다.
PUSHUP_SIDE_INDEXES = {
    "L": (5, 7, 9, 11, 15),
    "R": (6, 8, 10, 12, 16),
}
PUSHUP_FRONT_INDEXES = (5, 6, 7, 8, 9, 10, 11, 12)

KEYPOINT_CONFIDENCE = 0.5
FRONT_VIEW_RATIO = 0.65
FRONT_VIEW_EXIT_RATIO = 0.50
VIEW_CONFIRM_FRAMES = 5
TOP_ELBOW_ANGLE = 160
START_ELBOW_ANGLE = 145
BOTTOM_ELBOW_ANGLE = 100
STRAIGHT_BODY_ANGLE = 160
CONFIRM_FRAMES = 3


class PushupAnalyzer:
    """팔꿈치와 몸통 각도를 이용해 팔굽혀펴기 반복 상태를 추적한다."""

    def __init__(self):
        self.reset()

    def reset(self):
        """누적 횟수와 진행 중인 반복 상태를 초기화한다."""
        self.success_count = 0
        self.rep_in_progress = False
        self.reached_bottom = False
        self.bottom_frames = 0
        self.top_frames = 0
        self.status = "READY"
        self.current_view = None
        self.pending_view = None
        self.pending_view_frames = 0

    def analyze(self, points, scores):
        """한 프레임의 관절로 팔굽혀펴기 상태를 갱신하고 결과를 반환한다."""
        front_metrics = self._front_metrics(points, scores)
        selected_view = self._select_view(front_metrics)

        if selected_view == "FRONT":
            if front_metrics is None:
                self.status = "JOINTS_NOT_VISIBLE"
                return self._result(detected=False, side="FRONT")

            return self._analyze_angles(
                side="FRONT",
                elbow_angle=front_metrics["elbow_angle"],
                body_angle=None,
                body_is_straight=True,
                left_elbow_angle=front_metrics["left_elbow_angle"],
                right_elbow_angle=front_metrics["right_elbow_angle"],
                front_view_ratio=front_metrics["front_view_ratio"],
            )

        side = select_visible_side(
            scores,
            PUSHUP_SIDE_INDEXES,
            KEYPOINT_CONFIDENCE,
        )

        if side is None:
            self.status = "JOINTS_NOT_VISIBLE"
            return self._result(detected=False)

        shoulder_index, elbow_index, wrist_index, hip_index, ankle_index = (
            PUSHUP_SIDE_INDEXES[side]
        )
        shoulder = points[shoulder_index]
        elbow = points[elbow_index]
        wrist = points[wrist_index]
        hip = points[hip_index]
        ankle = points[ankle_index]

        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        body_angle = calculate_angle(shoulder, hip, ankle)
        body_is_straight = body_angle >= STRAIGHT_BODY_ANGLE

        return self._analyze_angles(
            side=side,
            elbow_angle=elbow_angle,
            body_angle=body_angle,
            body_is_straight=body_is_straight,
        )

    def _front_metrics(self, points, scores):
        """양팔이 모두 보일 때 정면 판정에 필요한 측정값을 반환한다."""
        if any(
            scores[index] < KEYPOINT_CONFIDENCE
            for index in PUSHUP_FRONT_INDEXES
        ):
            return None

        left_shoulder, right_shoulder = points[5], points[6]
        left_hip, right_hip = points[11], points[12]
        shoulder_center = (
            (left_shoulder[0] + right_shoulder[0]) / 2,
            (left_shoulder[1] + right_shoulder[1]) / 2,
        )
        hip_center = (
            (left_hip[0] + right_hip[0]) / 2,
            (left_hip[1] + right_hip[1]) / 2,
        )
        shoulder_width = math.dist(left_shoulder, right_shoulder)
        torso_length = max(math.dist(shoulder_center, hip_center), 1)
        front_view_ratio = shoulder_width / torso_length

        left_elbow_angle = calculate_angle(points[5], points[7], points[9])
        right_elbow_angle = calculate_angle(points[6], points[8], points[10])
        return {
            "elbow_angle": (left_elbow_angle + right_elbow_angle) / 2,
            "left_elbow_angle": left_elbow_angle,
            "right_elbow_angle": right_elbow_angle,
            "front_view_ratio": front_view_ratio,
        }

    def _select_view(self, front_metrics):
        """정면 비율을 연속 확인해 안정적인 촬영 방향을 선택한다."""
        front_view_ratio = (
            front_metrics["front_view_ratio"]
            if front_metrics is not None
            else 0
        )
        threshold = (
            FRONT_VIEW_EXIT_RATIO
            if self.current_view == "FRONT"
            else FRONT_VIEW_RATIO
        )
        candidate_view = (
            "FRONT"
            if front_view_ratio >= threshold
            else "SIDE"
        )

        if self.current_view is None:
            self.current_view = candidate_view
            return self.current_view

        if candidate_view == self.current_view:
            self.pending_view = None
            self.pending_view_frames = 0
            return self.current_view

        if candidate_view != self.pending_view:
            self.pending_view = candidate_view
            self.pending_view_frames = 1
        else:
            self.pending_view_frames += 1

        if self.pending_view_frames >= VIEW_CONFIRM_FRAMES:
            self.current_view = candidate_view
            self.pending_view = None
            self.pending_view_frames = 0
            self._reset_rep_progress()

        return self.current_view

    def _reset_rep_progress(self):
        """촬영 방향 전환 시 누적 횟수는 유지하고 진행 중인 반복만 취소한다."""
        self.rep_in_progress = False
        self.reached_bottom = False
        self.bottom_frames = 0
        self.top_frames = 0
        self.status = "READY"

    def _analyze_angles(
        self,
        *,
        side,
        elbow_angle,
        body_angle,
        body_is_straight,
        left_elbow_angle=None,
        right_elbow_angle=None,
        front_view_ratio=None,
    ):
        """촬영 방향에 맞게 계산된 각도로 공통 반복 상태를 갱신한다."""
        # 팔꿈치 각도와 몸통 정렬 상태로 위·아래 자세를 구분한다.
        is_top = (
            elbow_angle >= TOP_ELBOW_ANGLE
            and body_is_straight
        )
        has_started = elbow_angle <= START_ELBOW_ANGLE
        is_bottom = (
            elbow_angle <= BOTTOM_ELBOW_ANGLE
            and body_is_straight
        )

        # 팔꿈치가 굽혀지기 시작하면 새로운 반복을 시작한다.
        if has_started and not self.rep_in_progress:
            self.rep_in_progress = True
            self.reached_bottom = False
            self.status = "GO_DOWN"

        if self.rep_in_progress:
            # 연속 프레임 확인으로 순간적인 관절 좌표 흔들림을 걸러낸다.
            self.bottom_frames = (
                self.bottom_frames + 1 if is_bottom else 0
            )
            self.top_frames = self.top_frames + 1 if is_top else 0

            if self.bottom_frames >= CONFIRM_FRAMES:
                self.reached_bottom = True
                self.status = "GO_UP"

            if self.top_frames >= CONFIRM_FRAMES:
                if self.reached_bottom:
                    self.success_count += 1
                    self.status = "SUCCESS"
                else:
                    self.status = "READY"

                self.rep_in_progress = False
                self.reached_bottom = False
                self.bottom_frames = 0
                self.top_frames = 0
            elif not body_is_straight:
                self.status = "KEEP_BODY_STRAIGHT"
        elif is_top:
            self.status = "READY"

        return self._result(
            detected=True,
            side=side,
            elbow_angle=elbow_angle,
            body_angle=body_angle,
            left_elbow_angle=left_elbow_angle,
            right_elbow_angle=right_elbow_angle,
            front_view_ratio=front_view_ratio,
        )

    def person_not_found(self):
        """사람을 찾지 못한 프레임의 표준 결과를 반환한다."""
        self.status = "PERSON_NOT_FOUND"
        return self._result(detected=False)

    def _result(
        self,
        *,
        detected,
        side=None,
        elbow_angle=None,
        body_angle=None,
        left_elbow_angle=None,
        right_elbow_angle=None,
        front_view_ratio=None,
    ):
        """UI 계약에 맞는 팔굽혀펴기 분석 결과를 구성한다."""
        return {
            "detected": detected,
            "exercise": "pushup",
            "status": self.status,
            "success_count": self.success_count,
            "side": side,
            "metrics": {
                "elbow_angle": elbow_angle,
                "body_angle": body_angle,
                "left_elbow_angle": left_elbow_angle,
                "right_elbow_angle": right_elbow_angle,
                "front_view_ratio": front_view_ratio,
            },
            "error": None,
        }

