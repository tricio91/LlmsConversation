import os
from dataclasses import dataclass, field
from functools import lru_cache

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("URL_BASE_OLLAMA", "http://localhost:11434")
    )
    model_mistral: str = field(
        default_factory=lambda: os.getenv("MODEL_NAME_OLLAMA_MISTRAL", "mistral")
    )
    model_gemma: str = field(
        default_factory=lambda: os.getenv("MODEL_NAME_OLLAMA_GEMMA3", "gemma3")
    )
    judge_model: str = field(
        default_factory=lambda: os.getenv("MODEL_NAME_OLLAMA_JUDGE", "mistral")
    )
    temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.7"))
    )
    request_timeout: int = field(
        default_factory=lambda: int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
    )

    def validate(self):
        # Catch obviously broken config before it reaches the LLM client.
        if not self.ollama_base_url.startswith(("http://", "https://")):
            raise ValueError(f"URL_BASE_OLLAMA is not a valid URL: {self.ollama_base_url!r}")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(f"LLM_TEMPERATURE must be between 0 and 2, got {self.temperature}")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Read and validate the environment once, then reuse the same instance.
    s = Settings()
    s.validate()
    return s
