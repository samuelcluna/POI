import random

CATEGORIES = ["A", "B", "C", "D", "E", "F", "G", "H"]


def load_and_aggregate(rows: int, seed: int) -> dict:
    rng = random.Random(seed)
    dataset = [
        {
            "id": i,
            "category": CATEGORIES[i % len(CATEGORIES)],
            "value": rng.random(),
            "payload": f"registro-{i:012d}" * 4,
        }
        for i in range(rows)
    ]

    totals: dict[str, dict] = {}
    for row in dataset:
        agg = totals.setdefault(row["category"], {"count": 0, "sum": 0.0, "max": 0.0})
        agg["count"] += 1
        agg["sum"] += row["value"]
        agg["max"] = max(agg["max"], row["value"])
    return totals
