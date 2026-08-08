from __future__ import annotations

import re
from dataclasses import dataclass

HIGH_PRECISION_PATTERNS = {
    "generative_ai": [r"\bgenerative ai\b", r"\bgenai\b", r"\blarge language model(?:s)?\b", r"\bllm(?:s)?\b"],
    "machine_learning": [r"\bmachine learning\b", r"\bdeep learning\b", r"\bneural network(?:s)?\b"],
    "nlp": [r"\bnatural language processing\b", r"\bnlp\b"],
    "computer_vision": [r"\bcomputer vision\b", r"\bimage recognition\b"],
    "chatbot": [r"\bai chatbot(?:s)?\b", r"\bvirtual assistant(?:s)?\b"],
    "predictive_ai": [r"\bai[- ]powered predictive\b", r"\bmachine[- ]learning[- ]based\b"],
}

DEPLOYMENT_VERBS = re.compile(
    r"\b(deploy(?:ed|ing)?|implement(?:ed|ing)?|integrat(?:e|ed|ing)|use(?:d|s|ing)?|"
    r"adopt(?:ed|ing)?|launch(?:ed|ing)?|embed(?:ded|ding)?|automate(?:d|s|ing)?)\b",
    flags=re.I,
)

RHETORIC = re.compile(
    r"\b(explore|consider|future|potential|opportunit(?:y|ies)|strategy|roadmap|ambition|trend|risk)\b",
    flags=re.I,
)

FALSE_POSITIVE_SMART = re.compile(r"\bsmart\s+(?:tv|television|phone|meter|display|card|city|watch)\b", flags=re.I)

@dataclass(frozen=True)
class AIClassification:
    score: int
    category: str | None
    matched_terms: tuple[str, ...]
    rationale: str


def classify_ai_text(text: str | None) -> AIClassification:
    """High-precision candidate generator, not a substitute for manual research coding."""
    if not text:
        return AIClassification(0, None, (), "empty text")

    clean = " ".join(str(text).lower().split())
    if FALSE_POSITIVE_SMART.search(clean) and not any(
        re.search(p, clean) for pats in HIGH_PRECISION_PATTERNS.values() for p in pats
    ):
        return AIClassification(0, None, (), "generic smart-device language")

    matches: list[tuple[str, str]] = []
    for category, patterns in HIGH_PRECISION_PATTERNS.items():
        for pattern in patterns:
            m = re.search(pattern, clean, flags=re.I)
            if m:
                matches.append((category, m.group(0)))

    if not matches:
        return AIClassification(0, None, (), "no high-precision AI term")

    categories = [c for c, _ in matches]
    terms = tuple(sorted({m for _, m in matches}))
    has_deployment = bool(DEPLOYMENT_VERBS.search(clean))
    has_rhetoric = bool(RHETORIC.search(clean))

    category = categories[0]
    if has_deployment:
        score = 3 if re.search(r"\b(core|production|underwriting|pricing|risk|inspection|service delivery)\b", clean) else 2
        return AIClassification(score, category, terms, "AI term plus concrete deployment language")
    if has_rhetoric:
        return AIClassification(1, category, terms, "AI term appears in strategic/aspirational context")
    return AIClassification(1, category, terms, "AI term present but deployment is not explicit")
