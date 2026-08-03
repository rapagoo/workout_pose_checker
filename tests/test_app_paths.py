import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from src.workout_pose_checker.app_paths import (
    MODEL_FILENAME,
    get_application_root,
    get_model_path,
)


class AppPathsTest(unittest.TestCase):
    def test_uses_project_root_when_running_from_source(self):
        expected = Path(__file__).resolve().parents[1]

        with patch.object(sys, "frozen", False, create=True):
            self.assertEqual(get_application_root(), expected)
            self.assertEqual(
                get_model_path(),
                expected / "models" / MODEL_FILENAME,
            )

    def test_uses_executable_folder_when_frozen(self):
        executable = Path("C:/release/WorkoutPoseChecker.exe")

        with (
            patch.object(sys, "frozen", True, create=True),
            patch.object(sys, "executable", str(executable)),
        ):
            self.assertEqual(
                get_application_root(),
                executable.resolve().parent,
            )
            self.assertEqual(
                get_model_path(),
                executable.resolve().parent / "models" / MODEL_FILENAME,
            )


if __name__ == "__main__":
    unittest.main()
