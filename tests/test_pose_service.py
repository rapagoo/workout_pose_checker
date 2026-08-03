import unittest

import numpy as np

from src.workout_pose_checker.pose_service import PoseService


class FakeTensor:
    def __init__(self, value):
        self.value = np.asarray(value)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, index):
        return FakeTensor(self.value[index])

    def cpu(self):
        return self

    def numpy(self):
        return self.value


class FakeKeypoints:
    def __init__(self, points=None, scores=None):
        self.xy = FakeTensor(points if points is not None else [])
        self.conf = None if scores is None else FakeTensor(scores)


class FakeBoxes:
    def __init__(self, boxes=None):
        self.xyxy = FakeTensor(boxes if boxes is not None else [])


class FakeResult:
    def __init__(self, keypoints, boxes=None):
        self.keypoints = keypoints
        self.boxes = FakeBoxes(boxes)


class FakeModel:
    def __init__(self, result):
        self.result = result

    def predict(self, **kwargs):
        return [self.result]


class FakeAnalyzer:
    def __init__(self):
        self.reset()

    def analyze(self, points, scores):
        self.last_points = points
        self.last_scores = scores
        return self._result(True)

    def person_not_found(self):
        return self._result(False, "PERSON_NOT_FOUND")

    def reset(self):
        self.reset_called = True

    @staticmethod
    def _result(detected, status="READY"):
        return {
            "detected": detected,
            "exercise": "squat",
            "status": status,
            "success_count": 0,
            "side": None,
            "metrics": {},
            "error": None,
        }


class PoseServiceTest(unittest.TestCase):
    def test_registers_squat_and_pushup_by_default(self):
        service = PoseService(
            model=FakeModel(FakeResult(FakeKeypoints())),
        )

        self.assertEqual(
            set(service.analyzers),
            {"squat", "pushup"},
        )

    def test_analyzes_largest_detected_person_and_serializes_keypoints(self):
        points = np.zeros((2, 17, 2), dtype=float)
        points[0, :, :] = 10
        points[1, :, :] = 20
        scores = np.full((2, 17), 0.9, dtype=float)
        boxes = np.array(
            [
                [0, 0, 100, 100],
                [0, 0, 300, 400],
            ],
            dtype=float,
        )
        analyzer = FakeAnalyzer()
        service = PoseService(
            model=FakeModel(
                FakeResult(FakeKeypoints(points, scores), boxes)
            ),
            analyzers={"squat": analyzer},
        )

        result = service.analyze_frame(np.zeros((2, 2, 3)), "squat")

        self.assertTrue(result["detected"])
        self.assertEqual(len(result["keypoints"]), 17)
        self.assertEqual(result["keypoints"][0]["confidence"], 0.9)
        np.testing.assert_array_equal(analyzer.last_points, points[1])

    def test_returns_person_not_found_when_keypoints_are_empty(self):
        analyzer = FakeAnalyzer()
        service = PoseService(
            model=FakeModel(FakeResult(FakeKeypoints())),
            analyzers={"squat": analyzer},
        )

        result = service.analyze_frame(np.zeros((2, 2, 3)), "squat")

        self.assertFalse(result["detected"])
        self.assertEqual(result["status"], "PERSON_NOT_FOUND")
        self.assertEqual(result["keypoints"], [])

    def test_rejects_unsupported_exercise(self):
        service = PoseService(
            model=FakeModel(FakeResult(FakeKeypoints())),
            analyzers={"squat": FakeAnalyzer()},
        )

        with self.assertRaisesRegex(ValueError, "pushup"):
            service.analyze_frame(np.zeros((2, 2, 3)), "pushup")

    def test_reset_delegates_to_selected_analyzer(self):
        analyzer = FakeAnalyzer()
        analyzer.reset_called = False
        service = PoseService(
            model=FakeModel(FakeResult(FakeKeypoints())),
            analyzers={"squat": analyzer},
        )

        service.reset("squat")

        self.assertTrue(analyzer.reset_called)


if __name__ == "__main__":
    unittest.main()
