"""Gradio interface and entry point. Run `python app/gradio_app.py`."""

import sys
from pathlib import Path

import gradio as gr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from llm_conversation import (
    ConversationOrchestrator,
    Judge,
    build_default_roster,
    to_json,
    to_markdown,
)

DEFAULT_TOPIC = "The impact of artificial intelligence on the job market"
OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def run_debate(topic, rounds, use_judge):
    # Callback for the button: run the debate and return what the widgets show.
    if not topic.strip():
        return [], "Enter a topic to start.", None, None

    orchestrator = ConversationOrchestrator(build_default_roster())
    result = orchestrator.run(topic, session_id="ui", rounds=int(rounds))

    chat = [
        {
            "role": "assistant",
            "content": f"**Round {t.round} · {t.speaker} ({t.role})**\n\n{t.content}",
        }
        for t in result.turns
    ]

    verdict = None
    verdict_md = ""
    if use_judge:
        verdict = Judge().evaluate(result)
        verdict_md = f"### Verdict\n\n**Winner:** {verdict.winner}\n\n{verdict.summary}"

    # Write the downloadable files next to the app.
    OUT_DIR.mkdir(exist_ok=True)
    md_path = OUT_DIR / "debate.md"
    json_path = OUT_DIR / "debate.json"
    md_path.write_text(to_markdown(result, verdict), encoding="utf-8")
    json_path.write_text(to_json(result, verdict), encoding="utf-8")

    return chat, verdict_md, str(md_path), str(json_path)


def build_ui():
    # Lay out the page and wire the button to run_debate.
    with gr.Blocks(title="Local LLM Debate", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# Local LLM Debate\n"
            "Debate between two local LLM models (Ollama + LangChain)."
        )
        with gr.Row():
            with gr.Column(scale=1):
                topic = gr.Textbox(label="Debate topic", value=DEFAULT_TOPIC, lines=3)
                rounds = gr.Slider(1, 5, value=2, step=1, label="Rounds")
                use_judge = gr.Checkbox(value=True, label="Add the judge's verdict")
                run_btn = gr.Button("Start debate", variant="primary")
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(label="Debate", height=420)
                verdict_box = gr.Markdown()
                with gr.Row():
                    md_file = gr.File(label="Markdown")
                    json_file = gr.File(label="JSON")

        run_btn.click(
            run_debate,
            inputs=[topic, rounds, use_judge],
            outputs=[chatbot, verdict_box, md_file, json_file],
        )
    return demo


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    build_ui().launch(allowed_paths=[str(OUT_DIR)])
