"""팔굽혀펴기 자세의 단계와 성공 횟수를 판정한다."""

from ..pose_utils import calculate_angle, select_visible_side


# COCO 관절 번호: 어깨, 팔꿈치, 손목, 엉덩이, 발목 순서이다.
PUSHUP_SIDE_INDEXES = {
    "L": (5, 7, 9, 11, 15),
    "R": (6, 8, 10, 12, 16),
}

KEYPOINT_CONFIDENCE = 0.5
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
        self.failure_count = 0
        self.rep_in_progress = False
        self.reached_bottom = False
        self.bottom_frames = 0
        self.top_frames = 0
        self.status = "READY"

    def analyze(self, points, scores):
        """한 프레임의 관절로 팔굽혀펴기 상태를 갱신하고 결과를 반환한다."""
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
    ):
        """UI 계약에 맞는 팔굽혀펴기 분석 결과를 구성한다."""
        return {
            "detected": detected,
            "exercise": "pushup",
            "status": self.status,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "side": side,
            "metrics": {
                "elbow_angle": elbow_angle,
                "body_angle": body_angle,
            },
            "error": None,
        }

