"""API request models"""

import re

from pydantic import BaseModel, Field, field_validator

# ── Prompt injection / malicious input patterns ──
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+a",
    r"(system|admin|root)\s*:\s*",
    r"forget\s+(everything|all|your)\s+(you|instructions|rules)",
    r"do\s+not\s+follow\s+(your|the)\s+(instructions|rules|guidelines)",
    r"override\s+(your|the|all)\s+(instructions|rules|settings)",
    r"act\s+as\s+(if\s+you\s+are|a)\s+",
    r"pretend\s+(you\s+are|to\s+be)\s+",
    r"new\s+instructions?\s*:",
    r"<\s*script",
    r"javascript\s*:",
    r"on(load|error|click)\s*=",
    r"(\b(DROP|DELETE|INSERT|UPDATE|ALTER)\s+(TABLE|DATABASE|FROM))",
    r";\s*--",
    r"union\s+select",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)

# Excessive repetition (e.g., "aaaaaa..." or "ha ha ha ha ha ha ha")
_REPETITION_RE = re.compile(r"(.)\1{19,}|(\b\w+\b)(\s+\2){9,}", re.IGNORECASE)

# ── AI / ML topic relevance keywords ──
# If the input contains at least one of these, we consider it on-topic.
_AI_ML_KEYWORDS = [
    # Core AI/ML
    r"machine\s*learning", r"\bml\b", r"deep\s*learning", r"\bdl\b",
    r"artificial\s*intelligence", r"\bai\b", r"neural\s*network",
    r"reinforcement\s*learning", r"supervised\s*learning",
    r"unsupervised\s*learning", r"self[- ]supervised",
    r"semi[- ]supervised", r"federated\s*learning",
    r"transfer\s*learning", r"meta[- ]learning",
    r"few[- ]shot", r"zero[- ]shot", r"one[- ]shot",
    # NLP
    r"natural\s*language", r"\bnlp\b", r"transformer",
    r"language\s*model", r"\bllm\b", r"\bgpt\b", r"\bbert\b",
    r"attention\s*mechanism", r"text\s*(generation|classification|mining)",
    r"sentiment\s*analysis", r"named\s*entity", r"machine\s*translation",
    r"question\s*answering", r"summarization", r"tokeniz",
    r"word\s*embedding", r"retrieval[- ]augmented", r"\brag\b",
    r"prompt\s*(engineering|tuning)",
    # Computer Vision
    r"computer\s*vision", r"\bcnn\b", r"convolutional",
    r"object\s*detection", r"image\s*(recognition|classification|segmentation|generation)",
    r"generative\s*adversarial", r"\bgan\b", r"diffusion\s*model",
    r"stable\s*diffusion", r"visual\s*transformer", r"\bvit\b",
    # Models & architectures
    r"recurrent", r"\brnn\b", r"\blstm\b", r"\bgru\b",
    r"autoencoder", r"\bvae\b", r"graph\s*neural",
    r"knowledge\s*graph", r"embedding", r"fine[- ]?tun",
    r"pre[- ]?train", r"foundation\s*model",
    # Specific domains
    r"autonomous\s*(driving|vehicle)", r"robot(ics|ic\b)",
    r"speech\s*(recognition|synthesis)", r"recommender\s*system",
    r"anomaly\s*detection", r"time\s*series\s*(forecast|predict)",
    r"data\s*augment", r"feature\s*(extraction|engineering|selection)",
    r"bias\s*(in\s*ai|fairness|detection)", r"explainab", r"\bxai\b",
    r"adversarial\s*(attack|robustness|example)",
    # Optimization & training
    r"gradient\s*descent", r"backpropagat", r"hyperparameter",
    r"batch\s*normali", r"dropout", r"regulariz", r"overfit",
    r"loss\s*function", r"optimizer", r"\badam\b", r"\bsgd\b",
    # Data & benchmarks
    r"dataset", r"benchmark", r"(imagenet|cifar|mnist)",
    r"cross[- ]validat", r"train(ing)?\s*(data|set|pipeline)",
    # Hardware / infra
    r"\bgpu\b", r"\btpu\b", r"distributed\s*(training|computing)",
    r"model\s*(compression|pruning|distillation|quantiz)",
    r"edge\s*(ai|inference|deploy)",
    # Agents & multi-agent
    r"(multi[- ]?)?agent", r"autogen", r"langchain", r"langgraph",
    # Research areas
    r"(arxiv|paper|research|survey|review|study|literature)\b",
    r"classification", r"regression", r"clustering", r"segmentation",
    r"detection", r"prediction", r"generation", r"recognition",
]
_AI_ML_RE = re.compile("|".join(_AI_ML_KEYWORDS), re.IGNORECASE)

_OFF_TOPIC_MSG = (
    "I can only help with AI and Machine Learning research topics. "
    "Please enter a topic related to AI/ML, such as "
    "\"transformer architectures\", \"federated learning\", or "
    "\"object detection in autonomous driving\"."
)


class CreateReviewRequest(BaseModel):
    """Request model for creating a new literature review"""

    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Research topic to review",
        examples=["graph neural networks", "renewable energy storage"],
    )

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate, clean, and guard topic input"""
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Topic must be at least 3 characters long")

        # Block prompt injection attempts
        if _INJECTION_RE.search(v):
            raise ValueError(
                "Your input contains disallowed patterns. "
                "Please enter a valid research topic."
            )

        # Block excessive repetition / gibberish
        if _REPETITION_RE.search(v):
            raise ValueError(
                "Your input appears to contain excessive repetition. "
                "Please enter a meaningful research topic."
            )

        # Block off-topic requests — must relate to AI/ML
        if not _AI_ML_RE.search(v):
            raise ValueError(_OFF_TOPIC_MSG)

        return v

    class Config:
        json_schema_extra = {"example": {"topic": "graph neural networks"}}
