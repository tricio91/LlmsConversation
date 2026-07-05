from dataclasses import dataclass, field
from typing import Any, Optional

from .models import ModelConfig


@dataclass
class Turn:
    round: int
    speaker: str
    role: str
    content: str


@dataclass
class DebateResult:
    topic: str
    session_id: str
    turns: list[Turn] = field(default_factory=list)

    def transcript(self) -> str:
        # Flatten the turns into plain text, e.g. to feed the judge.
        lines = [f"Topic: {self.topic}", ""]
        for t in self.turns:
            lines.append(f"[Round {t.round}] {t.speaker} ({t.role}):\n{t.content}\n")
        return "\n".join(lines)


def _text(response: Any) -> str:
    # LangChain returns a Message with .content; other backends return a string.
    if hasattr(response, "content"):
        return str(response.content).strip()
    return str(response).strip()


class ConversationOrchestrator:
    def __init__(self, roster: list[ModelConfig]):
        # A debate needs at least two voices.
        if len(roster) < 2:
            raise ValueError("Need at least 2 models for a debate.")
        self.roster = roster
        self._history: dict[str, list[Turn]] = {}

    def history(self, session_id: str) -> list[Turn]:
        # Turns recorded so far for a session (empty list if it's new).
        return self._history.get(session_id, [])

    def _build_prompt(self, model: ModelConfig, topic: str, history: list[Turn]) -> str:
        # Stitch the model's persona, the topic and the running transcript together.
        parts = [model.system_prompt, f"\nDebate topic: {topic}\n"]
        if history:
            parts.append("Conversation so far:")
            for t in history:
                parts.append(f"- {t.speaker} ({t.role}): {t.content}")
        else:
            parts.append("You speak first. Open the debate with your position.")
        parts.append(f"\nNow respond as {model.name} ({model.role}):")
        return "\n".join(parts)

    def run(self, topic: str, session_id: str = "default", rounds: int = 2) -> DebateResult:
        # Run the debate: every model speaks once per round, sharing one history.
        if rounds < 1:
            raise ValueError("rounds must be >= 1")

        history = self._history.setdefault(session_id, [])
        result = DebateResult(topic=topic, session_id=session_id, turns=history)

        for r in range(1, rounds + 1):
            for model in self.roster:
                llm = model.ensure_llm()
                prompt = self._build_prompt(model, topic, history)
                answer = _text(llm.invoke(prompt))
                history.append(Turn(round=r, speaker=model.name, role=model.role,
                                    content=answer))
        return result


def run_multi_model_conversation(topic, session_id="default", rounds=2,
                                 roster: Optional[list[ModelConfig]] = None) -> DebateResult:
    # Thin wrapper kept under the old name so existing callers don't break.
    from .models import build_default_roster
    roster = roster or build_default_roster()
    return ConversationOrchestrator(roster).run(topic, session_id=session_id, rounds=rounds)
