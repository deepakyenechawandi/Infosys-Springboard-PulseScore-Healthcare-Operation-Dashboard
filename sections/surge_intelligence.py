import streamlit as st
from plotly import express as px
from plotly import graph_objects as go
import pandas as pd
import numpy as np

def render_surge_intelligence(filtered_df, state_stats_raw, context_sidebar, sub_text, get_k_color):
    st.markdown('<div class="card-header" style="font-size: 2.5rem; margin-bottom: 5px;">Dynamic Surge Risk Intelligence Engine</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 1.5rem;">Weighted systemic collapse model using the Composite Surge Risk Index (SRI).</p>', unsafe_allow_html=True)

    # ============================================================
    # STEP 1 — Surge Multiplier (S) + Elasticity
    # ============================================================
    with context_sidebar:
        st.markdown('<div style="font-size:18px; font-weight:700; color:white; margin-bottom:10px;">SURGE PARAMETERS</div>', unsafe_allow_html=True)
        S = st.slider("Surge Multiplier (S)", 1.0, 3.0, 1.0, step=0.1, help="Demand expansion factor relative to baseline.")
        
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px; font-weight:700; color:#38bdf8; margin-bottom:5px;">CAPACITY STRETCH</div>', unsafe_allow_html=True)
        elasticity_factor = st.slider("Elasticity Factor (%)", 0, 30, 15, step=5, help="Simulate temporary infrastructure stretch (e.g., 15% stretch).")
        E = 1 + (elasticity_factor / 100)
        
        st.markdown("---")
        with st.expander("SRI Mathematical Framework"):
            st.markdown("""
                **1. Scaling Logic**
                `Surge_Required_X = Required_X * S`
                
                **2. Stress Calculation**
                `Stress_X = Surge_Required_X / (Available_X * E)`
                
                **3. Composite Surge Risk Index (SRI)**
                `SRI = (0.4 * Stress_Beds) + (0.3 * Stress_Docs) + (0.2 * Stress_ICU) + (0.1 * Stress_ER)`
                
                **4. Risk Classification**
                - `< 1.0`: Stable
                - `1.0 - 1.2`: Saturated
                - `1.2 - 1.5`: High Risk
                - `> 1.5`: Critical
            """)

    # ============================================================
    # STEP 2 & 3 — Base & Surge-Adjusted Requirement (State Level)
    # ============================================================
    state_agg = filtered_df.groupby("State").agg(
        Avail_Beds=("Total_Num_Beds", "sum"),
        Avail_Docs=("Number_Doctor", "sum"),
        Avail_ICU=("has_icu", "sum"),
        Avail_ER=("is_emergency", "sum"),
        State_Pop=("State_Population", "max")
    ).reset_index()

    pop = state_agg["State_Pop"]
    # Required_X (Base)
    state_agg["Req_B_Base"] = pop * 3 / 1000
    state_agg["Req_D_Base"] = pop * 1 / 1000
    state_agg["Req_I_Base"] = pop * 10 / 100000
    state_agg["Req_E_Base"] = pop * 1 / 100000

    # STEP 4 — Create Surge Stress Ratios (State Level)
    state_agg["Stress_B"] = (state_agg["Req_B_Base"] * S) / (state_agg["Avail_Beds"].clip(1) * E)
    state_agg["Stress_D"] = (state_agg["Req_D_Base"] * S) / (state_agg["Avail_Docs"].clip(1) * E)
    state_agg["Stress_I"] = (state_agg["Req_I_Base"] * S) / (state_agg["Avail_ICU"].clip(1) * E)
    state_agg["Stress_E"] = (state_agg["Req_E_Base"] * S) / (state_agg["Avail_ER"].clip(1) * E)

    # STEP 5 — Composite Surge Risk Index (SRI)
    state_agg["SRI"] = (
        0.4 * state_agg["Stress_B"] +
        0.3 * state_agg["Stress_D"] +
        0.2 * state_agg["Stress_I"] +
        0.1 * state_agg["Stress_E"]
    ).round(3)

    # STEP 7 — District-Level Surge Index (Proportional Allocation)
    dist_agg = filtered_df.groupby(["State", "District"]).agg(
        Avail_Beds=("Total_Num_Beds", "sum"),
        Avail_Docs=("Number_Doctor", "sum"),
        Avail_ICU=("has_icu", "sum"),
        Avail_ER=("is_emergency", "sum"),
    ).reset_index()

    state_totals = dist_agg.groupby("State").agg({
        "Avail_Beds": "sum", "Avail_Docs": "sum", "Avail_ICU": "sum", "Avail_ER": "sum"
    }).rename(columns=lambda x: "State_" + x).reset_index()
    
    dist_agg = dist_agg.merge(state_totals, on="State").merge(state_agg[["State", "Req_B_Base", "Req_D_Base", "Req_I_Base", "Req_E_Base"]], on="State")
    
    # District Share (District_Beds / State_Total_Beds)
    dist_agg["Bed_Share"] = dist_agg["Avail_Beds"] / dist_agg["State_Avail_Beds"].clip(1)
    dist_agg["Doc_Share"] = dist_agg["Avail_Docs"] / dist_agg["State_Avail_Docs"].clip(1)
    dist_agg["ICU_Share"] = dist_agg["Avail_ICU"] / dist_agg["State_Avail_ICU"].clip(1)
    dist_agg["ER_Share"] = dist_agg["Avail_ER"] / dist_agg["State_Avail_ER"].clip(1)

    # District Required = (State_Required * District_Share) * S
    dist_agg["Stress_B"] = (dist_agg["Req_B_Base"] * dist_agg["Bed_Share"] * S) / (dist_agg["Avail_Beds"].clip(1) * E)
    dist_agg["Stress_D"] = (dist_agg["Req_D_Base"] * dist_agg["Doc_Share"] * S) / (dist_agg["Avail_Docs"].clip(1) * E)
    dist_agg["Stress_I"] = (dist_agg["Req_I_Base"] * dist_agg["ICU_Share"] * S) / (dist_agg["Avail_ICU"].clip(1) * E)
    dist_agg["Stress_E"] = (dist_agg["Req_E_Base"] * dist_agg["ER_Share"] * S) / (dist_agg["Avail_ER"].clip(1) * E)

    dist_agg["SRI"] = (
        0.4 * dist_agg["Stress_B"] + 
        0.3 * dist_agg["Stress_D"] + 
        0.2 * dist_agg["Stress_I"] + 
        0.1 * dist_agg["Stress_E"]
    ).round(3)

    # Calculations for Table (Additional Needed)
    dist_agg["Surge_Req_B"] = (dist_agg["Req_B_Base"] * dist_agg["Bed_Share"] * S).round(0)
    dist_agg["Add_B_Needed"] = (dist_agg["Surge_Req_B"] - (dist_agg["Avail_Beds"] * E)).clip(0).round(0)
    
    dist_agg["Surge_Req_I"] = (dist_agg["Req_I_Base"] * dist_agg["ICU_Share"] * S).round(0)
    dist_agg["Add_I_Needed"] = (dist_agg["Surge_Req_I"] - (dist_agg["Avail_ICU"] * E)).clip(0).round(0)
    
    dist_agg["Surge_Req_D"] = (dist_agg["Req_D_Base"] * dist_agg["Doc_Share"] * S).round(0)
    dist_agg["Add_D_Needed"] = (dist_agg["Surge_Req_D"] - (dist_agg["Avail_Docs"] * E)).clip(0).round(0)
    
    dist_agg["Surge_Req_E"] = (dist_agg["Req_E_Base"] * dist_agg["ER_Share"] * S).round(0)
    dist_agg["Add_E_Needed"] = (dist_agg["Surge_Req_E"] - (dist_agg["Avail_ER"] * E)).clip(0).round(0)

    # PAGE 4 VISUAL STRUCTURE
    # ============================================================
    # 1. Surge Slider + KPIs
    # ============================================================
    st.markdown("<br>", unsafe_allow_html=True)
    high_risk_states = len(state_agg[state_agg["SRI"] > 1.2])
    high_risk_districts = len(dist_agg[dist_agg["SRI"] > 1.2])
    worst_sri = state_agg["SRI"].max()

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card card-blue"><div class="kpi-title">Current Multiplier</div><div class="kpi-value">{S:.1f}x</div><div class="kpi-percent">Demand Growth</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card card-orange"><div class="kpi-title">High Risk States</div><div class="kpi-value">{high_risk_states}</div><div class="kpi-percent">SRI > 1.2</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card card-red"><div class="kpi-title">High Risk Districts</div><div class="kpi-value">{high_risk_districts}</div><div class="kpi-percent">SRI > 1.2</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card card-purple"><div class="kpi-title">Worst SRI Value</div><div class="kpi-value">{worst_sri:.2f}</div><div class="kpi-percent">Critical System Strain</div></div>', unsafe_allow_html=True)

    def get_risk_color(sri):
        if sri < 1.0: return "#10b981" # Green
        if sri < 1.2: return "#f59e0b" # Yellow (Orange-ish)
        if sri < 1.5: return "#f97316" # Orange
        return "#ef4444" # Red

    # ============================================================
    # 2. Dynamic High Risk States (Horizontal Bar)
    # ============================================================
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header">Dynamic State Risk Ranking (SRI > 1.0 @ {S:.1f}x Surge)</div>', unsafe_allow_html=True)
    
    risk_states = state_agg[state_agg["SRI"] > 1.0].sort_values("SRI", ascending=True).copy()
    if not risk_states.empty:
        risk_states["State"] = "<b>" + risk_states["State"] + "</b>"
        colors = [get_risk_color(s) for s in risk_states["SRI"]]
        fig_s = go.Figure(go.Bar(
            x=risk_states["SRI"], y=risk_states["State"], orientation="h",
            marker_color=colors, text=risk_states["SRI"], textposition="outside"
        ))
        fig_s.update_layout(height=max(200, len(risk_states)*25), margin=dict(l=0,r=40,t=40,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")))
        fig_s.add_vline(x=1.2, line_dash="dash", line_color="black", line_width=2)
        fig_s.add_annotation(x=1.2, y=1, yref="paper", text="High Risk Threshold", showarrow=False, yanchor="bottom", font=dict(size=14, color="black", weight="bold"))
        st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})
    else:
        st.success("No states currently at risk. System capacity fully adequate for this surge.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # 3. Dynamic High Risk Districts (Horizontal Bar)
    # ============================================================
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header">Top 25 Critical Districts (SRI > 1.0)</div>', unsafe_allow_html=True)
    
    risk_dist = dist_agg[dist_agg["SRI"] > 1.0].sort_values("SRI", ascending=True).tail(25).copy()
    if not risk_dist.empty:
        risk_dist["District"] = "<b>" + risk_dist["District"] + "</b>"
        colors = [get_risk_color(s) for s in risk_dist["SRI"]]
        fig_d = go.Figure(go.Bar(
            x=risk_dist["SRI"], y=risk_dist["District"], orientation="h",
            marker_color=colors, text=risk_dist["SRI"], textposition="outside"
        ))
        fig_d.update_layout(height=600, margin=dict(l=0,r=40,t=10,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), categoryorder="total ascending"))
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
    else:
        st.success("No districts currently at risk.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # 4. Surge Requirement Table
    # ============================================================
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header">Systemic Requirement Matrix ({S:.1f}x Surge @ {E:.1f}x Elasticity)</div>', unsafe_allow_html=True)
    
    table_df = dist_agg[[
        "State", "District", "SRI",
        "Avail_Beds", "Surge_Req_B", "Add_B_Needed",
        "Avail_ICU", "Surge_Req_I", "Add_I_Needed",
        "Avail_Docs", "Surge_Req_D", "Add_D_Needed",
        "Avail_ER", "Surge_Req_E", "Add_E_Needed"
    ]].copy()
    
    table_df.columns = [
        "State", "District", "SRI",
        "Avail Beds", "Surge Req Beds", "Add. Beds Needed",
        "Avail ICU", "Surge Req ICU", "Add. ICU Needed",
        "Avail Docs", "Surge Req Docs", "Add. Docs Needed",
        "Avail ER", "Surge Req ER", "Add. ER Needed"
    ]
    
    st.dataframe(table_df.sort_values("SRI", ascending=False), use_container_width=True, height=400)
    
    csv = table_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Full Surge Requirements CSV", data=csv, file_name=f"surge_plan_{S}x.csv", mime="text/csv", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
