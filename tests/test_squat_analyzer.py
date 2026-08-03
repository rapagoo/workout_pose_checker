import unittest

import numpy as np

from src.workout_pose_checker.analyzers.squat import (
    CONFIRM_FRAMES,
    SquatAnalyzer,
    VIEW_CONFIRM_FRAMES,
)


def make_pose(shoulder, hip, knee, ankle):
    points = np.zeros((17, 2), dtype=float)
    scores = np.full(17, 0.1, dtype=float)

    for index, point in zip((5, 11, 13, 15), (shoulder, hip, knee, ankle)):
        points[index] = point
        scores[index] = 0.9

    return points, scores


def make_front_pose(left_side, right_side):
    points = np.zeros((17, 2), dtype=float)
    scores = np.full(17, 0.1, dtype=float)

    for indexes, positions in (
        ((5, 11, 13, 15), left_side),
        ((6, 12, 14, 16), right_side),
    ):
        for index, point in zip(indexes, positions):
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
FRONT_STANDING_POSE = make_front_pose(
    left_side=((-1, 0), (-1, 2), (-1, 4), (-1, 6)),
    right_side=((1, 0), (1, 2), (1, 4), (1, 6)),
)
FRONT_BOTTOM_POSE = make_front_pose(
    left_side=((-1, 0), (-1, 2), (-2, 2), (-2, 4)),
    right_side=((1, 0), (1, 2), (2, 2), (2, 4)),
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

    def test_returns_to_ready_without_counting_shallow_movement(self):
        analyzer = SquatAnalyzer()

        analyzer.analyze(*PARTIAL_POSE)
        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*STANDING_POSE)

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["success_count"], 0)

    def test_prompts_user_to_go_down_after_movement_starts(self):
        analyzer = SquatAnalyzer()

        result = analyzer.analyze(*PARTIAL_POSE)

        self.assertEqual(result["status"], "GO_DOWN")

    def test_prompts_user_to_go_up_after_confirmed_bottom(self):
        analyzer = SquatAnalyzer()

        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*BOTTOM_POSE)

        self.assertEqual(result["status"], "GO_UP")

    def test_counts_front_view_squat_using_both_legs(self):
        analyzer = SquatAnalyzer()

        for _ in range(CONFIRM_FRAMES):
            analyzer.analyze(*FRONT_BOTTOM_POSE)
        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*FRONT_STANDING_POSE)

        self.assertEqual(result["side"], "FRONT")
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["success_count"], 1)
        self.assertAlmostEqual(result["metrics"]["left_knee_angle"], 180)
        self.assertAlmostEqual(result["metrics"]["right_knee_angle"], 180)

    def test_uses_side_view_when_both_legs_are_not_visible(self):
        analyzer = SquatAnalyzer()

        result = analyzer.analyze(*STANDING_POSE)

        self.assertEqual(result["side"], "L")
        self.assertIsNone(result["metrics"]["front_view_ratio"])

    def test_switches_from_front_to_side_after_confirmed_frames(self):
        analyzer = SquatAnalyzer()
        analyzer.analyze(*FRONT_STANDING_POSE)

        for _ in range(VIEW_CONFIRM_FRAMES - 1):
            result = analyzer.analyze(*STANDING_POSE)
            self.assertEqual(result["side"], "FRONT")

        result = analyzer.analyze(*STANDING_POSE)

        self.assertEqual(result["side"], "L")
        self.assertEqual(analyzer.current_view, "SIDE")

    def test_does_not_switch_view_after_one_noisy_frame(self):
        analyzer = SquatAnalyzer()
        analyzer.analyze(*FRONT_STANDING_POSE)

        noisy_result = analyzer.analyze(*STANDING_POSE)
        stable_result = analyzer.analyze(*FRONT_STANDING_POSE)

        self.assertEqual(noisy_result["side"], "FRONT")
        self.assertEqual(stable_result["side"], "FRONT")
        self.assertEqual(analyzer.current_view, "FRONT")

    def test_view_switch_cancels_only_in_progress_rep(self):
        analyzer = SquatAnalyzer()
        analyzer.success_count = 2
        analyzer.analyze(*FRONT_BOTTOM_POSE)
        self.assertTrue(analyzer.rep_in_progress)

        for _ in range(VIEW_CONFIRM_FRAMES):
            analyzer.analyze(*STANDING_POSE)

        self.assertEqual(analyzer.current_view, "SIDE")
        self.assertFalse(analyzer.rep_in_progress)
        self.assertEqual(analyzer.success_count, 2)

    def test_reset_clears_state_and_counts(self):
        analyzer = SquatAnalyzer()
        analyzer.success_count = 2
        analyzer.rep_in_progress = True

        analyzer.reset()

        self.assertEqual(analyzer.success_count, 0)
        self.assertFalse(analyzer.rep_in_progress)
        self.assertEqual(analyzer.status, "READY")


if __name__ == "__main__":
    unittest.main()
