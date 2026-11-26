# Demonstration amounts in points.
ENDOWMENT = 4
CORRECT_DECISION = 2
MAX_FORECAST_BONUS = 2
URN_MAX = 2


def urn_score(report_pct, posterior):
    return round(URN_MAX * (1 - (report_pct / 100 - posterior) ** 2), 2)


def forecast_win_probability(report, score, is_urn):
    if is_urn:
        error = (report - score) / URN_MAX
    else:
        error = report / 100 - score

    return 1 - error ** 2