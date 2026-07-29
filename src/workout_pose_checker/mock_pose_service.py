"""실제 포즈 추론 없이 UI 연동을 확인하기 위한 테스트 서비스."""


class MockPoseService:
    """실제 PoseService와 같은 형식의 가상 분석 결과를 반환한다."""

    # UI가 확인할 기본 운동 흐름을 프레임 수에 맞춰 순서대로 반복한다.
    STATUSES = ("READY", "GO_DOWN", "GO_UP", "SUCCESS")

    def __init__(self, frames_per_status=30):
        # 한 상태를 유지할 프레임 수이다. 30 FPS 기준 30은 약 1초이다.
        self.frames_per_status = frames_per_status
        self.frame_count = 0
        self.status_index = 0
        self.success_count = 0

    def analyze_frame(self, frame, exercise):
        """프레임을 분석하지 않고 현재 순서의 가상 결과를 반환한다."""
        status = self.STATUSES[self.status_index]

        # SUCCESS 상태에 처음 들어온 프레임에서만 횟수를 증가시킨다.
        if status == "SUCCESS" and self.frame_count == 0:
            self.success_count += 1

        result = {
            "detected": True,
            "exercise": exercise,
            "status": status,
            "success_count": self.success_count,
            "side": None,
            "metrics": self._metrics(exercise),
            "keypoints": [],
            "error": None,
        }

        self.frame_count += 1

        # 지정한 프레임 수가 지나면 다음 상태로 이동하고 끝에서는 반복한다.
        if self.frame_count >= self.frames_per_status:
            self.frame_count = 0
            self.status_index = (
                self.status_index + 1
            ) % len(self.STATUSES)

        return result

    def reset(self, exercise):
        """운동 변경 또는 초기화 요청 시 처음 상태로 되돌린다."""
        self.frame_count = 0
        self.status_index = 0
        self.success_count = 0

    @staticmethod
    def _metrics(exercise):
        """실제 서비스와 동일한 운동별 측정값 키를 제공한다."""
        if exercise == "squat":
            return {
                "hip_angle": None,
                "knee_angle": None,
                "hip_depth": None,
            }

        if exercise == "pushup":
            return {
                "elbow_angle": None,
                "body_angle": None,
            }

        raise ValueError(f"지원하지 않는 운동입니다: {exercise}")
