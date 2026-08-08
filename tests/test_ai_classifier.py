from mena_ai_labor.ai_classifier import classify_ai_text


def test_deployment_detected():
    x = classify_ai_text("We deployed computer vision inspection on the production line.")
    assert x.score >= 2
    assert x.category == "computer_vision"


def test_rhetoric_not_adoption():
    x = classify_ai_text("Artificial intelligence is a future opportunity in our strategy.")
    # generic phrase 'artificial intelligence' is intentionally not in the tiny high-precision starter dictionary
    assert x.score <= 1


def test_smart_display_false_positive():
    x = classify_ai_text("We installed a smart display in the store.")
    assert x.score == 0
