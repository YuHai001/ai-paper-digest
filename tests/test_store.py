from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from ai_paper_digest.models import Paper, PaperSummary
from ai_paper_digest.store import PaperStore


class StoreTests(unittest.TestCase):
    def test_upsert_and_summary_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PaperStore(Path(tmpdir) / "papers.sqlite")
            now = datetime(2026, 1, 1, tzinfo=UTC)
            paper = Paper(
                paper_id="2601.00001",
                title="Large language model agents",
                authors=["A. Researcher"],
                abstract="An LLM agent solves planning tasks.",
                published=now,
                updated=now,
                url="https://arxiv.org/abs/2601.00001",
            )
            summary = PaperSummary(
                one_sentence="An LLM agent improves planning.",
                research_category="大模型/基础模型",
                method_family="large language model",
                study_type="empirical study",
                task_or_domain="robotics",
                dataset_or_benchmark="摘要中未明确说明",
                model_or_system="LLM",
                evaluation_metrics="摘要中未明确说明",
                main_contribution="Improves planning.",
                limitations="Needs full text.",
                why_it_matters="Useful for tracking progress.",
            )

            self.assertTrue(store.upsert_paper(paper))
            store.save_summary(paper.paper_id, summary)
            loaded = store.get_summary(paper.paper_id)
            store.close()

        self.assertEqual(loaded, summary)
