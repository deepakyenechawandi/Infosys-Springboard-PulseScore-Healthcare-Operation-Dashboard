import streamlit as st
import pandas as pd
from plotly import graph_objects as go
from fpdf import FPDF
import plotly.io as pio
import os
import io

@st.cache_data
def load_data(uploaded_file=None):
  
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_dataset_path = os.path.join(base_path, "dataset", "India_Healthcare_Final_GeoPreserved.csv")
    
    if uploaded_file is not None:
        try: df = pd.read_csv(uploaded_file)
        except: df = pd.read_csv(default_dataset_path)
    else:
        df = pd.read_csv(default_dataset_path)
    
    df["State"] = df["State"].str.strip()
    
    uts_list = ["Andaman And Nicobar Islands", "Chandigarh", "Dadra And Nagar Haveli", "Daman And Diu", "Delhi", "Jammu And Kashmir", "Lakshadweep", "Puducherry"]
    df["Admin_Type"] = df["State"].apply(lambda x: "Union Territory" if x in uts_list else "State")
    
    if "Location_Coordinates" in df.columns:
        coords = df["Location_Coordinates"].str.split(",", expand=True)
        df["lat"] = pd.to_numeric(coords[0], errors="coerce")
        df["lon"] = pd.to_numeric(coords[1], errors="coerce")
    
    if "Facilities" in df.columns:
        df["has_icu"] = df["Facilities"].fillna("").str.contains("ICU", case=False)
    else:
        df["has_icu"] = False
        
    if "Emergency_Services" in df.columns:
        df["is_emergency"] = df["Emergency_Services"].str.lower() == "yes"
    else:
        df["is_emergency"] = False
    
    def clean_care_level(ct):
        if pd.isna(ct): return "Unclassified"
        ct = str(ct).lower().strip()
        if "primary" in ct: return "Primary"
        if "secondary" in ct: return "Secondary"
        if "tertiary" in ct or "super" in ct: return "Tertiary"
        return "Unclassified"
        
    if "Hospital_Care_Type" in df.columns:
        df["Care_Level_Clean"] = df["Hospital_Care_Type"].apply(clean_care_level)
    else:
        df["Care_Level_Clean"] = "Unclassified"
    
    state_stats = df.groupby("State").agg({"State_Population": "first", "Total_Num_Beds": "sum"}).reset_index()
    
    state_areas = {"Andhra Pradesh": 162970, "Arunachal Pradesh": 83743, "Assam": 78438, "Bihar": 94163, "Chhattisgarh": 135191, "Gujarat": 196024, "Haryana": 44212, "Himachal Pradesh": 55673, "Jharkhand": 79714, "Karnataka": 191791, "Kerala": 38863, "Madhya Pradesh": 308245, "Maharashtra": 307713, "Manipur": 22327, "Meghalaya": 22429, "Mizoram": 21081, "Nagaland": 16579, "Odisha": 155707, "Punjab": 50362, "Rajasthan": 342239, "Sikkim": 7096, "Tamil Nadu": 130058, "Telangana": 112077, "Tripura": 10486, "Uttar Pradesh": 240928, "Uttarakhand": 53483, "West Bengal": 88752, "Andaman And Nicobar Islands": 8249, "Chandigarh": 114, "Dadra And Nagar Haveli": 491, "Daman And Diu": 112, "Delhi": 1484, "Jammu And Kashmir": 42241}
    state_stats["Area"] = state_stats["State"].map(state_areas)
    state_stats["PopDensity"] = state_stats["State_Population"] / state_stats["Area"]
    
    return df, state_stats

def create_pdf_report(title, kpi_data, charts=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, title, ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Executive Summary KPIs:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for label, value in kpi_data.items():
        pdf.cell(0, 8, f"- {label}: {value}", ln=True)
    pdf.ln(10)
    if charts:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Visual Intelligence Report:", ln=True)
        for i, fig in enumerate(charts):
            try:
                img_bytes = pio.to_image(fig, format="png", width=800, height=450, scale=2)
                img_buf = io.BytesIO(img_bytes)
                pdf.image(img_buf, w=180)
                pdf.ln(5)
                if (i+1) % 2 == 0: pdf.add_page()
            except Exception as e:
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 10, f"[Chart {i+1} could not be rendered: {e}]", ln=True)
    return bytes(pdf.output())

def get_comprehensive_report_assets(df, global_stats, sub_text_color):
    assets = {}
    try:
        pb_df = df.groupby("State").agg({"Total_Num_Beds": "sum"}).reset_index().merge(global_stats[["State", "State_Population"]], on="State")
        fig_pb = go.Figure()
        fig_pb.add_trace(go.Bar(name="Population (M)", x=pb_df["State"], y=pb_df["State_Population"]/1e6, marker_color="#38bdf8"))
        fig_pb.add_trace(go.Bar(name="Beds (Unit x1k)", x=pb_df["State"], y=pb_df["Total_Num_Beds"]/1e3, marker_color="#ec4899"))
        fig_pb.update_layout(barmode="group", height=400, template="plotly_white", margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h", y=1.2))
        r_df = df.groupby("State").agg({"Number_Doctor": "sum", "Total_Num_Beds": "sum"}).reset_index().merge(global_stats[["State", "State_Population"]], on="State")
        r_df["Docs/10K"] = (r_df["Number_Doctor"] / r_df["State_Population"]) * 10000
        r_df["Beds/100K"] = (r_df["Total_Num_Beds"] / r_df["State_Population"]) * 100000
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(x=r_df["State"], y=r_df["Docs/10K"], mode="markers+lines", name="Doctors / 10K", line=dict(color="#8b5cf6")))
        fig_r.add_trace(go.Scatter(x=r_df["State"], y=r_df["Beds/100K"], mode="markers+lines", name="Beds / 100K", line=dict(color="#fbbf24"), yaxis="y2"))
        fig_r.update_layout(height=400, margin=dict(l=0,r=0,t=20,b=0), yaxis2=dict(overlaying="y", side="right"), legend=dict(orientation="h", y=1.2))
        assets["National Snapshot"] = [fig_pb, fig_r]
    except: pass
    return assets

def get_k_color(val):
    if val < 30: return "card-green"
    elif val < 60: return "card-orange"
    else: return "card-red"
