import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="BMTC Transit System",
    page_icon="🚌",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("integrated_analytics.csv")
    return df

df = load_data()

# ============================================================
# VIEW SELECTOR - PASSENGER OR MANAGEMENT
# ============================================================
st.title("🚌 BMTC Transit Intelligence System")

view_mode = st.sidebar.radio(
    "🔀 Select View:",
    ["👥 Passenger View", "👨‍💼 Management Dashboard"],
    help="Switch between passenger route checker and management analytics"
)

st.sidebar.markdown("---")

# ============================================================
# PASSENGER VIEW
# ============================================================
if view_mode == "👥 Passenger View":
    st.markdown("### Plan Your Journey - Check Route Crowding")
    st.markdown("---")
    
    # Route Finder
    st.markdown("## 🔎 Check Your Bus Route")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        route_search = st.selectbox("🚌 Select your route:", options=['-- Choose Route --'] + sorted(df['route'].unique()))
    
    with col2:
        travel_time = st.selectbox(
            "⏰ What time?",
            options=[
                '-- Select Time --',
                '6:00 AM - 7:00 AM',
                '7:00 AM - 8:00 AM',
                '8:00 AM - 9:00 AM',
                '9:00 AM - 10:00 AM',
                '10:00 AM - 12:00 PM',
                '12:00 PM - 2:00 PM',
                '2:00 PM - 3:00 PM',
                '3:00 PM - 4:00 PM',
                '4:00 PM - 5:00 PM',
                '5:00 PM - 6:00 PM',
                '6:00 PM - 7:00 PM',
                '7:00 PM - 8:00 PM',
                '8:00 PM onwards'
            ]
        )
    
    if route_search != '-- Choose Route --' and travel_time != '-- Select Time --':
        route_data = df[df['route'] == route_search].iloc[0]
        
        # Crowding logic
        is_school_route = route_data['num_stops'] > 10
        base_crowded = route_data['demand_level'] == 'OVERCROWDED'
        
        peak_morning = travel_time in ['7:00 AM - 8:00 AM', '8:00 AM - 9:00 AM']
        peak_evening = travel_time in ['5:00 PM - 6:00 PM', '6:00 PM - 7:00 PM', '7:00 PM - 8:00 PM']
        school_morning = travel_time in ['7:00 AM - 8:00 AM', '8:00 AM - 9:00 AM']
        school_afternoon = travel_time in ['2:00 PM - 3:00 PM', '3:00 PM - 4:00 PM']
        off_peak = travel_time in ['9:00 AM - 10:00 AM', '10:00 AM - 12:00 PM', '12:00 PM - 2:00 PM']
        
        if base_crowded and (peak_morning or peak_evening):
            status = "VERY CROWDED"
            color = "🔴"
            message = "⚠️ AVOID if possible! Buses will be packed."
        elif base_crowded and is_school_route and (school_morning or school_afternoon):
            status = "VERY CROWDED"
            color = "🔴"
            message = "⚠️ School + rush hour! Extra crowded."
        elif base_crowded and off_peak:
            status = "MODERATELY CROWDED"
            color = "🟡"
            message = "Manageable. Good time to travel."
        elif is_school_route and (school_morning or school_afternoon):
            status = "CROWDED"
            color = "🟠"
            message = "⚠️ School hours - expect students."
        elif peak_morning or peak_evening:
            status = "MODERATELY CROWDED"
            color = "🟡"
            message = "Rush hour. Board from early stops."
        else:
            status = "LESS CROWDED"
            color = "🟢"
            message = "✅ Good time! Seats available."
        
        st.markdown("---")
        st.markdown(f"### {color} Route {route_data['route']} at {travel_time}")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("### 📍 Route Info")
            st.write(f"**Length:** {route_data['route_length_km']:.2f} km")
            st.write(f"**Stops:** {int(route_data['num_stops'])}")
            st.write(f"**Trips/Day:** {int(route_data['trips'])}")
        
        with col2:
            st.markdown(f"### 🚦 Status")
            if status == "VERY CROWDED":
                st.error(f"**{status}**")
            elif "CROWDED" in status:
                st.warning(f"**{status}**")
            else:
                st.success(f"**{status}**")
            st.info(message)
        
        with col3:
            st.markdown("### 💡 Tips")
            if "VERY CROWDED" in status or "CROWDED" in status:
                st.write("✅ Board early")
                st.write("✅ Earlier stops better")
                st.write("✅ Have backup route")
            else:
                st.write("✅ Seats available")
                st.write("✅ Comfortable journey")
    
    st.markdown("---")
    st.markdown("## 📋 All Routes")
    st.dataframe(df[['route', 'route_length_km', 'num_stops', 'trips', 'demand_level']], width="stretch", height=300)

# ============================================================
# MANAGEMENT DASHBOARD
# ============================================================
else:
    st.markdown("### Analytics, Insights & Control Panel")
    st.markdown("---")
    
    
    # ============================================================
    # ALL ROUTES QUICK REFERENCE
    # ============================================================
    st.markdown("## 📋 All Routes Quick Reference")
    
    # Filter options
    view_option = st.radio(
        "Show me:",
        ["All Routes", "Overcrowded Routes Only", "Efficient Routes", "School Routes", "Overlap Routes"]
    )
    
    if view_option == "All Routes":
        display_df = df[['route', 'route_length_km', 'num_stops', 'trips', 'demand_level', 'efficiency_category']]
    elif view_option == "Overcrowded Routes Only":
        display_df = df[df['demand_level'] == 'OVERCROWDED'][['route', 'route_length_km', 'num_stops', 'trips', 'predicted_relative_demand','demand_level']]
    elif view_option == "Efficient Routes":
        display_df = df[df['efficiency_category'] == 'HIGH'][['route', 'route_length_km', 'trips', 'efficiency_score']]
    elif view_option == "School Routes":
        display_df = df[df['num_stops'] > 10][['route', 'num_stops', 'trips', 'demand_level']]
    else:  # Overlap Routes
        display_df = df[df['redundancy_category'] == 'HIGH'][['route', 'route_length_km', 'redundancy_score', 'trips']]
    
    
    st.dataframe(display_df, width="stretch", height=400)
    st.caption(f"Showing {len(display_df)} routes")
    
    st.markdown("---")
    
    # ============================================================
    # DETAILED ANALYTICS & VISUALIZATIONS
    # ============================================================
    st.markdown("## 📈 Detailed Analytics")
    
    tab1, tab2, tab3 = st.tabs(["🔥 Demand Analysis", "⚙️ Efficiency Analysis", "🎯 Priority Routes"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_demand = px.histogram(
                df, x='predicted_relative_demand', nbins=20, color='demand_level',
                title="Demand Distribution",
                labels={'predicted_relative_demand': 'Demand Index'},
                color_discrete_map={'OVERCROWDED': 'red', 'NORMAL': 'blue'}
            )
            st.plotly_chart(fig_demand, width="stretch")
        
        with col2:
            st.markdown("### 🔴 Top Congested")
            top10 = df.nlargest(10, 'predicted_relative_demand')[['route', 'predicted_relative_demand', 'trips']]
            st.dataframe(top10, hide_index=True, width="stretch")
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_eff = px.scatter(
                df, x='trips', y='efficiency_score', size='predicted_relative_demand',
                color='efficiency_category', hover_data=['route'],
                title="Efficiency vs Trips",
                color_discrete_map={'HIGH': 'green', 'LOW': 'red'}
            )
            st.plotly_chart(fig_eff, width="stretch")
        
        with col2:
            st.markdown("### 🔻 Least Efficient")
            bottom10 = df.nsmallest(10, 'efficiency_score')[['route', 'efficiency_score', 'trips']]
            st.dataframe(bottom10, hide_index=True, width="stretch")
    
    with tab3:
        urgent = df[df['priority_category'] == 'URGENT']
        high = df[df['priority_category'] == 'HIGH']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.error(f"**URGENT: {len(urgent)} routes**")
            if len(urgent) > 0:
                st.dataframe(urgent[['route', 'predicted_relative_demand', 'efficiency_score']], hide_index=True)
        
        with col2:
            st.warning(f"**HIGH: {len(high)} routes**")
            if len(high) > 0:
                st.dataframe(high[['route', 'predicted_relative_demand', 'efficiency_score']].head(10), hide_index=True)
    
    st.markdown("---")
    
    # ============================================================
    # MANAGEMENT CONTROL PANEL
    # ============================================================
    st.markdown("## 🎛️ Management Control Panel")
    
    control_tab1, control_tab2, control_tab3, control_tab4 = st.tabs([
        "➕ Add Buses",
        "🆕 Add Route", 
        "📊 Update Demand",
        "🏫 School Timings"
    ])
    
    with control_tab1:
        st.markdown("### ➕ Add Buses to Overcrowded Routes")
        
        overcrowded_list = df[df['demand_level'] == 'OVERCROWDED']['route'].tolist()
        selected_route = st.selectbox("Select route:", overcrowded_list)
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_trips = int(df[df['route'] == selected_route]['trips'].values[0])
            st.metric("Current Trips/Day", current_trips)
            
            additional_buses = st.slider("Add buses:", 0, 50, 10)
            new_trips = current_trips + additional_buses
            st.metric("New Trips/Day", new_trips, f"+{additional_buses}")
        
        with col2:
            current_demand = df[df['route'] == selected_route]['predicted_relative_demand'].values[0]
            st.metric("Current Demand", f"{current_demand:.2f}")
            
            demand_reduction = (additional_buses / current_trips) * 100
            new_demand = current_demand * (1 - demand_reduction/100)
            st.metric("Estimated New Demand", f"{new_demand:.2f}", f"-{demand_reduction:.1f}%")
        
        if st.button("💾 Save Changes", key="add_bus"):
            st.success(f"✅ Added {additional_buses} buses to Route {selected_route}")
    
    with control_tab2:
        st.markdown("### 🆕 Add New Route")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_route_name = st.text_input("Route Number:", placeholder="500X")
            new_route_length = st.number_input("Length (km):", 1.0, 50.0, 10.0)
            new_route_stops = st.number_input("Stops:", 5, 50, 15)
        
        with col2:
            new_route_trips = st.number_input("Trips/Day:", 10, 200, 50)
            expected_demand = st.slider("Expected Demand:", 10.0, 100.0, 40.0)
            route_type = st.selectbox("Type:", ["Regular", "School Route", "Express"])
        
        if st.button("➕ Add Route", key="add_route"):
            st.success(f"✅ New Route {new_route_name} added")
    
    with control_tab3:
        st.markdown("### 📊 Update Demand Patterns")
        
        update_source = st.selectbox(
            "Data Source:",
            ["Real-time GPS", "Ticket Sales", "Passenger Surveys", "App Usage"]
        )
        
        routes_to_update = st.multiselect(
            "Routes to update:",
            df['route'].tolist(),
            default=df['route'].tolist()[:5]
        )
        
        if st.button("🔄 Retrain ML Model", key="retrain"):
            st.success("✅ Model retraining initiated")
            progress_bar = st.progress(0)
            import time
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            st.success("✅ Model retrained successfully!")
    
    with control_tab4:
        st.markdown("### 🏫 Update School Timings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            school_start = st.time_input("School Start:", value=None)
            school_end = st.time_input("School End:", value=None)
        
        with col2:
            buffer_time = st.slider("Buffer (min):", 15, 60, 30)
            affected_routes = st.multiselect(
                "School Routes:",
                df[df['num_stops'] > 10]['route'].tolist()
            )
        
        if st.button("💾 Update Settings", key="school"):
            st.success(f"✅ School timings updated")
    
    st.markdown("---")
    st.download_button(
        "📥 Download Report",
        df.to_csv(index=False),
        "bmtc_report.csv",
        "text/csv"
    )
