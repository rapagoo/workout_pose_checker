from ..pose_utils import calculate_angle, select_visible_side


SQUAT_SIDE_INDEXES = {
    "L": (5, 11, 13, 15),
    "R": (6, 12, 14, 16),
}

KEYPOINT_CONFIDENCE = 0.5
STANDING_HIP_ANGLE = 155
STANDING_KNEE_ANGLE = 160
START_HIP_ANGLE = 145
START_KNEE_ANGLE = 150
BOTTOM_HIP_ANGLE = 100
BOTTOM_KNEE_ANGLE = 110
BOTTOM_HIP_DEPTH = -0.6
CONFIRM_FRAMES = 3


class SquatAnalyzer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.success_count = 0
        self.failure_count = 0
        self.rep_in_progress = False
        self.reached_bottom = False
        self.bottom_frames = 0
        self.standing_frames = 0
        self.status = "READY"

    def analyze(self, points, scores):
        side = select_visible_side(
            scores,
            SQUAT_SIDE_INDEXES,
            KEYPOINT_CONFIDENCE,
        )

        if side is None:
            self.status = "JOINTS_NOT_VISIBLE"
            return self._result(detected=False)

        shoulder_index, hip_index, knee_index, ankle_index = (
            SQUAT_SIDE_INDEXES[side]
        )
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

        if has_started and not self.rep_in_progress:
            self.rep_in_progress = True
            self.reached_bottom = False
            self.status = "GO_DOWN"

        if self.rep_in_progress:
            self.bottom_frames = (
                self.bottom_frames + 1 if is_bottom else 0
            )
            self.standing_frames = (
                self.standing_frames + 1 if is_standing else 0
            )

            if self.bottom_frames >= CONFIRM_FRAMES:
                self.reached_bottom = True
                self.status = "GO_UP"

            if self.standing_frames >= CONFIRM_FRAMES:
                if self.reached_bottom:
                    self.success_count += 1
                    self.status = "SUCCESS"
                else:
                    self.status = "READY"

                self.rep_in_progress = False
                self.reached_bottom = False
                self.bottom_frames = 0
                self.standing_frames = 0
        elif is_standing:
            self.status = "READY"

        return self._result(
            detected=True,
            side=side,
            hip_angle=hip_angle,
            knee_angle=knee_angle,
            hip_depth=hip_depth,
        )

    def person_not_found(self):
        self.status = "PERSON_NOT_FOUND"
        return self._result(detected=False)

    def _result(
        self,
        *,
        detected,
        side=None,
        hip_angle=None,
        knee_angle=None,
        hip_depth=None,
    ):
        return {
            "detected": detected,
            "exercise": "squat",
            "status": self.status,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "side": side,
            "metrics": {
                "hip_angle": hip_angle,
                "knee_angle": knee_angle,
                "hip_depth": hip_depth,
            },
            "error": None,
        }
