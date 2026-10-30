import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from core.command_builders import ExtractFramesCommandBuilder


# Simulate video input so these tests do not depend on installed video codecs.
script = Path(__file__).resolve().parents[1] / "scripts" / "extract_frames.py"
spec = importlib.util.spec_from_file_location("extract_frames", script)
extract_frames = importlib.util.module_from_spec(spec)
with patch.dict("sys.modules", {"cv2": Mock()}):
    spec.loader.exec_module(extract_frames)


class FrameLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cv2 = Mock()
        self.cv2.imwrite.return_value = True
        self.patch = patch.object(extract_frames, "cv2", self.cv2)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def video(self, frame_count):
        capture = Mock()
        capture.isOpened.return_value = True
        capture.get.return_value = frame_count
        capture.read.side_effect = [(True, object()) for _ in range(frame_count)] + [(False, None)]
        return capture

    def extract(self, frame_count=10, **options):
        capture = self.video(frame_count)
        self.cv2.VideoCapture.return_value = capture
        extractor = extract_frames.FrameExtractor(self.root / "clip.mp4", self.root / "out", **options)
        extractor._extract_from_video(str(self.root / "clip.mp4"), str(self.root / "out"))
        capture.release.assert_called_once()
        return capture

    def test_positive_limit_stops_at_maximum(self):
        capture = self.extract(max_photos=3)
        self.assertEqual(self.cv2.imwrite.call_count, 3)
        self.assertEqual(capture.read.call_count, 3)

    def test_zero_and_default_keep_all_frames(self):
        self.extract(frame_count=4)
        self.assertEqual(self.cv2.imwrite.call_count, 4)
        self.cv2.imwrite.reset_mock()
        self.extract(frame_count=4, max_photos=0)
        self.assertEqual(self.cv2.imwrite.call_count, 4)

    def test_limit_respects_every_nth_frame(self):
        self.extract(every_n=2, max_photos=3)
        names = [Path(call.args[0]).name for call in self.cv2.imwrite.call_args_list]
        self.assertEqual(names, ["frame_000000.jpg", "frame_000002.jpg", "frame_000004.jpg"])

    def test_short_video_stops_at_end(self):
        self.extract(frame_count=2, max_photos=5)
        self.assertEqual(self.cv2.imwrite.call_count, 2)

    def test_dry_run_respects_limit_without_writing(self):
        capture = self.extract(max_photos=2, dry_run=True)
        self.assertEqual(capture.read.call_count, 2)
        self.cv2.imwrite.assert_not_called()
        self.assertFalse((self.root / "out").exists())

    def test_failed_write_does_not_count_toward_limit(self):
        self.cv2.imwrite.side_effect = [False, True, True]
        capture = self.extract(max_photos=2)
        self.assertEqual(capture.read.call_count, 3)

    def test_limit_resets_for_each_video(self):
        self.cv2.VideoCapture.side_effect = [self.video(5), self.video(5)]
        extractor = extract_frames.FrameExtractor(self.root, self.root / "out", max_photos=2)
        extractor._get_video_files = Mock(return_value=[str(self.root / "a.mp4"), str(self.root / "b.mp4")])
        extractor.run()
        self.assertEqual(self.cv2.imwrite.call_count, 4)
        folders = [Path(call.args[0]).parent.name for call in self.cv2.imwrite.call_args_list]
        self.assertEqual(folders, ["a", "a", "b", "b"])

    def test_command_builder_passes_positive_limit(self):
        command = ExtractFramesCommandBuilder.build({"max_photos": "25", "every_n": 2})
        self.assertEqual(command[command.index("--max_photos") + 1], "25")
        self.assertEqual(command[command.index("--every_n") + 1], "2")

    def test_command_builder_omits_unlimited_or_invalid_limit(self):
        for value in (0, -1, "invalid", None):
            with self.subTest(value=value):
                command = ExtractFramesCommandBuilder.build({"max_photos": value})
                self.assertNotIn("--max_photos", command)


if __name__ == "__main__":
    unittest.main()
