from __future__ import annotations

import unittest
import urllib.error
from datetime import UTC, datetime
from unittest.mock import patch

from ai_paper_digest.models import Paper
from ai_paper_digest.sources import (
    _deduplicate_papers,
    _fetch_journal_watchlist,
    _fetch_query_pages,
    _parse_crossref_work,
    _parse_openalex_work,
    _parse_semantic_scholar_paper,
)


class SourceParsingTests(unittest.TestCase):
    def test_parse_openalex_work_reconstructs_abstract(self) -> None:
        paper = _parse_openalex_work(
            {
                "id": "https://openalex.org/W123",
                "doi": "https://doi.org/10.1234/example",
                "display_name": "Large language model agents",
                "authorships": [{"author": {"display_name": "A. Researcher"}}],
                "publication_date": "2026-07-01",
                "updated_date": "2026-07-02T00:00:00Z",
                "primary_location": {
                    "landing_page_url": "https://doi.org/10.1234/example",
                    "pdf_url": "https://example.org/paper.pdf",
                    "source": {"display_name": "Example Journal"},
                },
                "abstract_inverted_index": {"Large": [0], "language": [1], "models": [2], "reason": [3]},
                "primary_topic": {"display_name": "Artificial Intelligence"},
                "type": "article",
            }
        )

        self.assertIsNotNone(paper)
        assert paper is not None
        self.assertEqual(paper.paper_id, "doi:10.1234/example")
        self.assertEqual(paper.source, "OpenAlex")
        self.assertEqual(paper.abstract, "Large language models reason")

    def test_parse_crossref_work_extracts_dates_and_authors(self) -> None:
        paper = _parse_crossref_work(
            {
                "DOI": "10.1234/example",
                "title": ["Embodied AI agents for robot manipulation"],
                "author": [{"given": "A.", "family": "Researcher"}],
                "abstract": "<jats:p>Large language model agents improve robotic planning.</jats:p>",
                "published-online": {"date-parts": [[2026, 7, 1]]},
                "deposited": {"date-time": "2026-07-02T00:00:00Z"},
                "URL": "https://doi.org/10.1234/example",
                "subject": ["Artificial Intelligence"],
                "type": "journal-article",
            }
        )

        self.assertIsNotNone(paper)
        assert paper is not None
        self.assertEqual(paper.authors, ["A. Researcher"])
        self.assertEqual(paper.abstract, "Large language model agents improve robotic planning.")
        self.assertEqual(paper.published, datetime(2026, 7, 1, tzinfo=UTC))

    def test_parse_semantic_scholar_prefers_doi_identifier(self) -> None:
        paper = _parse_semantic_scholar_paper(
            {
                "paperId": "abc",
                "title": "Retrieval-augmented generation for scientific assistants",
                "abstract": "A retrieval-augmented generation system improves factuality.",
                "authors": [{"name": "A. Researcher"}],
                "url": "https://www.semanticscholar.org/paper/abc",
                "publicationDate": "2026-07-01",
                "externalIds": {"DOI": "10.1234/example"},
                "publicationTypes": ["JournalArticle"],
                "venue": "Example Journal",
                "openAccessPdf": {"url": "https://example.org/paper.pdf"},
            }
        )

        self.assertIsNotNone(paper)
        assert paper is not None
        self.assertEqual(paper.paper_id, "doi:10.1234/example")
        self.assertEqual(paper.source, "Semantic Scholar")
        self.assertEqual(paper.pdf_url, "https://example.org/paper.pdf")

    def test_deduplicate_papers_merges_sources_by_doi(self) -> None:
        now = datetime(2026, 7, 2, tzinfo=UTC)
        first = Paper(
            paper_id="doi:10.1234/example",
            title="Large language model agents",
            authors=["A"],
            abstract="Short.",
            published=now,
            updated=now,
            url="https://doi.org/10.1234/example",
            source="OpenAlex",
            doi="10.1234/example",
        )
        second = Paper(
            paper_id="doi:10.1234/example",
            title="Large language model agents",
            authors=["A", "B"],
            abstract="Longer abstract about embodied AI and planning.",
            published=now,
            updated=now,
            url="https://doi.org/10.1234/example",
            source="Crossref",
            doi="10.1234/example",
            categories=["Artificial Intelligence"],
        )

        papers = _deduplicate_papers([first, second])

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].source, "OpenAlex + Crossref")
        self.assertEqual(papers[0].authors, ["A", "B"])
        self.assertEqual(papers[0].categories, ["Artificial Intelligence"])

    def test_fetch_journal_watchlist_queries_crossref_by_issn(self) -> None:
        response = {
            "message": {
                "items": [
                    {
                        "DOI": "10.1234/watch",
                        "title": ["Large language model agents in a machine learning journal"],
                        "author": [{"given": "A.", "family": "Researcher"}],
                        "abstract": "A large language model agent is reported.",
                        "published-online": {"date-parts": [[2026, 7, 1]]},
                        "URL": "https://doi.org/10.1234/watch",
                        "container-title": ["Journal of Machine Learning Research"],
                        "type": "journal-article",
                    }
                ]
            }
        }
        source_config = {
            "request_pause_seconds": 0,
            "journal_watchlist": {
                "max_results_per_journal": 3,
                "journals": [
                    {
                        "name": "Journal of Machine Learning Research",
                        "publisher": "JMLR",
                        "group": "ml-core",
                        "issn": ["1533-7928"],
                        "tags": ["machine learning"],
                    }
                ],
            },
        }

        with patch("ai_paper_digest.sources._get_json", return_value=response) as get_json:
            papers = _fetch_journal_watchlist(
                datetime(2026, 7, 1, tzinfo=UTC),
                datetime(2026, 7, 2, tzinfo=UTC),
                10,
                source_config,
            )

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].source, "Crossref + Journal Watchlist")
        self.assertIn("Journal of Machine Learning Research", papers[0].categories)
        self.assertIn("machine learning", papers[0].categories)
        params = get_json.call_args.args[1]
        self.assertIn("issn:1533-7928", params["filter"])

    def test_fetch_query_pages_skips_failed_query(self) -> None:
        def fetch_items(query: str, per_query: int) -> list[dict[str, object]]:
            if query == "bad":
                raise urllib.error.HTTPError("https://example.org", 429, "Too Many Requests", {}, None)
            return [
                {
                    "paperId": "abc",
                    "title": "Large language model agents",
                    "abstract": "A compact LLM agent is demonstrated.",
                    "authors": [{"name": "A. Researcher"}],
                    "url": "https://www.semanticscholar.org/paper/abc",
                    "publicationDate": "2026-07-01",
                    "externalIds": {"DOI": "10.1234/example"},
                }
            ]

        papers = _fetch_query_pages(["bad", "good"], 10, fetch_items, _parse_semantic_scholar_paper, 0)

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Large language model agents")
