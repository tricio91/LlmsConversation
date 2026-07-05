import json
from dataclasses import asdict
from typing import Optional

from .conversation import DebateResult
from .judge import Verdict


def to_markdown(result: DebateResult, verdict: Optional[Verdict] = None) -> str:
    # Render the debate (and optional verdict) as readable Markdown.
    lines = [
        f"# Debate: {result.topic}",
        "",
        f"_Session: `{result.session_id}` · {len(result.turns)} turns_",
        "",
    ]
    current_round = None
    for t in result.turns:
        if t.round != current_round:
            current_round = t.round
            lines += [f"## Round {t.round}", ""]
        lines += [f"**{t.speaker}** _({t.role})_", "", t.content, ""]

    if verdict:
        lines += [
            "## Verdict",
            "",
            f"**Summary:** {verdict.summary}",
            "",
            f"**Winner:** {verdict.winner}",
            "",
            f"**Reason:** {verdict.rationale}",
            "",
        ]
    return "\n".join(lines)


def to_json(result: DebateResult, verdict: Optional[Verdict] = None, indent: int = 2) -> str:
    # Serialize the debate (and optional verdict) to JSON for storage or reuse.
    payload = {
        "topic": result.topic,
        "session_id": result.session_id,
        "turns": [asdict(t) for t in result.turns],
    }
    if verdict:
        payload["verdict"] = asdict(verdict)
    return json.dumps(payload, ensure_ascii=False, indent=indent)
