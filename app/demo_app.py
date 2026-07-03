"""
CKD Clinical Decision Support — research prototype (Streamlit).

Loads frozen MIMIC Step-2 artifacts from outputs/supervisor_runs/.
Run from CKD Dataset folder:
  .venv312/bin/streamlit run app/demo_app.py
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.calibration import CalibratedClassifierCV
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

try:
    from sklearn.frozen import FrozenEstimator
except ImportError:
    from sklearn.base import BaseEstimator

    class FrozenEstimator(BaseEstimator):
        def __init__(self, estimator):
            self.estimator = estimator

        def fit(self, X, y=None):
            return self

        def predict_proba(self, X):
            return self.estimator.predict_proba(X)

        def predict(self, X):
            return self.estimator.predict(X)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "outputs" / "supervisor_runs"
CHECKPOINT = OUT / "step2_mimic_checkpoint.pkl"
SHAP_CSV = OUT / "step2_mimic_shap_top15.csv"
REPORTING_LOCK = OUT / "final_reporting_lock.json"
CALIBRATION_CSV = OUT / "step2_mimic_calibration_summary.csv"
PRIMARY_MODEL = "logreg_sigmoid_cal"

ADMISSION_TYPES = [
    "EW EMER.",
    "EU OBSERVATION",
    "OBSERVATION ADMIT",
    "ELECTIVE",
    "URGENT",
    "DIRECT EMER.",
    "SURGICAL SAME DAY ADMISSION",
    "AMBULATORY OBSERVATION",
    "DIRECT OBSERVATION",
]
INSURANCE_OPTIONS = ["Medicare", "Medicaid", "Private", "Other", "No charge"]
MARITAL_OPTIONS = ["MARRIED", "SINGLE", "DIVORCED", "WIDOWED"]
RACE_OPTIONS = [
    "WHITE",
    "BLACK/AFRICAN AMERICAN",
    "HISPANIC OR LATINO",
    "ASIAN",
    "OTHER",
    "UNKNOWN",
    "PATIENT DECLINED TO ANSWER",
]

# Default demo: CKD-proxy positive admission with admission-window labs populated.
DEFAULT_ADMISSION_INDEX = 148
DEMO_HADM_ID = "24251211"


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .ckd-hero {
            padding: 1rem 1.25rem;
            border-radius: 0.5rem;
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
            color: #f8fafc;
            margin-bottom: 1rem;
        }
        .ckd-hero h1 {
            color: #f8fafc !important;
            font-size: 1.55rem !important;
            margin-bottom: 0.25rem !important;
        }
        .ckd-hero p {
            margin: 0.15rem 0;
            color: #cbd5e1;
            font-size: 0.95rem;
        }
        .ckd-disclaimer {
            padding: 0.65rem 0.9rem;
            border-left: 4px solid #f59e0b;
            background: #fffbeb;
            border-radius: 0.25rem;
            margin: 0.75rem 0 1rem 0;
            font-size: 0.9rem;
            color: #78350f;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="ckd-hero">
            <h1>CKD Admission Risk — Clinical Decision Support Prototype</h1>
            <p>FYDP · MIMIC-IV tabular branch · calibrated logistic regression · explainable AI</p>
            <p>Primary model: <strong>logreg_sigmoid_cal</strong> · Research / demonstration only</p>
        </div>
        <div class="ckd-disclaimer">
            <strong>Not for clinical use.</strong> This interface supports thesis demonstration of
            calibrated risk and interpretability. It does not diagnose CKD or replace eGFR / creatinine staging.
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner="Loading MIMIC model bundle…")
def load_bundle():
    if not CHECKPOINT.is_file():
        raise FileNotFoundError(f"Missing checkpoint. Run notebook 12B first: {CHECKPOINT}")

    with open(CHECKPOINT, "rb") as f:
        ckpt = pickle.load(f)

    X2_df: pd.DataFrame = ckpt["X2_df"]
    base2 = ckpt["base2"]
    m2: pd.DataFrame = ckpt["m2"].reset_index(drop=True)
    X2_df = X2_df.reset_index(drop=True)
    X2_va = ckpt["X2_va"]
    y2_va = ckpt["y2_va"]

    imp = SimpleImputer(strategy="median")
    imp.fit(X2_df)
    sc = StandardScaler()
    sc.fit(imp.transform(X2_df))

    cal = CalibratedClassifierCV(FrozenEstimator(base2), method="sigmoid")
    cal.fit(X2_va, y2_va)

    threshold = 0.16
    if CALIBRATION_CSV.is_file():
        cal_df = pd.read_csv(CALIBRATION_CSV)
        row = cal_df.loc[cal_df["model"] == PRIMARY_MODEL]
        if len(row):
            threshold = float(row.iloc[0]["threshold"])

    shap_df = None
    if SHAP_CSV.is_file():
        shap_df = pd.read_csv(SHAP_CSV).head(10)

    reporting = {}
    if REPORTING_LOCK.is_file():
        with open(REPORTING_LOCK, encoding="utf-8") as f:
            reporting = json.load(f)

    hadm_to_idx = {int(h): i for i, h in enumerate(m2["hadm_id"].astype(int))}

    return {
        "X2_df": X2_df,
        "m2": m2,
        "base2": base2,
        "imp": imp,
        "sc": sc,
        "cal": cal,
        "threshold": threshold,
        "shap_df": shap_df,
        "reporting": reporting,
        "feature_cols": list(X2_df.columns),
        "hadm_to_idx": hadm_to_idx,
    }


def transform_row(bundle, row_df: pd.DataFrame) -> np.ndarray:
    x = row_df[bundle["feature_cols"]].replace([np.inf, -np.inf], np.nan)
    x_imp = bundle["imp"].transform(x)
    return bundle["sc"].transform(x_imp)


def predict_proba(bundle, row_df: pd.DataFrame) -> float:
    X = transform_row(bundle, row_df)
    return float(bundle["cal"].predict_proba(X)[0, 1])


def local_linear_attributions(bundle, row_df: pd.DataFrame, top_k: int = 8) -> pd.DataFrame:
    X = transform_row(bundle, row_df)
    coef = bundle["base2"].coef_.ravel()
    contrib = X.ravel() * coef
    out = pd.DataFrame({"feature": bundle["feature_cols"], "contribution": contrib})
    out["abs"] = out["contribution"].abs()
    return out.sort_values("abs", ascending=False).head(top_k).drop(columns="abs")


def build_manual_row(bundle, form: dict) -> pd.DataFrame:
    row = {c: 0.0 for c in bundle["feature_cols"]}
    row["anchor_age"] = form["age"]
    row["los_hours"] = form["los_hours"]
    for lab in [
        "lab_creatinine",
        "lab_urea_nitrogen",
        "lab_potassium",
        "lab_sodium",
        "lab_chloride",
        "lab_bicarbonate",
        "lab_hemoglobin",
        "lab_platelet",
    ]:
        if lab in row:
            row[lab] = form.get(lab, np.nan)

    gender_col = f"gender_{form['gender']}" if form["gender"] != "Unknown" else "gender_nan"
    if gender_col in row:
        row[gender_col] = 1.0

    adm_col = (
        f"admission_type_{form['admission_type']}"
        if form["admission_type"] != "Unknown"
        else "admission_type_nan"
    )
    if adm_col in row:
        row[adm_col] = 1.0

    ins_col = (
        f"insurance_{form['insurance']}"
        if form["insurance"] != "Unknown"
        else "insurance_nan"
    )
    if ins_col in row:
        row[ins_col] = 1.0

    mar_col = (
        f"marital_status_{form['marital_status']}"
        if form["marital_status"] != "Unknown"
        else "marital_status_nan"
    )
    if mar_col in row:
        row[mar_col] = 1.0

    race_col = f"race_{form['race']}" if form["race"] != "Unknown" else "race_nan"
    if race_col in row:
        row[race_col] = 1.0

    return pd.DataFrame([row])


def risk_band(prob: float) -> tuple[str, str]:
    if prob >= 0.35:
        return "Elevated", "🔴"
    if prob >= 0.20:
        return "Moderate", "🟠"
    return "Lower", "🟢"


def format_patient_summary(row_meta: pd.Series) -> dict[str, str]:
    def _fmt(val, suffix=""):
        if pd.isna(val):
            return "—"
        if isinstance(val, float):
            return f"{val:.2f}{suffix}"
        return f"{val}{suffix}"

    return {
        "Age": _fmt(row_meta.get("anchor_age")),
        "Gender": _fmt(row_meta.get("gender")),
        "Creatinine": _fmt(row_meta.get("lab_creatinine")),
        "BUN": _fmt(row_meta.get("lab_urea_nitrogen")),
        "Admission type": _fmt(row_meta.get("admission_type")),
    }


def resolve_admission_index(bundle, hadm_input: int | None, index_input: int) -> tuple[int, bool]:
    """Return (row_index, hadm_lookup_succeeded)."""
    n = len(bundle["m2"]) - 1
    if hadm_input is not None and hadm_input in bundle["hadm_to_idx"]:
        return int(bundle["hadm_to_idx"][hadm_input]), True
    return int(min(max(index_input, 0), n)), False


def render_prediction(bundle, row_df: pd.DataFrame, true_label: int | None, meta: str):
    prob = predict_proba(bundle, row_df)
    thr = st.session_state.get("threshold", bundle["threshold"])
    flagged = prob >= thr
    band, icon = risk_band(prob)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calibrated CKD-related risk", f"{prob * 100:.1f}%")
    c2.metric("Risk band", f"{icon} {band}")
    c3.metric("Screening flag (≥ threshold)", "YES" if flagged else "NO")
    c4.metric("Decision threshold", f"{thr:.2f}")

    st.progress(min(max(prob, 0.0), 1.0), text=f"Calibrated probability vs threshold {thr:.2f}")
    st.caption(meta)
    if true_label is not None:
        label_txt = "Positive" if true_label == 1 else "Negative"
        st.caption(f"Dataset CKD proxy label (ICD): **{label_txt}** — for evaluation only, not clinical truth.")

    st.subheader("Local explanation (per-admission logistic contributions)")
    st.caption("Updates when you change index or hadm_id. For population-level SHAP, see the Global SHAP tab.")
    attr = local_linear_attributions(bundle, row_df)
    st.bar_chart(attr.set_index("feature")["contribution"], height=320)


def render_sidebar(bundle) -> None:
    with st.sidebar:
        st.header("Clinical settings")
        st.session_state["threshold"] = st.slider(
            "Decision threshold",
            0.05,
            0.95,
            float(bundle["threshold"]),
            0.01,
            help="Default from F1-optimal validation policy (step2_mimic_calibration_summary.csv).",
        )
        st.caption(f"Locked primary model: **{PRIMARY_MODEL}**")

        st.markdown("---")
        with st.expander("About this prototype", expanded=False):
            st.markdown(
                """
                This UI implements the **MIMIC clinical branch** only.

                - **NHANES** and **WESAD** are trained and evaluated offline in the supervisor notebook.
                - **Multimodal fusion** is a documented protocol (§14); not shown live here.
                - Outputs are **calibrated probabilities** plus **local/global explanations**.

                Use the **Example admission** tab for thesis screenshots.
                """
            )

        with st.expander("Developer / reproducibility", expanded=False):
            st.markdown("**Reporting lock**")
            st.json(bundle["reporting"] or {"note": "final_reporting_lock.json not found"})
            st.caption(f"Checkpoint: `{CHECKPOINT.name}`")


def render_example_tab(bundle) -> None:
    st.subheader("Browse cohort admissions")
    st.caption(
        "Search by hospital admission ID (`hadm_id`) or use the row index. "
        f"Default index **{DEFAULT_ADMISSION_INDEX}** (`hadm_id={DEMO_HADM_ID}`) is a CKD-proxy "
        "positive example with creatinine/BUN available for demonstration."
    )

    m2 = bundle["m2"]
    X2_df = bundle["X2_df"]
    n_max = len(m2) - 1

    if "hadm_search" not in st.session_state:
        st.session_state["hadm_search"] = ""

    col_a, col_b = st.columns([2, 1])
    with col_a:
        demo_col, inp_col = st.columns([1.2, 2.8])
        with demo_col:
            if st.button("Demo ID", help=f"Load hadm_id {DEMO_HADM_ID} (CKD-proxy positive, labs present)"):
                st.session_state["hadm_search"] = DEMO_HADM_ID
        with inp_col:
            hadm_text = st.text_input(
                "Search by hadm_id (optional)",
                key="hadm_search",
                placeholder=f"e.g. {DEMO_HADM_ID} — leave blank to use index",
                help="MIMIC admission IDs are large integers (typically 8 digits). "
                "Leave empty and use the index control below.",
            )
    with col_b:
        idx = st.number_input(
            f"Admission index (0–{n_max})",
            min_value=0,
            max_value=n_max,
            value=DEFAULT_ADMISSION_INDEX,
            step=1,
        )

    hadm_query: int | None = None
    if hadm_text.strip():
        try:
            hadm_query = int(hadm_text.strip())
        except ValueError:
            st.warning("hadm_id must be numeric. Showing admission by index instead.")

    resolved_idx, hadm_found = resolve_admission_index(bundle, hadm_query, int(idx))
    if hadm_query is not None and not hadm_found:
        st.warning(
            f"No admission with hadm_id={hadm_query}. "
            f"Showing index **{int(idx)}** instead (example: **{DEMO_HADM_ID}**)."
        )

    row_meta = m2.iloc[resolved_idx]
    row_df = X2_df.iloc[[resolved_idx]]
    summary = format_patient_summary(row_meta)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Age", summary["Age"])
    s2.metric("Gender", summary["Gender"])
    s3.metric("Creatinine", summary["Creatinine"])
    s4.metric("BUN", summary["BUN"])
    s5.metric("Admission type", summary["Admission type"][:18] + ("…" if len(summary["Admission type"]) > 18 else ""))

    meta = (
        f"hadm_id={row_meta.get('hadm_id', '—')} · "
        f"subject_id={row_meta.get('subject_id', '—')} · "
        f"resolved index={resolved_idx}"
    )
    true_label = (
        int(row_meta.get("ckd_label"))
        if pd.notna(row_meta.get("ckd_label"))
        else None
    )
    render_prediction(bundle, row_df, true_label, meta)


def render_manual_tab(bundle) -> None:
    st.subheader("Simplified admission form")
    st.info(
        "Illustrative entry only: unspecified features default to zero. "
        "Use **Example admission** for faithful cohort cases."
    )
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age (anchor_age)", 18, 95, 65)
        los = st.number_input("Length of stay (hours)", 0.0, 500.0, 48.0)
        gender = st.selectbox("Gender", ["M", "F", "Unknown"])
        admission_type = st.selectbox("Admission type", ["Unknown"] + ADMISSION_TYPES)
        insurance = st.selectbox("Insurance", ["Unknown"] + INSURANCE_OPTIONS)
    with col_b:
        marital = st.selectbox("Marital status", ["Unknown"] + MARITAL_OPTIONS)
        race = st.selectbox("Race", ["Unknown"] + RACE_OPTIONS)
        st.markdown("**Admission labs (optional)**")
        cr = st.number_input("Creatinine", 0.0, 20.0, 1.2)
        bun = st.number_input("Urea nitrogen (BUN)", 0.0, 200.0, 18.0)
        k = st.number_input("Potassium", 0.0, 10.0, 4.0)
        na = st.number_input("Sodium", 100.0, 180.0, 140.0)

    if st.button("Estimate risk", type="primary"):
        form = {
            "age": age,
            "los_hours": los,
            "gender": gender,
            "admission_type": admission_type,
            "insurance": insurance,
            "marital_status": marital,
            "race": race,
            "lab_creatinine": cr,
            "lab_urea_nitrogen": bun,
            "lab_potassium": k,
            "lab_sodium": na,
            "lab_chloride": np.nan,
            "lab_bicarbonate": np.nan,
            "lab_hemoglobin": np.nan,
            "lab_platelet": np.nan,
        }
        row_df = build_manual_row(bundle, form)
        render_prediction(bundle, row_df, None, "Manual prototype entry (partial feature vector)")


def render_shap_tab(bundle) -> None:
    st.subheader("Global SHAP — MIMIC held-out test set (fixed summary)")
    st.caption(
        "Mean |SHAP| over the test cohort, computed once in notebook §15B. "
        "This chart does **not** change per admission; use **Example admission** for case-level explanations."
    )
    if bundle["shap_df"] is None:
        st.warning(f"Run notebook cell 15B first. Expected: {SHAP_CSV}")
    else:
        st.bar_chart(bundle["shap_df"].set_index("feature")["mean_abs_shap"], height=360)
        st.caption(f"Source: `{SHAP_CSV.name}` · model: `{PRIMARY_MODEL}`")


def main():
    st.set_page_config(
        page_title="CKD Risk CDS Prototype",
        page_icon="🫀",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()
    render_hero()

    try:
        bundle = load_bundle()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    render_sidebar(bundle)

    tab_ex, tab_manual, tab_global = st.tabs(
        ["Example admission", "Manual entry", "Global SHAP (test set summary)"]
    )

    with tab_ex:
        render_example_tab(bundle)
    with tab_manual:
        render_manual_tab(bundle)
    with tab_global:
        render_shap_tab(bundle)


if __name__ == "__main__":
    main()
