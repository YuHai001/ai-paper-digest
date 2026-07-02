from __future__ import annotations

import unittest
from datetime import UTC, datetime

from ai_paper_digest.models import Paper
from ai_paper_digest.ranking import rank_papers, score_paper


CONFIG = {
    "strong_terms": ["large language model", "embodied ai"],
    "support_terms": ["agent", "planning", "benchmark"],
    "exclude_terms": ["classical database"],
    "minimum_score": 4,
}


def make_paper(title: str, abstract: str) -> Paper:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return Paper(
        paper_id="2601.00001",
        title=title,
        authors=["A. Researcher"],
        abstract=abstract,
        published=now,
        updated=now,
        url="https://arxiv.org/abs/2601.00001",
        categories=["cs.AI"],
    )


class RankingTests(unittest.TestCase):
    def test_score_paper_rewards_relevant_terms(self) -> None:
        paper = make_paper(
            "Large language model agents for embodied AI",
            "The agent improves planning benchmark performance.",
        )

        score, terms = score_paper(paper, CONFIG)

        self.assertGreaterEqual(score, 10)
        self.assertIn("large language model", terms)
        self.assertIn("embodied ai", terms)

    def test_rank_papers_filters_excluded_topics(self) -> None:
        relevant = make_paper("Large language model agents", "An LLM agent solves planning tasks.")
        excluded = make_paper("Classical database indexing", "This classical database paper is unrelated to AI models.")

        ranked = rank_papers([excluded, relevant], CONFIG)

        self.assertEqual([paper.title for paper in ranked], ["Large language model agents"])
