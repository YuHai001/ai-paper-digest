from __future__ import annotations

import unittest
from datetime import UTC, datetime

from ai_paper_digest.models import Paper, PaperSummary
from ai_paper_digest.report import render_report


class ReportTests(unittest.TestCase):
    def test_render_report_includes_core_sections(self) -> None:
        now = datetime(2026, 7, 2, 0, 30, tzinfo=UTC)
        paper = Paper(
            paper_id="2607.00001",
            title="Large language model agents for embodied reasoning",
            authors=["A. Researcher"],
            abstract="Example abstract.",
            published=now,
            updated=now,
            url="https://arxiv.org/abs/2607.00001",
            categories=["cs.AI"],
            score=8,
            matched_terms=["large language model"],
        )
        summary = PaperSummary(
            research_category="大模型/基础模型",
            one_sentence="This is a concise finding.",
            method_family="large language model",
            study_type="empirical study",
            task_or_domain="robotics",
            dataset_or_benchmark="摘要中未明确说明",
            model_or_system="LLM",
            evaluation_metrics="摘要中未明确说明",
            main_contribution="Improves embodied reasoning.",
            limitations="Needs full text.",
            why_it_matters="Useful for tracking progress.",
        )

        markdown = render_report([(paper, summary)], "AI/机器学习/大模型每日论文进展", now, "Asia/Shanghai")

        self.assertIn("# AI/机器学习/大模型每日论文进展 - 2026-07-02", markdown)
        self.assertIn("## 今日概览", markdown)
        self.assertIn("## 论文详情", markdown)
        self.assertIn("Large language model agents", markdown)
