"""YOLO 포즈 추론 결과와 운동별 분석기를 연결하는 서비스."""

from pathlib import Path

from .analyzers import PushupAnalyzer, SquatAnalyzer


class PoseService:
    """한 프레임을 추론하고 선택한 운동 분석 결과를 UI 형식으로 반환한다."""

    def __init__(
        self,
        model_path=None,
        device=None,
        *,
        model=None,
        analyzers=None,
        confidence=0.5,
        image_size=640,
    ):
        """모델과 운동 분석기를 준비한다.

        테스트에서는 ``model``과 ``analyzers``를 주입해 실제 YOLO 없이 사용할 수 있다.
        """
        if model is None:
            if model_path is None:
                raise ValueError("model_path가 필요합니다.")

            model_path = Path(model_path)
            if not model_path.exists():
                raise FileNotFoundError(
                    f"모델 파일을 찾을 수 없습니다: {model_path}"
                )

            from ultralytics import YOLO

            model = YOLO(model_path)

        self.model = model
        self.device = device
        self.confidence = confidence
        self.image_size = image_size
        self.analyzers = (
            analyzers
            if analyzers is not None
            else {
                "pushup": PushupAnalyzer(),
                "squat": SquatAnalyzer(),
            }
        )

    def analyze_frame(self, frame, exercise):
        """OpenCV 프레임에서 가장 크게 감지된 한 사람의 운동을 분석한다."""
        analyzer = self._get_analyzer(exercise)
        result = self.model.predict(
            source=frame,
            conf=self.confidence,
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )[0]

        keypoints = result.keypoints
        if (
            keypoints is None
            or keypoints.conf is None
            or len(keypoints.xy) == 0
        ):
            analysis = analyzer.person_not_found()
            analysis["keypoints"] = []
            return analysis

        # UI가 여러 사람 중 누구를 분석할지 고민하지 않도록 가장 큰 사람을 고른다.
        boxes = result.boxes.xyxy.cpu().numpy()
        widths = boxes[:, 2] - boxes[:, 0]
        heights = boxes[:, 3] - boxes[:, 1]
        areas = widths * heights
        person_index = int(areas.argmax())

        # 분석기는 선택된 사람의 COCO 관절 좌표와 신뢰도만 전달받는다.
        points = keypoints.xy[person_index].cpu().numpy()
        scores = keypoints.conf[person_index].cpu().numpy()

        analysis = analyzer.analyze(points, scores)
        analysis["keypoints"] = self._serialize_keypoints(points, scores)
        return analysis

    def reset(self, exercise):
        """운동 변경 또는 UI 초기화 요청 시 해당 운동의 횟수와 상태를 초기화한다."""
        self._get_analyzer(exercise).reset()

    def _get_analyzer(self, exercise):
        """운동 코드에 맞는 분석기를 반환하고 잘못된 코드는 명확히 거부한다."""
        try:
            return self.analyzers[exercise]
        except KeyError as error:
            supported = ", ".join(sorted(self.analyzers))
            raise ValueError(
                f"지원하지 않는 운동입니다: {exercise}. "
                f"지원 운동: {supported}"
            ) from error

    @staticmethod
    def _serialize_keypoints(points, scores):
        """NumPy 관절 데이터를 UI가 다루기 쉬운 기본 Python 값으로 변환한다."""
        return [
            {
                "index": index,
                "x": float(point[0]),
                "y": float(point[1]),
                "confidence": float(scores[index]),
            }
            for index, point in enumerate(points)
        ]
