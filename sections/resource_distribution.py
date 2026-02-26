import streamlit as st
from plotly import express as px
from plotly import graph_objects as go
import pandas as pd

def render_resource_distribution(filtered_df, sub_text, get_k_color):
    st.markdown('<div class="card-header" style="font-size: 2.5rem; margin-bottom: 5px;">District Infrastructure & Critical Care Distribution</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 1.5rem;">Where are healthcare resources concentrated at district level, and where do critical gaps exist?</p>', unsafe_allow_html=True)

    # ============================================================
    # DISTRICT-LEVEL AGGREGATION
    # ============================================================
    dist_agg = filtered_df.groupby(["State", "District"]).agg(
        Total_Beds=("Total_Num_Beds", "sum"),
        Total_Doctors=("Number_Doctor", "sum"),
        ICU_Count=("has_icu", "sum"),
        Emergency_Count=("is_emergency", "sum"),
    ).reset_index()

    dist_agg["Doc_per_100Beds"] = ((dist_agg["Total_Doctors"] / dist_agg["Total_Beds"].clip(1)) * 100).round(1)

    # ============================================================
    # NATIONAL KPIs
    # ============================================================
    nat_beds = dist_agg["Total_Beds"].sum()
    nat_icu = dist_agg["ICU_Count"].sum()
    nat_er = dist_agg["Emergency_Count"].sum()
    nat_docs = dist_agg["Total_Doctors"].sum()
    nat_doc_per_100 = (nat_docs / max(nat_beds, 1)) * 100

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card card-blue"><div class="kpi-title">Total District Bed Capacity</div><div class="kpi-value">{nat_beds:,}</div><div class="kpi-percent">National Aggregate</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card card-purple"><div class="kpi-title">ICU-Enabled Hospitals</div><div class="kpi-value">{nat_icu:,}</div><div class="kpi-percent">Critical Care Points</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card card-pink"><div class="kpi-title">Emergency-Enabled Hospitals</div><div class="kpi-value">{nat_er:,}</div><div class="kpi-percent">24/7 Service Points</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card card-indigo"><div class="kpi-title">Avg Doctors per 100 Beds</div><div class="kpi-value">{nat_doc_per_100:.1f}</div><div class="kpi-percent">National Workforce Density</div></div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 1: BED DISTRIBUTION
    # ============================================================
    st.markdown('<div style="margin: 2rem 0 0.5rem; font-size: 1.2rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px;">Bed Concentration</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)

    with b1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Top 10 Districts \u2013 Highest Bed Capacity</div>', unsafe_allow_html=True)
        top10_beds = dist_agg.sort_values("Total_Beds", ascending=False).head(10).sort_values("Total_Beds", ascending=True).copy()
        top10_beds["District"] = "<b>" + top10_beds["District"] + "</b>"
        fig = px.bar(top10_beds, y="District", x="Total_Beds", orientation="h", height=350,
                     color="Total_Beds", color_continuous_scale=["#312e81", "#6366f1", "#a78bfa"],
                     hover_data={"State": True, "Total_Beds": ":,"})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Bottom 10 Districts \u2013 Lowest Bed Capacity</div>', unsafe_allow_html=True)
        bottom_beds = dist_agg[dist_agg["Total_Beds"] > 50].sort_values("Total_Beds", ascending=True).head(10).copy()
        if len(bottom_beds) < 10:
            bottom_beds = dist_agg.sort_values("Total_Beds", ascending=True).head(10).copy()
        bottom_beds["District"] = "<b>" + bottom_beds["District"] + "</b>"
        fig = px.bar(bottom_beds, y="District", x="Total_Beds", orientation="h", height=350,
                     color="Total_Beds", color_continuous_scale=["#ef4444", "#f59e0b", "#fbbf24"],
                     hover_data={"State": True, "Total_Beds": ":,"})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 2: ICU DISTRIBUTION
    # ============================================================
    st.markdown('<div style="margin: 2rem 0 0.5rem; font-size: 1.2rem; font-weight: 700; color: #a78bfa; text-transform: uppercase; letter-spacing: 1px;">ICU Distribution</div>', unsafe_allow_html=True)
    i1, i2 = st.columns(2)

    with i1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Top 10 Districts \u2013 Highest ICU Presence</div>', unsafe_allow_html=True)
        top10_icu = dist_agg.sort_values("ICU_Count", ascending=False).head(10).sort_values("ICU_Count", ascending=True).copy()
        top10_icu["District"] = "<b>" + top10_icu["District"] + "</b>"
        fig = px.bar(top10_icu, y="District", x="ICU_Count", orientation="h", height=350,
                     color="ICU_Count", color_continuous_scale=["#312e81", "#8b5cf6", "#c4b5fd"],
                     hover_data={"State": True})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with i2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Largest Districts Without ICU Facilities</div>', unsafe_allow_html=True)
        no_icu = dist_agg[dist_agg["ICU_Count"] == 0].sort_values("Total_Beds", ascending=False).head(10).sort_values("Total_Beds", ascending=True).copy()
        if len(no_icu) > 0:
            no_icu["District"] = "<b>" + no_icu["District"] + "</b>"
            fig = px.bar(no_icu, y="District", x="Total_Beds", orientation="h", height=350,
                         color="Total_Beds", color_continuous_scale=["#881337", "#e11d48", "#fb7185"],
                         hover_data={"State": True, "Total_Beds": ":,"})
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis_title="Total Beds (No ICU)", xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold")))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.success("All districts have at least one ICU-enabled hospital.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 3: EMERGENCY SERVICE DISTRIBUTION
    # ============================================================
    st.markdown('<div style="margin: 2rem 0 0.5rem; font-size: 1.2rem; font-weight: 700; color: #ec4899; text-transform: uppercase; letter-spacing: 1px;">Emergency Service Distribution</div>', unsafe_allow_html=True)
    e1, e2 = st.columns(2)

    with e1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Top 10 Districts \u2013 Emergency Facility Presence</div>', unsafe_allow_html=True)
        top10_er = dist_agg.sort_values("Emergency_Count", ascending=False).head(10).sort_values("Emergency_Count", ascending=True).copy()
        top10_er["District"] = "<b>" + top10_er["District"] + "</b>"
        fig = px.bar(top10_er, y="District", x="Emergency_Count", orientation="h", height=350,
                     color="Emergency_Count", color_continuous_scale=["#831843", "#ec4899", "#f9a8d4"],
                     hover_data={"State": True})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with e2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Largest Districts Without Emergency Facilities</div>', unsafe_allow_html=True)
        no_er = dist_agg[dist_agg["Emergency_Count"] == 0].sort_values("Total_Beds", ascending=False).head(10).sort_values("Total_Beds", ascending=True).copy()
        if len(no_er) > 0:
            no_er["District"] = "<b>" + no_er["District"] + "</b>"
            fig = px.bar(no_er, y="District", x="Total_Beds", orientation="h", height=350,
                         color="Total_Beds", color_continuous_scale=["#7c2d12", "#ea580c", "#fdba74"],
                         hover_data={"State": True, "Total_Beds": ":,"})
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis_title="Total Beds (No Emergency)", xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold")))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.success("All districts have at least one emergency-enabled hospital.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 4: DOCTOR-TO-BED RATIO
    # ============================================================
    st.markdown('<div style="margin: 2rem 0 0.5rem; font-size: 1.2rem; font-weight: 700; color: #f59e0b; text-transform: uppercase; letter-spacing: 1px;">Workforce Balance</div>', unsafe_allow_html=True)
    w1, w2 = st.columns(2)

    # Filter to districts with meaningful data
    ratio_df = dist_agg[dist_agg["Total_Beds"] > 50].copy()

    with w1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Bottom 10 Districts \u2013 Lowest Doctors per 100 Beds</div>', unsafe_allow_html=True)
        bottom_ratio = ratio_df.sort_values("Doc_per_100Beds", ascending=True).head(10).copy()
        bottom_ratio["District"] = "<b>" + bottom_ratio["District"] + "</b>"
        fig = px.bar(bottom_ratio, y="District", x="Doc_per_100Beds", orientation="h", height=350,
                     color="Doc_per_100Beds", color_continuous_scale=["#ef4444", "#f59e0b", "#fbbf24"],
                     hover_data={"State": True, "Total_Beds": ":,", "Total_Doctors": ":,"})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis_title="Doctors per 100 Beds", xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with w2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Top 10 Districts \u2013 Highest Doctors per 100 Beds</div>', unsafe_allow_html=True)
        top_ratio = ratio_df.sort_values("Doc_per_100Beds", ascending=False).head(10).sort_values("Doc_per_100Beds", ascending=True).copy()
        top_ratio["District"] = "<b>" + top_ratio["District"] + "</b>"
        fig = px.bar(top_ratio, y="District", x="Doc_per_100Beds", orientation="h", height=420,
                     color="Doc_per_100Beds", color_continuous_scale=["#065f46", "#10b981", "#6ee7b7"],
                     hover_data={"State": True, "Total_Beds": ":,", "Total_Doctors": ":,"})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans")), xaxis_title="Doctors per 100 Beds", xaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 5: CARE TYPE DISTRIBUTION (State-Level Grouped Bar)
    # ============================================================
    st.markdown('<div style="margin: 2rem 0 0.5rem; font-size: 1.2rem; font-weight: 700; color: #06b6d4; text-transform: uppercase; letter-spacing: 1px;">Care Hierarchy</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">State-wise Care Type Distribution</div>', unsafe_allow_html=True)

    care_col = "Care_Level_Clean" if "Care_Level_Clean" in filtered_df.columns else "Hospital_Care_Type"
    if care_col in filtered_df.columns:
        care_state = filtered_df.groupby(["State", care_col]).size().reset_index(name="Count").copy()
        care_state["State"] = "<b>" + care_state["State"] + "</b>"
        fig_care = px.bar(care_state, x="State", y="Count", color=care_col, barmode="group", height=400,
                          color_discrete_sequence=["#06b6d4", "#8b5cf6", "#ec4899", "#f59e0b"])
        fig_care.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=sub_text, size=18),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", title="", font=dict(size=16, family="Plus Jakarta Sans", weight="bold")),
            xaxis=dict(tickangle=-45, tickfont=dict(size=16, family="Plus Jakarta Sans")),
            yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold"))
        )
        st.plotly_chart(fig_care, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Care Type column not available in this dataset.")

    st.markdown('</div>', unsafe_allow_html=True)
