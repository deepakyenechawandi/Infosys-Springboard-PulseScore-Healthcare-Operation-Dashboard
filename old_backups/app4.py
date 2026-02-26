
import base64
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sections.nearest_hospital import show_nearest_hospital

st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    layout="wide",
    page_icon="🏥"
)





if "theme" not in st.session_state:
    st.session_state.theme = "Light"

top1, top2, top3 = st.columns([6, 2, 1])

with top3:
    if st.toggle("Dark Mode", value=st.session_state.theme == "Dark"):
        st.session_state.theme = "Dark"
    else:
        st.session_state.theme = "Light"

theme = st.session_state.theme


if theme == "Dark":
    BG = "#0b1220"
    CARD = "#24005A"
    TEXT = "#ffffff"
    SIDEBAR = "#0f172a"
    ACCENT = "#38bdf8"
    HEADER = "#111827"
    BORDER = "#1f2937"
    PLOT_THEME = "plotly_dark"
else:
    BG = "#e8f1fb"
    CARD = "#ffffff"
    TEXT = "#000000"
    SIDEBAR = "#ffffff"
    ACCENT = "#2f6fad"
    HEADER = "#bcd3ea"
    BORDER = "#c5d6ea"
    PLOT_THEME = "plotly"


import os
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return "" # Return empty string if image is missing
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()



st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
/* Main App Body */
.stApp {{
background: radial-gradient(circle at top left, {BG}, #f0f4f8);
color: {TEXT};
font-family: 'Inter', sans-serif;
}}

/* Sidebar Styling */
section[data-testid="stSidebar"] {{
background: linear-gradient(180deg, {SIDEBAR} 0%, #0a2540 100%);
box-shadow: 4px 0 15px rgba(0,0,0,0.1);
}}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div {{
color: {TEXT} !important;
font-weight: 500;
font-size: 22px !important;
line-height: 1.5 !important;
}}

[data-testid="stSidebar"] h1 {{
font-size: 35px !important;
font-weight: 800 !important;
color: {TEXT} !important;
}}

[data-testid="stSidebar"] h2 {{
font-size: 25px !important;
font-weight: 700 !important;
color: {TEXT} !important;
}}

/* Global Text and Component Labels */
.stApp label, 
.stApp span, 
.stApp p, 
.stApp div[data-testid="stMarkdownContainer"] p,
.stApp .stWidgetLabel p {{
    color: {TEXT} !important;
}}

/* Fix for widgets like radio, slider, and inputs */
div[data-testid="stRadio"] label, 
div[data-testid="stSlider"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {{
    color: {TEXT} !important;
}}

/* Glassmorphism Sidebar Buttons */
[data-testid="stSidebar"] .stButton > button {{
background: rgba(255, 255, 255, 0.05) !important;
border: 1px solid rgba(255, 255, 255, 0.1) !important;
color: white !important;
border-radius: 12px !important;
padding: 12px 20px !important;
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
text-transform: capitalize;
font-weight: 600 !important;
font-size: 20px !important;
height: auto !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
background: rgba(255, 255, 255, 0.15) !important;
transform: translateX(5px);
border: 1px solid rgba(255, 255, 255, 0.3) !important;
}}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
background: linear-gradient(90deg, #3b82f6, #2563eb) !important;
border: none !important;
box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}}

/* KPI Card Enhancement */
.kpi-card {{
background: {CARD};
backdrop-filter: blur(10px);
-webkit-backdrop-filter: blur(10px);
padding: 25px;
border-radius: 20px;
border: 1px solid {BORDER};
box-shadow: 0 10px 30px rgba(0,0,0,0.05);
transition: all 0.4s ease;
display: flex;
flex-direction: column;
justify-content: flex-start;
position: relative;
overflow: hidden;
height: 300px !important;
}}

.kpi-card:hover {{
transform: translateY(-10px);
box-shadow: 0 20px 40px rgba(0,0,0,0.1);
border-color: {ACCENT};
}}

.kpi-card::after {{
content: '';
position: absolute;
top: 0;
left: 0;
width: 100%;
height: 4px;
background: linear-gradient(90deg, transparent, {ACCENT}, transparent);
opacity: 0;
transition: opacity 0.3s;
}}

.kpi-card:hover::after {{
opacity: 1;
}}

.kpi-icon {{
font-size: 60px !important;
margin-bottom: 20px !important;
opacity: 0.8;
}}

.kpi-title {{
font-size: 35px !important;
font-weight: 700 !important;
color: #000000 !important;
text-transform: uppercase;
letter-spacing: 0.05em;
margin-bottom: 5px !important;
min-height: 100px !important;
display: flex !important;
align-items: center !important;
}}

.kpi-value {{
font-size: 35px !important;
font-weight: 900 !important;
color: {TEXT};
letter-spacing: -0.02em;
margin-top: auto !important;
}}

/* Header and Titles */
.section-title {{
font-size: 42px;
font-weight: 900;
background: linear-gradient(135deg, {TEXT} 0%, #64748b 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
margin: 40px 0 25px 0;
letter-spacing: -0.03em;
}}

/* Plotly Chart Containers */
.stPlotlyChart {{
background: {CARD};
padding: 10px; /* Reduced padding to give more space for chart */
border-radius: 20px;
border: 1px solid {BORDER};
box-shadow: 0 4px 20px rgba(0,0,0,0.03);
overflow: hidden !important; /* Prevent chart overflow */
box-sizing: border-box !important;
}}

/* Tables and Dataframes */
.stDataFrame {{
border-radius: 15px;
overflow: hidden;
border: 1px solid {BORDER};
}}

/* Text Input and Multiselect Enhancement */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stMultiselect div[data-baseweb="select"] span,
.stMultiselect div[data-baseweb="select"] div {{
background: rgba(0,0,0,0.4) !important;
border: 1px solid rgba(255,255,255,0.1) !important;
border-radius: 10px !important;
color: #ffffff !important;
}}

/* Placeholder and internal text color fixes */
.stMultiselect input::placeholder,
.stTextInput input::placeholder {{
    color: rgba(255, 255, 255, 0.6) !important;
}}

/* Custom Scrollbar */
::-webkit-scrollbar {{
width: 8px;
height: 8px;
}}
::-webkit-scrollbar-track {{
background: transparent;
}}
::-webkit-scrollbar-thumb {{
background: rgba(100, 116, 139, 0.2);
border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{
background: rgba(100, 116, 139, 0.4);
}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("India_Healthcare_Final_GeoPreserved.csv")

    # numeric cleaning
    df["Total_Num_Beds"] = pd.to_numeric(df["Total_Num_Beds"], errors="coerce")
    df["Number_Doctor"] = pd.to_numeric(df["Number_Doctor"], errors="coerce")

    # emergency flag
    df["Emergency_Flag"] = (
        df["Emergency_Services"]
        .astype(str)
        .str.lower()
        .str.contains("yes")
        .astype(int)
    )

    # doctor-bed ratio
    df["Doctor_Bed_Ratio"] = df["Number_Doctor"] / df["Total_Num_Beds"]

    # coordinate parsing
    coords = df["Location_Coordinates"].str.split(",", expand=True)
    df["lat"] = pd.to_numeric(coords[0], errors="coerce")
    df["lon"] = pd.to_numeric(coords[1], errors="coerce")

    return df

df = load_data()

#sidebar

st.sidebar.title("Healthcare Dashboard")

search = st.sidebar.text_input("Search Hospital")

state_filter = st.sidebar.multiselect(
    "Select State",
    sorted(df["State"].dropna().unique())
)

category_filter = st.sidebar.multiselect(
    "Hospital Category",
    sorted(df["Hospital_Category"].dropna().unique())
)

st.sidebar.markdown("## Navigation")

if "page" not in st.session_state:
    st.session_state.page = "Overview"

pages = ["Overview", "Infrastructure", "Emergency", "Doctor Analysis", "Geographic", "Nearest Hospital", "Insights"]

for p in pages:
    if st.sidebar.button(
        p,
        use_container_width=True,
        type="primary" if st.session_state.page == p else "secondary"
    ):
        st.session_state.page = p

# ============================================
# FILTER LOGIC
# ============================================

filtered_df = df.copy()

if state_filter:
    filtered_df = filtered_df[filtered_df["State"].isin(state_filter)]

if category_filter:
    filtered_df = filtered_df[filtered_df["Hospital_Category"].isin(category_filter)]

if search:
    filtered_df = filtered_df[
        filtered_df["Hospital_Name"].str.contains(search, case=False, na=False)
    ]

# ============================================
# DATA EXPORT
# ============================================
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Export")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Download Data",
    data=csv,
    file_name="healthcare_data_filtered.csv",
    mime="text/csv",
    use_container_width=True
)

page = st.session_state.page

# ============================================
# WELCOME HEADER
# ============================================

# Load image
img_base64 = get_base64_image("hospital1.jpg")

st.markdown(f"""
<div style="
background: linear-gradient(135deg, {HEADER} 0%, {ACCENT} 100%);
padding: 40px;
border-radius: 24px;
margin-bottom: 35px;
border: 1px solid rgba(255,255,255,0.1);
box-shadow: 0 20px 40px rgba(0,0,0,0.1);
display: flex;
justify-content: space-between;
align-items: center;
position: relative;
overflow: hidden;
">
<!-- Subtle Background Pattern -->
<div style="
position: absolute;
top: -50%;
left: -20%;
width: 140%;
height: 200%;
background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
transform: rotate(-15deg);
pointer-events: none;
"></div>

<div style="position: relative; z-index: 1;">
<h1 style="
margin: 0;
font-size: 42px;
font-weight: 800;
color: {TEXT};
letter-spacing: -0.04em;
line-height: 1.1;
">
Welcome, Administrator
</h1>
<p style="
margin-top: 15px;
font-size: 18px;
color: {TEXT};
opacity: 0.85;
max-width: 550px;
font-weight: 400;
line-height: 1.6;
">
Global Health Infrastructure & Intelligence Systems. 
Real-time monitoring of workforce capacity, emergency readiness, and asset distribution.
</p>
</div>

<div style="
position: relative;
z-index: 1;
background: rgba(255, 255, 255, 0.2);
backdrop-filter: blur(15px);
padding: 12px;
border-radius: 20px;
border: 1px solid rgba(255, 255, 255, 0.3);
">
<img src="data:image/png;base64,{img_base64}" 
width="140" 
style="border-radius: 12px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));"
alt="Hospital System">
</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# KPI SECTION
# ============================================

col1, col2, col3, col4 = st.columns(4)

if page == "Overview":
    metrics = [
        ("", "Total Hospitals", len(filtered_df)),
        ("", "States Covered", filtered_df["State"].nunique()),
        ("", "Hospital Categories", filtered_df["Hospital_Category"].nunique()),
        ("", "Avg Beds", f"{filtered_df['Total_Num_Beds'].mean():,.0f}")
    ]
elif page == "Infrastructure":
    metrics = [
        ("", "Total Beds", f"{filtered_df['Total_Num_Beds'].sum():,.0f}"),
        ("", "Avg Beds", f"{filtered_df['Total_Num_Beds'].mean():,.0f}"),
        ("", "Hospitals", len(filtered_df)),
        ("", "States", filtered_df["State"].nunique())
    ]

elif page == "Emergency":
    emergency_percent = filtered_df["Emergency_Flag"].mean() * 100
    metrics = [
        ("", "Emergency Ready %", f"{emergency_percent:.1f}%"),
        ("", "Ready Hospitals", filtered_df["Emergency_Flag"].sum()),
        ("", "Not Ready", len(filtered_df) - filtered_df["Emergency_Flag"].sum()),
        ("", "Total Hospitals", len(filtered_df))
    ]

elif page == "Doctor Analysis":
    metrics = [
        ("", "Total Doctors", f"{filtered_df['Number_Doctor'].sum():,.0f}"),
        ("", "Avg Doctors", f"{filtered_df['Number_Doctor'].mean():,.0f}"),
        ("", "Hospitals", len(filtered_df)),
        ("", "States", filtered_df["State"].nunique())
    ]

elif page == "Geographic":
    metrics = [
        ("", "Locations", filtered_df["Location_Coordinates"].nunique()),
        ("", "Hospitals", len(filtered_df)),
        ("", "Beds", f"{filtered_df['Total_Num_Beds'].sum():,.0f}"),
        ("", "States", filtered_df["State"].nunique())
    ]

else:
    metrics = [
        ("", "Hospitals", len(filtered_df)),
        ("", "States", filtered_df["State"].nunique()),
        ("", "Emergency %", f"{filtered_df['Emergency_Flag'].mean()*100:.1f}%"),
        ("", "Beds", f"{filtered_df['Total_Num_Beds'].sum():,.0f}")
    ]

for col, metric in zip([col1, col2, col3, col4], metrics):
    icon, title, value = metric
    col.markdown(f"""
<div class="kpi-card">
<div class="kpi-icon">{icon}</div>
<div class="kpi-title">{title}</div>
<div class="kpi-value">{value}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================
# PAGE CONTENT
# ============================================

if page == "Overview":
    st.markdown('<div class="section-title">System Overview</div>', unsafe_allow_html=True)
    state_counts = filtered_df["State"].value_counts().reset_index()
    fig = px.bar(state_counts, x="count", y="State", orientation="h", template=PLOT_THEME)
    fig.update_layout(
        title=dict(text="Total Hospitals by State", font=dict(size=24)),
        xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        yaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )
    st.plotly_chart(fig, use_container_width=True)

        # ============================================
    # VISUALIZATION 2  DISTRICT DISTRIBUTION HEATMAP
    # ============================================

    st.markdown("### District Distribution Within Each State")

    # ---- aggregate hospital counts ----
    heatmap_df = (
        filtered_df
        .groupby(["State", "District"])["Hospital_Name"]
        .count()
        .reset_index(name="Hospital_Count")
    )

    # ---- pivot for heatmap ----
    heatmap_pivot = heatmap_df.pivot(
        index="State",
        columns="District",
        values="Hospital_Count"
    ).fillna(0)

    # ---- optional: limit wide tables for performance ----
    if heatmap_pivot.shape[1] > 40:
        top_districts = (
            heatmap_df.groupby("District")["Hospital_Count"]
            .sum()
            .sort_values(ascending=False)
            .head(40)
            .index
        )
        heatmap_pivot = heatmap_pivot[top_districts]

    # ---- heatmap chart ----
    fig_heatmap = px.imshow(
        heatmap_pivot,
        aspect="auto",
        color_continuous_scale="Blues",
        template=PLOT_THEME,
        height=600,
    )

    fig_heatmap.update_layout(
        xaxis_title="District",
        yaxis_title="State",
        title="Hospital Distribution (State vs District)",
        title_x=0.5,
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        coloraxis_colorbar=dict(tickfont=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Heatmap visualization completed

    
        # ============================================
    # VISUALIZATION 8: HOSPITAL CATEGORY MIX
    # ============================================

    st.subheader("Hospital Category Distribution")

    # aggregate
    category_mix = (
        filtered_df.groupby(["State", "Hospital_Category"])
        .size()
        .reset_index(name="Hospital_Count")
    )

    # stacked column chart
    fig = px.bar(
        category_mix,
        x="State",
        y="Hospital_Count",
        color="Hospital_Category",
        barmode="stack",
        template=PLOT_THEME,
        title="Structural Composition of Hospital Categories",
        height=520
    )

    fig.update_layout(
        xaxis_title="State",
        yaxis_title="Number of Hospitals",
        legend_title="Hospital Category",
        hovermode="x unified",
        title_x=0.5,
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        legend=dict(font=dict(size=14), title_font=dict(size=16)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Category distribution visualization completed

elif page == "Infrastructure":
    st.markdown('<div class="section-title">Infrastructure Analysis</div>', unsafe_allow_html=True)

    density = filtered_df.groupby("State")["Total_Num_Beds"].sum().reset_index()
    fig = px.bar(density, x="State", y="Total_Num_Beds", template=PLOT_THEME)
    fig.update_layout(
        title=dict(text="Total Beds by State", font=dict(size=24)),
        xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        yaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Beds in Public, Private and Trust Hospitals")

    beds_by_type = (
    filtered_df.groupby("Hospital_Care_Type")["Total_Num_Beds"]
    .sum()
    .reset_index()
)

    fig1 = px.bar(
    beds_by_type,
    x="Hospital_Care_Type",
    y="Total_Num_Beds",
    color="Hospital_Care_Type",
    template=PLOT_THEME,
    title="Total Beds by Hospital Care Type"
)
    fig1.update_layout(
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        legend=dict(font=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig1, use_container_width=True)
    # 🛏 Beds Distribution per Hospital
    st.subheader("Beds Distribution per Hospital")

    fig2 = px.histogram(
    filtered_df,
    x="Total_Num_Beds",
    nbins=30,
    template=PLOT_THEME,
    title="Distribution of Beds Across Hospitals"
)
    fig2.update_layout(
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )
    
    

    st.plotly_chart(fig2, use_container_width=True)

     # 🧪 System-wise Bed Capacity
    st.subheader("System-wise Bed Capacity (Allopathy, Ayurveda, etc.)")

    dept_beds = (
    filtered_df.groupby("Discipline_Systems_Of_Medicine")["Total_Num_Beds"]
    .sum()
    .reset_index()
    .sort_values(by="Total_Num_Beds", ascending=False)
)

    fig = px.bar(
    dept_beds,
    x="Total_Num_Beds",
    y="Discipline_Systems_Of_Medicine",
    orientation="h",
    color="Discipline_Systems_Of_Medicine",
    template=PLOT_THEME,
    title="Bed Capacity by System of Medicine"
)
    fig.update_layout(
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        legend=dict(font=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Urban vs rural proxy
          # ============================================
    # URBAN vs RURAL  BENCHMARK VIEW
    # ============================================

    st.subheader("Urban vs Rural Infrastructure Benchmark")

    # aggregate
    state_hosp = (
        filtered_df.groupby("State")["Hospital_Name"]
        .count()
        .reset_index(name="Total_Hospitals")
    )

    state_dist = (
        filtered_df.groupby("State")["District"]
        .nunique()
        .reset_index(name="Total_Districts")
    )

    urban_rural = state_hosp.merge(state_dist, on="State")

    # density metric
    urban_rural["Hospitals_per_District"] = (
        urban_rural["Total_Hospitals"] / urban_rural["Total_Districts"]
    ).round(2)

    # national benchmark
    national_avg = urban_rural["Hospitals_per_District"].mean()

    # classification
    def classify(val):
        if val >= national_avg * 1.2:
            return "Urban Concentrated"
        elif val <= national_avg * 0.8:
            return "Rural Gap"
        else:
            return "Balanced"

    urban_rural["Infrastructure_Type"] = urban_rural[
        "Hospitals_per_District"
    ].apply(classify)

    # sort descending for executive look
    urban_rural = urban_rural.sort_values(
        "Hospitals_per_District", ascending=False
    )

    # chart
    fig = px.bar(
        urban_rural,
        x="State",
        y="Hospitals_per_District",
        color="Infrastructure_Type",
        template=PLOT_THEME,
        title="Hospital Density vs National Benchmark",
        height=520
    )

    # benchmark line
    fig.add_hline(
        y=national_avg,
        line_dash="dash",
        annotation_text="National Average",
        annotation_position="top left"
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title="Hospitals per District",
        xaxis_title="State",
        title_x=0.5,
        hovermode="x unified",
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        legend=dict(font=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Infrastructure benchmark completed
     

    

         # ============================================
    # HOSPITALS PER DISTRICT (LOW DENSITY FINDER)
    # ============================================

    st.subheader("Hospitals per District (Administrative Density)")

    # hospital count per state
    state_hospitals = (
        filtered_df.groupby("State")["Hospital_Name"]
        .count()
        .reset_index(name="Hospital_Count")
    )

    # district count per state
    state_districts = (
        filtered_df.groupby("State")["District"]
        .nunique()
        .reset_index(name="District_Count")
    )

    # merge
    density_df = state_hospitals.merge(state_districts, on="State")

    # hospitals per district
    density_df["Hospitals_per_District"] = (
        density_df["Hospital_Count"] / density_df["District_Count"]
    )

    # sort ascending  lowest density first
    density_df = density_df.sort_values("Hospitals_per_District")

    # bar chart
    fig = px.bar(
        density_df,
        x="Hospitals_per_District",
        y="State",
        orientation="h",
        color="Hospitals_per_District",
        template=PLOT_THEME,
        title="States with Low Hospital Density Relative to Districts"
    )
    fig.update_layout(
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Low density finder completed


    

elif page == "Emergency":
    st.markdown(
        """
<div style="
font-size:28px;
font-weight:700;
color:"#38bdf8;
background: linear-gradient(90deg, #fbbf24, #f97316);
padding: 12px 20px;
border-radius:12px;
margin-bottom:15px;
box-shadow: 0 6px 15px rgba(0,0,0,0.1);
">
Emergency Readiness Dashboard
</div>
""", unsafe_allow_html=True
    )
    
    # Aggregate emergency readiness by state
    emergency = filtered_df.groupby("State")["Emergency_Flag"].mean().reset_index()
    emergency["Emergency %"] = emergency["Emergency_Flag"] * 100
    
    # Sort by Emergency % descending
    emergency = emergency.sort_values(by="Emergency %", ascending=False)
    
    # Create a premium bar chart
    fig = px.bar(
        emergency, 
        x="State", 
        y="Emergency %",
        template=PLOT_THEME, 
        text="Emergency %",
        color="Emergency %",
        color_continuous_scale="reds",
        labels={"Emergency %":"Emergency Readiness (%)"},
        hover_data={"State":True, "Emergency %":":.2f"}
    )
    
    # Update layout for a polished look
    fig.update_traces(marker_line_color='black', marker_line_width=1.5, texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        yaxis=dict(range=[0, 100], title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        title_font=dict(size=24),
        margin=dict(l=20, r=20, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        autosize=True,
    )
    
    st.plotly_chart(fig, use_container_width=True)


    



    st.markdown("### Surge Preparedness Simulator")

    # severity control
    severity = st.slider(
        "Select Surge Severity",
        min_value=1.0,
        max_value=3.0,
        value=1.5,
        step=0.1,
        help="Higher value = more hospitals required during crisis"
    )

    # aggregate emergency hospitals
    surge_df = (
        filtered_df.groupby("State").agg(
            Emergency_Hospitals=("Emergency_Flag", "sum"),
            State_Population=("State_Population", "max")
        ).reset_index()
    )

    # avoid divide issues
    surge_df["State_Population"] = pd.to_numeric(
        surge_df["State_Population"], errors="coerce"
    ).fillna(0)

    # population-based required capacity
    surge_df["Required_Capacity"] = (
        surge_df["Emergency_Hospitals"] * severity
    )

    # preparedness gap
    surge_df["Gap"] = (
        surge_df["Required_Capacity"]
        - surge_df["Emergency_Hospitals"]
    )

    # risk classification
    def classify_risk(gap):
        if gap <= 0:
            return "Prepared"
        elif gap < 20:
            return "Moderate Risk"
        else:
            return "High Risk"

    surge_df["Risk_Level"] = surge_df["Gap"].apply(classify_risk)

    # reshape for line chart
    surge_long = surge_df.melt(
        id_vars=["State", "Risk_Level"],
        value_vars=["Emergency_Hospitals", "Required_Capacity"],
        var_name="Capacity_Type",
        value_name="Hospitals"
    )

    # line chart
    fig = px.line(
        surge_long,
        x="State",
        y="Hospitals",
        color="Capacity_Type",
        markers=True,
        template=PLOT_THEME,
        title="State-wise Surge Preparedness Gap"
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        legend=dict(font=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("High Risk States Under Surge")

    risk_view = surge_df.sort_values("Gap", ascending=False).head(10)

    fig2 = px.bar(
        risk_view,
        x="State",
        y="Gap",
        color="Risk_Level",
        template=PLOT_THEME,
        title="Top States with Emergency Capacity Gap"
    )
    fig2.update_layout(
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        legend=dict(font=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Surge preparedness metrics completed

    st.subheader("Emergency + Advanced Care Intelligence")

    view_mode = st.radio(
        "View Mode",
        ["Top 15 States", "All States"],
        horizontal=True
    )

    overlay = filtered_df.groupby("State").agg(
        Total_Hospitals=("Hospital_Name", "count"),
        Emergency_Ready=("Emergency_Flag", "sum"),
        Tertiary_Count=(
            "Hospital_Category",
            lambda x: x.str.contains("Tertiary", case=False, na=False).sum()
        )
    ).reset_index()

    # percentages
    overlay["Emergency %"] = (
        overlay["Emergency_Ready"] / overlay["Total_Hospitals"] * 100
    ).round(1)

    overlay["Tertiary %"] = (
        overlay["Tertiary_Count"] / overlay["Total_Hospitals"] * 100
    ).round(1)

    # readiness score
    overlay["Readiness Score"] = (
        overlay["Emergency %"] * 0.6 +
        overlay["Tertiary %"] * 0.4
    ).round(1)

    overlay = overlay.sort_values("Readiness Score", ascending=False)

    if view_mode == "Top 15 States":
        plot_df = overlay.head(15)
    else:
        plot_df = overlay

    # ============================================
    # PREMIUM CHART
    # ============================================

    fig = px.bar(
        plot_df,
        x="State",
        y=["Emergency_Ready", "Tertiary_Count"],
        barmode="group",
        template=PLOT_THEME,
        title="Operational Readiness vs Advanced Care",
        height=560
    )

    fig.update_traces(marker_line_width=0, opacity=0.92)

    fig.update_layout(
        hovermode="x unified",
        legend_title_text="Capability",
        xaxis_title="State",
        yaxis_title="Hospitals",
        title_x=0.5,
        title_font=dict(size=24),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        legend=dict(font=dict(size=14), title_font=dict(size=16)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    worst_state_row = overlay.sort_values("Readiness Score").iloc[0]

    # Readiness chart completed

    st.plotly_chart(fig, use_container_width=True)

    # Executive snapshot completed

    # ============================================
    #  DETAIL TABLE
    # ============================================

    with st.expander("View Detailed Readiness Table"):
        st.dataframe(
            overlay.sort_values("Readiness Score"),
            use_container_width=True,
            height=350
        )

# Doctor Analysis & System of Medicine
if page == "Doctor Analysis":
    st.markdown('<div class="section-title">Doctor Infrastructure Analysis</div>', unsafe_allow_html=True)

    # ---------- Mirror Bar Chart: Doctors vs Beds ----------
    import plotly.graph_objects as go
    
    st.subheader("Comparative Analysis: Doctors vs Beds (Top Hospitals)")
    
    # Select top hospitals by doctor count for the mirror chart
    top_mirror_hospitals = filtered_df.nlargest(20, "Number_Doctor").sort_values("Number_Doctor", ascending=True)

    fig_mirror = go.Figure()

    # Doctors (Left Side - Negative values)
    fig_mirror.add_trace(go.Bar(
        y=top_mirror_hospitals["Hospital_Name"],
        x=-top_mirror_hospitals["Number_Doctor"],
        name="Doctors",
        orientation='h',
        marker_color='#1f77b4', # Professional Blue
        text=top_mirror_hospitals["Number_Doctor"],
        textposition='inside',
        insidetextanchor='end',
        hovertemplate="Hospital: %{y}<br>Doctors: %{text}"
    ))

    # Beds (Right Side - Positive values)
    fig_mirror.add_trace(go.Bar(
        y=top_mirror_hospitals["Hospital_Name"],
        x=top_mirror_hospitals["Total_Num_Beds"],
        name="Beds",
        orientation='h',
        marker_color='#ff7f0e', # Professional Orange
        text=top_mirror_hospitals["Total_Num_Beds"],
        textposition='inside',
        insidetextanchor='start',
        hovertemplate="Hospital: %{y}<br>Beds: %{x}"
    ))

    # Calculate symmetry for X-axis
    max_val = max(top_mirror_hospitals["Number_Doctor"].max(), top_mirror_hospitals["Total_Num_Beds"].max())
    tick_step = 500 if max_val > 1000 else 100
    ticks = list(range(0, int(max_val) + tick_step, tick_step))
    neg_ticks = [-t for t in ticks[::-1][:-1]]
    all_ticks = neg_ticks + ticks
    all_labels = [str(abs(t)) for t in all_ticks]

    fig_mirror.update_layout(
        title=dict(text="Doctors vs Beds by Hospital (Mirror Bar Chart)", font=dict(size=24)),
        barmode='relative',
        xaxis=dict(
            title="Count",
            tickvals=all_ticks,
            ticktext=all_labels,
            gridcolor='rgba(128,128,128,0.2)',
            title_font=dict(size=18),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=12)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=16)
        ),
        margin=dict(l=20, r=20, t=80, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=700,
        autosize=True
    )

    st.plotly_chart(fig_mirror, use_container_width=True)

    # ---------- Row for Pie Charts ----------
    col1, col2, col3 = st.columns(3)

    # ---------- Pie 1: System of Medicine ----------
    if "Discipline_Systems_Of_Medicine" in filtered_df.columns:
        med_sys_count = (
            filtered_df.groupby("Discipline_Systems_Of_Medicine")["Number_Doctor"]
            .sum()
            .reset_index()
        )
        med_sys_count.columns = ["System", "Total_Doctors"]

        if not med_sys_count.empty:
            fig1 = px.pie(
                med_sys_count,
                names="System",
                values="Total_Doctors",
                hole=0.55,
                template=PLOT_THEME,
            )
            fig1.update_traces(textinfo="percent+label", pull=[0.05]*len(med_sys_count))
            fig1.update_layout(
                title=dict(text="Doctors by System", font=dict(size=18)),
                legend=dict(font=dict(size=12)),
                margin=dict(l=10, r=10, t=50, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                autosize=True,
                height=350
            )
            col1.plotly_chart(fig1, use_container_width=True)

    # ---------- Pie 2: Care Type (Public vs Private) ----------
    if "Hospital_Care_Type" in filtered_df.columns:
        care_count = (
            filtered_df.groupby("Hospital_Care_Type")["Number_Doctor"]
            .sum()
            .reset_index()
        )
        care_count.columns = ["Care_Type", "Total_Doctors"]

        fig2 = px.pie(
            care_count,
            names="Care_Type",
            values="Total_Doctors",
            hole=0.55,
            template=PLOT_THEME,
        )
        fig2.update_traces(textinfo="percent+label", pull=[0.05]*len(care_count))
        fig2.update_layout(
            title=dict(text="Doctors by Care Type", font=dict(size=18)),
            legend=dict(font=dict(size=12)),
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=True,
            height=350
        )
        col2.plotly_chart(fig2, use_container_width=True)

    # ---------- Pie 3: Top 5 States by Doctor Count ----------
    top_states = (
        filtered_df.groupby("State")["Number_Doctor"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    fig3 = px.pie(
        top_states,
        names="State",
        values="Number_Doctor",
        hole=0.55,
        template=PLOT_THEME
    )
    fig3.update_traces(textinfo="percent+label", pull=[0.05]*len(top_states))
    fig3.update_layout(
        title=dict(text="Top 5 States by Doctors", font=dict(size=18)),
        legend=dict(font=dict(size=12)),
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        height=350
    )
    col3.plotly_chart(fig3, use_container_width=True)

    # ---------- Bar Chart: Doctor-to-Bed Ratio ----------
    st.subheader("Doctor-to-Bed Ratio by State")
    ratio_df = (
        filtered_df.groupby("State").agg(
            Total_Doctors=("Number_Doctor", "sum"),
            Total_Beds=("Total_Num_Beds", "sum")
        ).reset_index()
    )
    ratio_df["Doctor_Bed_Ratio"] = ratio_df["Total_Doctors"] / ratio_df["Total_Beds"]

    fig4 = px.bar(
        ratio_df.sort_values("Doctor_Bed_Ratio", ascending=False),
        x="State",
        y="Doctor_Bed_Ratio",
        color="Doctor_Bed_Ratio",
        template=PLOT_THEME,
        title="Doctors per Bed Across States",
        text=ratio_df["Doctor_Bed_Ratio"].round(2),
    )
    fig4.update_traces(textposition="outside", marker_line_width=1.2)
    fig4.update_layout(
        title=dict(text="Doctors per Bed Across States", font=dict(size=24)),
        yaxis_title="Doctor-to-Bed Ratio",
        xaxis_title="State",
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        height=500
    )
    st.plotly_chart(fig4, use_container_width=True)


    

elif page == "Geographic":
    st.markdown('<div class="section-title">Geographic Intelligence</div>', unsafe_allow_html=True)

    st.subheader("Hospital Footprint Across India")

    map_df = filtered_df.dropna(subset=["lat", "lon"]).copy()

    fig_points = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="Total_Num_Beds",
        color="Hospital_Category",
        hover_name="Hospital_Name",
        zoom=4,
        height=620,
        template=PLOT_THEME,
    )

    fig_points.update_traces(marker=dict(opacity=0.75))
    fig_points.update_layout(
        title=dict(text="Hospital Placement (Detailed View)", font=dict(size=24)),
        mapbox=dict(
            style="carto-positron" if theme == "Light" else "carto-darkmatter",
            center=dict(lat=20.5937, lon=78.9629),
            zoom=3.8,
            bounds={"west": 68.1, "east": 97.4, "south": 8.0, "north": 37.1}
        ),
        legend=dict(font=dict(size=14), title_font=dict(size=16)),
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    st.plotly_chart(fig_points, use_container_width=True)

    st.markdown("---")

    # State Infrastructure Intensity Map

    st.subheader("State Infrastructure Intensity Map")

    # ---- state aggregates ----
    state_hosp = (
        filtered_df.groupby("State")["Hospital_Name"]
        .count()
        .reset_index(name="Total_Hospitals")
    )

    state_dist = (
        filtered_df.groupby("State")["District"]
        .nunique()
        .reset_index(name="Total_Districts")
    )

    urban_rural = state_hosp.merge(state_dist, on="State")
    urban_rural["Hospitals_per_District"] = (
        urban_rural["Total_Hospitals"] / urban_rural["Total_Districts"]
    ).round(2)

    # ---- centroids ----
    state_centroids = (
        map_df.groupby("State")[["lat", "lon"]]
        .mean()
        .reset_index()
    )

    geo_density = urban_rural.merge(state_centroids, on="State", how="left")

    fig_bubble = px.scatter_mapbox(
        geo_density,
        lat="lat",
        lon="lon",
        size="Hospitals_per_District",
        color="Hospitals_per_District",
        hover_name="State",
        size_max=48,
        zoom=4,
        height=620,
        template=PLOT_THEME,
    )

    fig_bubble.update_traces(marker=dict(opacity=0.8))
    fig_bubble.update_layout(
        title=dict(text="Infrastructure Intensity by State", font=dict(size=24)),
        mapbox=dict(
            style="carto-positron" if theme == "Light" else "carto-darkmatter",
            center=dict(lat=20.5937, lon=78.9629),
            zoom=3.8,
            bounds={"west": 68.1, "east": 97.4, "south": 8.0, "north": 37.1}
        ),
        coloraxis_colorbar=dict(tickfont=dict(size=14), title_font=dict(size=16)),
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    # Geographic insights completed


elif page == "Nearest Hospital":
    show_nearest_hospital(filtered_df, theme, CARD, TEXT, BORDER)

elif page == "Insights":

    st.markdown('<div class="section-title">AI Insights & Advanced Analytics</div>', unsafe_allow_html=True)

    # AI text insights completed

    st.markdown("---")

    # ============================================
    # TOP STATES CHART
    # ============================================

    st.subheader("Top 10 States by Number of Hospitals")

    state_counts = (
        filtered_df["State"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    fig1 = px.bar(
        state_counts,
        x="count",
        y="State",
        orientation="h",
        color="count",
        template=PLOT_THEME,
        title="Hospital Concentration by State"
    )

    fig1.update_layout(
        title_font=dict(size=24),
        xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        yaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
        margin=dict(l=20, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        autosize=True,
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ============================================
    # PUBLIC VS PRIVATE
    # ============================================

    if "Hospital_Category" in filtered_df.columns:

        st.subheader("Public vs Private Hospital Distribution")

        category = (
            filtered_df["Hospital_Category"]
            .value_counts()
            .reset_index()
        )

        fig2 = px.pie(
            category,
            names="Hospital_Category",
            values="count",
            template=PLOT_THEME,
            title="Hospital Category Share"
        )

        fig2.update_layout(
            title_font=dict(size=20),
            legend=dict(font=dict(size=14)),
            margin=dict(l=10, r=10, t=60, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=True,
            height=400
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ============================================
    # TOP HOSPITALS BY BEDS
    # ============================================

    if "Total_Num_Beds" in filtered_df.columns:

        st.subheader("lowest 10 Hospitals by Bed Capacity")

        beds = (
            filtered_df
            .sort_values("Total_Num_Beds", ascending=False)
            .tail(10) 
        )

        fig3 = px.bar(
            beds,
            x="Total_Num_Beds",
            y="Hospital_Name",
            orientation="h",
            color="Total_Num_Beds",
            template=PLOT_THEME,
            title="Lowest 10 Hospitals by Bed Capacity"
        )

        fig3.update_layout(
            title_font=dict(size=24),
            xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
            yaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
            margin=dict(l=20, r=20, t=60, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            autosize=True,
        )

        st.plotly_chart(fig3, use_container_width=True)

    # ============================================
    # TOP DISTRICTS BY DOCTORS
    # ============================================

    if "District" in filtered_df.columns:

        st.subheader("Top 10 Districts by Doctor Strength")

        doctors = (
            filtered_df
            .groupby("District")["Number_Doctor"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig4 = px.bar(
            doctors,
            x="Number_Doctor",
            y="District",
            orientation="h",
            color="Number_Doctor",
            template=PLOT_THEME,
            title="Doctor Distribution by District"
        )

        fig4.update_layout(
            title_font=dict(size=24),
            xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
            yaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
            margin=dict(l=20, r=20, t=60, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            autosize=True,
        )

        st.plotly_chart(fig4, use_container_width=True)

    


    