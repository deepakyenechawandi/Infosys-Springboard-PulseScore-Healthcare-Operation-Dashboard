import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import textwrap

def render_hospital_card(row, distance=None):
    # Safe Numbers
    def safe_int(val):
        try: return int(float(val))
        except: return 0

    # Fields
    h_name = str(row.get('Hospital_Name', 'Facility'))
    location = str(row.get('Location', 'N/A'))
    district = str(row.get('District', 'District'))
    pincode = str(row.get('Pincode', 'N/A'))
    category = str(row.get('Hospital_Category', 'General Facility'))
    care_type = str(row.get('Hospital_Care_Type', 'Standard'))
    beds = safe_int(row.get('Total_Num_Beds', 0))
    specialties = str(row.get('Specialties', 'General Services'))

    # Card HTML (Increased font sizes for better readability)
    card_html = f"""
<div style="padding: 20px; border-radius: 16px; font-family: 'Plus Jakarta Sans', sans-serif;">
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 25px;">
<div style="display: flex; flex-direction: column; gap: 15px;">
<div style="display: flex; align-items: center; gap: 12px;"><span style="font-weight: 700; font-size: 1.15rem; min-width: 100px;">Location:</span><span style="color: #94a3b8; font-size: 1.15rem;">{location}</span></div>
<div style="display: flex; align-items: center; gap: 12px;"><span style="font-weight: 700; font-size: 1.15rem; min-width: 100px;">District:</span><span style="color: #94a3b8; font-size: 1.15rem;">{district}</span></div>
<div style="display: flex; align-items: center; gap: 12px;"><span style="font-weight: 700; font-size: 1.15rem; min-width: 100px;">Pincode:</span><span style="color: #94a3b8; font-size: 1.15rem;">{pincode}</span></div>
</div>
<div style="display: flex; flex-direction: column; gap: 15px;">
<div style="display: flex; align-items: center; gap: 12px;"><span style="font-weight: 700; font-size: 1.15rem; min-width: 100px;">Category:</span><span style="color: #94a3b8; font-size: 1.15rem;">{category}</span></div>
<div style="display: flex; align-items: center; gap: 12px;"><span style="font-weight: 700; font-size: 1.15rem; min-width: 100px;">Care Type:</span><span style="color: #94a3b8; font-size: 1.15rem;">{care_type}</span></div>
<div style="display: flex; align-items: center; gap: 12px;"><span style="font-weight: 700; font-size: 1.15rem; min-width: 100px;">Total Beds:</span><span style="color: #94a3b8; font-size: 1.15rem;">{beds:,}</span></div>
</div>
</div>
<div style="background: rgba(56, 189, 248, 0.15); border-radius: 14px; padding: 20px; border: 1px solid rgba(56, 189, 248, 0.2);"><span style="font-weight: 700; font-size: 1.2rem;">Specialties:</span><span style="color: #38bdf8; margin-left: 8px; font-size: 1.2rem; font-weight: 500;">{specialties}</span></div>
</div>
"""
    st.markdown(card_html, unsafe_allow_html=True)

def render_hospital_finder(df_raw, sub_text):
    search_mode = st.radio("Search Context", ["Coordinates (GPS)", "District Name", "Pincode"], horizontal=True, label_visibility="collapsed")

    # Ensure GPS columns exist in df_raw for robust search
    has_coords = "lat" in df_raw.columns and "lon" in df_raw.columns

    if search_mode == "Coordinates (GPS)":
        if not has_coords:
            st.error("Coordinate data is missing or not parsed in the current dataset. GPS search is unavailable.")
            return

        col1, col2, col3 = st.columns(3)
        with col1: lat = st.number_input("Latitude", value=19.5208, format="%.4f") # Default to Odisha sample
        with col2: lon = st.number_input("Longitude", value=85.0902, format="%.4f") # Default to Odisha sample
        with col3: radius = st.number_input("Search Radius (km)", value=50, min_value=1, max_value=500)
        
        st.info("Tip: Try the default coordinates (Odisha) to verify results, or enter your own.")

        if st.button("Query Nearby Facilities", use_container_width=True):
            user_loc = (lat, lon)
            def calculate_dist(row):
                try: 
                    if pd.isna(row["lat"]) or pd.isna(row["lon"]): return float("inf")
                    return geodesic(user_loc, (row["lat"], row["lon"])).km
                except: return float("inf")
            
            with st.spinner("Calculating distances across registry..."):
                df_search = df_raw.copy()
                df_search["distance"] = df_search.apply(calculate_dist, axis=1)
                st.session_state.gps_results = df_search[df_search["distance"] <= radius].sort_values("distance")

        if "gps_results" in st.session_state:
            results = st.session_state.gps_results
            if len(results) == 0:
                st.warning(f"No facilities located within {radius} km of ({lat}, {lon}). Try increasing the radius.")
            else:
                st.success(f"Located {len(results)} facilities within {radius} km.")
                
                st.markdown("### Detailed Facility Insights")
                for _, row in results.head(20).iterrows():
                    title = f"{row.get('Hospital_Name', 'Facility')} ({row.get('District', 'District')}) — {row.get('distance', 0):.1f} km away"
                    with st.expander(title):
                        render_hospital_card(row, distance=row["distance"])
                
                st.markdown("---")
                st.markdown("### Result Matrix (Data View)")
                st.dataframe(results, use_container_width=True)
                st.download_button("Download Data (CSV)", results.to_csv(index=False), "hospital_search.csv", "text/csv", use_container_width=True)

    elif search_mode == "District Name":
        district_query = st.text_input("Enter District Keyword (e.g., Pune, Lucknow)")
        if district_query:
            if st.button("Search by District", use_container_width=True):
                matches = df_raw[df_raw["District"].str.contains(district_query, case=False, na=False)]
                st.session_state.dt_results = matches

            if "dt_results" in st.session_state:
                results = st.session_state.dt_results
                if len(results) == 0:
                    st.warning("No matching districts found in the registry.")
                else:
                    st.success(f"Located {len(results)} facilities in {district_query}")
                    
                    st.markdown("### Detailed Facility Insights")
                    for _, row in results.head(20).iterrows():
                        title = f"{row.get('Hospital_Name', 'Facility')} ({row.get('District', 'District')})"
                        with st.expander(title):
                            render_hospital_card(row)
                    
                    st.markdown("---")
                    st.markdown("### Result Matrix (Data View)")
                    st.dataframe(results, use_container_width=True)
                    st.download_button("Download Data (CSV)", results.to_csv(index=False), "district_search.csv", "text/csv", use_container_width=True)

    elif search_mode == "Pincode":
        pincode_query = st.text_input("Enter 6-Digit Pincode")
        if pincode_query:
            if st.button("Search by Pincode", use_container_width=True):
                matches = df_raw[df_raw["Pincode"].astype(str).str.contains(str(pincode_query), na=False)]
                st.session_state.pc_results = matches

            if "pc_results" in st.session_state:
                results = st.session_state.pc_results
                if len(results) == 0:
                    st.warning("No facilities registered under this Pincode.")
                else:
                    st.success(f"Located {len(results)} facilities matching Pincode {pincode_query}")
                    
                    st.markdown("### Detailed Facility Insights")
                    for _, row in results.head(20).iterrows():
                        title = f"{row.get('Hospital_Name', 'Facility')} ({row.get('District', 'District')}) — Pincode {row.get('Pincode', 'N/A')}"
                        with st.expander(title):
                            render_hospital_card(row)
                    
                    st.markdown("---")
                    st.markdown("### Result Matrix (Data View)")
                    st.dataframe(results, use_container_width=True)
                    st.download_button("Download Data (CSV)", results.to_csv(index=False), "pincode_search.csv", "text/csv", use_container_width=True)
