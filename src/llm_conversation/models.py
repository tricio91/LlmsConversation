from dataclasses import dataclass
from typing import Any, Optional

from .config import Settings, get_settings


def create_llm(model_id, settings: Optional[Settings] = None):
    # Build a ChatOllama client for the given model. Imported here so the
    # package still loads if langchain isn't installed yet.
    from langchain_ollama import ChatOllama
    settings = settings or get_settings()
    return ChatOllama(model=model_id, base_url=settings.ollama_base_url,
                      temperature=settings.temperature)


@dataclass
class ModelConfig:
    name: str
    role: str
    system_prompt: str
    model_id: str
    llm: Optional[Any] = None

    def ensure_llm(self, settings: Optional[Settings] = None):
        # Build the client on first use and cache it on the instance.
        if self.llm is None:
            self.llm = create_llm(self.model_id, settings=settings)
        return self.llm


def build_default_roster(settings: Optional[Settings] = None) -> list[ModelConfig]:
    # The two debaters shipped by default; extend this list to add more.
    settings = settings or get_settings()
    return [
        ModelConfig(
            name="Economist",
            role="Economist",
            model_id=settings.model_mistral,
            system_prompt=(
                "You are a pragmatic economist. You back your positions with data, "
                "market incentives and trade-offs. Answer in 4-6 sentences and quote "
                "the other side's previous argument before rebutting it."
            ),
        ),
        ModelConfig(
            name="Technologist",
            role="Technologist",
            model_id=settings.model_gemma,
            system_prompt=(
                "You are an optimistic but rigorous technologist. You argue from "
                "technical feasibility and long-term impact. Answer in 4-6 sentences "
                "and acknowledge the other side's valid point before qualifying it."
            ),
        ),
    ]
