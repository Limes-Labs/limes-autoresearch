import tomllib
import unittest
from pathlib import Path

import autoresearch_limes


class MetadataTests(unittest.TestCase):
    def test_package_version_matches_pyproject(self) -> None:
        data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(autoresearch_limes.__version__, data["project"]["version"])
        self.assertEqual(autoresearch_limes.__version__, "0.2.0")


if __name__ == "__main__":
    unittest.main()
