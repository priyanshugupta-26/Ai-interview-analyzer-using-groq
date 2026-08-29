from utils.validators import parse_questions_json

def test_question_json_is_parsed():
    questions = parse_questions_json('{"questions":[{"question":"Explain decorators", "category":"Technical", "difficulty":"Medium"}]}', 5)
    assert questions[0].id == 1
    assert questions[0].question == "Explain decorators"
