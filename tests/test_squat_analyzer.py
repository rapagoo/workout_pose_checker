import unittest

import numpy as np

from src.workout_pose_checker.analyzers.squat import (
    CONFIRM_FRAMES,
    SquatAnalyzer,
)


def make_pose(shoulder, hip, knee, ankle):
    points = np.zeros((17, 2), dtype=float)
    scores = np.full(17, 0.1, dtype=float)

    for index, point in zip((5, 11, 13, 15), (shoulder, hip, knee, ankle)):
        points[index] = point
        scores[index] = 0.9

    return points, scores


STANDING_POSE = make_pose(
    shoulder=(0, 0),
    hip=(0, 1),
    knee=(0, 2),
    ankle=(0, 3),
)
BOTTOM_POSE = make_pose(
    shoulder=(0, 0),
    hip=(0, 1),
    knee=(1, 1),
    ankle=(1, 2),
)
PARTIAL_POSE = make_pose(
    shoulder=(0, 0),
    hip=(0, 1),
    knee=(1, 2),
    ankle=(1, 3),
)


class SquatAnalyzerTest(unittest.TestCase):
    def test_counts_success_after_confirmed_bottom_and_standing(self):
        analyzer = SquatAnalyzer()

        for _ in range(CONFIRM_FRAMES):
            analyzer.analyze(*BOTTOM_POSE)
        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*STANDING_POSE)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["success_count"], 1)
        self.assertEqual(result["failure_count"], 0)

    def test_returns_to_ready_without_counting_shallow_movement(self):
        analyzer = SquatAnalyzer()

        analyzer.analyze(*PARTIAL_POSE)
        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*STANDING_POSE)

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["success_count"], 0)
        self.assertEqual(result["failure_count"], 0)

    def test_prompts_user_to_go_down_after_movement_starts(self):
        analyzer = SquatAnalyzer()

        result = analyzer.analyze(*PARTIAL_POSE)

        self.assertEqual(result["status"], "GO_DOWN")

    def test_prompts_user_to_go_up_after_confirmed_bottom(self):
        analyzer = SquatAnalyzer()

        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*BOTTOM_POSE)

        self.assertEqual(result["status"], "GO_UP")

    def test_reset_clears_state_and_counts(self):
        analyzer = SquatAnalyzer()
        analyzer.success_count = 2
        analyzer.failure_count = 1
        analyzer.rep_in_progress = True

        analyzer.reset()

        self.assertEqual(analyzer.success_count, 0)
        self.assertEqual(analyzer.failure_count, 0)
        self.assertFalse(analyzer.rep_in_progress)
        self.assertEqual(analyzer.status, "READY")


if __name__ == "__main__":
    unittest.main()
