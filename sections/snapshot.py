import streamlit as st
from plotly import express as px
from plotly import graph_objects as go
import json, os

def render_snapshot(filtered_df, state_stats_raw, total_population, total_beds, total_doctors, distinct_states, distinct_uts, icu_percent, emergency_percent, sub_text, get_k_color=None):
    img_html = ""
    if hasattr(st.session_state, "avatar_b64") and st.session_state.avatar_b64:
        img_html = f'<img src="data:image/png;base64,{st.session_state.avatar_b64}" style="width: 100%; filter: drop-shadow(0 10px 20px rgba(0,0,0,0.3)); transform: scale(1.1);">'

    st.markdown(f'''<div style="margin-top: -30px; margin-bottom: 2rem;">
<h1 style="font-size: 3rem; font-weight: 850; color: white; letter-spacing: -1.5px; margin-bottom: 5px;">National Health Infrastructure Intelligence</h1>
<p style="font-size: 1.2rem; color: #94a3b8; font-weight: 500; margin-bottom: 2rem;">Strategic Overview of India\'s Healthcare Capacity & Resource Distribution</p>
<div style="background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%); border-radius: 28px; padding: 40px; margin-bottom: 2.5rem; display: flex; align-items: center; position: relative; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.2);">
<div style="position: absolute; right: -50px; bottom: -50px; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
<div style="flex: 0 0 180px; margin-right: 30px; position: relative; z-index: 1;">{img_html}</div>
<div style="position: relative; z-index: 1;">
    <h2 style="color: white; font-size: 2.8rem; font-weight: 850; margin: 0; letter-spacing: -1px;">Welcome Administrator</h2>
    <h3 style="color: rgba(255,255,255,0.9); font-size: 1.5rem; font-weight: 600; margin: 5px 0 15px 0;">Have a nice day.</h3>
    <p style="color: rgba(255,255,255,0.75); font-size: 1.1rem; margin: 0; max-width: 600px; line-height: 1.4; font-weight: 400;">Monitor resource alignment, search readiness, and system performance in real time.</p>
</div>
</div>
</div>''', unsafe_allow_html=True)

    # === KPI ROW ===
    total_hospitals = len(filtered_df)
    st.markdown('<div style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.markdown(f'<div class="kpi-card card-purple"><div class="kpi-title">Administrative Scope</div><div class="kpi-value">{distinct_states} <span style="font-size:16px; opacity:0.8;">States</span></div><div class="kpi-percent">{distinct_uts} Union Territories</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card card-blue"><div class="kpi-title">Total Bed Capacity</div><div class="kpi-value">{total_beds:,}</div><div class="kpi-percent">Beds Available</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card card-indigo"><div class="kpi-title">Total Medical Doctors</div><div class="kpi-value">{total_doctors:,}</div><div class="kpi-percent">Active Personnel</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card card-pink"><div class="kpi-title">National Population</div><div class="kpi-value">{total_population/1e6:.1f}M</div><div class="kpi-percent">Census Aggregate</div></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="kpi-card card-orange"><div class="kpi-title">ICU Availability</div><div class="kpi-value">{filtered_df["has_icu"].sum():,}</div><div class="kpi-percent">{icu_percent:.1f}% Hospitals</div></div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div class="kpi-card card-blue"><div class="kpi-title">Emergency Services</div><div class="kpi-value">{filtered_df["is_emergency"].sum():,}</div><div class="kpi-percent">{emergency_percent:.1f}% 24/7 Coverage</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # === CHART ROW 1: Population vs Beds + Resource Ratios ===
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">National Population vs Bed Volume</div>', unsafe_allow_html=True)
        pb_df = filtered_df.groupby("State").agg({"Total_Num_Beds": "sum"}).reset_index().merge(state_stats_raw[["State", "State_Population"]], on="State")
        pb_df["State"] = "<b>" + pb_df["State"] + "</b>"
        fig_pb = go.Figure()
        fig_pb.add_trace(go.Bar(name="Population (M)", x=pb_df["State"], y=pb_df["State_Population"]/1e6, marker_color="#38bdf8"))
        fig_pb.add_trace(go.Bar(name="Beds (Unit x1k)", x=pb_df["State"], y=pb_df["Total_Num_Beds"]/1e3, marker_color="#ec4899"))
        fig_pb.update_layout(barmode="group", height=500, template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), legend=dict(orientation="h", y=1.1, x=0, font=dict(size=16, family="Plus Jakarta Sans", weight="bold")))
        fig_pb.update_xaxes(tickfont=dict(size=16, family="Plus Jakarta Sans"))
        fig_pb.update_yaxes(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold"))
        st.plotly_chart(fig_pb, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Healthcare Resource Ratios</div>', unsafe_allow_html=True)
        r_df = filtered_df.groupby("State").agg({"Number_Doctor": "sum", "Total_Num_Beds": "sum"}).reset_index().merge(state_stats_raw[["State", "State_Population"]], on="State")
        r_df["State"] = "<b>" + r_df["State"] + "</b>"
        r_df["Docs/10K"] = (r_df["Number_Doctor"] / r_df["State_Population"]) * 10000
        r_df["Beds/100K"] = (r_df["Total_Num_Beds"] / r_df["State_Population"]) * 100000
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(x=r_df["State"], y=r_df["Docs/10K"], mode="markers+lines", name="Doctors / 10K", line=dict(color="#8b5cf6", width=4), marker=dict(size=10)))
        fig_r.add_trace(go.Scatter(x=r_df["State"], y=r_df["Beds/100K"], mode="markers+lines", name="Beds / 100K", line=dict(color="#fbbf24", width=4), marker=dict(size=10), yaxis="y2"))
        fig_r.update_layout(height=500, margin=dict(l=0, r=40, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), 
                            yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold")),
                            yaxis2=dict(overlaying="y", side="right", tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold")), 
                            legend=dict(orientation="h", y=1.1, x=0, font=dict(size=16, family="Plus Jakarta Sans", weight="bold")))
        fig_r.update_xaxes(tickfont=dict(size=16, family="Plus Jakarta Sans"))
        fig_r.update_yaxes(tickfont=dict(size=16, family="Plus Jakarta Sans"), title_font=dict(size=18, weight="bold"))
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # === CHART ROW 2: Administrative Sector Mix + Care Delivery Profile ===
    d1, d2 = st.columns(2)
    with d1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Administrative Sector Mix</div>', unsafe_allow_html=True)
        if "Hospital_Category" in filtered_df.columns:
            cat_counts = filtered_df["Hospital_Category"].value_counts()
            fig_sector = go.Figure(data=[go.Pie(
                labels=["<b>" + str(l) + "</b>" for l in cat_counts.index], values=cat_counts.values,
                hole=0.55, textinfo="percent", textposition="outside",
                marker=dict(colors=["#a78bfa", "#6366f1", "#312e81", "#818cf8", "#c4b5fd"]),
                textfont=dict(size=18, color=sub_text, weight="bold")
            )])
            fig_sector.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(size=16, family="Plus Jakarta Sans", weight="bold")))
            st.plotly_chart(fig_sector, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with d2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Healthcare Care Delivery Profile</div>', unsafe_allow_html=True)
        care_counts = None
        if "Care_Level_Clean" in filtered_df.columns:
            care_counts = filtered_df["Care_Level_Clean"].value_counts()
        elif "Hospital_Care_Type" in filtered_df.columns:
            care_counts = filtered_df["Hospital_Care_Type"].value_counts()
        if care_counts is not None:
            fig_care = go.Figure(data=[go.Pie(
                labels=["<b>" + str(l) + "</b>" for l in care_counts.index], values=care_counts.values,
                hole=0.55, textinfo="percent", textposition="outside",
                marker=dict(colors=["#ec4899", "#be185d", "#f472b6", "#fda4af", "#831843"]),
                textfont=dict(size=18, color=sub_text, weight="bold")
            )])
            fig_care.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=sub_text, size=18), legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(size=16, family="Plus Jakarta Sans", weight="bold")))
            st.plotly_chart(fig_care, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # === CHART ROW 3: National Density Map + Regional Capacity Ranking ===
    m1, m2 = st.columns([1.5, 1])
    with m1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">National Density Profile</div>', unsafe_allow_html=True)
        geo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "geojson", "india_state.geojson")
        if os.path.exists(geo_path):
            with open(geo_path, "r") as gf:
                india_geo = json.load(gf)
            # Map dataset state names to geojson state names
            name_map = {
                "Andaman And Nicobar Islands": "Andaman and Nicobar",
                "Dadra And Nagar Haveli": "Dadra and Nagar Haveli",
                "Daman And Diu": "Daman and Diu",
                "Jammu And Kashmir": "Jammu and Kashmir",
                "Odisha": "Orissa",
                "Uttarakhand": "Uttaranchal",
                "Telangana": "Andhra Pradesh",
            }
            density_df = state_stats_raw[["State", "PopDensity"]].dropna().copy()
            density_df["GeoName"] = density_df["State"].map(name_map).fillna(density_df["State"])
            fig_map = px.choropleth(
                density_df, geojson=india_geo, locations="GeoName",
                featureidkey="properties.NAME_1", color="PopDensity",
                color_continuous_scale=["#1e1b4b", "#6366f1", "#a78bfa", "#c4b5fd"],
                labels={"PopDensity": "Dens."},
                hover_data={"State": True, "GeoName": False}
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(height=800, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"), font=dict(color=sub_text, size=18, family="Plus Jakarta Sans"), coloraxis_colorbar=dict(len=0.5, y=0.5, tickfont=dict(size=16, weight="bold"), title_font=dict(size=18, weight="bold")))
            st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("GeoJSON file not found at: " + geo_path)
        st.markdown('</div>', unsafe_allow_html=True)

    with m2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Regional Capacity Ranking</div>', unsafe_allow_html=True)
        rank_mode = st.radio("Rank By", ["Beds", "Docs", "Pop"], horizontal=True, key="rank_radio")
        rank_df = filtered_df.groupby("State").agg({"Total_Num_Beds": "sum", "Number_Doctor": "sum"}).reset_index().merge(state_stats_raw[["State", "State_Population"]], on="State")
        rank_df["State"] = "<b>" + rank_df["State"] + "</b>"
        if rank_mode == "Beds":
            rank_df = rank_df.sort_values("Total_Num_Beds", ascending=True).tail(20)
            fig_rank = px.bar(rank_df, y="State", x="Total_Num_Beds", orientation="h", height=800, color="Total_Num_Beds", color_continuous_scale=["#312e81", "#6366f1", "#a78bfa"], text="Total_Num_Beds")
        elif rank_mode == "Docs":
            rank_df = rank_df.sort_values("Number_Doctor", ascending=True).tail(20)
            fig_rank = px.bar(rank_df, y="State", x="Number_Doctor", orientation="h", height=800, color="Number_Doctor", color_continuous_scale=["#312e81", "#6366f1", "#a78bfa"], text="Number_Doctor")
        else:
            rank_df = rank_df.sort_values("State_Population", ascending=True).tail(20)
            fig_rank = px.bar(rank_df, y="State", x="State_Population", orientation="h", height=800, color="State_Population", color_continuous_scale=["#312e81", "#6366f1", "#a78bfa"], text="State_Population")
        
        fig_rank.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont=dict(size=14, weight="bold"))
        fig_rank.update_layout(
            margin=dict(l=0, r=60, t=10, b=0), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color=sub_text, size=18), 
            coloraxis_showscale=False,
            xaxis=dict(showticklabels=False, title="", showgrid=False),
            yaxis=dict(tickfont=dict(size=16, family="Plus Jakarta Sans"), title="")
        )
        st.plotly_chart(fig_rank, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

