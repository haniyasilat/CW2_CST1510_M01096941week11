import streamlit as st
import pandas as pd
import plotly.express as px
from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident
from services.ai_assistant import AIAssistant

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    if st.button("Go to Login"):
        st.switch_page("pages/1_🔑Login.py")
    st.stop()

st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")
st.title("🛡️ Cybersecurity Incident Dashboard")

# 1. Replace direct SQL calls with DatabaseManager method
db = DatabaseManager("database/intelligence_platform.db")
incidents_data = db.fetch_all("SELECT * FROM cyber_incidents")

# 2. Wrap row data into SecurityIncident objects
incidents = []
for row in incidents_data:
    incident = SecurityIncident(
        date_reported=row[0],
        incident_type=row[1],
        severity=row[2],
        status=row[3],
        description=row[4]
    )
    incidents.append(incident)

# Initialize AI Assistant
ai_assistant = AIAssistant()

# --- ONE BUTTON TO ANALYZE ALL INCIDENTS AT TOP ---
if incidents:  # Only show button if there are incidents
    st.subheader("🤖 AI Bulk Analysis")
    
    if st.button("🚀 Analyze ALL Incidents at Once", type="primary", use_container_width=True):
        # Prepare all incidents data for AI
        all_incidents_summary = ""
        for i, incident in enumerate(incidents, 1):
            all_incidents_summary += f"""
            Incident #{i}:
            - Type: {incident.get_incident_type()}
            - Date: {incident.get_date_reported()}
            - Severity: {incident.get_severity()}
            - Status: {incident.get_status()}
            - Description: {incident.get_description()[:200] if incident.get_description() else "No description"}
            """
        
        # Create prompt for analyzing ALL incidents
        ai_prompt = f"""
        Analyze ALL {len(incidents)} cybersecurity incidents at once:
        
        {all_incidents_summary}
        
        Provide a comprehensive analysis covering:
        1. OVERALL RISK ASSESSMENT - What's the overall security posture?
        2. TOP THREAT PATTERNS - Any recurring incident types or patterns?
        3. SEVERITY DISTRIBUTION - Breakdown of critical/high/medium/low incidents
        4. URGENT ACTIONS - What needs immediate attention?
        5. RECOMMENDATIONS - Specific, actionable recommendations for all incidents
        
        Be concise but thorough.
        """
        
        with st.spinner(f"Analyzing all {len(incidents)} incidents..."):
            analysis = ai_assistant.send_message(ai_prompt, domain="Cybersecurity")
            
        st.subheader("📊 Analysis of ALL Incidents")
        st.write(analysis)
        st.divider()

st.subheader("📊 Overview Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Incidents", len(incidents))

with col2:
    open_count = sum(1 for incident in incidents if incident.get_status() == "Open")
    st.metric("Open Incidents", open_count)

with col3:
    medium_priority = sum(1 for incident in incidents if incident.get_severity_level() >= 1)
    st.metric("Medium Priority", medium_priority)


st.divider()

# Prepare data for graphs
graph_data = []
for incident in incidents:
    graph_data.append({
        'Date': incident.get_date_reported(),
        'Type': incident.get_incident_type(),
        'Severity': incident.get_severity(),
        'Status': incident.get_status(),
        'Description': incident.get_description()
    })

df = pd.DataFrame(graph_data)


st.subheader("Visual Representations 📊")
if not df.empty:
        type_counts = df['Type'].value_counts().reset_index()
        type_counts.columns = ['Incident Type', 'Count']
        
        fig_bar = px.bar(
            type_counts,
            x='Incident Type',
            y='Count',
            title="Number of Incidents by Type",
            color='Count'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
if not df.empty:
        # Convert date
        df['Year'] = pd.to_datetime(df['Date'], errors='coerce')
        df_clean = df.dropna(subset=['Year'])
        
        if not df_clean.empty:
            fig_scatter = px.scatter(
                df_clean,
                x='Year',
                y='Type',
                title="Incidents Over Time by Severity",
                hover_data=['Status', 'Description']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()
st.subheader(f"📋 Incident Details ({len(incidents)} total)")

for incident in incidents:
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write(f"**Date:** {incident.get_date_reported()}")
            st.write(f"**Type:** {incident.get_incident_type()}")
            st.write(f"**Status:** {incident.get_status()}")
            
        with col2:
            severity_level = incident.get_severity_level()
            st.write(f"**Level:** {severity_level}/4")
            
            if severity_level >= 3:
                st.error("🚨 High Priority")
            elif severity_level == 2:
                st.warning("⚠️ Medium Priority")
            else:
                st.info("ℹ️ Low Priority")
    
        description = incident.get_description()
        if description:
            short_desc = description[:100] + "..." if len(description) > 100 else description
            st.write(f"**Description:** {short_desc}")
            
            with st.expander("View Full Description"):
                st.write(f"**Full Description:** {description}")
                
        st.divider()

# Close database connection
db.close()