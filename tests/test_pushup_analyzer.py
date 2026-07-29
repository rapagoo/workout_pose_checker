import unittest

import numpy as np

from src.workout_pose_checker.analyzers.pushup import (
    CONFIRM_FRAMES,
    PushupAnalyzer,
)


def make_pose(shoulder, elbow, wrist, hip, ankle):
    points = np.zeros((17, 2), dtype=float)
    scores = np.full(17, 0.1, dtype=float)

    indexes = (5, 7, 9, 11, 15)
    positions = (shoulder, elbow, wrist, hip, ankle)
    for index, point in zip(indexes, positions):
        points[index] = point
        scores[index] = 0.9

    return points, scores


TOP_POSE = make_pose(
    shoulder=(0, 0),
    elbow=(1, 0),
    wrist=(2, 0),
    hip=(0, 1),
    ankle=(0, 2),
)
BOTTOM_POSE = make_pose(
    shoulder=(0, 0),
    elbow=(1, 0),
    wrist=(1, 1),
    hip=(0, 1),
    ankle=(0, 2),
)
PARTIAL_POSE = make_pose(
    shoulder=(0, 0),
    elbow=(1, 0),
    wrist=(2, 1),
    hip=(0, 1),
    ankle=(0, 2),
)
BENT_BODY_POSE = make_pose(
    shoulder=(0, 0),
    elbow=(1, 0),
    wrist=(1, 1),
    hip=(0, 1),
    ankle=(1, 1),
)


class PushupAnalyzerTest(unittest.TestCase):
    def test_counts_success_after_confirmed_bottom_and_top(self):
        analyzer = PushupAnalyzer()

        for _ in range(CONFIRM_FRAMES):
            analyzer.analyze(*BOTTOM_POSE)
        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*TOP_POSE)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["success_count"], 1)

    def test_does_not_count_shallow_movement(self):
        analyzer = PushupAnalyzer()

        analyzer.analyze(*PARTIAL_POSE)
        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*TOP_POSE)

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["success_count"], 0)

    def test_prompts_user_to_go_up_after_confirmed_bottom(self):
        analyzer = PushupAnalyzer()

        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*BOTTOM_POSE)

        self.assertEqual(result["status"], "GO_UP")

    def test_warns_when_body_is_not_straight(self):
        analyzer = PushupAnalyzer()

        result = analyzer.analyze(*BENT_BODY_POSE)

        self.assertEqual(result["status"], "KEEP_BODY_STRAIGHT")
        self.assertEqual(result["success_count"], 0)

    def test_reports_when_required_joints_are_not_visible(self):
        analyzer = PushupAnalyzer()
        points, scores = TOP_POSE
        scores = np.full_like(scores, 0.1)

        result = analyzer.analyze(points, scores)

        self.assertFalse(result["detected"])
        self.assertEqual(result["status"], "JOINTS_NOT_VISIBLE")

    def test_reset_clears_state_and_counts(self):
        analyzer = PushupAnalyzer()
        analyzer.success_count = 2
        analyzer.rep_in_progress = True

        analyzer.reset()

        self.assertEqual(analyzer.success_count, 0)
        self.assertFalse(analyzer.rep_in_progress)
        self.assertEqual(analyzer.status, "READY")


if __name__ == "__main__":
    unittest.main()
