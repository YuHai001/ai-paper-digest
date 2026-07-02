from __future__ import annotations

import unittest

from ai_paper_digest.models import infer_method_family, infer_model_or_system, infer_research_category, infer_study_type, infer_task_or_domain


class ModelInferenceTests(unittest.TestCase):
    def test_infers_large_model_and_multimodal_categories(self) -> None:
        self.assertEqual(infer_research_category("A large language model with tool use and reasoning"), "大模型/基础模型")
        self.assertEqual(infer_method_family("retrieval-augmented generation for language models"), "retrieval-augmented generation")
        self.assertEqual(infer_model_or_system("LLaMA and CLIP are used for a vision-language task"), "llama, clip")

    def test_infers_embodied_ai_and_study_types(self) -> None:
        self.assertEqual(infer_research_category("Embodied AI for robot manipulation with sim-to-real transfer"), "具身智能/机器人")
        self.assertEqual(infer_task_or_domain("robot manipulation and navigation using vision-language policies"), "NLP, computer vision, robotics, multimodal")
        self.assertEqual(infer_study_type("A benchmark dataset and evaluation suite for LLM agents"), "benchmark/dataset")

    def test_filters_unrelated_uses_of_ai(self) -> None:
        self.assertEqual(infer_research_category("AI alloy phase design using thermodynamic screening"), "其他/相关性存疑")
