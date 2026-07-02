from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from .models import Paper, PaperSummary


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
SUMMARY_FIELDS = [
    "one_sentence",
    "research_category",
    "method_family",
    "study_type",
    "task_or_domain",
    "dataset_or_benchmark",
    "model_or_system",
    "evaluation_metrics",
    "main_contribution",
    "limitations",
    "why_it_matters",
]


class Summarizer:
    def summarize(self, paper: Paper) -> PaperSummary:
        raise NotImplementedError


class FallbackSummarizer(Summarizer):
    def summarize(self, paper: Paper) -> PaperSummary:
        return PaperSummary.fallback(paper)


class OpenAISummarizer(Summarizer):
    def __init__(self, api_key: str, model: str | None = None) -> None:
        self.api_key = api_key
        self.model = model or os.getenv("OPENAI_MODEL") or "gpt-5.5"

    def summarize(self, paper: Paper) -> PaperSummary:
        payload = {
            "model": self.model,
            "instructions": (
                "你是 AI、机器学习、深度学习、大模型和具身智能方向的文献助理。"
                "只根据用户提供的标题、作者、分类和摘要总结，不要编造摘要中没有的实验结果、数据集或指标。"
                "请先判断论文是否确实属于 AI/机器学习/深度学习/大模型/具身智能相关研究，"
                "依据包括 artificial intelligence、machine learning、deep learning、neural network、LLM、foundation model、"
                "transformer、diffusion model、reinforcement learning、multimodal、vision-language、embodied AI、robot learning 等核心证据。"
                "如果核心相关性不足，将 research_category 写为‘其他/相关性存疑’。"
                "若核心相关性成立，再将 research_category 归为以下之一：大模型/基础模型、深度学习方法、机器学习理论、"
                "多模态/视觉语言、自然语言处理、计算机视觉/生成视觉、强化学习/智能体、具身智能/机器人、"
                "AI安全与对齐、AI系统与效率、机器学习方法、其他。"
                "method_family 应描述核心方法族，例如 Transformer、LLM、diffusion model、reinforcement learning、GNN、RAG、deep neural network。"
                "task_or_domain 写任务或应用领域；dataset_or_benchmark 写摘要明确提到的数据集/基准；"
                "model_or_system 写摘要明确提到的模型、系统或框架；evaluation_metrics 写摘要明确提到的指标。"
                "输出必须是 JSON 对象，字段固定为："
                + ", ".join(SUMMARY_FIELDS)
                + "。如果摘要未提供某项信息，写“摘要中未明确说明”。"
            ),
            "input": _build_input(paper),
        }
        request = urllib.request.Request(
            OPENAI_RESPONSES_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = _extract_output_text(data)
        return _summary_from_json(text, paper)


def make_summarizer(use_openai: bool = True) -> Summarizer:
    api_key = os.getenv("OPENAI_API_KEY")
    if use_openai and api_key:
        return OpenAISummarizer(api_key=api_key)
    return FallbackSummarizer()


def _build_input(paper: Paper) -> str:
    return "\n".join(
        [
            f"Title: {paper.title}",
            f"Authors: {', '.join(paper.authors)}",
            f"Paper ID: {paper.paper_id}",
            f"Source: {paper.source}",
            f"Categories: {', '.join(paper.categories)}",
            f"Published: {paper.published.isoformat()}",
            f"Updated: {paper.updated.isoformat()}",
            "",
            "Abstract:",
            paper.abstract,
        ]
    )


def _extract_output_text(data: dict[str, Any]) -> str:
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    chunks = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks)


def _summary_from_json(text: str, paper: Paper) -> PaperSummary:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return PaperSummary.fallback(paper)
    values = {field: _string_or_default(payload.get(field)) for field in SUMMARY_FIELDS}
    return PaperSummary(**values)


def _string_or_default(value: object) -> str:
    if value is None:
        return "摘要中未明确说明"
    if isinstance(value, str):
        return value.strip() or "摘要中未明确说明"
    return json.dumps(value, ensure_ascii=False)
