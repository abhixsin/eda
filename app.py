import io
import html
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).with_name("achive.csv")
MAX_CATEGORIES = 20

st.set_page_config(
    page_title="ChurnIQ | Retention intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

with st.sidebar:
    theme_choice = st.radio("Appearance", ["Light", "Dark"], horizontal=True, index=1)

theme_palettes = {
    "Light": {
        "app_bg": "#f3f5f8",
        "surface": "#ffffff",
        "text": "#202b3c",
        "muted": "#526174",
        "border": "#dfe5ec",
        "sidebar": "#1d2939",
        "sidebar_text": "#e7edf4",
        "field_bg": "#f8fafc",
        "field_text": "#202b3c",
        "hero": "linear-gradient(115deg, #1d2939 0%, #294457 68%, #3b696c 100%)",
        "hero_text": "#f8fafc",
        "hero_muted": "#d3dee6",
        "grid": "#e4e9ef",
        "accent_scale": ["#c4d2d3", "#7d9996", "#bd775d"],
    },
    "Dark": {
        "app_bg": "#090b0c",
        "surface": "#15191a",
        "text": "#f0f2f0",
        "muted": "#a0a6a2",
        "border": "#303636",
        "sidebar": "#101415",
        "sidebar_text": "#e6ebe7",
        "field_bg": "#202626",
        "field_text": "#f1f5f9",
        "hero": "linear-gradient(115deg, #111515 0%, #131b19 62%, #1a2821 100%)",
        "hero_text": "#f0f2f0",
        "hero_muted": "#b7c1bc",
        "grid": "#303636",
        "accent_scale": ["#40544c", "#718b7c", "#a8ffbf"],
    },
}
palette = theme_palettes[theme_choice]

st.markdown(
    """
    <style>
    .stApp { background: #f3f5f8; color: #202b3c; }
    .block-container { max-width: 1200px; padding-top: 1.2rem; padding-bottom: 4rem; }
    [data-testid="stAppViewContainer"] { background: #f3f5f8; }
    [data-testid="stMain"] { scroll-behavior: smooth; scroll-padding-top: 24px; }
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stSidebar"] { background: #1d2939; }
    [data-testid="stSidebar"] * { color: #e7edf4; }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: #27364a; border: 1px solid #46566b; border-radius: 12px;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: #27364a; border: 1px dashed #64748b;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
        color: #e7edf4 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: #394b61; border-color: #64748b; color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #f8fafc; border-color: #94a3b8;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #202b3c !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #dce5ed;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] * {
        color: #202b3c !important;
    }
    [data-testid="stSidebar"] input {
        color: #202b3c !important;
    }
    .hero {
        background: linear-gradient(115deg, #1d2939 0%, #294457 68%, #3b696c 100%);
        border-radius: 22px; padding: 30px 34px; margin: 0 0 22px;
        color: #f8fafc; box-shadow: 0 12px 28px rgba(29, 41, 57, .13);
    }
    .hero-kicker {
        color: #b7d8d1; font-size: 11px; font-weight: 800;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 9px;
    }
    .hero-title {
        color: #f8fafc; font-size: clamp(28px, 4vw, 40px); font-weight: 800;
        letter-spacing: -1.2px; line-height: 1.1; margin: 0 0 10px;
    }
    .hero-copy { color: #d9e3ea; font-size: 15px; margin: 0; max-width: 720px; }
    .insight-card {
        background: #fff; border: 1px solid #dfe5ec; border-left: 5px solid #bd775d;
        border-radius: 15px; padding: 17px 20px; margin: 5px 0 18px;
        box-shadow: 0 5px 16px rgba(29, 41, 57, .04);
    }
    .insight-label {
        color: #64748b; font-size: 11px; font-weight: 800;
        letter-spacing: 1px; text-transform: uppercase;
    }
    .insight-title { color: #202b3c; font-size: 19px; font-weight: 800; margin-top: 5px; }
    .insight-detail { color: #526174; font-size: 13px; margin-top: 4px; }
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid #dfe5ec; border-radius: 15px;
        padding: 16px 18px; box-shadow: 0 5px 16px rgba(29, 41, 57, .035);
    }
    [data-testid="stMetricLabel"] { color: #64748b; font-weight: 650; }
    [data-testid="stMetricValue"] { color: #202b3c; }
    [data-testid="stDataFrame"] { border: 1px solid #dfe5ec; border-radius: 12px; }
    div[data-testid="stDownloadButton"] > button {
        background: #426d70; color: #fff; border: 0; border-radius: 10px; font-weight: 700;
    }
    div[data-testid="stDownloadButton"] > button:hover { background: #34585b; color: #fff; }
    h2, h3 { letter-spacing: -.3px; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <style>
    .stApp {{ background: {palette["app_bg"]}; color: {palette["text"]}; }}
    [data-testid="stAppViewContainer"] {{ background: {palette["app_bg"]}; }}
    [data-testid="stMain"] {{ scroll-behavior: smooth; scroll-padding-top: 24px; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{ background: {palette["sidebar"]}; }}
    [data-testid="stSidebar"] * {{ color: {palette["sidebar_text"]}; }}
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stTextInput"] input {{
        background: {palette["field_bg"]}; color: {palette["field_text"]} !important;
        border-color: {palette["border"]};
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="tag"] * {{
        color: {palette["field_text"]} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="tag"] {{ background: {palette["border"]}; }}
    [data-testid="stSidebar"] [data-testid="stFileUploader"],
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background: {palette["field_bg"]}; border-color: {palette["border"]};
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {{
        color: {palette["field_text"]} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stWidgetLabel"] * {{
        color: {palette["field_text"]} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {{
        color: {palette["field_text"]} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {{
        background: {palette["sidebar"]}; color: {palette["sidebar_text"]} !important;
        border-color: {palette["border"]};
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {{
        color: {palette["sidebar_text"]} !important;
    }}
    .hero {{
        position: relative; overflow: hidden; isolation: isolate;
        background: {palette["hero"]}; color: {palette["text"]};
        border: 1px solid {palette["border"]}; border-radius: 28px;
        padding: clamp(30px, 6vw, 72px); margin: 22px 0 24px;
        box-shadow: 0 24px 80px rgba(0, 0, 0, .18);
        animation: enter-view .55s ease-out both;
    }}
    .hero::after {{
        content: ""; position: absolute; z-index: -1; inset: 42% 0 0;
        background-image: radial-gradient(circle, {palette["muted"]} 1px, transparent 1.5px);
        background-size: 19px 19px; opacity: .2;
        mask-image: linear-gradient(to bottom, transparent, black);
        pointer-events: none;
    }}
    .hero-kicker {{
        color: #a8ffbf; font-size: 11px; font-weight: 750;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 15px;
    }}
    .hero-title {{
        color: {palette["hero_text"]}; font-size: clamp(38px, 7vw, 76px);
        font-weight: 650; letter-spacing: clamp(-3.4px, -.055em, -1.5px);
        line-height: 1.03; max-width: 900px; margin: 0 0 18px;
        font-size: clamp(2.8rem, 8.5vw, 7.4rem);
    }}
    .hero-line {{
        display: block; overflow: clip; padding: 0 .04em .08em 0;
    }}
    .hero-line-inner {{
        display: inline-block; transform: translateY(115%);
        clip-path: inset(0 0 100% 0); font-weight: 650;
        background: linear-gradient(100deg, {palette["hero_text"]} 5%, {palette["hero_muted"]} 94%);
        -webkit-background-clip: text; background-clip: text;
        color: transparent !important; -webkit-text-fill-color: transparent;
    }}
    .hero-line:nth-child(2) .hero-line-inner {{ font-weight: 500; }}
    .hero.motion-ready.is-visible .hero-line-inner {{
        animation: headline-reveal .95s cubic-bezier(.2, .75, .25, 1) forwards;
    }}
    .hero.motion-ready.is-visible .hero-line:nth-child(2) .hero-line-inner {{
        animation-delay: .14s;
    }}
    .hero-title span {{
        font-weight: 500;
    }}
    .hero-copy {{
        color: {palette["hero_muted"]}; font-size: 16px;
        line-height: 1.65; max-width: 620px; margin: 0;
    }}
    .hero-signals {{
        display: flex; flex-wrap: wrap; gap: 9px; margin-top: 25px;
    }}
    .hero-signals span {{
        padding: 9px 13px; border: 1px solid {palette["border"]};
        border-radius: 999px; background: rgba(255,255,255,.035);
        color: {palette["hero_muted"]}; font-size: 12px;
    }}
    .hero-signals strong {{ color: {palette["hero_text"]}; font-weight: 750; }}
    .hero-signals strong, [data-testid="stMetricValue"] {{
        display: inline-block; font-variant-numeric: tabular-nums;
    }}
    .top-nav {{
        position: sticky; top: 12px; z-index: 99;
        display: flex; align-items: center; justify-content: space-between;
        max-width: 620px; margin: 0 auto 34px; padding: 9px 10px 9px 20px;
        border: 1px solid {palette["border"]}; border-radius: 999px;
        background: color-mix(in srgb, {palette["surface"]} 88%, transparent);
        backdrop-filter: blur(18px); box-shadow: 0 8px 28px rgba(0,0,0,.12);
    }}
    .nav-brand {{
        display: inline-flex; align-items: center; gap: 10px;
        color: {palette["text"]} !important; font-size: 17px; font-weight: 750;
        text-decoration: none !important;
    }}
    .nav-mark {{
        width: 18px; height: 18px; border: 2px solid #a8ffbf;
        border-radius: 50%; box-shadow: inset 6px 0 0 {palette["surface"]};
    }}
    .nav-links {{ display: flex; align-items: center; gap: 22px; }}
    .nav-links a {{
        color: {palette["muted"]} !important; font-size: 13px; font-weight: 600;
        text-decoration: none !important; transition: color .18s ease;
    }}
    .nav-links a:hover {{ color: {palette["text"]} !important; }}
    .nav-cta {{
        padding: 11px 17px; border-radius: 999px; background: #f3f5f2;
        color: #111615 !important; font-weight: 700 !important;
    }}
    .scenario-shell {{
        padding: 22px; margin: 0 0 22px; border-radius: 22px;
        border: 1px solid {palette["border"]}; background: {palette["surface"]};
        box-shadow: 0 16px 44px rgba(0,0,0,.1);
    }}
    .scenario-eyebrow {{
        color: #a8ffbf; font-size: 11px; font-weight: 750;
        letter-spacing: 1.4px; text-transform: uppercase; margin-bottom: 7px;
    }}
    .scenario-title {{
        color: {palette["text"]}; font-size: clamp(18px, 3vw, 24px);
        font-weight: 650; letter-spacing: -.5px; margin: 0 0 4px;
    }}
    .scenario-copy {{ color: {palette["muted"]}; font-size: 13px; margin: 0; }}
    [data-testid="stForm"] {{
        border: 1px solid {palette["border"]}; border-radius: 16px;
        padding: 14px; background: {palette["app_bg"]};
    }}
    [data-testid="stFormSubmitButton"] button {{
        background: #a8ffbf !important; color: #101713 !important; border: 0;
        border-radius: 999px; font-weight: 750; min-height: 44px;
        transition: transform .18s ease, box-shadow .18s ease;
    }}
    [data-testid="stFormSubmitButton"] button p {{
        color: #101713 !important; font-weight: 750;
    }}
    [data-testid="stFormSubmitButton"] button:hover {{
        background: #c1ffd0 !important; color: #101713 !important;
        transform: translateY(-1px); box-shadow: 0 5px 18px rgba(168,255,191,.18);
    }}
    [data-testid="stMetric"] {{ border-radius: 18px; }}
    [data-testid="stMetricValue"] {{
        letter-spacing: -.7px; font-size: clamp(1.75rem, 3.5vw, 2.45rem);
    }}
    .scroll-reveal {{
        opacity: .01; transform: translateY(28px); filter: blur(2px);
        transition: opacity .72s cubic-bezier(.2,.7,.2,1),
                    transform .72s cubic-bezier(.2,.7,.2,1),
                    filter .72s cubic-bezier(.2,.7,.2,1);
        will-change: opacity, transform;
    }}
    .scroll-reveal.is-visible {{
        opacity: 1; transform: translateY(0); filter: blur(0);
    }}
    .journey-rail {{
        position: fixed; z-index: 20; right: 12px; top: 28vh;
        width: 38px; height: 48vh; overflow: visible;
        pointer-events: none; opacity: .72;
        filter: drop-shadow(0 0 5px rgba(168,255,191,.2));
    }}
    .journey-track, .journey-progress {{
        fill: none; stroke-linecap: round; stroke-linejoin: round;
        vector-effect: non-scaling-stroke;
    }}
    .journey-track {{ stroke: {palette["border"]}; stroke-width: 1.5; }}
    .journey-progress {{
        stroke: #a8ffbf; stroke-width: 2;
        stroke-dasharray: 1; stroke-dashoffset: 1;
    }}
    .journey-node {{
        fill: {palette["app_bg"]}; stroke: #a8ffbf; stroke-width: 2;
    }}
    .journey-node.is-current {{
        fill: #a8ffbf; filter: drop-shadow(0 0 5px #a8ffbf);
    }}
    @media (max-width: 640px) {{
        .top-nav {{ margin-bottom: 20px; padding-left: 15px; }}
        .nav-links {{ gap: 12px; }}
        .nav-links a {{ font-size: 11px; }}
        .nav-links .nav-optional {{ display: none; }}
        .hero-title {{ letter-spacing: -1.7px; }}
    }}
    @media (max-width: 900px) {{
        .journey-rail {{ right: 3px; width: 25px; height: 34vh; opacity: .45; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
        [data-testid="stMain"] {{ scroll-behavior: auto; }}
        .scroll-reveal {{ opacity: 1; transform: none; filter: none; transition: none; }}
        .hero-line-inner {{ transform: none; clip-path: none; }}
        .hero.motion-ready.is-visible .hero-line-inner {{ animation: none; }}
        .journey-progress {{ stroke-dashoffset: 0 !important; }}
        [data-testid="stMetricValue"], .hero-signals strong {{ transform: none !important; }}
    }}
    @keyframes headline-reveal {{
        0% {{ transform: translateY(115%); clip-path: inset(0 0 100% 0); }}
        100% {{ transform: translateY(0); clip-path: inset(0 0 0 0); }}
    }}
    .insight-card, [data-testid="stMetric"] {{
        background: {palette["surface"]}; border-color: {palette["border"]};
        transition: transform .18s ease, box-shadow .18s ease;
    }}
    .insight-card {{ border-left-color: #bd775d; }}
    .insight-card.positive {{ border-left-color: #668f83; }}
    .insight-label, [data-testid="stMetricLabel"] {{ color: {palette["muted"]}; }}
    .insight-title, [data-testid="stMetricValue"] {{ color: {palette["text"]}; }}
    .insight-detail {{ color: {palette["muted"]}; }}
    [data-testid="stDataFrame"] {{ border-color: {palette["border"]}; }}
    [data-testid="stDataFrame"] .stDataFrameGlideDataEditor {{
        --gdg-bg-cell: {palette["surface"]} !important;
        --gdg-bg-cell-medium: {palette["surface"]} !important;
        --gdg-bg-header: {palette["app_bg"]} !important;
        --gdg-bg-header-hovered: {palette["border"]} !important;
        --gdg-bg-header-has-focus: {palette["border"]} !important;
        --gdg-bg-group-header: {palette["app_bg"]} !important;
        --gdg-bg-group-header-hovered: {palette["border"]} !important;
        --gdg-bg-bubble: {palette["surface"]} !important;
        --gdg-bg-bubble-selected: {palette["surface"]} !important;
        
        --gdg-text-dark: {palette["text"]} !important;
        --gdg-text-medium: {palette["muted"]} !important;
        --gdg-text-light: {palette["muted"]} !important;
        --gdg-text-bubble: {palette["muted"]} !important;
        --gdg-border-color: {palette["border"]} !important;
        --gdg-horizontal-border-color: {palette["border"]} !important;
    }}
    h1, h2, h3, p, label {{ color: {palette["text"]}; }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {{ color: {palette["sidebar_text"]}; }}
    @keyframes enter-view {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    [data-testid="stMetric"]:hover, .insight-card:hover {{
        transform: translateY(-2px); box-shadow: 0 9px 22px rgba(20, 35, 50, .12);
    }}
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: .01ms !important; transition-duration: .01ms !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def load_data(uploaded_file):
    """Load the selected CSV, trying common encodings for uploaded files."""
    if uploaded_file is None:
        if not DATA_PATH.is_file():
            raise FileNotFoundError(f"The included sample dataset was not found: {DATA_PATH}")
        raw_data = DATA_PATH.read_bytes()
    else:
        raw_data = uploaded_file.getvalue()

    errors = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(raw_data), encoding=encoding)
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            errors.append(f"{encoding}: {exc}")

    details = errors[-1] if errors else "The file is empty or not a valid CSV."
    raise ValueError(f"Could not read the CSV. Check the file format. {details}")


def prepare_data(frame):
    """Convert columns containing numeric text so they can be analyzed."""
    data = frame.copy()
    for column in data.select_dtypes(include=["object", "string"]).columns:
        text = data[column].astype("string").str.strip().replace("", pd.NA)
        converted = pd.to_numeric(text, errors="coerce")
        nonempty = text.notna()
        if nonempty.any() and converted[nonempty].notna().mean() >= 0.95:
            data[column] = converted
    return data


def detect_target(columns):
    return next(
        (column for column in columns if re.search(r"churn|target|label|outcome", str(column), re.I)),
        columns[-1],
    )


def detect_positive_label(labels):
    return next(
        (
            label
            for label in labels
            if re.search(r"yes|churn|left|true|positive|cancel|^1$", str(label), re.I)
        ),
        labels[0],
    )


def make_risk_report(data, target_column, positive_label):
    """Summarize churn rate by categorical groups and numeric quartiles."""
    valid = data[target_column].notna()
    analyzed = data.loc[valid].copy()
    if analyzed.empty:
        return pd.DataFrame(), 0.0, 0

    churned = analyzed[target_column].astype(str).eq(str(positive_label)).astype(int)
    overall_rate = float(np.mean(churned.to_numpy()) * 100)
    analyzed["_churned"] = churned.to_numpy()
    min_group_size = max(5, math.ceil(len(analyzed) * 0.01))
    report_rows = []

    for column in data.columns:
        if column == target_column:
            continue

        values = analyzed[column]
        unique_count = values.nunique(dropna=True)
        if unique_count == 0:
            continue

        if unique_count <= MAX_CATEGORIES:
            segments = values.astype("string").fillna("(Missing)")
        elif pd.api.types.is_numeric_dtype(values):
            try:
                segments = pd.qcut(values, q=4, duplicates="drop").astype("string")
            except ValueError:
                continue
            segments = segments.fillna("(Missing)")
        else:
            continue

        grouped = (
            pd.DataFrame({"Segment": segments, "Churned": analyzed["_churned"]})
            .groupby("Segment", dropna=False)["Churned"]
            .agg(Customers="size", Churned_count="sum", Churn_rate="mean")
            .reset_index()
        )
        for row in grouped.itertuples(index=False):
            if row.Customers < min_group_size:
                continue
            rate = float(row.Churn_rate * 100)
            report_rows.append(
                {
                    "Factor": column,
                    "Segment": row.Segment,
                    "Customers": int(row.Customers),
                    "Churned": int(row.Churned_count),
                    "Churn rate (%)": round(rate, 2),
                    "vs overall (pp)": round(rate - overall_rate, 2),
                }
            )

    report = pd.DataFrame(
        report_rows,
        columns=["Factor", "Segment", "Customers", "Churned", "Churn rate (%)", "vs overall (pp)"],
    )
    if not report.empty:
        report = report.sort_values(
            ["vs overall (pp)", "Customers"], ascending=[False, False]
        ).reset_index(drop=True)
    return report, overall_rate, min_group_size


def build_markdown_report(
    report,
    data,
    dataset_name,
    target_column,
    positive_label,
    churn_rate,
    filter_description,
):
    """Create a portable Markdown summary for the current dashboard analysis."""
    valid_count = int(data[target_column].notna().sum())
    churned_count = int(
        data[target_column].astype("string").eq(str(positive_label)).sum()
    )
    missing_count = int(data.isna().sum().sum())
    lines = [
        "# Customer churn analysis",
        "",
        f"- **Dataset:** {dataset_name}",
        f"- **Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **Outcome:** {target_column} = {positive_label}",
        f"- **Filter:** {filter_description}",
        "",
        "## Summary",
        "",
        f"- Customers with an outcome value: **{valid_count:,}**",
        f"- Customers marked as churned: **{churned_count:,}**",
        f"- Churn rate: **{churn_rate:.2f}%**",
        f"- Columns: **{len(data.columns):,}**",
        f"- Missing cells: **{missing_count:,}**",
        "",
        "## Highest-risk segments",
        "",
    ]
    if report.empty:
        lines.append("No customer segments met the minimum group-size threshold.")
    else:
        lines.extend(
            [
                "| Factor | Segment | Customers | Churned | Churn rate (%) | vs overall (pp) |",
                "|---|---|---:|---:|---:|---:|",
            ]
        )
        for row in report.head(15).itertuples(index=False):
            factor = str(row[0]).replace("|", "\\|").replace("\n", " ")
            segment = str(row[1]).replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {factor} | {segment} | {row[2]:,} | {row[3]:,} | "
                f"{row[4]:.2f} | {row[5]:+.2f} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Segment differences are exploratory associations, not proof of cause "
            "or a predictive model. Validate findings before making business decisions.",
            "",
        ]
    )
    return "\n".join(lines)


st.markdown(
    """
    <nav class="top-nav" aria-label="Main navigation">
      <a class="nav-brand" href="#top"><span class="nav-mark"></span> ChurnIQ</a>
      <div class="nav-links">
        <a class="nav-optional" href="#insights">Insights</a>
        <a href="#explore">Explore</a>
        <a class="nav-cta" href="#simulator">Run a scenario&nbsp; ↗</a>
      </div>
    </nav>
    <div id="top"></div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ◈ Retention Insights")
    st.caption("CUSTOMER CHURN ANALYSIS")
    st.divider()
    st.markdown("### Choose your data")
    uploaded_file = st.file_uploader("Upload a CSV (optional)", type=["csv"])
    st.caption("The included sample loads automatically when no file is uploaded.")

try:
    raw_data = load_data(uploaded_file)
except (FileNotFoundError, ValueError) as exc:
    st.error(str(exc))
    st.stop()

if raw_data.empty:
    st.error("The selected CSV has no data rows.")
    st.stop()

data = prepare_data(raw_data)
target_default = detect_target(data.columns)

with st.sidebar:
    st.markdown("### Analysis settings")
    target_column = st.selectbox(
        "Outcome column",
        options=list(data.columns),
        index=list(data.columns).index(target_default),
    )

target_labels = data[target_column].dropna().astype(str).unique().tolist()
if not target_labels:
    st.error(f"The selected target column, '{target_column}', has no values to analyze.")
    st.stop()

positive_default = detect_positive_label(target_labels)
with st.sidebar:
    positive_label = st.selectbox(
        "Value representing churn",
        options=target_labels,
        index=target_labels.index(positive_default),
    )

filterable_columns = [
    column
    for column in data.columns
    if column != target_column and data[column].nunique(dropna=True) <= MAX_CATEGORIES
]
with st.sidebar:
    st.markdown("### Segment filter")
    filter_options = ["(No filter)"] + filterable_columns
    filter_column = st.selectbox("Filter by", options=filter_options)
    if filter_column == "(No filter)":
        selected_values = []
    else:
        available_values = (
            data[filter_column].astype("string").fillna("(Missing)").unique().tolist()
        )
        selected_values = st.multiselect(
            "Keep values",
            options=available_values,
            default=available_values,
            help="Clear the selection to include every value.",
        )
    st.markdown("### Chart")
    top_segment_count = st.slider("Segments to show", min_value=5, max_value=12, value=8)
    chart_ranking = st.selectbox(
        "Rank chart by",
        options=["Churn rate (%)", "vs overall (pp)"],
    )

analysis_data = data
filter_description = "None"
if filter_column != "(No filter)" and selected_values:
    filter_values = data[filter_column].astype("string").fillna("(Missing)")
    analysis_data = data.loc[filter_values.isin(selected_values)].copy()
    filter_description = f"{filter_column}: {', '.join(selected_values)}"
elif filter_column != "(No filter)":
    filter_description = f"{filter_column}: all values"

if analysis_data.empty:
    st.warning("No rows match the selected filter. Choose at least one value to continue.")
    st.stop()

risk_report, churn_rate, min_group_size = make_risk_report(
    analysis_data, target_column, positive_label
)
churned_count = int(
    analysis_data[target_column].astype("string").eq(str(positive_label)).sum()
)
valid_count = int(analysis_data[target_column].notna().sum())

dataset_name = uploaded_file.name if uploaded_file else DATA_PATH.name
top_lift = (
    float(risk_report.iloc[0]["vs overall (pp)"])
    if not risk_report.empty
    else 0.0
)
st.markdown(
    f"""
    <section class="hero">
      <div class="hero-kicker">Retention intelligence&nbsp; · &nbsp;live analysis</div>
      <h1 class="hero-title">
        <span class="hero-line"><span class="hero-line-inner">Make the next move</span></span>
        <span class="hero-line"><span class="hero-line-inner">with a clearer signal.</span></span>
      </h1>
      <p class="hero-copy">
        Explore what is happening across your customer base, then test a retention
        assumption against the patterns in your data.
      </p>
      <div class="hero-signals">
        <span>Current churn&nbsp; <strong>{churn_rate:.1f}%</strong></span>
        <span>Highest segment lift&nbsp; <strong>{top_lift:+.1f} pp</strong></span>
        <span>Customers analyzed&nbsp; <strong>{valid_count:,}</strong></span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)
st.caption(
    f"**Dataset:** {html.escape(dataset_name)}  ·  "
    f"**Outcome:** {html.escape(str(target_column))} = {html.escape(str(positive_label))}  ·  "
    f"**Rows in view:** {len(analysis_data):,}"
)

st.markdown(
    """
    <section class="scenario-shell" id="simulator">
      <div class="scenario-eyebrow">Decision simulator</div>
      <h2 class="scenario-title">What if we reduced churn in a customer segment?</h2>
      <p class="scenario-copy">
        Test a relative reduction assumption against observed segment churn.
        This is a scenario estimate, not a causal forecast.
      </p>
    </section>
    """,
    unsafe_allow_html=True,
)
if risk_report.empty:
    st.info("A scenario can be run after at least one segment meets the group-size threshold.")
else:
    with st.form("churn_scenario_form"):
        scenario_controls = st.columns([3, 2, 1])
        scenario_index = scenario_controls[0].selectbox(
            "Customer segment",
            options=list(range(len(risk_report))),
            format_func=lambda index: (
                f"{risk_report.iloc[index]['Factor']} · {risk_report.iloc[index]['Segment']} "
                f"({risk_report.iloc[index]['Churn rate (%)']:.1f}%)"
            ),
        )
        reduction_percent = scenario_controls[1].slider(
            "Assumed relative churn reduction",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            format="%d%%",
        )
        scenario_submitted = scenario_controls[2].form_submit_button(
            "Simulate  ↗", use_container_width=True
        )

    scenario_row = risk_report.iloc[scenario_index]
    scenario_signature = (
        dataset_name,
        str(target_column),
        str(positive_label),
        filter_description,
        str(scenario_row["Factor"]),
        str(scenario_row["Segment"]),
        reduction_percent,
        valid_count,
        churned_count,
    )
    if scenario_submitted:
        estimated_prevented = float(scenario_row["Churned"]) * reduction_percent / 100
        projected_churn_rate = max(
            0.0, (churned_count - estimated_prevented) / valid_count * 100
        ) if valid_count else 0.0
        st.session_state["churn_scenario_result"] = {
            "signature": scenario_signature,
            "estimated_prevented": estimated_prevented,
            "projected_rate": projected_churn_rate,
        }

    scenario_result = st.session_state.get("churn_scenario_result")
    if scenario_result and scenario_result["signature"] == scenario_signature:
        result_columns = st.columns(3)
        result_columns[0].metric(
            "Estimated fewer churners",
            f"{scenario_result['estimated_prevented']:.0f}",
            help="Observed churn count in the selected segment × the assumed relative reduction.",
        )
        result_columns[1].metric(
            "Scenario churn rate",
            f"{scenario_result['projected_rate']:.2f}%",
            f"{scenario_result['projected_rate'] - churn_rate:+.2f} pp vs. current",
        )
        result_columns[2].metric(
            "Segment in scenario",
            f"{int(scenario_row['Customers']):,}",
            f"{scenario_row['Churn rate (%)']:.1f}% observed churn",
        )
        st.caption(
            "Illustrative arithmetic only: assumes the selected segment achieves the "
            "chosen relative reduction. It does not estimate intervention effectiveness."
        )
    else:
        st.caption(
            f"Choose a segment and assumption, then run the scenario. Current analysis: "
            f"{html.escape(dataset_name)} · {html.escape(filter_description)}."
        )

metric_columns = st.columns(5)
metric_columns[0].metric("Analyzed", f"{valid_count:,}")
metric_columns[1].metric("Churned", f"{churned_count:,}")
metric_columns[2].metric("Churn rate", f"{churn_rate:.1f}%")
metric_columns[3].metric("Segments", f"{len(risk_report):,}")
metric_columns[4].metric("Missing cells", f"{int(analysis_data.isna().sum().sum()):,}")

st.subheader("Where churn risk is highest")
st.markdown('<div id="insights"></div>', unsafe_allow_html=True)
st.caption(
    f"Segments with at least {min_group_size} customers are ranked against the overall "
    "churn rate. Use these patterns as a starting point for investigation, not as proof of cause."
)

if risk_report.empty:
    st.info("No suitable customer groups were found to compare.")
else:
    top_risk = risk_report.iloc[0]
    lowest_risk = risk_report.sort_values("Churn rate (%)").iloc[0]
    insight_columns = st.columns(2)
    with insight_columns[0]:
        st.markdown(
            f"""
            <div class="insight-card">
              <div class="insight-label">Highest churn segment</div>
              <div class="insight-title">{html.escape(str(top_risk['Factor']))} ·
                {html.escape(str(top_risk['Segment']))} — {top_risk['Churn rate (%)']:.1f}% churn
              </div>
              <div class="insight-detail">
                {top_risk['Customers']:,} customers · {top_risk['Churned']:,} churned ·
                {top_risk['vs overall (pp)']:+.1f} percentage points vs. overall
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with insight_columns[1]:
        st.markdown(
            f"""
            <div class="insight-card positive">
              <div class="insight-label">Lowest churn segment</div>
              <div class="insight-title">{html.escape(str(lowest_risk['Factor']))} ·
                {html.escape(str(lowest_risk['Segment']))} — {lowest_risk['Churn rate (%)']:.1f}% churn
              </div>
              <div class="insight-detail">
                {lowest_risk['Customers']:,} customers · {lowest_risk['Churned']:,} churned ·
                {lowest_risk['vs overall (pp)']:+.1f} percentage points vs. overall
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    chart_data = risk_report.sort_values(
        chart_ranking, ascending=False
    ).head(top_segment_count).copy()
    chart_data["Customer segment"] = chart_data.apply(
        lambda row: f"{row['Factor']} · {row['Segment']}", axis=1
    )
    chart_data = chart_data.sort_values("Churn rate (%)")
    chart = px.bar(
        chart_data,
        x="Customer segment",
        y="Churn rate (%)",
        color="vs overall (pp)",
        hover_data=["Customers", "Churned", "vs overall (pp)"],
        title=f"Top {len(chart_data)} segments by {chart_ranking}",
        text="Churn rate (%)",
        color_continuous_scale=palette["accent_scale"],
    )
    chart.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
    )
    chart.add_hline(
        y=churn_rate,
        line_dash="dash",
        line_color=palette["muted"],
        annotation_text=f"Overall {churn_rate:.1f}%",
        annotation_position="top left",
        annotation_font_color=palette["muted"],
    )
    chart.update_layout(
        xaxis_title=None,
        yaxis_title="Customers who churned (%)",
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": palette["text"]},
        xaxis={"tickangle": -32, "automargin": True},
        yaxis={"gridcolor": palette["grid"], "rangemode": "tozero"},
        margin={"l": 18, "r": 25, "t": 55, "b": 110},
        height=520,
        transition={"duration": 450, "easing": "cubic-in-out"},
    )
    st.plotly_chart(chart, width="stretch")
    st.markdown('<div id="explore"></div>', unsafe_allow_html=True)
    st.subheader("Explore customer segments")
    st.caption("Search factors or segment labels to narrow the report table.")
    report_search = st.text_input("Search segments", placeholder="For example: contract, tenure, or No")
    visible_report = risk_report
    if report_search.strip():
        search_match = risk_report.astype(str).apply(
            lambda column: column.str.contains(report_search.strip(), case=False, na=False)
        ).any(axis=1)
        visible_report = risk_report.loc[search_match]
    st.dataframe(visible_report, width="stretch", hide_index=True)
    st.download_button(
        "Download visible segment report as CSV",
        data=visible_report.to_csv(index=False).encode("utf-8-sig"),
        file_name="churn_risk_report.csv",
        mime="text/csv",
    )

markdown_report = build_markdown_report(
    risk_report,
    analysis_data,
    uploaded_file.name if uploaded_file else DATA_PATH.name,
    target_column,
    positive_label,
    churn_rate,
    filter_description,
)
st.download_button(
    "Download analysis report as Markdown",
    data=markdown_report.encode("utf-8"),
    file_name="churn_analysis_report.md",
    mime="text/markdown",
)

with st.expander("Dataset summary and preview"):
    left, right = st.columns(2)
    with left:
        st.write("**Numeric summary**")
        numeric_data = analysis_data.select_dtypes(include=np.number)
        if numeric_data.empty:
            st.info("No numeric columns were detected.")
        else:
            st.dataframe(numeric_data.describe().T, width="stretch")
    with right:
        st.write("**Data quality**")
        quality = pd.DataFrame(
            {
                "Column": analysis_data.columns,
                "Missing values": analysis_data.isna().sum().to_numpy(),
                "Unique values": analysis_data.nunique(dropna=True).to_numpy(),
            }
        )
        st.dataframe(quality, width="stretch", hide_index=True)
    st.write("**First 10 records**")
    st.dataframe(analysis_data.head(10), width="stretch", hide_index=True)
    st.download_button(
        "Download filtered data as CSV",
        data=analysis_data.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_customer_data.csv",
        mime="text/csv",
    )

st.html(
    """
    <script>
    (() => {
      window.__churnIqMotion?.destroy?.();

      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const root = document.querySelector('[data-testid="stMain"]') || document.body;
      const svgNamespace = "http://www.w3.org/2000/svg";
      const journeyPathData =
        "M27 0 C5 95 48 155 27 250 S6 410 27 500 S48 655 27 750 S6 910 27 1000";
      const revealSelector = [
        ".hero", ".scenario-shell", '[data-testid="stMetric"]',
        ".insight-card", '[data-testid="stPlotlyChart"]',
        '[data-testid="stDataFrame"]', '[data-testid="stExpander"]'
      ].join(",");
      const counterSelector = ".hero-signals strong, [data-testid='stMetricValue']";
      const observedReveals = new WeakSet();
      const previousCounterTargets = new WeakMap();
      const runningCounters = new WeakSet();
      let mutationObserver;
      let revealObserver;
      let counterObserver;
      let scanFrame = 0;
      let scrollFrame = 0;

      function createSvgElement(tagName, attributes) {
        const element = document.createElementNS(svgNamespace, tagName);
        Object.entries(attributes).forEach(([name, value]) => {
          element.setAttribute(name, value);
        });
        return element;
      }

      function createJourneyRail() {
        document.querySelector(".journey-rail")?.remove();
        const rail = createSvgElement("svg", {
          class: "journey-rail",
          viewBox: "0 0 54 1000",
          role: "presentation",
          "aria-hidden": "true"
        });
        rail.append(
          createSvgElement("path", {
            class: "journey-track",
            d: journeyPathData
          }),
          createSvgElement("path", {
            class: "journey-progress",
            pathLength: "1",
            d: journeyPathData
          }),
          createSvgElement("circle", {
            class: "journey-node",
            cx: "27",
            cy: "0",
            r: "7"
          }),
          createSvgElement("circle", {
            class: "journey-node",
            cx: "27",
            cy: "1000",
            r: "7"
          }),
          createSvgElement("circle", {
            class: "journey-node is-current",
            cx: "27",
            cy: "0",
            r: "6"
          })
        );
        document.body.appendChild(rail);
      }

      function reveal(element) {
        element.classList.add("scroll-reveal", "is-visible");
        if (element.matches(".hero")) element.classList.add("motion-ready");
      }

      function formatCount(value, parsed) {
        const formatted = new Intl.NumberFormat("en-US", {
          minimumFractionDigits: parsed.decimals,
          maximumFractionDigits: parsed.decimals
        }).format(Math.abs(value));
        const sign = value < 0 ? "-" : (parsed.explicitPlus && value > 0 ? "+" : "");
        return `${parsed.prefix}${sign}${formatted}${parsed.suffix}`;
      }

      function animateCounter(element) {
        if (runningCounters.has(element)) return;
        const original = element.textContent.trim();
        const match = original.match(/^([^\\d+\\-\\u2212]*)([+\\-\\u2212]?\\d[\\d,]*(?:\\.\\d+)?)(.*)$/s);
        if (!match) return;

        const target = Number(match[2].replace(/,/g, "").replace("\\u2212", "-"));
        if (!Number.isFinite(target)) return;
        const decimals = (match[2].split(".")[1] || "").length;
        const parsed = {
          prefix: match[1],
          suffix: match[3],
          decimals,
          explicitPlus: match[2].startsWith("+")
        };
        previousCounterTargets.set(element, original);
        if (reducedMotion) return;

        runningCounters.add(element);
        const startedAt = performance.now();
        const duration = 1250;
        const step = (now) => {
          const progress = Math.min((now - startedAt) / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 4);
          element.textContent = formatCount(target * eased, parsed);
          element.style.transform = `scale(${1 + Math.sin(progress * Math.PI) * .045})`;
          if (progress < 1) {
            requestAnimationFrame(step);
          } else {
            element.textContent = original;
            element.style.transform = "";
            runningCounters.delete(element);
          }
        };
        requestAnimationFrame(step);
      }

      function scan() {
        scanFrame = 0;
        root.querySelectorAll(revealSelector).forEach((element) => {
          if (!observedReveals.has(element)) {
            observedReveals.add(element);
            if (reducedMotion) reveal(element);
            else revealObserver.observe(element);
          }
        });
        root.querySelectorAll(counterSelector).forEach((element) => {
          if (runningCounters.has(element)) return;
          const current = element.textContent.trim();
          if (previousCounterTargets.get(element) !== current) {
            if (reducedMotion) {
              previousCounterTargets.set(element, current);
            } else {
              counterObserver.observe(element);
            }
          }
        });
      }

      function scheduleScan() {
        if (!scanFrame) scanFrame = requestAnimationFrame(scan);
      }

      function updateJourney() {
        scrollFrame = 0;
        const progressPath = document.querySelector(".journey-progress");
        const currentNode = document.querySelector(".journey-node.is-current");
        if (!progressPath || !currentNode) return;
        const scrollable = root.scrollHeight - root.clientHeight;
        const progress = scrollable > 0
          ? Math.min(1, Math.max(0, root.scrollTop / scrollable))
          : 0;
        progressPath.style.strokeDashoffset = String(1 - progress);
        const point = progressPath.getPointAtLength(progress * progressPath.getTotalLength());
        currentNode.setAttribute("cx", String(point.x));
        currentNode.setAttribute("cy", String(point.y));
      }

      function scheduleJourneyUpdate() {
        if (!scrollFrame) scrollFrame = requestAnimationFrame(updateJourney);
      }

      if ("IntersectionObserver" in window) {
        revealObserver = new IntersectionObserver((entries, observer) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            reveal(entry.target);
            observer.unobserve(entry.target);
          });
        }, { threshold: 0.12, rootMargin: "0px 0px -7% 0px" });
        counterObserver = new IntersectionObserver((entries, observer) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            animateCounter(entry.target);
            observer.unobserve(entry.target);
          });
        }, { threshold: 0.55 });
      } else {
        revealObserver = { observe: reveal };
        counterObserver = { observe: animateCounter };
      }

      mutationObserver = new MutationObserver(scheduleScan);
      mutationObserver.observe(root, { childList: true, subtree: true });
      createJourneyRail();
      root.addEventListener("scroll", scheduleJourneyUpdate, { passive: true });
      window.addEventListener("resize", scheduleJourneyUpdate, { passive: true });
      scan();
      updateJourney();

      window.__churnIqMotion = {
        destroy() {
          mutationObserver?.disconnect();
          revealObserver?.disconnect?.();
          counterObserver?.disconnect?.();
          root.removeEventListener("scroll", scheduleJourneyUpdate);
          window.removeEventListener("resize", scheduleJourneyUpdate);
          if (scanFrame) cancelAnimationFrame(scanFrame);
          if (scrollFrame) cancelAnimationFrame(scrollFrame);
        }
      };
    })();
    </script>
    """,
    unsafe_allow_javascript=True,
)
