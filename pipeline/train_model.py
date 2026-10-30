"""Train an XGBoost bridge-posting classifier from the dbt star schema.

Reads fct_bridge_inspection joined to its dimensions, trains on the 2024 inspection
year and tests on 2025. Splitting by year (not randomly) matters here: the same bridge
appears in both years, so a random split would let the model "see" test bridges
during training and inflate the scores.

Writes metrics to results/pipeline_model_metrics.json.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import duckdb
import pandas as pd
from sklearn.metrics import (average_precision_score, precision_score,
                             recall_score, roc_auc_score)
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]

NUMERIC = ["bridge_age", "max_span_ft", "avg_daily_traffic", "truck_pct", "is_movable"]
CATEGORICAL = ["state_abbr", "material_family", "owner_level", "main_span_design",
               "design_load_code"]

QUERY = """
SELECT f.inspection_year, f.is_posted,
       f.bridge_age, f.max_span_ft, f.avg_daily_traffic, f.truck_pct,
       CAST(f.is_movable AS INTEGER) AS is_movable,
       f.main_span_design, f.design_load_code,
       s.state_abbr, m.material_family, o.owner_level
FROM main_marts.fct_bridge_inspection f
JOIN main_marts.dim_state    s USING (state_key)
JOIN main_marts.dim_material m USING (material_key)
JOIN main_marts.dim_owner    o USING (owner_key)
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path,
                    default=Path(os.getenv("NBI_DUCKDB_PATH", ROOT / "warehouse" / "nbi.duckdb")))
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "pipeline_model_metrics.json")
    ap.add_argument("--n-jobs", type=int, default=4, help="cap CPU threads (laptop runs hot)")
    args = ap.parse_args()

    con = duckdb.connect(str(args.db), read_only=True)
    df = con.execute(QUERY).df()
    con.close()

    for c in CATEGORICAL:
        df[c] = df[c].fillna("Unknown").astype("category")
    X_cols = NUMERIC + CATEGORICAL

    train = df[df.inspection_year == 2024]
    test = df[df.inspection_year == 2025]
    y_train = train.is_posted.astype(int)
    y_test = test.is_posted.astype(int)

    # Posted bridges are rare (~9%), so weight them up instead of resampling.
    pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)

    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        tree_method="hist", enable_categorical=True,
        scale_pos_weight=pos_weight, n_jobs=args.n_jobs,
        eval_metric="aucpr", random_state=42,
    )
    model.fit(train[X_cols], y_train)  # XGBoost handles missing numbers natively

    proba = model.predict_proba(test[X_cols])[:, 1]
    pred = (proba >= 0.5).astype(int)
    metrics = {
        "split": "train=2024, test=2025",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "test_base_rate": round(float(y_test.mean()), 4),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "pr_auc": round(float(average_precision_score(y_test, proba)), 4),
        "recall@0.5": round(float(recall_score(y_test, pred)), 4),
        "precision@0.5": round(float(precision_score(y_test, pred)), 4),
        "scale_pos_weight": round(float(pos_weight), 2),
    }
    importance = pd.Series(model.feature_importances_, index=X_cols).sort_values(ascending=False)
    metrics["feature_importance"] = {k: round(float(v), 4) for k, v in importance.items()}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
