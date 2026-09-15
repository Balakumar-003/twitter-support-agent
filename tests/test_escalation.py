import sys
import os

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from escalation import make_escalation_decision

def get_base_mock():
    return {
        "customer_message": "My phone is slightly warm",
        "predicted_intent": "battery_drain",
        "classifier_confidence": 0.9,
        "retrieved_cases": [{"similarity_score": 0.85}],
        "generated_reply_data": {"uncertainty_flag": False, "grounding_status": "Successful"}
    }

def test_high_confidence_routine():
    inputs = get_base_mock()
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "auto_handle"

def test_explicit_human_request():
    inputs = get_base_mock()
    inputs["customer_message"] = "I want to talk to a human agent right now"
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "explicit_human_request" in res["signals"]

def test_high_risk_content():
    inputs = get_base_mock()
    inputs["customer_message"] = "Fix it or I will sue you"
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "high_risk_content" in res["signals"]

def test_sensitive_intent():
    inputs = get_base_mock()
    inputs["predicted_intent"] = "account_authentication"
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "sensitive_intent" in res["signals"]

def test_low_classifier_confidence():
    inputs = get_base_mock()
    inputs["classifier_confidence"] = 0.5
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "low_intent_confidence" in res["signals"]

def test_no_retrieval_evidence():
    inputs = get_base_mock()
    inputs["retrieved_cases"] = []
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "no_retrieval_evidence" in res["signals"]

def test_low_retrieval_similarity():
    inputs = get_base_mock()
    inputs["retrieved_cases"] = [{"similarity_score": 0.05}]
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "low_retrieval_similarity" in res["signals"]

def test_generation_failed():
    inputs = get_base_mock()
    inputs["generated_reply_data"] = {"uncertainty_flag": True, "grounding_status": "Failed"}
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "generation_uncertainty" in res["signals"]

def test_empty_message():
    inputs = get_base_mock()
    inputs["customer_message"] = "   "
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "empty_input" in res["signals"]

def test_missing_metadata():
    inputs = get_base_mock()
    inputs["generated_reply_data"] = None
    res = make_escalation_decision(**inputs)
    assert res["decision"] == "escalate"
    assert "generation_uncertainty" in res["signals"]
