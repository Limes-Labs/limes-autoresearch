import unittest

from autoresearch_limes.backends import detect_backends


class BackendDetectionTests(unittest.TestCase):
    def test_detects_optional_backends_without_required_dependencies(self) -> None:
        report = detect_backends()

        self.assertIn(report.preferred, {"cpu", "mps", "cuda", "mlx"})
        self.assertIsInstance(report.torch_available, bool)
        self.assertIsInstance(report.torch_mps_available, bool)
        self.assertIsInstance(report.mlx_available, bool)
        self.assertTrue(report.python_version)


if __name__ == "__main__":
    unittest.main()
