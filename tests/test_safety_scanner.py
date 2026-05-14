import pytest

from chat.safety_scanner import (
    DIAGNOSIS_PATTERNS,
    DISCLAIMER,
    EMERGENCY_PATTERNS,
    ESCALATION_MESSAGE,
    SafetyResult,
    apply_escalation_override,
    scan_ai_response,
    scan_user_message,
)


EMERGENCY_EXAMPLES = [
    "I have chest pain",
    "There is chest pressure",
    "I can't breathe",
    "I cannot breathe",
    "I have shortness of breath",
    "I have difficulty breathing",
    "There is blood in vomit",
    "There is blood in stool",
    "There is blood in urine",
    "There is blood in poop",
    "I had bloody vomit",
    "I had bloody stool",
    "I had bloody urine",
    "I have a severe headache",
    "This is the worst headache",
    "There was loss of consciousness",
    "I passed out",
    "I keep fainting",
    "My face has facial droop",
    "I have arm weakness",
    "I have speech difficulty",
    "My speech slurred",
    "My throat is swelling",
    "My throat is closing",
    "This feels like anaphylaxis",
    "I took an overdose",
    "This may be poisoning",
    "I think it is a stroke",
    "I think it is a heart attack",
    "I am dying",
    "I'm dying",
    "I feel suicidal",
    "I may self-harm",
]


DIAGNOSIS_EXAMPLES = [
    "You have influenza.",
    "This is definitely dengue.",
    "You are suffering from pneumonia.",
    "You are diagnosed with flu.",
    "I diagnose migraine.",
    "My diagnosis is bronchitis.",
    "This is a confirmed diagnosis.",
    "This is a confirmed condition.",
]


def test_escalation_message_exact_text():
    assert ESCALATION_MESSAGE == (
        "⚠️ The symptoms you're describing may require immediate medical attention. "
        "Please call emergency services (112 / 911) or go to your nearest emergency room immediately. "
        "Do not wait or self-medicate."
    )


def test_disclaimer_exact_text():
    assert DISCLAIMER == (
        "⚕️ This is not medical advice. If symptoms worsen or you have any concerns, "
        "please consult a qualified healthcare professional."
    )


@pytest.mark.parametrize("message", EMERGENCY_EXAMPLES)
def test_all_emergency_phrases_block_user_message(message):
    result = scan_user_message(message)

    assert result.verdict == SafetyResult.BLOCK
    assert result.modified_response == ESCALATION_MESSAGE


def test_normal_user_message_passes():
    result = scan_user_message("I have a mild headache after sleeping late")

    assert result.verdict == SafetyResult.PASS
    assert result.modified_response is None


@pytest.mark.parametrize("response", DIAGNOSIS_EXAMPLES)
def test_definitive_diagnosis_language_is_flagged(response):
    result = scan_ai_response(response)

    assert result.verdict == SafetyResult.FLAG
    assert result.modified_response is not None
    assert DISCLAIMER in result.modified_response


def test_disclaimer_is_appended_when_missing():
    result = scan_ai_response("One possible explanation is dehydration.")

    assert result.verdict == SafetyResult.FLAG
    assert result.modified_response == "One possible explanation is dehydration.\n\n" + DISCLAIMER


def test_existing_disclaimer_is_not_duplicated():
    response = "One possible explanation is dehydration.\n\n" + DISCLAIMER

    result = scan_ai_response(response)

    assert result.verdict == SafetyResult.PASS
    assert result.modified_response == response


def test_emergency_content_in_ai_response_is_replaced_with_escalation():
    result = scan_ai_response("The user reports chest pain.")

    assert result.verdict == SafetyResult.BLOCK
    assert result.modified_response == ESCALATION_MESSAGE


def test_escalation_override_prioritizes_user_emergency():
    result = apply_escalation_override(
        "I have chest pain",
        "One possible explanation is muscle strain.",
    )

    assert result.verdict == SafetyResult.BLOCK
    assert result.modified_response == ESCALATION_MESSAGE


def test_escalation_override_scans_ai_response_when_user_passes():
    result = apply_escalation_override(
        "I feel tired",
        "You have anemia.",
    )

    assert result.verdict == SafetyResult.FLAG
    assert result.modified_response is not None
    assert DISCLAIMER in result.modified_response


def test_pattern_lists_are_not_empty():
    assert EMERGENCY_PATTERNS
    assert DIAGNOSIS_PATTERNS
