from interview.question_bank import fallback_questions

def test_fallback_returns_requested_count():
    assert len(fallback_questions("Unknown Domain", 10)) == 10
