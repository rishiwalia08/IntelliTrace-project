from __future__ import annotations

from typing import Any


def calculate_risk_score(
    graph_signals: dict[str, Any],
    duplicate_signals: dict[str, Any],
    invoice_data: dict[str, Any],
) -> int:
    score = 0.0

    if graph_signals.get("cycle_detected"):
        score += 30

    if duplicate_signals.get("similarity_score", 0.0) > 0.9:
        score += 25

    if graph_signals.get("high_frequency_flag"):
        score += 15

    if graph_signals.get("velocity_flag"):
        score += 15

    if graph_signals.get("hub_anomaly_flag"):
        score += 10

    amount = float(invoice_data.get("amount", 0) or 0)
    historical_avg = invoice_data.get("historical_average")
    if historical_avg:
        historical_avg = float(historical_avg)
        if historical_avg > 0 and amount > (2.0 * historical_avg):
            score += 5
    elif amount >= 1_000_000:
        score += 5

    return max(0, min(100, int(round(score))))


def get_risk_level(score: int) -> str:
    if score <= 30:
        return "LOW"
    if score <= 70:
        return "MEDIUM"
    return "HIGH"


def generate_explanation(
    graph_signals: dict[str, Any],
    duplicate_signals: dict[str, Any],
    invoice_data: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []

    if graph_signals.get("cycle_detected"):
        cycles = graph_signals.get("cycles", [])
        if cycles:
            reasons.append(f"Circular trade detected ({cycles[0]})")
        else:
            reasons.append("Circular trade pattern detected in supplier network")

    similarity_score = float(duplicate_signals.get("similarity_score", 0.0) or 0.0)
    if similarity_score > 0.9:
        reasons.append(f"Invoice is {int(round(similarity_score * 100))}% similar to an existing invoice")

    if graph_signals.get("high_frequency_flag"):
        reasons.append("Repeated supplier-buyer transaction frequency exceeds baseline")

    if graph_signals.get("velocity_flag"):
        reasons.append("Supplier shows abnormal transaction velocity in recent window")

    if graph_signals.get("hub_anomaly_flag"):
        reasons.append("Entity connected to unusually dense transaction hub")

    amount = float(invoice_data.get("amount", 0) or 0)
    historical_avg = invoice_data.get("historical_average")
    if historical_avg and float(historical_avg) > 0 and amount > (2.0 * float(historical_avg)):
        reasons.append("Invoice amount is significantly above supplier historical average")
    elif not historical_avg and amount >= 1_000_000:
        reasons.append("Invoice amount exceeds configured high-value threshold")

    if not reasons:
        reasons.append("No strong fraud signal detected in current rule set")

    return reasons


def build_risk_assessment(
    graph_signals: dict[str, Any],
    duplicate_signals: dict[str, Any],
    invoice_data: dict[str, Any],
) -> dict[str, Any]:
    score = calculate_risk_score(graph_signals, duplicate_signals, invoice_data)
    risk_level = get_risk_level(score)
    reasons = generate_explanation(graph_signals, duplicate_signals, invoice_data)

    return {
        "score": score,
        "risk": risk_level,
        "reasons": reasons,
        "flags": {
            "cycle": bool(graph_signals.get("cycle_detected", False)),
            "duplicate": bool(duplicate_signals.get("duplicate", False)),
            "velocity": bool(graph_signals.get("velocity_flag", False)),
            "high_frequency": bool(graph_signals.get("high_frequency_flag", False)),
            "hub": bool(graph_signals.get("hub_anomaly_flag", False)),
        },
    }
