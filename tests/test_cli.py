import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from intune_doc.cli import ExportCommandOptions, parse_args  # noqa: E402
from intune_doc.reports.cli import SUPPORTED_FORMATS  # noqa: E402
from intune_doc.reports.schema import DEFAULT_REPORT_SCOPE  # noqa: E402


class TestCliParsing(unittest.TestCase):
    def test_parse_args_defaults(self) -> None:
        options = parse_args(["export"])

        self.assertIsInstance(options, ExportCommandOptions)
        self.assertEqual(options.formats, list(SUPPORTED_FORMATS))
        self.assertEqual(options.audience, "client")
        self.assertEqual(options.scope, DEFAULT_REPORT_SCOPE)
        self.assertEqual(options.output, "intune-report")

    def test_parse_args_combines_formats(self) -> None:
        options = parse_args(["export", "--format", "word,excel", "--format", "pdf"])

        self.assertEqual(options.formats, ["word", "excel", "pdf"])

    def test_parse_args_rejects_invalid_formats(self) -> None:
        with self.assertRaises(ValueError):
            parse_args(["export", "--format", "not-a-format"])

    def test_parse_args_requires_command(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args([])


if __name__ == "__main__":
    unittest.main()
