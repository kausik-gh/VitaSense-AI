import re
from dataclasses import dataclass
from enum import Enum


class SafetyResult(Enum):
    PASS = "pass"
    FLAG = "flag"
    BLOCK = "block"


ESCALATION_MESSAGE = (
    "⚠️ The symptoms you're describing may require immediate medical attention. "
    "Please call emergency services (112 / 911) or go to your nearest emergency room immediately. "
    "Do not wait or self-medicate."
)

DISCLAIMER = (
    "⚕️ This is not medical advice. If symptoms worsen or you have any concerns, "
    "please consult a qualified healthcare professional."
)

EMERGENCY_PATTERNS: tuple[str, ...] = (
    r"\bchest pain\b",
    r"\bchest pressure\b",
    r"\bcan't breathe\b",
    r"\bcannot breathe\b",
    r"\bshortness of breath\b",
    r"\bdifficulty breathing\b",
    r"\bblood in (vomit|stool|urine|poop)\b",
    r"\bbloody (vomit|stool|urine|stool)\b",
    r"\bsevere headache\b",
    r"\bworst headache\b",
    r"\bloss of consciousness\b",
    r"\bpassed out\b",
    r"\bfainting\b",
    r"\bfacial droop\b",
    r"\barm weakness\b",
    r"\bspeech (difficulty|slurred)\b",
    r"\bthroat (is )?(swelling|closing)\b",
    r"\banaphylaxis\b",
    r"\boverdose\b",
    r"\bpoisoning\b",
    r"\bstroke\b",
    r"\bheart attack\b",
    r"\bi\s*(am|'m) dying\b",
    r"\bsuicid\w*\b",
    r"\bself.harm\b",
)

DIAGNOSIS_PATTERNS: tuple[str, ...] = (
    r"\byou have [a-z ]+\b",
    r"\bthis is definitely\b",
    r"\byou are (suffering from|diagnosed with)\b",
    r"\bi diagnose\b",
    r"\bmy diagnosis is\b",
    r"\bconfirmed (diagnosis|condition)\b",
)


@dataclass(frozen=True)
class ScanResult:
    verdict: SafetyResult
    reason: str
    modified_response: str | None = None


def _matches_any(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return pattern
    return None


def _append_disclaimer(response_text: str) -> str:
    if DISCLAIMER in response_text:
        return response_text
    return response_text.rstrip() + "\n\n" + DISCLAIMER


def scan_user_message(message: str) -> ScanResult:
    matched_pattern = _matches_any(message, EMERGENCY_PATTERNS)
    if matched_pattern is not None:
        return ScanResult(
            verdict=SafetyResult.BLOCK,
            reason=f"Emergency keyword matched: {matched_pattern}",
            modified_response=ESCALATION_MESSAGE,
        )

    return ScanResult(verdict=SafetyResult.PASS, reason="No emergency keywords detected")


def scan_ai_response(response_text: str) -> ScanResult:
    emergency_pattern = _matches_any(response_text, EMERGENCY_PATTERNS)
    if emergency_pattern is not None:
        return ScanResult(
            verdict=SafetyResult.BLOCK,
            reason="Emergency content in AI response",
            modified_response=ESCALATION_MESSAGE,
        )

    response_without_disclaimer = response_text.replace(DISCLAIMER, "")
    diagnosis_pattern = _matches_any(response_without_disclaimer, DIAGNOSIS_PATTERNS)
    if diagnosis_pattern is not None:
        return ScanResult(
            verdict=SafetyResult.FLAG,
            reason=f"Diagnosis language detected: {diagnosis_pattern}",
            modified_response=_append_disclaimer(response_text),
        )

    if DISCLAIMER not in response_text:
        return ScanResult(
            verdict=SafetyResult.FLAG,
            reason="Disclaimer missing",
            modified_response=_append_disclaimer(response_text),
        )

    return ScanResult(
        verdict=SafetyResult.PASS,
        reason="OK",
        modified_response=response_text,
    )


def apply_escalation_override(user_message: str, ai_response: str | None = None) -> ScanResult:
    user_scan = scan_user_message(user_message)
    if user_scan.verdict == SafetyResult.BLOCK:
        return user_scan

    if ai_response is not None:
        return scan_ai_response(ai_response)

    return user_scan
