from pathlib import Path

from .analyzers import SquatAnalyzer


class PoseService:
    def __init__(
        self,
        model_path=None,
        device="cuda:0",
        *,
        model=None,
        analyzers=None,
        confidence=0.5,
        image_size=640,
    ):
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
            else {"squat": SquatAnalyzer()}
        )

    def analyze_frame(self, frame, exercise):
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

        points = keypoints.xy[0].cpu().numpy()
        scores = keypoints.conf[0].cpu().numpy()
        analysis = analyzer.analyze(points, scores)
        analysis["keypoints"] = self._serialize_keypoints(points, scores)
        return analysis

    def reset(self, exercise):
        self._get_analyzer(exercise).reset()

    def _get_analyzer(self, exercise):
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
        return [
            {
                "index": index,
                "x": float(point[0]),
                "y": float(point[1]),
                "confidence": float(scores[index]),
            }
            for index, point in enumerate(points)
        ]
