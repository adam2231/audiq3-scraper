import streamlit as st
import pandas as pd
import re

# Set up the page
st.set_page_config(page_title="Audi Q3 Finder for Mum", layout="wide")
st.title("🚗 Audi Q3 e-hybrid: Configuration Finder")
st.markdown("Select the features below to find the perfect car.")

@st.cache_data
def load_data():
    try:
        # Load the newly scraped verified data
        df = pd.read_excel("audi_q3_stock.xlsx")
        # Ensure Packages is a string and handle empty values
        df['Packages'] = df['Packages'].fillna("No additional packages listed")
        return df
    except FileNotFoundError:
        st.error("Could not find the Excel file. Please run scraper.py first!")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter by Features")
    
    # 1. Create a master list of all unique options found across all 35 cars
    all_options = set()
    for row in df['Packages']:
        # Split the string by the comma-space separator we created in the scraper
        parts = [p.strip() for p in str(row).split(",")]
        all_options.update(parts)
    
    # Sort them alphabetically for easier reading
    sorted_options = sorted(list(all_options))
    
    # 2. Add a search box in the sidebar to find specific options quickly
    query = st.sidebar.text_input("Search for a package (e.g. 'Comfort'):")
    
    # 3. Create checkboxes for the filtered options
    selected_features = []
    st.sidebar.write("---")
    for option in sorted_options:
        if not query or query.lower() in option.lower():
            if st.sidebar.checkbox(option, key=option):
                selected_features.append(option)
    
    # --- MAIN LOGIC ---
    filtered_df = df.copy()
    
    # Apply filters: A car must contain ALL selected features
    if selected_features:
        for feature in selected_features:
            # We use a regex word boundary or exact match check to avoid partial string errors
            filtered_df = filtered_df[filtered_df['Packages'].str.contains(re.escape(feature), na=False)]

    # --- DISPLAY ---
    st.write(f"### Found {len(filtered_df)} cars matching your selection")
    
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df,
            column_config={
                "URL": st.column_config.LinkColumn("View Full Specs on Audi.pl"),
                "Price (PLN)": st.column_config.NumberColumn(format="%d zł"),
                "Packages": st.column_config.TextColumn(width="large")
            },
            hide_index=True,
            width='stretch'
        )
    else:
        st.warning("No cars match every single selected filter. Try unchecking one!")

else:
    st.info("Waiting for data... Ensure 'scraper.py' has finished running.")