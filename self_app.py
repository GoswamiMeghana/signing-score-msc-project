"""
What Is a "Perfect" Signing? — Interactive Dashboard
Run with: streamlit run app.py
Expects to be run from a directory containing data/processed/*.parquet
(the same checkpoint files produced by Notebooks 1-5).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------------------------------------------------------------------------
# Page config & style
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="What Is a \"Perfect\" Signing?",
    page_icon="\u26bd",
    layout="wide",
)

PALETTE = {
    "primary": "#1B4332",
    "secondary": "#D4A24C",
    "highlight": "#B3452C",
    "neutral": "#5B6B73",
    "light": "#CFE0E8",
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    /* Hide default Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}

    .block-container {{
        padding-top: 2rem;
        max-width: 1200px;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {PALETTE['primary']};
    }}
    section[data-testid="stSidebar"] * {{
        color: #F4F6F5 !important;
    }}
    section[data-testid="stSidebar"] .stRadio > label {{
        color: #F4F6F5 !important;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        background-color: rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.4rem;
        transition: background-color 0.15s ease;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background-color: rgba(255,255,255,0.14);
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15);
    }}

    /* Headers */
    .main-header {{
        font-size: 2.3rem; font-weight: 800; color: {PALETTE['primary']};
        margin-bottom: 0.15rem; letter-spacing: -0.02em;
    }}
    .sub-header {{
        font-size: 1.05rem; color: {PALETTE['neutral']}; margin-bottom: 1.8rem;
        font-weight: 400; line-height: 1.5;
    }}
    .kicker {{
        font-size: 0.78rem; font-weight: 700; color: {PALETTE['secondary']};
        letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.3rem;
    }}

    /* Stat / info cards */
    .stat-card {{
        background-color: #F7F9F8; border-radius: 14px; padding: 1.5rem 1.7rem;
        border: 1px solid #E5E9E7; box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}
    .stat-value {{
        font-size: 2.6rem; font-weight: 800; color: {PALETTE['primary']};
        letter-spacing: -0.02em;
    }}
    .stat-label {{
        font-size: 0.88rem; color: {PALETTE['neutral']}; font-weight: 500;
    }}
    .insight-box {{
        background-color: #FBF3E9; border-left: 4px solid {PALETTE['secondary']};
        border-radius: 10px; padding: 1.1rem 1.4rem; font-size: 0.95rem;
        color: #3A3A3A; line-height: 1.55;
    }}
    .success-box {{
        background-color: #EDF5F0; border-left: 4px solid {PALETTE['primary']};
        border-radius: 10px; padding: 1.1rem 1.4rem; font-size: 0.95rem;
        color: #3A3A3A; line-height: 1.55;
    }}
    .warn-box {{
        background-color: #FCEFEA; border-left: 4px solid {PALETTE['highlight']};
        border-radius: 10px; padding: 1.1rem 1.4rem; font-size: 0.95rem;
        color: #3A3A3A; line-height: 1.55;
    }}

    /* Streamlit metric widget restyle */
    div[data-testid="stMetric"] {{
        background-color: #F7F9F8; border-radius: 14px; padding: 1rem 1.2rem;
        border: 1px solid #E5E9E7;
    }}
    div[data-testid="stMetricValue"] {{
        color: {PALETTE['primary']} !important; font-weight: 800 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {PALETTE['neutral']} !important; font-weight: 500 !important;
    }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        font-weight: 600; font-size: 0.95rem;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {PALETTE['primary']} !important;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: {PALETTE['primary']} !important;
    }}

    /* Buttons / selects */
    div[data-testid="stSelectbox"] label, div[data-testid="stTextInput"] label {{
        font-weight: 600; color: {PALETTE['primary']};
    }}

    /* Dataframe */
    div[data-testid="stDataFrame"] {{
        border-radius: 10px; overflow: hidden; border: 1px solid #E5E9E7;
    }}

    hr {{ margin: 1.5rem 0; border-color: #E5E9E7; }}
</style>
""", unsafe_allow_html=True)

def section_kicker(text):
    st.markdown(f'<div class="kicker">{text}</div>', unsafe_allow_html=True)

def insight(text, kind="insight"):
    box_class = {"insight": "insight-box", "success": "success-box", "warn": "warn-box"}[kind]
    st.markdown(f'<div class="{box_class}">{text}</div>', unsafe_allow_html=True)




# ---------------------------------------------------------------------------
# Password protection (only active if APP_PASSWORD is configured — e.g. on
# Streamlit Cloud via secrets. Running locally without secrets.toml simply
# skips this, since only you can reach localhost anyway.)
# ---------------------------------------------------------------------------

def check_password():
    if "APP_PASSWORD" not in st.secrets:
        return True  # no password configured (local run) - skip the gate

    def password_entered():
        if st.session_state.get("password_input") == st.secrets.get("APP_PASSWORD", ""):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown('<div class="main-header">What Is a "Perfect" Signing?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">This dashboard contains player data covered by an NDA. Enter the password to continue.</div>', unsafe_allow_html=True)
    st.text_input("Password", type="password", on_change=password_entered, key="password_input")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Incorrect password.")
    return False

if not check_password():
    st.stop()

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
# LOCAL MODE: reads directly from data/processed/ on this machine. Used for
# local testing and for the local screen-share demo. The Wasabi/Streamlit
# Cloud version (reading via s3fs + st.secrets) is a separate, later step —
# not needed for local runs.

DATA_DIR = "data/processed"

@st.cache_data
def load_parquet_safe(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None

@st.cache_data
def load_all_data():
    return {
        "signing_score": load_parquet_safe("notebook4_unified_signing_score_FINAL.parquet"),
        "transfer_eval": load_parquet_safe("notebook5_transfer_outcome_evaluation.parquet"),
        "durability_eval": load_parquet_safe("notebook5_durability_evaluation.parquet"),
        "team_aggregate": load_parquet_safe("notebook5_team_aggregate_check.parquet"),
        "player_career": load_parquet_safe("player_career.parquet"),
        "genuine_manager_changes": load_parquet_safe("genuine_manager_changes.parquet"),
        "myth3_manager_bounce": load_parquet_safe("myth3_manager_bounce_final.parquet"),
    }

data = load_all_data()

missing = [k for k, v in data.items() if v is None]
if missing:
    st.sidebar.warning(
        "Some data files were not found in `data/processed/`:\n\n"
        + "\n".join(f"- {m}" for m in missing)
        + "\n\nThe corresponding sections will be hidden. "
        "Make sure this app is run from your project's root folder "
        "(the one containing `data/processed/`)."
    )

missing = [k for k, v in data.items() if v is None]
if missing:
    st.sidebar.warning(
        "Some data files could not be loaded from Wasabi:\n\n"
        + "\n".join(f"- {m}" for m in missing)
        + "\n\nThe corresponding sections will be hidden. "
        "Check that WASABI_* credentials are set correctly in Streamlit secrets, "
        "and that the file paths in WASABI_FILES match your actual bucket structure."
    )


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("What Is a \u201cPerfect\u201d Signing?")

page = st.sidebar.radio(
    "Navigate",
    [
        "Signing Score Explorer",
        "Compare Players",
        "Recruitment Lookup",
        "Summary",
    ],
)

st.sidebar.divider()
st.sidebar.caption(
    "Built on validated player-season data across 5 top European leagues, "
    "2022-23 to 2024-25. See the accompanying dissertation for full methodology."
)



# ---------------------------------------------------------------------------
# Shared helper: consistent, brand-aligned color palette for positions
# ---------------------------------------------------------------------------
POSITION_PALETTE = [
    "#1B4332", "#D4A24C", "#B3452C", "#2D6A4F", "#40798C",
    "#873E23", "#70A288", "#9C6644", "#5B6B73", "#C08552", "#3A5A40",
]

def color_map_for(categories):
    cats = sorted(categories)
    return {c: POSITION_PALETTE[i % len(POSITION_PALETTE)] for i, c in enumerate(cats)}

LEAGUE_DISPLAY = {
    "Premier League": "Premier League",
    "1. Bundesliga": "Bundesliga",
    "La Liga": "La Liga",
    "Ligue 1": "Ligue 1",
    "Serie A": "Serie A",
}

@st.cache_data
def prep_signing_score(ss_raw):
    ss_out = ss_raw.copy()
    ss_out["league_display"] = ss_out["league"].map(LEAGUE_DISPLAY).fillna(ss_out["league"])
    ss_out["position_group"] = np.where(ss_out["player_type"] == "goalkeeper", "Goalkeeper", ss_out["primary_position"])
    return ss_out


# ===========================================================================
# PAGE 1: SIGNING SCORE EXPLORER
# ===========================================================================
if page == "Signing Score Explorer":
    st.markdown('<div class="main-header">Signing Score Explorer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Browse the full, bias-adjusted Signing Score across every '
        'player-season.</div>',
        unsafe_allow_html=True,
    )

    ss = data["signing_score"]
    if ss is None:
        st.info("Signing score data not found \u2014 needs `notebook4_unified_signing_score_FINAL.parquet`.")
    else:
        ss = prep_signing_score(ss)

        outfield_positions = sorted(
            ss.loc[ss["player_type"] == "outfield", "primary_position"].dropna().unique().tolist()
        )
        position_options = outfield_positions + ["Goalkeeper"]
        pos_colors = color_map_for(position_options)

        c1, c2, c3 = st.columns([1.2, 1, 1.5])
        leagues = ["All"] + sorted(ss["league_display"].dropna().unique().tolist())
        seasons = ["All"] + sorted(ss["season"].dropna().unique().tolist())
        sel_league = c1.selectbox("League", leagues)
        sel_season = c2.selectbox("Season", seasons)
        sel_positions = c3.multiselect("Position(s)", position_options, default=position_options)
        min_matches = st.slider("Minimum matches played", 1, 38, 10)

        filtered = ss.copy()
        if sel_league != "All":
            filtered = filtered[filtered["league_display"] == sel_league]
        if sel_season != "All":
            filtered = filtered[filtered["season"] == sel_season]
        if sel_positions:
            filtered = filtered[filtered["position_group"].isin(sel_positions)]
        else:
            filtered = filtered.iloc[0:0]
        filtered = filtered[filtered["n_matches"] >= min_matches]

        # --- KPI row ---
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Player-seasons", f"{len(filtered):,}")
        k2.metric("Mean Signing Score", f"{filtered['final_score'].mean():.3f}" if len(filtered) else "\u2014")
        k3.metric("Top score", f"{filtered['final_score'].max():.3f}" if len(filtered) else "\u2014")
        k4.metric("Positions shown", f"{filtered['position_group'].nunique()}" if len(filtered) else "0")

        st.divider()

        col_table, col_chart = st.columns([1.3, 1])

        with col_table:
            section_kicker("Leaderboard")
            show_cols = ["player", "league_display", "season", "team", "primary_position", "n_matches", "final_score"]
            show_cols = [c for c in show_cols if c in filtered.columns]
            display_df = filtered[show_cols].sort_values("final_score", ascending=False).reset_index(drop=True)
            display_df = display_df.rename(columns={"league_display": "league", "primary_position": "position", "final_score": "signing_score"})
            st.dataframe(display_df, use_container_width=True, height=460)

        with col_chart:
            section_kicker("Top 10 in Current Filter")
            top10 = filtered.sort_values("final_score", ascending=False).head(10)
            top10_fig = go.Figure(go.Bar(
                x=top10["final_score"],
                y=top10["player"] + " (" + top10["season"] + ")",
                orientation="h",
                marker_color=[pos_colors.get(p, PALETTE["neutral"]) for p in top10["position_group"]],
                text=top10["final_score"].round(3),
                textposition="outside",
            ))
            top10_fig.update_layout(
                height=460, plot_bgcolor="white", xaxis_title="Signing Score", yaxis_title="",
                yaxis=dict(autorange="reversed"), margin=dict(l=10, r=30, t=10, b=10),
            )
            st.plotly_chart(top10_fig, use_container_width=True)

        st.divider()
        section_kicker("Score Distribution")
        st.markdown("**Signing Score distribution by position**")

        dist_fig = px.histogram(
            filtered, x="final_score", color="position_group", nbins=50,
            labels={"final_score": "Signing Score", "position_group": "Position"},
            color_discrete_map=pos_colors,
        )
        dist_fig.update_layout(height=400, plot_bgcolor="white", legend_title_text="Position", bargap=0.02)
        st.plotly_chart(dist_fig, use_container_width=True)


# ===========================================================================
# PAGE 2: COMPARE PLAYERS
# ===========================================================================
elif page == "Compare Players":
    st.markdown('<div class="main-header">Compare Players</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Search for specific players and compare their Signing Scores '
        'side by side.</div>',
        unsafe_allow_html=True,
    )

    ss = data["signing_score"]
    if ss is None:
        st.info("Signing score data not found \u2014 needs `notebook4_unified_signing_score_FINAL.parquet`.")
    else:
        ss = prep_signing_score(ss)
        pos_colors = color_map_for(ss["position_group"].dropna().unique().tolist())

        player_labels = (
            ss["player"].astype(str) + "  \u2014  " + ss["season"].astype(str) + "  \u2022  " + ss["team"].astype(str)
        )
        label_lookup = dict(zip(player_labels, ss.index))

        selected_labels = st.multiselect(
            "Search and add players (type to filter, select multiple)",
            options=sorted(player_labels.tolist()),
            default=[],
            max_selections=8,
            key="compare_players_select",
        )

        if not selected_labels:
            st.markdown("""
            <div class="stat-card" style="text-align:center; padding: 3rem 1.5rem;">
                <div style="font-size:1.1rem; color:#5B6B73;">Search for players above to start comparing.</div>
                <div style="font-size:0.9rem; color:#8A9490; margin-top:0.4rem;">Add up to 8 player-seasons at once.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            compare_rows = ss.loc[[label_lookup[l] for l in selected_labels]].copy()

            # Percentile within each player's own position group, computed against the FULL dataset
            compare_rows["percentile"] = compare_rows.apply(
                lambda r: (ss.loc[ss["position_group"] == r["position_group"], "final_score"] <= r["final_score"]).mean() * 100,
                axis=1,
            )
            player_colors = {label: POSITION_PALETTE[i % len(POSITION_PALETTE)] for i, label in enumerate(selected_labels)}

            # --- Player cards ---
            section_kicker(f"Comparing {len(compare_rows)} Player-Season{'s' if len(compare_rows) != 1 else ''}")
            card_cols = st.columns(len(compare_rows))
            for i, (label, (_, row)) in enumerate(zip(selected_labels, compare_rows.iterrows())):
                with card_cols[i]:
                    c = player_colors[label]
                    st.markdown(f"""
                    <div class="stat-card" style="border-top: 4px solid {c}; text-align:center; padding: 1.2rem 0.8rem;">
                        <div style="font-size:0.95rem; font-weight:700; color:{PALETTE['primary']}; min-height:2.6em;">{row['player']}</div>
                        <div style="font-size:0.75rem; color:{PALETTE['neutral']}; margin-bottom:0.6rem;">{row['team']} \u00b7 {row['season']}</div>
                        <div style="font-size:1.7rem; font-weight:800; color:{c};">{row['final_score']:.3f}</div>
                        <div style="font-size:0.72rem; color:{PALETTE['neutral']};">{row['position_group']} \u00b7 {row['percentile']:.0f}th pct.</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # --- Score comparison bar chart ---
            c1, c2 = st.columns(2)
            with c1:
                section_kicker("Signing Score")
                fig1 = go.Figure(go.Bar(
                    x=[compare_rows.loc[label_lookup[l], "final_score"] for l in selected_labels],
                    y=[compare_rows.loc[label_lookup[l], "player"] for l in selected_labels],
                    orientation="h",
                    marker_color=[player_colors[l] for l in selected_labels],
                    text=[f"{compare_rows.loc[label_lookup[l], 'final_score']:.3f}" for l in selected_labels],
                    textposition="outside",
                ))
                fig1.update_layout(height=max(260, 60 * len(compare_rows)), plot_bgcolor="white",
                                    xaxis_title="Signing Score", yaxis_title="",
                                    yaxis=dict(autorange="reversed"), margin=dict(l=10, r=30, t=10, b=10))
                st.plotly_chart(fig1, use_container_width=True)

            with c2:
                section_kicker("Matches Played")
                fig2 = go.Figure(go.Bar(
                    x=[compare_rows.loc[label_lookup[l], "n_matches"] for l in selected_labels],
                    y=[compare_rows.loc[label_lookup[l], "player"] for l in selected_labels],
                    orientation="h",
                    marker_color=[player_colors[l] for l in selected_labels],
                    text=[compare_rows.loc[label_lookup[l], "n_matches"] for l in selected_labels],
                    textposition="outside",
                ))
                fig2.update_layout(height=max(260, 60 * len(compare_rows)), plot_bgcolor="white",
                                    xaxis_title="Matches Played", yaxis_title="",
                                    yaxis=dict(autorange="reversed"), margin=dict(l=10, r=30, t=10, b=10))
                st.plotly_chart(fig2, use_container_width=True)

            st.divider()

            # --- Context: where they sit in the full position distribution ---
            section_kicker("In Context")
            st.markdown("**Where each player sits within their position's full score distribution**")
            context_positions = compare_rows["position_group"].unique().tolist()
            context_pool = ss[ss["position_group"].isin(context_positions)]

            ctx_fig = px.histogram(
                context_pool, x="final_score", color="position_group", nbins=50, opacity=0.55,
                labels={"final_score": "Signing Score", "position_group": "Position"},
                color_discrete_map=pos_colors,
            )
            for label in selected_labels:
                row = compare_rows.loc[label_lookup[label]]
                ctx_fig.add_vline(
                    x=row["final_score"], line_dash="dash", line_width=2.5, line_color=player_colors[label],
                    annotation_text=row["player"], annotation_position="top",
                )
            ctx_fig.update_layout(height=400, plot_bgcolor="white", legend_title_text="Position", bargap=0.02)
            st.plotly_chart(ctx_fig, use_container_width=True)


# ===========================================================================
# PAGE 2: RECRUITMENT LOOKUP TOOL
# ===========================================================================
elif page == "Recruitment Lookup":
    st.markdown('<div class="main-header">Recruitment Lookup</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Look up a real transfer and see how the Signing Score '
        'would have flagged it before the move.</div>',
        unsafe_allow_html=True,
    )

    te = data["transfer_eval"]
    pc = data["player_career"]

    if te is None:
        st.info("Transfer-outcome data not found \u2014 this tool needs `notebook5_transfer_outcome_evaluation.parquet`.")
    else:
        te = te.copy()
        if pc is not None and "player_name" in pc.columns:
            te = te.merge(pc[["player_id", "player_name"]], on="player_id", how="left")
            name_col = "player_name"
        elif "player" in te.columns:
            name_col = "player"
        else:
            name_col = "player_id"

        te["post_pct"] = te["score_after"].rank(pct=True)
        te["pre_pct"] = te["score_before"].rank(pct=True)
        te["is_flop"] = te["post_pct"] <= 0.25
        te["is_success"] = te["post_pct"] >= 0.75

        st.caption(f"{len(te):,} real transfers in this evaluation set \u2014 type to search, or scroll to browse")

        te_sorted = te.sort_values(name_col, key=lambda s: s.astype(str).str.lower())
        options = (
            te_sorted[name_col].astype(str) + "  \u2014  "
            + te_sorted["before_season"].astype(str) + " \u2192 " + te_sorted["after_season"].astype(str)
        ).tolist()

        selection = st.selectbox(
            "Select a transfer to inspect",
            options,
            index=None,
            placeholder="Type a player name or scroll through the list\u2026",
        )

        if selection is None:
            st.info("Select a player above to see their pre-move and post-move Signing Score.")
        else:
            sel_name = selection.split("  \u2014  ")[0]
            sel_before_season = selection.split("  \u2014  ")[1].split(" \u2192 ")[0]
            row = te_sorted[
                (te_sorted[name_col].astype(str) == sel_name) & (te_sorted["before_season"].astype(str) == sel_before_season)
            ].iloc[0]

            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Pre-move score", f"{row['score_before']:.3f}", help=f"Percentile: {row['pre_pct']*100:.0f}th")
            c2.metric("Post-move score", f"{row['score_after']:.3f}", help=f"Percentile: {row['post_pct']*100:.0f}th")
            change = row["score_after"] - row["score_before"]
            c3.metric("Change", f"{change:+.3f}")

            if row["is_flop"]:
                c4.error("Flagged: FLOP (bottom 25% post-move)")
            elif row["is_success"]:
                c4.success("Top-quartile performer post-move")
            else:
                c4.info("Mid-range post-move")

            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=row["pre_pct"] * 100,
                title={"text": "Pre-Move Score Percentile"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": PALETTE["primary"]},
                    "steps": [
                        {"range": [0, 50], "color": "#F4E4DC"},
                        {"range": [50, 100], "color": "#D9E8DD"},
                    ],
                },
            ))
            gauge.update_layout(height=280)
            st.plotly_chart(gauge, use_container_width=True)

            if row["pre_pct"] > 0.5:
                st.success(
                    f"This player scored in the **top half** pre-move. Players in this group "
                    f"flopped only 11.6% of the time historically \u2014 a lower-risk signal."
                )
            else:
                st.warning(
                    f"This player scored in the **bottom half** pre-move. Players in this group "
                    f"flopped 38.3% of the time historically \u2014 a higher-risk signal, worth "
                    f"weighing against other scouting information."
                )


# ===========================================================================
# PAGE 3: SUMMARY  (Mythbusting + Evaluation)
# ===========================================================================
elif page == "Summary":
    st.markdown('<div class="main-header">Summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Six recruitment myths tested, and three tests of whether '
        'the Signing Score predicts anything real.</div>',
        unsafe_allow_html=True,
    )

    summary_tab1, summary_tab2 = st.tabs(["Mythbusting", "Evaluation"])

    # --- Mythbusting sub-tab ---
    with summary_tab1:
        myths = [
            {"name": "Hot-Start Bias", "verdict": "Confirmed strongly", "color": PALETTE["primary"],
             "detail": "d = -0.964 (discovery), -0.911 (confirmation). Robust across 10-30% threshold choices.",
             "implication": "A hot early-season start should NOT raise your valuation of a target."},
            {"name": "Adaptation Tax", "verdict": "No causal evidence", "color": PALETTE["neutral"],
             "detail": "d \u2248 -0.02 to -0.05 after propensity/stratified matching against similar non-switchers.",
             "implication": "No evidence to discount a target for an expected settling-in dip."},
            {"name": "New Manager Bounce", "verdict": "Confirmed, with nuance", "color": PALETTE["primary"],
             "detail": "d = 0.65-0.68. Post-change form exceeds even the team's own longer-run baseline.",
             "implication": "Recent form after a managerial change may be a genuine signal, not noise."},
            {"name": "Relative Age Effect", "verdict": "Split verdict", "color": PALETTE["secondary"],
             "detail": "Overrepresentation confirmed (\u03c7\u00b2\u2248104-113); performance advantage NOT confirmed.",
             "implication": "Early representation in a talent pool is a selection bias, not a quality signal."},
            {"name": "Peak Age Curve", "verdict": "Confirmed (position-dependent)", "color": PALETTE["primary"],
             "detail": "Pooled peak age 29.1; position-group replication improved from r=0.474 to r=0.738.",
             "implication": "Age expectations should account for position \u2014 wide/attacking roles peak earlier."},
            {"name": "Injury Recency Penalty", "verdict": "No confirmed effect (power-limited)", "color": PALETTE["neutral"],
             "detail": "Binary test null both halves; severity-weighted signal borderline, doesn't fully replicate.",
             "implication": "Insufficient evidence to discount a target for a recent injury history."},
        ]

        cols = st.columns(2)
        for i, m in enumerate(myths):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="stat-card" style="margin-bottom: 1rem; border-left: 4px solid {m['color']};">
                    <div style="font-size:1.2rem; font-weight:700; color:{PALETTE['primary']};">{m['name']}</div>
                    <div style="font-size:0.95rem; font-weight:600; color:{m['color']}; margin: 0.2rem 0 0.6rem 0;">{m['verdict']}</div>
                    <div style="font-size:0.85rem; color:{PALETTE['neutral']}; margin-bottom:0.5rem;">{m['detail']}</div>
                    <div style="font-size:0.85rem; font-style:italic; color:#333;">{m['implication']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.caption(
            "All six myths tested using a permanent discovery/confirmation split established before "
            "any exploratory analysis, with Benjamini-Hochberg correction applied across all formal "
            "tests. See the dissertation for full methodology."
        )

    # --- Evaluation sub-tab ---
    with summary_tab2:
        eval_tab1, eval_tab2, eval_tab3 = st.tabs(["Transfer Outcomes (Headline)", "Durability", "Team-Aggregate Check"])

        with eval_tab1:
            te = data["transfer_eval"]
            if te is None:
                st.info("Transfer-outcome evaluation data not found.")
            else:
                col1, col2, col3 = st.columns(3)
                corr = te["score_before"].corr(te["score_after"])
                col1.metric("Pre-move \u2192 Post-move correlation", f"r = {corr:.3f}")
                col2.metric("Real transfers evaluated", f"{len(te):,}")

                te2 = te.copy()
                te2["post_pct"] = te2["score_after"].rank(pct=True)
                te2["pre_pct"] = te2["score_before"].rank(pct=True)
                te2["is_flop"] = te2["post_pct"] <= 0.25
                top_half = te2[te2["pre_pct"] > 0.5]
                bottom_half = te2[te2["pre_pct"] <= 0.5]
                flop_top = top_half["is_flop"].mean() * 100
                flop_bottom = bottom_half["is_flop"].mean() * 100
                col3.metric("Flop-rate reduction", f"{flop_bottom/flop_top:.1f}\u00d7")

                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Pre-Move vs. Post-Move Score")
                    fig = px.scatter(te2, x="score_before", y="score_after", trendline="ols", opacity=0.4,
                                      labels={"score_before": "Signing Score (pre-move)", "score_after": "Signing Score (post-move)"},
                                      color_discrete_sequence=[PALETTE["neutral"]])
                    fig.update_traces(marker=dict(size=7))
                    fig.update_layout(height=400, plot_bgcolor="white", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    st.subheader("Flop Rate by Pre-Move Score Tier")
                    flop_fig = go.Figure(go.Bar(
                        x=["Top Half\n(pre-move score)", "Bottom Half\n(pre-move score)"],
                        y=[flop_top, flop_bottom],
                        marker_color=[PALETTE["primary"], PALETTE["highlight"]],
                        text=[f"{flop_top:.1f}%", f"{flop_bottom:.1f}%"], textposition="outside",
                    ))
                    flop_fig.update_layout(height=400, plot_bgcolor="white",
                                            yaxis_title="% ending in bottom-25% post-move",
                                            yaxis_range=[0, max(flop_bottom, flop_top) * 1.3])
                    st.plotly_chart(flop_fig, use_container_width=True)

                insight(
                    f"<b>Headline finding:</b> players scoring in the top half before a real transfer "
                    f"flop at only {flop_top:.1f}%, versus {flop_bottom:.1f}% for bottom-half scorers "
                    f"\u2014 a {flop_bottom/flop_top:.1f}\u00d7 difference, replicated independently "
                    f"across discovery and confirmation halves (\u03c7\u00b2=69.16, p&lt;0.0001).",
                    "success",
                )

        with eval_tab2:
            de = data["durability_eval"]
            if de is None:
                st.info("Durability evaluation data not found.")
            else:
                col1, col2 = st.columns(2)
                injured = de[de["was_injured_2425"] == True]["score_2324"]
                not_injured = de[de["was_injured_2425"] == False]["score_2324"]
                col1.metric("Mean score \u2014 subsequently injured", f"{injured.mean():.4f}")
                col2.metric("Mean score \u2014 not injured", f"{not_injured.mean():.4f}")

                fig = go.Figure()
                fig.add_trace(go.Box(y=not_injured, name="Not Injured (2024-25)", marker_color=PALETTE["primary"]))
                fig.add_trace(go.Box(y=injured, name="Injured (2024-25)", marker_color=PALETTE["highlight"]))
                fig.update_layout(height=420, plot_bgcolor="white", yaxis_title="Signing Score (2023-24)", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                insight(
                    "<b>Higher-scoring players show HIGHER subsequent injury risk</b> (d=0.423, p&lt;0.0001) "
                    "\u2014 not a flaw in the score. Explained by playing-time exposure: higher-scoring "
                    "players accumulate more minutes, mechanically increasing exposure. Score does "
                    "<b>not</b> predict injury severity among those injured (r=-0.094, not significant). "
                    "Performance and durability should be treated as separate recruitment considerations.",
                    "warn",
                )

        with eval_tab3:
            ta = data["team_aggregate"]
            if ta is None:
                st.info("Team-aggregate check data not found.")
            else:
                col1, col2 = st.columns(2)
                corr_score = ta["squad_score_per_contributor"].corr(ta["final_rank"])
                col1.metric("Signing Score vs. final rank", f"r = {corr_score:.3f}")
                col2.metric("Raw OBV vs. final rank (for comparison)", "r = -0.486")

                fig = px.scatter(ta, x="squad_score_per_contributor", y="final_rank", trendline="ols", opacity=0.6,
                                  labels={"squad_score_per_contributor": "Squad Signing Score (per contributor)", "final_rank": "Final League Rank"},
                                  color_discrete_sequence=[PALETTE["neutral"]])
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(height=400, plot_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)

                insight(
                    "<b>This is expected, not a failure.</b> The Signing Score deliberately removes "
                    "team-strength effects at the individual level \u2014 isolating personal contribution "
                    "from squad context. It should therefore NOT strongly predict team-level outcomes; "
                    "that is a different question, better answered by raw OBV or points-per-game. "
                    "<i>Right tool for the right question.</i>",
                )