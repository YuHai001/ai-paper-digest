from __future__ import annotations

import re
from typing import Any

from .models import Paper


def rank_papers(papers: list[Paper], ranking_config: dict[str, Any]) -> list[Paper]:
    minimum_score = int(ranking_config.get("minimum_score", 0))
    ranked = []
    for paper in papers:
        score, matched_terms = score_paper(paper, ranking_config)
        paper.score = score
        paper.matched_terms = matched_terms
        if score >= minimum_score:
            ranked.append(paper)
    return sorted(ranked, key=lambda paper: (paper.score, paper.updated), reverse=True)


def score_paper(paper: Paper, ranking_config: dict[str, Any]) -> tuple[int, list[str]]:
    title = paper.title.lower()
    abstract = paper.abstract.lower()
    categories = " ".join(paper.categories).lower()
    matched_terms: list[str] = []

    for term in ranking_config.get("exclude_terms", []):
        if _contains(title, term) or _contains(abstract, term):
            return -10, [f"excluded:{term}"]

    score = 0
    for term in ranking_config.get("strong_terms", []):
        title_hit = _contains(title, term)
        abstract_hit = _contains(abstract, term)
        if title_hit:
            score += 5
            matched_terms.append(term)
        elif abstract_hit:
            score += 3
            matched_terms.append(term)

    for term in ranking_config.get("support_terms", []):
        title_hit = _contains(title, term)
        abstract_hit = _contains(abstract, term)
        if title_hit:
            score += 2
            matched_terms.append(term)
        elif abstract_hit:
            score += 1
            matched_terms.append(term)

    if "physics.plasm-ph" in categories:
        score += 2
    if "physics.acc-ph" in categories:
        score += 1

    unique_terms = list(dict.fromkeys(matched_terms))
    return score, unique_terms


def _contains(text: str, term: str) -> bool:
    lowered = term.lower().strip().strip('"')
    if not lowered:
        return False
    if re.fullmatch(r"[a-z0-9+.-]+", lowered):
        return re.search(rf"\b{re.escape(lowered)}\b", text) is not None
    return lowered in text
