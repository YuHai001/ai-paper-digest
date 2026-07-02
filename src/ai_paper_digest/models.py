from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Paper:
    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    published: datetime
    updated: datetime
    url: str
    source: str = "arXiv"
    pdf_url: str | None = None
    doi: str | None = None
    primary_category: str | None = None
    categories: list[str] = field(default_factory=list)
    comment: str | None = None
    score: int = 0
    matched_terms: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PaperSummary:
    one_sentence: str
    research_category: str
    method_family: str
    study_type: str
    task_or_domain: str
    dataset_or_benchmark: str
    model_or_system: str
    evaluation_metrics: str
    main_contribution: str
    limitations: str
    why_it_matters: str

    @classmethod
    def fallback(cls, paper: Paper) -> "PaperSummary":
        abstract = " ".join(paper.abstract.split())
        if len(abstract) > 300:
            abstract = abstract[:297].rstrip() + "..."
        text = paper.title + " " + paper.abstract
        return cls(
            one_sentence=abstract or "摘要为空，需阅读原文确认主要贡献。",
            research_category=infer_research_category(text),
            method_family=infer_method_family(text),
            study_type=infer_study_type(text),
            task_or_domain=infer_task_or_domain(text),
            dataset_or_benchmark="摘要中未明确说明",
            model_or_system=infer_model_or_system(text),
            evaluation_metrics="摘要中未明确说明",
            main_contribution="基于标题和摘要，该论文与 AI/机器学习/大模型/具身智能相关，建议阅读全文确认方法细节和实验设置。",
            limitations="未进行全文解析，局限性需从正文判断。",
            why_it_matters="该条目被关键词、分类或重点期刊规则识别为相关，可作为每日跟踪候选。",
        )


def infer_research_category(text: str) -> str:
    lowered = text.lower()
    if not _has_ai_core(lowered):
        return "其他/相关性存疑"

    if any(term in lowered for term in ["embodied", "robot", "robotics", "manipulation", "locomotion", "humanoid", "sim-to-real", "world model"]):
        return "具身智能/机器人"
    if any(term in lowered for term in ["large language model", "llm", "foundation model", "pre-trained model", "pretrained model", "gpt", "language model"]):
        return "大模型/基础模型"
    if any(term in lowered for term in ["vision-language", "vision language", "multimodal", "multi-modal", "vlm", "image-text", "video-language"]):
        return "多模态/视觉语言"
    if any(term in lowered for term in ["alignment", "safety", "red teaming", "jailbreak", "hallucination", "rlhf", "constitutional ai", "trustworthy ai"]):
        return "AI安全与对齐"
    if any(term in lowered for term in ["reinforcement learning", "rl ", "policy gradient", "agent", "multi-agent", "planning", "decision making"]):
        return "强化学习/智能体"
    if any(term in lowered for term in ["natural language processing", "nlp", "translation", "question answering", "information retrieval", "retrieval-augmented", "rag"]):
        return "自然语言处理"
    if any(term in lowered for term in ["computer vision", "object detection", "segmentation", "image generation", "video generation", "diffusion model"]):
        return "计算机视觉/生成视觉"
    if any(term in lowered for term in ["learning theory", "generalization", "optimization theory", "sample complexity", "statistical learning"]):
        return "机器学习理论"
    if any(term in lowered for term in ["training system", "inference system", "accelerator", "distributed training", "serving", "quantization", "compression"]):
        return "AI系统与效率"
    if any(term in lowered for term in ["deep learning", "neural network", "transformer", "graph neural network", "representation learning"]):
        return "深度学习方法"
    return "机器学习方法"


def infer_method_family(text: str) -> str:
    lowered = text.lower()
    if "transformer" in lowered:
        return "Transformer"
    if "diffusion" in lowered:
        return "diffusion model"
    if "large language model" in lowered or "llm" in lowered:
        return "large language model"
    if "vision-language" in lowered or "vision language" in lowered or "vlm" in lowered:
        return "vision-language model"
    if "reinforcement learning" in lowered or "policy" in lowered:
        return "reinforcement learning"
    if "graph neural network" in lowered or "gnn" in lowered:
        return "graph neural network"
    if "retrieval-augmented" in lowered or "rag" in lowered:
        return "retrieval-augmented generation"
    if "neural network" in lowered or "deep learning" in lowered:
        return "deep neural network"
    if "machine learning" in lowered:
        return "machine learning"
    return "摘要中未明确说明"


def infer_study_type(text: str) -> str:
    lowered = text.lower()
    if "survey" in lowered or "review" in lowered:
        return "survey/review"
    if any(term in lowered for term in ["benchmark", "dataset", "leaderboard", "evaluation suite"]):
        return "benchmark/dataset"
    if any(term in lowered for term in ["empirical", "experiments", "evaluate", "evaluation", "outperforms", "state-of-the-art", "sota"]):
        return "empirical study"
    if any(term in lowered for term in ["theory", "theoretical", "proof", "bound", "convergence", "generalization"]):
        return "theory"
    if any(term in lowered for term in ["system", "serving", "training framework", "inference", "deployment"]):
        return "system"
    return "method"


def infer_task_or_domain(text: str) -> str:
    lowered = text.lower()
    domains = []
    for label, terms in [
        ("NLP", ["language", "nlp", "translation", "question answering", "retrieval"]),
        ("computer vision", ["vision", "image", "video", "segmentation", "detection"]),
        ("robotics", ["robot", "embodied", "manipulation", "locomotion", "navigation"]),
        ("multimodal", ["multimodal", "multi-modal", "vision-language", "audio", "speech"]),
        ("AI safety", ["safety", "alignment", "jailbreak", "hallucination"]),
        ("AI systems", ["training", "inference", "serving", "distributed", "accelerator"]),
    ]:
        if any(term in lowered for term in terms):
            domains.append(label)
    return ", ".join(dict.fromkeys(domains)) if domains else "摘要中未明确说明"


def infer_model_or_system(text: str) -> str:
    lowered = text.lower()
    names = []
    for name in ["gpt", "bert", "llama", "mistral", "gemini", "claude", "clip", "dino", "sam", "stable diffusion", "diffusion transformer"]:
        if name in lowered:
            names.append(name)
    if names:
        return ", ".join(names)
    if "large language model" in lowered or "llm" in lowered:
        return "LLM"
    if "foundation model" in lowered:
        return "foundation model"
    if "transformer" in lowered:
        return "Transformer"
    return "摘要中未明确说明"


def _has_ai_core(lowered: str) -> bool:
    core_phrases = [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "neural network",
        "large language model",
        "language model",
        "foundation model",
        "generative ai",
        "transformer",
        "diffusion model",
        "reinforcement learning",
        "computer vision",
        "natural language processing",
        "vision-language",
        "multimodal",
        "embodied ai",
        "robot learning",
        "retrieval-augmented generation",
    ]
    if any(term in lowered for term in core_phrases):
        return True
    abbreviations = [" llm", " gnn", " nlp", " rag", " rlhf", " vlm"]
    return any(term in f" {lowered}" for term in abbreviations)
