import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Store Action List", layout="wide")

st.title("📋 Store Priority Action List")

# 1. GENERATE DATA (Session State)
if 'inventory_data' not in st.session_state:
    items = []
    for i in range(1, 51):
        tsl = random.randint(50, 200)
        rand_val = random.random()
        
        # Logic: 10% Black, 20% Red
        if rand_val < 0.10:
            stock = 0 
        elif rand_val < 0.30:
            stock = random.randint(1, int(tsl * 0.30)) 
        else:
            stock = random.randint(int(tsl * 0.35), int(tsl * 1.1))
        
        if stock == 0:
            status = "Black (Stockout)"
            sort_key = 1
        elif stock < (tsl * 0.33):
            status = "Red (Risk)"
            sort_key = 2
        elif stock < (tsl * 0.67):
            status = "Yellow (Warning)"
            sort_key = 3
        else:
            status = "Green (OK)"
            sort_key = 4
        
        # CRITICAL FIX: We store the value as 45.0 instead of 0.45
        # This allows the progress bar format string to print "45%" correctly
        buffer_pct = (stock / tsl) * 100 

        items.append({
            "SKU": f"SKU-{1000+i}",
            "Description": f"Item {chr(65+i%26)}-{i}",
            "Stock": stock,
            "TSL": tsl,
            "Status": status,
            "Buffer %": buffer_pct, 
            "Sort_Key": sort_key
        })
    
    st.session_state.inventory_data = pd.DataFrame(items)

df = st.session_state.inventory_data

# 2. SIDEBAR
selected_store = st.sidebar.selectbox("Select Store", ["Jakarta Central", "Bali Denpasar"])

# 3. SORTING
df_sorted = df.sort_values(by=["Sort_Key", "Buffer %"], ascending=[True, True])

# 4. FILTERING
filter_option = st.radio(
    "Filter Priority:",
    ["Show Critical (Black/Red)", "Show All"],
    horizontal=True
)

if filter_option == "Show Critical (Black/Red)":
    df_display = df_sorted[df_sorted["Sort_Key"] <= 2]
else:
    df_display = df_sorted

# 5. ROBUST STYLING (Text Columns only)
def color_status_columns(row):
    status = row["Status"]
    
    # Define Colors
    if "Black" in status:
        bg_color = "black"
        text_color = "white"
    elif "Red" in status:
        bg_color = "#ffcccc" # Light Red
        text_color = "darkred"
    elif "Yellow" in status:
        bg_color = "#ffffcc" # Light Yellow
        text_color = "black"
    else:
        bg_color = "#ccffcc" # Light Green
        text_color = "green"
    
    styles = []
    for col in row.index:
        if col == "Buffer %":
            styles.append("") # Leave Buffer column clean
        else:
            styles.append(f'background-color: {bg_color}; color: {text_color}')
            
    return styles

# Apply row colors
styled_df = df_display.style.apply(color_status_columns, axis=1)

# 6. DISPLAY
st.dataframe(
    styled_df, 
    use_container_width=True,
    column_config={
        "Sort_Key": None,
        "Status": st.column_config.TextColumn("Zone Status"),
        "Buffer %": st.column_config.ProgressColumn(
            "Buffer Depth",
            format="%.0f%%", # Now "45.0" becomes "45%"
            min_value=0,
            max_value=100,   # Scale is now 0-100
        )
    },
    height=800
)

if st.sidebar.button("GENERATE NEW DAY"):
    del st.session_state.inventory_data
    st.rerun()