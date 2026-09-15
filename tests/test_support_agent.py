import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from support_agent import run_pipeline

@patch('support_agent.predict_intent')
@patch('support_agent.retrieve_cases')
@patch('support_agent.generate_template_reply')
def test_normal_routine_request(mock_gen, mock_ret, mock_pred):
    # Mocking a high-confidence, well-retrieved routine request
    mock_pred.return_value = {"intent": "battery_drain", "confidence": 0.95}
    mock_ret.return_value = [{"case_id": "CASE-1", "company_response": "Here is a safe reply.", "similarity_score": 0.8}]
    mock_gen.return_value = {
        "draft_reply": "Here is a safe reply.",
        "grounding_status": "Successful",
        "uncertainty_flag": False,
        "escalation_recommendation": False,
        "explanation": "Success"
    }
    
    result = run_pipeline("My battery is dying fast")
    
    # In normal case, if generated reply is safe and retrieval is good, we expect auto_handle
    assert result["decision"] == "auto_handle"
    assert result["draft_reply"] == "Here is a safe reply."
    assert result["predicted_intent"] == "battery_drain"

def test_empty_message():
    result = run_pipeline("   ")
    assert result["decision"] == "escalate"
    assert result["escalation_reason"] == "Message is empty or null."
    assert result["draft_reply"] is None

@patch('support_agent.predict_intent')
def test_unknown_intent_escalation(mock_pred):
    mock_pred.return_value = {"intent": "unknown", "confidence": 0.0}
    # Retrieval and generation will run normally (which means they will return empty due to our empty corpus constraints)
    result = run_pipeline("Something weird is happening")
    assert result["decision"] == "escalate"
    # Even if they didn't return empty, the intent is unknown with low confidence, so it must escalate.

@patch('support_agent.retrieve_cases')
@patch('support_agent.predict_intent')
def test_no_retrieval_result(mock_pred, mock_ret):
    mock_pred.return_value = {"intent": "battery_drain", "confidence": 0.9}
    mock_ret.return_value = []
    
    result = run_pipeline("My battery is dying fast")
    assert result["decision"] == "escalate"
    assert result["draft_reply"] is None # Draft reply should be nullified when escalated

@patch('support_agent.predict_intent')
def test_component_failure(mock_pred):
    mock_pred.side_effect = Exception("Classifier crashed")
    result = run_pipeline("Will this crash?")
    
    # Should safely catch the exception and fall back
    assert result["decision"] == "escalate"
    assert result["escalation_reason"] == "Intent classification component failed."
    assert result["draft_reply"] is None
