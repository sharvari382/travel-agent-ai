"""
Lightweight guardrails layer.

This is intentionally simple and dependency-free so you can see exactly
what's happening. Later you can swap this for Guardrails AI, NeMo
Guardrails, or LLM-based moderation — the call sites in main.py stay the same.
"""
import re

MAX_INPUT_CHARS = 4000

BLOCKED_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"reveal your (prompt|instructions)",
]

OFF_TOPIC_HINT = (
    "I'm a travel planning assistant — I can help with destinations, "
    "budgets, weather, and itineraries. Could you ask me something travel-related?"
)


class GuardrailResult:
    def __init__(self, allowed: bool, message: str = ""):
        self.allowed = allowed
        self.message = message


def check_input(user_message: str) -> GuardrailResult:
    if len(user_message) > MAX_INPUT_CHARS:
        return GuardrailResult(False, "Your message is too long — please shorten it.")

    lowered = user_message.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, lowered):
            return GuardrailResult(
                False,
                "I can't comply with that request. I'm happy to help with travel planning though!",
            )

    return GuardrailResult(True)


def check_output(agent_reply: str) -> str:
    """Final pass over the agent's reply before it reaches the user.
    Right now this just trims; this is the hook where you'd later plug in
    PII redaction, profanity filtering, or hallucination checks."""
    return agent_reply.strip()
