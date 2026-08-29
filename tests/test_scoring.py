from interview.scoring import calculate_scores

def test_weighted_score_is_bounded():
    scores = calculate_scores([{"answer_score": 80, "communication_score": 70, "voice": {"voice_score": 75}, "emotion": {"distribution": {"neutral": 60}}}])
    assert 0 <= scores["overall"] <= 100
    assert scores["technical"] == 80
