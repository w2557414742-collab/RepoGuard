from repoguard.impact import risk_step


def bounded_step(score: float, weight: float, uncertain: bool) -> float:
    """pre: 0.0 <= score <= 5.0 and 0.0 <= weight <= 1.0
    post: 0.0 <= _ <= score
    """
    return risk_step(score, weight, uncertain)


def reversed_uncertainty(score: float) -> float:
    """pre: 1.0 <= score <= 5.0
    post: _ <= risk_step(score, 1.0, True)
    """
    return risk_step(score, 1.0, False)
