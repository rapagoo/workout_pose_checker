import unittest

import numpy as np

from src.workout_pose_checker.pose_renderer import draw_pose


class PoseRendererTest(unittest.TestCase):
    def test_draws_visible_keypoints_and_connection(self):
        frame = np.zeros((60, 60, 3), dtype=np.uint8)
        keypoints = [
            {"index": 5, "x": 15, "y": 30, "confidence": 0.9},
            {"index": 6, "x": 45, "y": 30, "confidence": 0.9},
        ]

        result = draw_pose(frame, keypoints)

        self.assertIs(result, frame)
        self.assertTrue(np.any(frame[30, 20:40] != 0))
        np.testing.assert_array_equal(frame[30, 15], [0, 0, 255])
        np.testing.assert_array_equal(frame[30, 45], [0, 0, 255])

    def test_ignores_keypoints_below_confidence_threshold(self):
        frame = np.zeros((30, 30, 3), dtype=np.uint8)
        keypoints = [
            {"index": 0, "x": 15, "y": 15, "confidence": 0.49},
        ]

        draw_pose(frame, keypoints)

        self.assertFalse(np.any(frame))

    def test_accepts_empty_keypoints(self):
        frame = np.zeros((30, 30, 3), dtype=np.uint8)

        draw_pose(frame, [])

        self.assertFalse(np.any(frame))


if __name__ == "__main__":
    unittest.main()
