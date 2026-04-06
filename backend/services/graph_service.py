from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from threading import RLock
from typing import Any

import networkx as nx
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.invoice import Invoice

_GRAPH_LOCK = RLock()
_SUPPLY_CHAIN_GRAPH: nx.MultiDiGraph | None = None


def initialize_graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.graph["pair_counts"] = defaultdict(int)
    graph.graph["pair_first_seen"] = {}
    graph.graph["supplier_txn_dates"] = defaultdict(list)
    return graph


def get_graph() -> nx.MultiDiGraph:
    global _SUPPLY_CHAIN_GRAPH
    with _GRAPH_LOCK:
        if _SUPPLY_CHAIN_GRAPH is None:
            _SUPPLY_CHAIN_GRAPH = initialize_graph()
        return _SUPPLY_CHAIN_GRAPH


def _coerce_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    return datetime.utcnow().date()


def add_transaction(
    graph: nx.MultiDiGraph,
    supplier_id: str,
    buyer_id: str,
    invoice_data: dict[str, Any],
) -> None:
    txn_date = _coerce_date(invoice_data.get("date"))
    amount = Decimal(str(invoice_data.get("amount", 0)))

    graph.add_node(supplier_id)
    graph.add_node(buyer_id)

    graph.add_edge(
        supplier_id,
        buyer_id,
        invoice_id=invoice_data.get("invoice_id"),
        amount=float(amount),
        date=txn_date.isoformat(),
        hash=invoice_data.get("hash"),
    )

    pair = (supplier_id, buyer_id)
    graph.graph["pair_counts"][pair] += 1
    graph.graph["pair_first_seen"].setdefault(pair, txn_date)
    graph.graph["supplier_txn_dates"][supplier_id].append(txn_date)


def detect_cycles(graph: nx.MultiDiGraph, min_cycle_length: int = 3) -> list[str]:
    cycles: list[str] = []
    for cycle in nx.simple_cycles(graph):
        if len(cycle) >= min_cycle_length:
            cycles.append(" → ".join([*cycle, cycle[0]]))
    return cycles


def detect_anomalies(
    graph: nx.MultiDiGraph,
    *,
    high_frequency_threshold: int = 4,
    new_connection_window_days: int = 1,
) -> dict[str, Any]:
    pair_counts: dict[tuple[str, str], int] = graph.graph.get("pair_counts", {})
    pair_first_seen: dict[tuple[str, str], date] = graph.graph.get("pair_first_seen", {})

    frequent_edges = [
        {"supplier_id": src, "buyer_id": dst, "count": count}
        for (src, dst), count in pair_counts.items()
        if count >= high_frequency_threshold
    ]

    degrees = [graph.degree(node) for node in graph.nodes]
    hub_nodes: list[str] = []
    if degrees:
        mean_degree = sum(degrees) / len(degrees)
        variance = sum((degree - mean_degree) ** 2 for degree in degrees) / len(degrees)
        std_dev = variance**0.5
        threshold = mean_degree + (2 * std_dev)
        hub_nodes = [node for node in graph.nodes if graph.degree(node) > threshold and graph.degree(node) >= 4]

    today = datetime.utcnow().date()
    recent_new_connections = [
        {"supplier_id": src, "buyer_id": dst, "first_seen": first_seen.isoformat()}
        for (src, dst), first_seen in pair_first_seen.items()
        if (today - first_seen).days <= new_connection_window_days
    ]

    return {
        "high_frequency_flag": len(frequent_edges) > 0,
        "high_frequency_edges": frequent_edges,
        "hub_anomaly_flag": len(hub_nodes) > 0,
        "suspicious_nodes": hub_nodes,
        "new_connection_flag": len(recent_new_connections) > 0,
        "new_connections": recent_new_connections,
    }


def detect_velocity(
    supplier_id: str,
    *,
    graph: nx.MultiDiGraph | None = None,
    window_days: int = 7,
    spike_multiplier: float = 2.5,
    minimum_recent_count: int = 5,
) -> dict[str, Any]:
    graph = graph or get_graph()
    supplier_txn_dates: dict[str, list[date]] = graph.graph.get("supplier_txn_dates", {})
    txn_dates = sorted(supplier_txn_dates.get(supplier_id, []))

    if not txn_dates:
        return {"velocity_flag": False, "recent_count": 0, "historical_window_avg": 0.0}

    today = datetime.utcnow().date()
    cutoff = today - timedelta(days=window_days)

    recent_count = sum(1 for txn_date in txn_dates if txn_date >= cutoff)
    historical_dates = [txn_date for txn_date in txn_dates if txn_date < cutoff]

    if not historical_dates:
        velocity_flag = recent_count >= minimum_recent_count
        return {
            "velocity_flag": velocity_flag,
            "recent_count": recent_count,
            "historical_window_avg": 0.0,
        }

    historical_span_days = max((cutoff - historical_dates[0]).days, 1)
    historical_daily_avg = len(historical_dates) / historical_span_days
    historical_window_avg = historical_daily_avg * window_days

    velocity_flag = recent_count > max(historical_window_avg * spike_multiplier, minimum_recent_count)
    return {
        "velocity_flag": velocity_flag,
        "recent_count": recent_count,
        "historical_window_avg": round(historical_window_avg, 2),
    }


def run_fraud_checks(graph: nx.MultiDiGraph, supplier_id: str) -> dict[str, Any]:
    cycles = detect_cycles(graph)
    anomaly_signals = detect_anomalies(graph)
    velocity_signals = detect_velocity(supplier_id, graph=graph)

    return {
        "cycle_detected": len(cycles) > 0,
        "cycles": cycles,
        **anomaly_signals,
        **velocity_signals,
    }


def register_transaction_and_detect(invoice: Invoice) -> dict[str, Any]:
    graph = get_graph()
    with _GRAPH_LOCK:
        add_transaction(
            graph,
            supplier_id=invoice.supplier_id,
            buyer_id=invoice.buyer_id,
            invoice_data={
                "invoice_id": invoice.invoice_id,
                "amount": invoice.amount,
                "date": invoice.date,
                "hash": invoice.hash,
            },
        )
        return run_fraud_checks(graph, supplier_id=invoice.supplier_id)


def bootstrap_graph_from_db(db: Session) -> None:
    graph = get_graph()
    invoices = db.scalars(select(Invoice)).all()

    with _GRAPH_LOCK:
        for invoice in invoices:
            add_transaction(
                graph,
                supplier_id=invoice.supplier_id,
                buyer_id=invoice.buyer_id,
                invoice_data={
                    "invoice_id": invoice.invoice_id,
                    "amount": invoice.amount,
                    "date": invoice.date,
                    "hash": invoice.hash,
                },
            )
