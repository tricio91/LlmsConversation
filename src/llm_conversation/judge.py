from dataclasses import dataclass
from typing import Optional

from .config import Settings, get_settings
from .conversation import DebateResult, _text
from .models import create_llm


@dataclass
class Verdict:
    summary: str
    winner: str
    rationale: str


class Judge:
    SYSTEM_PROMPT = (
        "You are an impartial moderator. Summarize the debate in 3-4 sentences, "
        "decide which participant made the strongest case and justify it briefly. "
        "Answer EXACTLY in this format:\n"
        "SUMMARY: <text>\n"
        "WINNER: <name>\n"
        "REASON: <text>"
    )

    def __init__(self, model_id: Optional[str] = None, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.model_id = model_id or self.settings.judge_model
        self._llm = None

    def _get_llm(self):
        # Lazily create the judge's own client, separate from the debaters.
        if self._llm is None:
            self._llm = create_llm(self.model_id, settings=self.settings)
        return self._llm

    @staticmethod
    def _parse(text: str) -> Verdict:
        # Pull the three fields out of the model's reply, tolerating bad formatting.
        summary = winner = rationale = ""
        for line in text.splitlines():
            low = line.lower()
            if low.startswith("summary:"):
                summary = line.split(":", 1)[1].strip()
            elif low.startswith("winner:"):
                winner = line.split(":", 1)[1].strip()
            elif low.startswith("reason:"):
                rationale = line.split(":", 1)[1].strip()
        # If the model ignores the format, keep the raw text as the summary.
        if not summary:
            summary = text.strip()
        return Verdict(summary=summary, winner=winner or "Undecided", rationale=rationale)

    def evaluate(self, result: DebateResult) -> Verdict:
        # Send the full transcript to the judge and parse its verdict.
        llm = self._get_llm()
        prompt = f"{self.SYSTEM_PROMPT}\n\nDEBATE:\n{result.transcript()}"
        return self._parse(_text(llm.invoke(prompt)))
