from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ai_paper_digest import cli
from ai_paper_digest.sources import FetchResult


class CliTests(unittest.TestCase):
    def test_allow_fetch_failure_renders_warning_report(self) -> None:
        stdout = io.StringIO()
        with patch("ai_paper_digest.cli.fetch_recent_papers", side_effect=RuntimeError("source down")):
            with redirect_stdout(stdout):
                exit_code = cli.main(["--allow-fetch-failure", "--dry-run", "--no-openai"])

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("## 数据源告警", output)
        self.assertIn("论文数据源暂时不可用", output)

    def test_source_warnings_are_rendered(self) -> None:
        stdout = io.StringIO()
        with patch(
            "ai_paper_digest.cli.fetch_recent_papers",
            return_value=FetchResult(papers=[], warnings=["OpenAlex 暂时不可用"]),
        ):
            with redirect_stdout(stdout):
                exit_code = cli.main(["--dry-run", "--no-openai"])

        self.assertEqual(exit_code, 0)
        self.assertIn("OpenAlex 暂时不可用", stdout.getvalue())
