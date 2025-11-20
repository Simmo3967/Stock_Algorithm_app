import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import deque

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="TOC Replenishment Sim")

st.title("Dynamic Buffer Management (TOC)")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("1. Policy Settings")
initial_stock = st.sidebar.number_input("Initial Stock", value=150, step=10)
tsl_start = st.sidebar.number_input("Initial Target Stock Level (TSL)", value=150, step=10)

st.sidebar.header("2. Real World Constraints")
lead_time = st.sidebar.slider("Replenishment Period (Delivery Days)", 0, 14, 1)
order_freq = st.sidebar.slider("Ordering Period (Place order every X days)", 1, 14, 1)

# Display the Reliable Replenishment Time (RRT)
rrt = lead_time + order_freq
st.sidebar.info(f"Reliable Replenishment Time (RRT): {rrt} Days")

# --- LOAD DATA ---
try:
    df = pd.read_csv('sales_simulation.csv')
except FileNotFoundError:
    st.error("File not found. Please create 'sales_simulation.csv' first.")
    st.stop()

# --- SIMULATION STATE ---
current_stock = initial_stock
tsl = tsl_start
pipeline = deque([0] * (lead_time + 1)) # A queue to hold orders in transit

# HISTORY LISTS
days = []
stock_history = []
tsl_history = []
sales_history = []
# We track the zone boundaries for the graph
green_top = []
yellow_top = []
red_top = []

# ALGORITHM VARIABLES
green_streak = 0
red_penetration_sum = 0
days_since_last_order = 0

# --- MAIN LOOP ---
for index, row in df.iterrows():
    day = row['Day']
    sales = row['Daily_Sales']

    # 1. RECEIVE ORDERS (Pipeline moves forward)
    # We pop the order arriving today from the pipeline
    arriving_stock = pipeline.popleft()
    current_stock += arriving_stock
    
    # 2. FULFILL SALES
    current_stock -= sales
    # Constraint: Stock cannot go negative
    if current_stock < 0:
        current_stock = 0

    # 3. DEFINE ZONES (Dynamic based on current TSL)
    red_limit = tsl * 0.33
    yellow_limit = tsl * 0.67
    green_limit = tsl * 1.00

    # 4. CHECK ZONES (Buffer Management Logic)
    # GREEN ZONE CHECK
    if current_stock > yellow_limit:
        green_streak += 1
        red_penetration_sum = 0 # Reset red logic
        if green_streak >= 2: # Simplification of the rule for demo
            tsl = int(tsl * 0.67)
            green_streak = 0
    else:
        green_streak = 0
    
    # RED ZONE CHECK
    if current_stock < red_limit:
        penetration = red_limit - current_stock
        red_penetration_sum += penetration
        if red_penetration_sum > red_limit:
            tsl = int(tsl * 1.33)
            red_penetration_sum = 0

    # 5. PLACING ORDERS (The new Logic)
    days_since_last_order += 1
    
    # Only order if we are on an "Ordering Day"
    if days_since_last_order >= order_freq:
        # Calculate Need
        total_inventory = current_stock + sum(pipeline) # Stock on hand + Stock on water
        order_qty = tsl - total_inventory
        
        if order_qty > 0:
            # Add to the END of the pipeline (will arrive in 'lead_time' days)
            pipeline.append(order_qty)
        else:
            pipeline.append(0)
            
        days_since_last_order = 0 # Reset counter
    else:
        # If not ordering day, nothing is ordered
        pipeline.append(0)

    # 6. RECORD HISTORY
    days.append(day)
    stock_history.append(current_stock)
    tsl_history.append(tsl)
    sales_history.append(sales)
    
    # Record Zone Boundaries for the fancy graph
    red_top.append(tsl * 0.33)
    yellow_top.append(tsl * 0.33) # Thickness of yellow band
    green_top.append(tsl * 0.34)  # Thickness of green band

# --- VISUALIZATION (The TOC Standard View) ---
fig = go.Figure()

# 1. THE ZONES (Drawn as Stacked Areas)
# Red Zone (Bottom)
fig.add_trace(go.Scatter(
    x=days, y=red_top,
    mode='lines', line=dict(width=0),
    fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)',
    name='Red Zone', hoverinfo='skip'
))

# Yellow Zone (Stacked on Red)
fig.add_trace(go.Scatter(
    x=days, y=[r + y for r, y in zip(red_top, yellow_top)],
    mode='lines', line=dict(width=0),
    fill='tonexty', fillcolor='rgba(255, 255, 0, 0.2)',
    name='Yellow Zone', hoverinfo='skip'
))

# Green Zone (Stacked on Yellow)
fig.add_trace(go.Scatter(
    x=days, y=[r + y + g for r, y, g in zip(red_top, yellow_top, green_top)],
    mode='lines', line=dict(width=0),
    fill='tonexty', fillcolor='rgba(0, 128, 0, 0.2)',
    name='Green Zone', hoverinfo='skip'
))

# 2. THE STOCK LINE (The Hero)
fig.add_trace(go.Scatter(
    x=days, y=stock_history,
    mode='lines+markers',
    line=dict(color='black', width=3),
    name='Stock Level'
))

# 3. LAYOUT TWEAKS
fig.update_layout(
    title="Buffer Management Simulation",
    xaxis_title="Day",
    yaxis_title="Units",
    hovermode="x unified",
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# --- METRICS ---
c1, c2, c3 = st.columns(3)
c1.metric("Ending Stock", current_stock)
c2.metric("Final TSL", tsl)
c3.metric("Total Sales", sum(sales_history))

