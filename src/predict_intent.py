def predict_intent(text):
    """
    Mock intent classifier.
    Due to the lack of labeled training data in Milestone 11,
    the model was not trained. This safely returns 'unknown'
    to ensure the downstream pipeline defaults to escalation.
    """
    return {
        "intent": "unknown",
        "confidence": 0.0
    }
