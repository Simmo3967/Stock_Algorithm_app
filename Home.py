import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supply Chain Command Center", layout="wide")

st.title("📊 Supply Chain Command Center")

# 1. THE "FAKE" DATABASE (Since we don't have real store data yet)
data = {
    "Store Name": ["Jakarta Central", "Bali Denpasar", "Surabaya East", "Medan City", "Bandung West"],
    "Total SKUs": [150, 80, 200, 120, 90],
    "Black Zone (Stockouts)": [12, 2, 5, 0, 8],
    "Red Zone (Risk)": [25, 5, 15, 8, 12],
    "Status": ["CRITICAL", "Healthy", "Warning", "Healthy", "CRITICAL"]
}
df_stores = pd.DataFrame(data)

# 2. KEY METRICS
c1, c2, c3 = st.columns(3)
c1.metric("Total Stores", "5")
c2.metric("Active SKUs", "640")
c3.metric("Critical Alerts", "2", delta="-1", delta_color="inverse")

st.markdown("---")

# 3. THE STORE GRID
st.subheader("Store Performance Overview")

st.data_editor(
    df_stores,
    column_config={
        "Status": st.column_config.TextColumn(
            "Health Status",
            validate="^(Healthy|Warning|CRITICAL)$",
        ),
        "Black Zone (Stockouts)": st.column_config.ProgressColumn(
            "Stockouts (Black Zone)",
            format="%d Items",
            min_value=0,
            max_value=20,
        ),
    },
    hide_index=True,
    use_container_width=True,
)

st.info("👉 To analyze a specific item, click **'Simulation Playground'** in the left sidebar.")