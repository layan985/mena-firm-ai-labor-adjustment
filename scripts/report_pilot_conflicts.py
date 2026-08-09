from __future__ import annotations

import json

from build_pilot_coverage import _load_employment_batches, _validate_csv_shapes


def main() -> None:
    _validate_csv_shapes()
    employment = _load_employment_batches()
    conflicts: list[dict] = []
    for (firm_id, year), group in employment.groupby(["firm_id", "year"], dropna=False):
        numeric = group[group["employees_numeric"].notna()].copy()
        values = sorted(numeric["employees_numeric"].astype(float).unique().tolist())
        if len(values) <= 1:
            continue
        conflicts.append({
            "firm_id": str(firm_id),
            "year": int(year),
            "values": [int(v) if float(v).is_integer() else float(v) for v in values],
            "source_batches": sorted(numeric["source_batch"].astype(str).unique().tolist()),
        })
    print(json.dumps({"conflicts": conflicts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
