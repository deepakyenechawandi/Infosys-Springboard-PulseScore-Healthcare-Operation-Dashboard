import streamlit as st
from plotly import express as px
from plotly import graph_objects as go
import pandas as pd

def render_equity_allocation(filtered_df, sub_text, get_k_color):
    st.markdown('<div class="card-header" style="font-size: 2.5rem; margin-bottom: 5px;">Social Equity & EWS Allocation Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 1.5rem;">Monitoring Economically Weaker Section (EWS) safeguards and allocative fairness across sectors.</p>', unsafe_allow_html=True)

    # ============================================================
    # EQUITY AGGREGATION
    # ============================================================
    # Columns: Num_Bed_For_Eco_Weaker_Sec, Total_Num_Beds, Hospital_Category
    
    total_ews_beds = filtered_df["Num_Bed_For_Eco_Weaker_Sec"].sum()
    total_beds = filtered_df["Total_Num_Beds"].sum()
    ews_ratio = (total_ews_beds / total_beds * 100) if total_beds > 0 else 0
    
    public_hospitals = len(filtered_df[filtered_df["Hospital_Category"].str.contains("Govt|Public", case=False, na=False)])
    private_hospitals = len(filtered_df) - public_hospitals
    public_ratio = (public_hospitals / len(filtered_df) * 100) if len(filtered_df) > 0 else 0

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card card-purple"><div class="kpi-title">Total EWS Bed Assets</div><div class="kpi-value">{total_ews_beds:,}</div><div class="kpi-percent">Reserved Capacity</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card card-blue"><div class="kpi-title">Equity Saturation</div><div class="kpi-value">{ews_ratio:.1f}%</div><div class="kpi-percent">Avg Bed Reservation</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card card-indigo"><div class="kpi-title">Public Sector Share</div><div class="kpi-value">{public_ratio:.1f}%</div><div class="kpi-percent">Government Backbone</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card card-pink"><div class="kpi-title">Allocative Justice Index</div><div class="kpi-value">{(ews_ratio * 0.7 + public_ratio * 0.3):.1f}</div><div class="kpi-percent">Equity Metric</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">EWS Bed Deployment by State</div>', unsafe_allow_html=True)
        state_ews = filtered_df.groupby("State").agg({"Num_Bed_For_Eco_Weaker_Sec": "sum"}).reset_index().sort_values("Num_Bed_For_Eco_Weaker_Sec", ascending=True)
        fig_ews = px.bar(state_ews, y="State", x="Num_Bed_For_Eco_Weaker_Sec", orientation="h", height=500,
                         color="Num_Bed_For_Eco_Weaker_Sec", color_continuous_scale=["#312e81", "#6366f1", "#a78bfa"])
        fig_ews.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=16), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=14)), xaxis=dict(tickfont=dict(size=14)))
        st.plotly_chart(fig_ews, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Sectoral Balance: Public vs Private</div>', unsafe_allow_html=True)
        if "Hospital_Category" in filtered_df.columns:
            cat_counts = filtered_df["Hospital_Category"].value_counts().head(5)
            fig_cat = px.pie(names=cat_counts.index, values=cat_counts.values, hole=0.6,
                             color_discrete_sequence=["#6366f1", "#0ea5e9", "#ec4899", "#f59e0b", "#10b981"])
            fig_cat.update_layout(height=450, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=16), legend=dict(orientation="h", y=-0.1, font=dict(size=14)))
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Prescriptive Allocation Engine (Top 10 High-Priority Districts)</div>', unsafe_allow_html=True)
    st.markdown("""Analyzing current EWS bed gaps and population densities to recommend strategic asset placement.""")
    
    # Simple logic: Districts with highest beds but < 5% EWS share are high priority for mandates
    dist_priority = filtered_df.groupby(["State", "District"]).agg({
        "Total_Num_Beds": "sum",
        "Num_Bed_For_Eco_Weaker_Sec": "sum"
    }).reset_index()
    dist_priority["EWS_Share"] = (dist_priority["Num_Bed_For_Eco_Weaker_Sec"] / dist_priority["Total_Num_Beds"] * 100).round(2)
    
    priority_table = dist_priority[dist_priority["Total_Num_Beds"] > 500].sort_values("EWS_Share", ascending=True).head(10)
    priority_table.columns = ["State", "District", "Current Total Beds", "EWS Beds", "EWS Share (%)"]
    
    st.dataframe(priority_table, use_container_width=True)
    st.info("Policy Recommendation: Districts listed above show high infrastructure volume but critical undersupply of EWS-guaranteed beds. Mandating a 10% EWS conversion in these zones could fix urban equity gaps without new construction.")
    st.markdown('</div>', unsafe_allow_html=True)
