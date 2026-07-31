import unittest

import numpy as np

from src.workout_pose_checker.analyzers.pushup import (
    CONFIRM_FRAMES,
    PushupAnalyzer,
    VIEW_CONFIRM_FRAMES,
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


def make_front_pose(left_arm, right_arm):
    points = np.zeros((17, 2), dtype=float)
    scores = np.full(17, 0.1, dtype=float)

    positions = {
        5: left_arm[0],
        7: left_arm[1],
        9: left_arm[2],
        6: right_arm[0],
        8: right_arm[1],
        10: right_arm[2],
        11: (-1, 2),
        12: (1, 2),
    }
    for index, point in positions.items():
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
FRONT_TOP_POSE = make_front_pose(
    left_arm=((-1, 0), (-2, 0), (-3, 0)),
    right_arm=((1, 0), (2, 0), (3, 0)),
)
FRONT_BOTTOM_POSE = make_front_pose(
    left_arm=((-1, 0), (-2, 0), (-2, 1)),
    right_arm=((1, 0), (2, 0), (2, 1)),
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

    def test_counts_front_view_pushup_using_both_arms(self):
        analyzer = PushupAnalyzer()

        for _ in range(CONFIRM_FRAMES):
            analyzer.analyze(*FRONT_BOTTOM_POSE)
        for _ in range(CONFIRM_FRAMES):
            result = analyzer.analyze(*FRONT_TOP_POSE)

        self.assertEqual(result["side"], "FRONT")
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["success_count"], 1)
        self.assertAlmostEqual(result["metrics"]["left_elbow_angle"], 180)
        self.assertAlmostEqual(result["metrics"]["right_elbow_angle"], 180)

    def test_uses_side_view_when_both_arms_are_not_visible(self):
        analyzer = PushupAnalyzer()

        result = analyzer.analyze(*TOP_POSE)

        self.assertEqual(result["side"], "L")
        self.assertIsNone(result["metrics"]["front_view_ratio"])

    def test_switches_from_front_to_side_after_confirmed_frames(self):
        analyzer = PushupAnalyzer()
        analyzer.analyze(*FRONT_TOP_POSE)

        for _ in range(VIEW_CONFIRM_FRAMES - 1):
            result = analyzer.analyze(*TOP_POSE)
            self.assertEqual(result["side"], "FRONT")

        result = analyzer.analyze(*TOP_POSE)

        self.assertEqual(result["side"], "L")
        self.assertEqual(analyzer.current_view, "SIDE")

    def test_does_not_switch_view_after_one_noisy_frame(self):
        analyzer = PushupAnalyzer()
        analyzer.analyze(*FRONT_TOP_POSE)

        noisy_result = analyzer.analyze(*TOP_POSE)
        stable_result = analyzer.analyze(*FRONT_TOP_POSE)

        self.assertEqual(noisy_result["side"], "FRONT")
        self.assertEqual(stable_result["side"], "FRONT")
        self.assertEqual(analyzer.current_view, "FRONT")

    def test_view_switch_cancels_only_in_progress_rep(self):
        analyzer = PushupAnalyzer()
        analyzer.success_count = 2
        analyzer.analyze(*FRONT_BOTTOM_POSE)
        self.assertTrue(analyzer.rep_in_progress)

        for _ in range(VIEW_CONFIRM_FRAMES):
            analyzer.analyze(*TOP_POSE)

        self.assertEqual(analyzer.current_view, "SIDE")
        self.assertFalse(analyzer.rep_in_progress)
        self.assertEqual(analyzer.success_count, 2)

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
