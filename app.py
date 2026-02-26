import streamlit as st
import pandas as pd
import base64
import os
from logic.core import load_data, create_pdf_report, get_comprehensive_report_assets, get_k_color
from sections.snapshot import render_snapshot
from sections.structural_gaps import render_structural_gaps
from sections.resource_distribution import render_resource_distribution
from sections.surge_intelligence import render_surge_intelligence
from sections.hospital_finder import render_hospital_finder

st.set_page_config(page_title="Executive Healthcare Dashboard", layout="wide", initial_sidebar_state="expanded")


@st.dialog("Methodology & Indicator Framework", width="large")
def show_methodology_dialog():
    st.markdown("""
        <div style="background: rgba(56, 189, 248, 0.1); padding: 25px; border-radius: 15px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 25px;">
            <h2 style="color: #38bdf8; margin-top: 0; font-size: 1.8rem;">PulseScore Analytical Engine</h2>
            <p style="color: #94a3b8; font-size: 1.1rem; line-height: 1.6; margin-bottom: 0;">
                Our framework translates raw healthcare infrastructure data into actionable "Readiness Scores".
                This requires a two-step process: <b>Static Baseline Benchmarking</b> and <b>Dynamic Surge Stress-Testing</b>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. Static Baseline Requirements")
    st.info("These formulas define the 'Target Capacity' based on population size, regardless of active demand.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Required Bed Capacity**")
        st.latex(r"R_B = \frac{Population \times 3}{1,000}")
        st.markdown("<p style='font-size:0.9rem; color:#94a3b8;'>Determines the total hospital beds needed per international safety norms (3 beds per 1k population).</p>", unsafe_allow_html=True)
    
    with c2:
        st.markdown("**Required Physician Density**")
        st.latex(r"R_D = \frac{Population \times 1}{1,000}")
        st.markdown("<p style='font-size:0.9rem; color:#94a3b8;'>Targets 1 medical doctor per 1,000 individuals as a primary care baseline.</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 2. The Dynamic Surge Model (SRI)")
    st.warning("The Surge Risk Index (SRI) measures how close the system is to a collapse during a crisis.")

    st.markdown("**Core Risk Formula:**")
    st.latex(r"SRI = \sum (Weight_i \times Stress_i)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Variable Definitions and Component Logic")
    
    v1, v2 = st.columns(2)
    with v1:
        st.markdown("**Component 1: Infrastructure Stress ($Stress_B$)**")
        st.latex(r"Stress_B = \frac{R_B \times S}{Available\_Beds \times Elasticity}")
        st.markdown("""
        - **$R_B$**: Required Baseline Beds.
        - **$S$**: Surge Multiplier (e.g., 1.5x demand).
        - **Elasticity**: System stretch factor (Default 1.15).
        """)

    with v2:
        st.markdown("**Component 2: Staffing Stress ($Stress_D$)**")
        st.latex(r"Stress_D = \frac{R_D \times S}{Available\_Docs \times Elasticity}")
        st.markdown("""
        - **$R_D$**: Required Baseline Doctors.
        - **Interpretation**: A score > 1.0 means demand exceeds total supply.
        """)

    st.markdown("---")
    st.markdown("### 3. Composite Weighting Strategy")
    st.markdown("""
    To generate a single **PulseScore**, we weigh components based on clinical criticality:
    """)
    
    st.markdown("""
    | Resource Component | Weight ($W_i$) | System Role |
    | :--- | :---: | :--- |
    | **Bed Capacity ($Stress_B$)** | **40%** | Hard physical limitation for admissions. |
    | **Medical Personnel ($Stress_D$)** | **30%** | Clinical decision-making and triage throughput. |
    | **ICU Critical Care ($Stress_I$)** | **20%** | Mortality prevention for acute surge cases. |
    | **Emergency Services ($Stress_E$)** | **10%** | Front-line 24/7 entry-point resilience. |
    """)

    st.markdown("---")
    st.markdown("### System Interpretation Bands")
    
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown("<div style='background:rgba(16,185,129,0.1); padding:15px; border-left:4px solid #10b981; border-radius:8px;'><b>STABLE (SRI &lt; 0.8)</b><br><small>Redundant capacity available.</small></div>", unsafe_allow_html=True)
    with b2:
        st.markdown("<div style='background:rgba(245,158,11,0.1); padding:15px; border-left:4px solid #f59e0b; border-radius:8px;'><b>SATURATED (0.8 - 1.2)</b><br><small>System at elastic limit.</small></div>", unsafe_allow_html=True)
    with b3:
        st.markdown("<div style='background:rgba(239,68,68,0.1); padding:15px; border-left:4px solid #ef4444; border-radius:8px;'><b>CRITICAL (SRI &gt; 1.2)</b><br><small>Active structural failure.</small></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("PulseScore Methodology v3.1 | Strategic Decision Intelligence Framework")


with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px;">
            <svg width="40" height="40" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M50 10C27.9 10 10 27.9 10 50C10 72.1 27.9 90 50 90" stroke="#38bdf8" stroke-width="8" stroke-linecap="round"/>
                <path d="M75 18C84.4 26.5 90 37.8 90 50C90 56.4 88.5 62.5 85.8 68" stroke="#38bdf8" stroke-width="8" stroke-linecap="round"/>
                <path d="M78 80L65 67" stroke="#38bdf8" stroke-width="8" stroke-linecap="round"/>
                <rect x="32" y="55" width="8" height="15" rx="2" fill="#38bdf8"/>
                <rect x="44" y="45" width="8" height="25" rx="2" fill="#38bdf8"/>
                <rect x="56" y="50" width="8" height="20" rx="2" fill="#38bdf8"/>
                <rect x="68" y="35" width="8" height="35" rx="2" fill="#38bdf8"/>
            </svg>
            <span style="font-size: 30px; font-weight: 850; color: white; letter-spacing: -1px; font-family: 'Plus Jakarta Sans', sans-serif;">PulseScore</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="font-size:18px; font-weight:850; color:rgba(255,255,255,0.6); margin-bottom:12px; text-transform:uppercase; letter-spacing:1.5px;">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("Navigation", 
                     ["National Snapshot", 
                      "Structural Gap Diagnosis", 
                      "Resource Distribution", 
                      "Surge Risk Intelligence",
                      "Nearest Hospital Finder"], 
                    label_visibility="collapsed")
    
    st.markdown('<div style="margin: 20px 0;"></div>', unsafe_allow_html=True)
    
    st.markdown('<div style="font-size:18px; font-weight:850; color:rgba(255,255,255,0.6); margin-bottom:12px; text-transform:uppercase; letter-spacing:1.5px;">Data Assets</div>', unsafe_allow_html=True)
    with st.expander("Import External Data", expanded=False):
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
        if uploaded_file:
            st.success("Analysis Target: Active Upload")
        else:
            st.info("System loaded with India Master Dataset")

    st.markdown('<div style="margin: 15px 0;"></div>', unsafe_allow_html=True)
    context_sidebar = st.container()

df_raw, state_stats_raw = load_data(uploaded_file)

with st.sidebar:
    st.markdown('<div style="font-size:18px; font-weight:850; color:rgba(255,255,255,0.6); margin-bottom:12px; text-transform:uppercase; letter-spacing:1.5px;">Analysis Filters</div>', unsafe_allow_html=True)
    with st.expander("Intelligence Filters", expanded=False):
        selected_states = st.multiselect("State", sorted(df_raw[df_raw['Admin_Type']=='State']['State'].unique()))
        selected_uts = st.multiselect("Union Territory", sorted(df_raw[df_raw['Admin_Type']=='Union Territory']['State'].unique()))
        filter_set = selected_states + selected_uts
        relevant_districts = sorted(df_raw[df_raw['State'].isin(filter_set)]['District'].unique()) if filter_set else sorted(df_raw['District'].unique())
        selected_districts = st.multiselect("District", relevant_districts)
        selected_hosp_cat = st.multiselect("Hospital Category", sorted(df_raw['Hospital_Category'].unique()))
        selected_care_type = st.multiselect("Care Type", sorted(df_raw['Hospital_Care_Type'].unique()))
        
        st.markdown('<div style="font-size:14px; font-weight:700; color:#94a3b8; margin-top:10px;">FACILITY CAPABILITY</div>', unsafe_allow_html=True)
        icu_filter = st.radio("ICU Available", ["All", "Yes", "No"], horizontal=True)
        emergency_filter = st.radio("Emergency Available", ["All", "Yes", "No"], horizontal=True)
        
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        if st.button("View Methodology and Framework", use_container_width=True, type="secondary"):
            show_methodology_dialog()

    st.markdown('<div style="margin: 20px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:18px; font-weight:850; color:rgba(255,255,255,0.6); margin-bottom:12px; text-transform:uppercase; letter-spacing:1.5px;">System Settings</div>', unsafe_allow_html=True)
    dark_mode = st.toggle("Dark Mode", value=True)
    st.markdown('<div style="font-size:16px; font-weight:600; color:rgba(255,255,255,0.5); margin-top:20px;">v2.8 Enterprise Command Center</div>', unsafe_allow_html=True)


if dark_mode:
    primary_bg = "#0f172a"
    card_bg = "#1e293b"
    card_border = "#334155"
    main_text = "#f8fafc"
    sub_text = "#94a3b8"
    card_shadow = "rgba(0,0,0,0.3)"
    grad_opacity = "0.2"
else:
    primary_bg = "#f8fafc"
    card_bg = "white"
    card_border = "#f1f5f9"
    main_text = "#1e1b4b"
    sub_text = "#64748b"
    card_shadow = "rgba(30,27,75,0.04)"
    grad_opacity = "0.12"


st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    :root {{ --bg-main: {primary_bg}; --card-bg: {card_bg}; --card-border: {card_border}; --text-main: {main_text}; --text-sub: {sub_text}; --sidebar-bg: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%); }}
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; color: var(--text-main); }}
    .stApp {{ background-color: var(--bg-main); background-image: radial-gradient(at 0% 0%, rgba(14, 165, 233, {grad_opacity}) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(168, 85, 247, {grad_opacity}) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(236, 72, 153, {grad_opacity}) 0px, transparent 50%), radial-gradient(at 0% 100%, rgba(99, 102, 241, {grad_opacity}) 0px, transparent 50%); background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background: var(--sidebar-bg) !important; border-right: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px; }}
    [data-testid="stSidebar"] * {{ color: #e0e7ff !important; }}
    [data-testid="stSidebar"] div[role="radiogroup"] label {{ font-size: 1.1rem !important; font-weight: 700 !important; padding: 8px 12px !important; border-radius: 12px !important; margin-bottom: 6px !important; transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important; border: 1px solid transparent !important; background: rgba(255, 255, 255, 0.03) !important; display: flex !important; position: relative !important; overflow: hidden !important; }}
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background: rgba(255, 255, 255, 0.1) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; transform: scale(1.02) translateX(4px) !important; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important; }}
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{ background: linear-gradient(90deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.05) 100%) !important; border: 1px solid rgba(255, 255, 255, 0.3) !important; font-weight: 800 !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important; }}
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before {{ content: ""; position: absolute; left: 0; top: 25%; height: 50%; width: 3px; background: #38bdf8; border-radius: 0 4px 4px 0; box-shadow: 0 0 8px rgba(56, 189, 248, 0.8); }}
    .chart-container {{ background: var(--card-bg); border-radius: 24px; padding: 1.5rem; border: 1px solid var(--card-border); box-shadow: {card_shadow}; margin-bottom: 1.5rem; }}
    .card-header {{ font-size: 1.4rem; font-weight: 800; color: var(--text-main); margin-bottom: 1rem; }}
    .kpi-card {{ border-radius: 20px; color: white !important; box-shadow: 0 8px 16px rgba(0,0,0,0.1); padding: 1.2rem; margin-bottom: 0.8rem; min-height: 150px; display: flex; flex-direction: column; justify-content: center; }}
    .card-purple {{ background: linear-gradient(135deg, #a855f7 0%, #7e22ce 100%); }}
    .card-blue {{ background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); }}
    .card-indigo {{ background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%); }}
    .card-pink {{ background: linear-gradient(135deg, #ec4899 0%, #be185d 100%); }}
    .card-red {{ background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); }}
    .card-orange {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }}
    .card-green {{ background: linear-gradient(135deg, #10b981 0%, #047857 100%); }}
    .kpi-title {{ font-size: 14px !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.9; }}
    .kpi-value {{ font-size: 28px !important; font-weight: 800; margin: 0.2rem 0; }}
    .kpi-percent {{ font-size: 0.9rem; font-weight: 600; opacity: 0.8; }}
    /* Sidebar Widget Scaling */
    [data-testid="stSidebar"] [data-testid="stExpander"] label p {{ font-size: 1.4rem !important; font-weight: 700 !important; }}
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ font-size: 1.4rem !important; font-weight: 700 !important; }}
    [data-testid="stSidebar"] div[data-testid="stExpander"] {{ border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important; margin-bottom: 8px !important; }}
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{ font-size: 1rem !important; padding: 2px 6px !important; }}
    [data-testid="stSidebar"] .stMultiSelect span {{ font-size: 1.1rem !important; }}
</style>
""", unsafe_allow_html=True)


base_dir = os.path.dirname(os.path.abspath(__file__))
avatar_path = os.path.join(base_dir, "avatar", "download.png")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

st.session_state.avatar_b64 = get_base64_image(avatar_path)


filtered_df = df_raw.copy()
if selected_states: filtered_df = filtered_df[filtered_df['State'].isin(selected_states)]
if selected_uts: filtered_df = filtered_df[filtered_df['State'].isin(selected_uts)]
if selected_districts: filtered_df = filtered_df[filtered_df['District'].isin(selected_districts)]
if selected_hosp_cat: filtered_df = filtered_df[filtered_df['Hospital_Category'].isin(selected_hosp_cat)]
if selected_care_type: filtered_df = filtered_df[filtered_df['Hospital_Care_Type'].isin(selected_care_type)]
if icu_filter != "All": filtered_df = filtered_df[filtered_df['has_icu'] == (icu_filter == "Yes")]
if emergency_filter != "All": filtered_df = filtered_df[filtered_df['is_emergency'] == (emergency_filter == "Yes")]


total_hospitals = len(filtered_df)
total_beds = filtered_df['Total_Num_Beds'].sum()
total_doctors = filtered_df['Number_Doctor'].sum()
distinct_states = filtered_df[filtered_df['Admin_Type'] == 'State']['State'].nunique()
distinct_uts = filtered_df[filtered_df['Admin_Type'] == 'Union Territory']['State'].nunique()
total_population = state_stats_raw[state_stats_raw['State'].isin(filtered_df['State'].unique())]['State_Population'].sum()
icu_percent = (filtered_df['has_icu'].sum() / total_hospitals * 100) if total_hospitals > 0 else 0
emergency_percent = (filtered_df['is_emergency'].sum() / total_hospitals * 100) if total_hospitals > 0 else 0

if page == "National Snapshot":
    render_snapshot(filtered_df, state_stats_raw, total_population, total_beds, total_doctors, distinct_states, distinct_uts, icu_percent, emergency_percent, sub_text, get_k_color)
elif page == "Structural Gap Diagnosis":
    render_structural_gaps(filtered_df, state_stats_raw, sub_text, get_k_color)
elif page == "Resource Distribution":
    render_resource_distribution(filtered_df, sub_text, get_k_color)
elif page == "Surge Risk Intelligence":
    render_surge_intelligence(filtered_df, state_stats_raw, context_sidebar, sub_text, get_k_color)
elif page == "Nearest Hospital Finder":
    render_hospital_finder(df_raw, sub_text)


with st.sidebar:
    st.markdown('<div style="margin: 20px 0;"></div><div style="font-size:18px; font-weight:850; color:rgba(255,255,255,0.6); margin-bottom:12px; text-transform:uppercase; letter-spacing:1.5px;">Global Reporting</div>', unsafe_allow_html=True)
    if st.checkbox("Generate Master Report (All Pages)"):
        with st.spinner("Compiling comprehensive visual assets..."):
            kpis = {"Total Admin Reach": f"{distinct_states} States", "Infrastructure": f"{total_beds:,} Beds", "Personnel": f"{total_doctors:,} Doctors"}
            report_assets = get_comprehensive_report_assets(filtered_df, state_stats_raw, sub_text)
            pdf_data = create_pdf_report("PulseScore Intelligence Report", kpis, [f for s in report_assets.values() for f in s])
            st.download_button("Download Master PDF", pdf_data, "PulseScore_Report.pdf", "application/pdf", use_container_width=True)
