import streamlit as st
from plotly import express as px
from plotly import graph_objects as go
import pandas as pd

def render_structural_gaps(filtered_df, state_stats_raw, sub_text, get_k_color):
    st.markdown('<div class="card-header" style="font-size: 2.5rem; margin-bottom: 5px;">Structural Deficit Ranking & Baseline Adequacy</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 1.5rem;">State-level deficit analysis benchmarked against WHO capacity scaling norms</p>', unsafe_allow_html=True)

    with st.expander("Methodology: Capacity Benchmarks & Deficit Analysis"):
        st.markdown("**1. State-Level Aggregation**")
        st.markdown("""
        From hospital-level data, we aggregate per state:
        - `Total_Beds` = SUM(Total_Num_Beds)
        - `Total_Doctors` = SUM(Number_Doctor)
        - `Total_Emergency` = COUNT where Emergency_Services == "Yes"
        - `Total_ICU` = COUNT where Facilities contains "ICU"
        - `State_Population` = MAX(State_Population) per state
        """)
        st.markdown("**2. WHO-Scaled Required Capacity**")
        c1, c2 = st.columns(2)
        with c1:
            st.latex(r"Required\_Beds = \frac{Pop \times 3}{1,000}")
            st.latex(r"Required\_Docs = \frac{Pop \times 1}{1,000}")
        with c2:
            st.latex(r"Required\_ICU = \frac{Pop \times 10}{100,000}")
            st.latex(r"Required\_ER = \frac{Pop \times 1}{100,000}")
        st.markdown("**3. Deficit Calculation**")
        st.latex(r"Deficit\% = \max(0, \min(100, \frac{Required - Available}{Required} \times 100))")
        st.markdown("**4. Structural Deficit Score (SDS)**")
        st.latex(r"SDS = \frac{Bed\% + Doctor\% + ICU\% + Emergency\%}{4}")
        st.markdown("<p style='font-size:0.9rem; color:#94a3b8;'>Equal weighting across all four components. State-level only — no district estimation.</p>", unsafe_allow_html=True)

    # ============================================================
    # STEP 1: Aggregate dataset to state level
    # ============================================================
    state_agg = filtered_df.groupby("State").agg(
        Total_Beds=("Total_Num_Beds", "sum"),
        Total_Doctors=("Number_Doctor", "sum"),
        Total_ICU=("has_icu", "sum"),
        Total_Emergency=("is_emergency", "sum"),
        State_Pop=("State_Population", "max")
    ).reset_index()

    # ============================================================
    # STEP 2: Required capacity (WHO scaling)
    # ============================================================
    pop = state_agg["State_Pop"]
    state_agg["Req_Beds"] = pop * 3 / 1000
    state_agg["Req_Docs"] = pop * 1 / 1000
    state_agg["Req_ICU"] = pop * 10 / 100000
    state_agg["Req_ER"] = pop * 1 / 100000

    # ============================================================
    # STEP 3: Deficit % (capped 0-100)
    # ============================================================
    state_agg["Bed_Deficit"] = (((state_agg["Req_Beds"] - state_agg["Total_Beds"]) / state_agg["Req_Beds"]) * 100).clip(0, 100)
    state_agg["Doc_Deficit"] = (((state_agg["Req_Docs"] - state_agg["Total_Doctors"]) / state_agg["Req_Docs"]) * 100).clip(0, 100)
    state_agg["ICU_Deficit"] = (((state_agg["Req_ICU"] - state_agg["Total_ICU"]) / state_agg["Req_ICU"]) * 100).clip(0, 100)
    state_agg["ER_Deficit"] = (((state_agg["Req_ER"] - state_agg["Total_Emergency"]) / state_agg["Req_ER"]) * 100).clip(0, 100)

    # ============================================================
    # STEP 4: SDS = WEIGHTED average of 4 deficits
    # ============================================================
    state_agg["SDS"] = (
        0.4 * state_agg["Bed_Deficit"] +
        0.3 * state_agg["Doc_Deficit"] +
        0.2 * state_agg["ICU_Deficit"] +
        0.1 * state_agg["ER_Deficit"]
    )

    # ============================================================
    # NATIONAL KPIs (aggregated from all states)
    # ============================================================
    nat_pop = state_agg["State_Pop"].sum()
    nat_beds = state_agg["Total_Beds"].sum()
    nat_docs = state_agg["Total_Doctors"].sum()
    nat_icu = state_agg["Total_ICU"].sum()
    nat_er = state_agg["Total_Emergency"].sum()

    nat_req_beds = nat_pop * 3 / 1000
    nat_req_docs = nat_pop * 1 / 1000
    nat_req_icu = nat_pop * 10 / 100000
    nat_req_er = nat_pop * 1 / 100000

    nat_bed_def = max(0, min(100, ((nat_req_beds - nat_beds) / nat_req_beds) * 100)) if nat_req_beds > 0 else 0
    nat_doc_def = max(0, min(100, ((nat_req_docs - nat_docs) / nat_req_docs) * 100)) if nat_req_docs > 0 else 0
    nat_icu_def = max(0, min(100, ((nat_req_icu - nat_icu) / nat_req_icu) * 100)) if nat_req_icu > 0 else 0
    nat_er_def = max(0, min(100, ((nat_req_er - nat_er) / nat_req_er) * 100)) if nat_req_er > 0 else 0

    # Weighted National SDS
    nat_sds = (0.4 * nat_bed_def + 0.3 * nat_doc_def + 0.2 * nat_icu_def + 0.1 * nat_er_def)
    systemic_adequacy = 100 - nat_sds

    # ============================================================
    # ROW 1: 4 RECALCULATED KPI CARDS
    # ============================================================
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card card-blue"><div class="kpi-title">National SDS (Weighted)</div><div class="kpi-value">{nat_sds:.1f}%</div><div class="kpi-percent">Composite Systemic Deficit</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card card-purple"><div class="kpi-title">Systemic Adequacy</div><div class="kpi-value">{systemic_adequacy:.1f}%</div><div class="kpi-percent">Capacity Health Index</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card {get_k_color(nat_bed_def)}"><div class="kpi-title">Backbone Gap (Beds)</div><div class="kpi-value">{nat_bed_def:.1f}%</div><div class="kpi-percent">Infrastructure Deficit</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card {get_k_color(nat_icu_def)}"><div class="kpi-title">Critical Gap (ICU)</div><div class="kpi-value">{nat_icu_def:.1f}%</div><div class="kpi-percent">Escalation Deficit</div></div>', unsafe_allow_html=True)

    # ============================================================
    # ROW 2: GRAPH 1 — Top 10 Structurally Deficient States
    # ============================================================
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Top 10 States \u2013 Highest Structural Deficit (Weighted SDS)</div>', unsafe_allow_html=True)
    top10_def = state_agg.sort_values("SDS", ascending=False).head(10).copy()
    top10_def["State"] = "<b>" + top10_def["State"] + "</b>"
    fig_def = go.Figure()
    fig_def.add_trace(go.Bar(name="Bed Deficit %", x=top10_def["State"], y=top10_def["Bed_Deficit"], marker_color="#ef4444"))
    fig_def.add_trace(go.Bar(name="Doctor Deficit %", x=top10_def["State"], y=top10_def["Doc_Deficit"], marker_color="#f59e0b"))
    fig_def.add_trace(go.Bar(name="ICU Deficit %", x=top10_def["State"], y=top10_def["ICU_Deficit"], marker_color="#8b5cf6"))
    fig_def.add_trace(go.Bar(name="Emergency Deficit %", x=top10_def["State"], y=top10_def["ER_Deficit"], marker_color="#ec4899"))
    fig_def.update_layout(
        barmode="group", height=400,
        yaxis=dict(range=[0, 100], title="Deficit %", ticksuffix="%"),
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=sub_text, size=18),
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center", font=dict(size=16, family="Plus Jakarta Sans", weight="bold"))
    )
    fig_def.update_xaxes(tickangle=-45, tickfont=dict(size=16, family="Plus Jakarta Sans"))
    fig_def.update_yaxes(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold"))
    st.plotly_chart(fig_def, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # ROW 3: GRAPH 2 — Top 10 Structurally Strong States
    # ============================================================
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Top 10 States \u2013 Lowest Structural Deficit (Baseline Strength)</div>', unsafe_allow_html=True)
    top10_strong = state_agg.sort_values("SDS", ascending=True).head(10).copy()
    top10_strong["State"] = "<b>" + top10_strong["State"] + "</b>"
    fig_strong = go.Figure()
    fig_strong.add_trace(go.Bar(name="Bed Deficit %", x=top10_strong["State"], y=top10_strong["Bed_Deficit"], marker_color="#10b981"))
    fig_strong.add_trace(go.Bar(name="Doctor Deficit %", x=top10_strong["State"], y=top10_strong["Doc_Deficit"], marker_color="#06b6d4"))
    fig_strong.add_trace(go.Bar(name="ICU Deficit %", x=top10_strong["State"], y=top10_strong["ICU_Deficit"], marker_color="#6366f1"))
    fig_strong.add_trace(go.Bar(name="Emergency Deficit %", x=top10_strong["State"], y=top10_strong["ER_Deficit"], marker_color="#38bdf8"))
    fig_strong.update_layout(
        barmode="group", height=400,
        yaxis=dict(range=[0, 100], title="Deficit %", ticksuffix="%"),
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=sub_text, size=18),
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center", font=dict(size=16, family="Plus Jakarta Sans", weight="bold"))
    )
    fig_strong.update_xaxes(tickangle=-45, tickfont=dict(size=16, family="Plus Jakarta Sans"))
    fig_strong.update_yaxes(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold"))
    st.plotly_chart(fig_strong, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
