import streamlit as st
import pandas as pd
import plotly.express as px
from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident
from services.ai_assistant import AIAssistant

#requires login first before accessing 
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    if st.button("Go to Login"):
        st.switch_page("pages/1_🔑Login.py")
    st.stop()
#configuriation and title
st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")
st.title("🛡️ Cybersecurity Incident Dashboard")

#initialize service and AIAssistant provies ai based analysis
#DatabaseManager handles SQL operations
db = DatabaseManager("database/intelligence_platform.db")
ai = AIAssistant()

#add incident, this is displayed at sidebar (crud)
#uses a form to avaoid partial submissions
with st.sidebar:
    st.subheader("➕ Add Incident")
    with st.form("add_form"):
        i_type = st.selectbox("Type", ["Malware", "Phishing", "DDoS", "Unauthorized Access", "Data Breach", "Other"])
        i_severity = st.select_slider("Severity", ["Low", "Medium", "High", "Critical"], "Medium")
        i_desc = st.text_area("Description")
        #when a new incidnets is submitted its added to the database
        if st.form_submit_button("Add") and i_desc:
            from datetime import datetime
            #current date is added using the module
            db.execute_query(
                "INSERT INTO cyber_incidents (date_reported, incident_type, severity, status, description) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().strftime("%m/%d/%Y"), i_type, i_severity, "Open", i_desc)
            )
            st.success("Added!")
            st.rerun()

# Load data
data = db.fetch_all("SELECT * FROM cyber_incidents")
incidents = [SecurityIncident(*row[:5]) for row in data]

# AI Analysis
#AI analysis and summarizes all the incidents at once
if incidents and st.button("🚀 Analyze ALL Incidents", type="primary", use_container_width=True):
    summary = "\n".join([f"- {i.get_incident_type()} ({i.get_severity()})" for i in incidents])
    with st.spinner("Analyzing..."):
        analysis = ai.send_message(f"Analyze: {summary}", domain="Cybersecurity")
    st.subheader("📊 AI Analysis")
    st.write(analysis)
    st.divider()

# Metrics
#displayes total incidnets, all oepn incidents and all medium incidents
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total", len(incidents))
with col2:
    st.metric("Open", sum(1 for i in incidents if i.get_status() == "Open"))
with col3:
    st.metric("Medium", sum(1 for i in incidents if i.get_severity_level() >= 2))
st.divider()

# Visualizations using pandas and plotly.express
if incidents:
    st.subheader("📈 Visualizations")
    df = pd.DataFrame([{ #convert incidents into datafram for plotting
        'Date': i.get_date_reported(),
        'Type': i.get_incident_type(),
        'Severity': i.get_severity(),
        'Status': i.get_status()
    } for i in incidents])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart
        type_counts = df['Type'].value_counts().reset_index()
        fig_bar = px.bar(type_counts, x='Type', y='count', title="Incidents by Type", color='count')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Scatter plot
        df['Date_parsed'] = pd.to_datetime(df['Date'], errors='coerce')
        df_clean = df.dropna(subset=['Date_parsed'])
        if not df_clean.empty:
            fig_scatter = px.scatter(df_clean, x='Date_parsed', y='Type', color='Severity', 
                                   title="Incidents Over Time", hover_data=['Status'])
            st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

#incident List with CRUD
st.subheader(f"📋 Incidents ({len(incidents)} total)")

for idx, incident in enumerate(incidents):
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.write(f"**{incident.get_incident_type()}**")
            st.write(f"Date: {incident.get_date_reported()}")
            st.write(f"Status: {incident.get_status()}")
        
        with col2:
            level = incident.get_severity_level()
            st.write(f"Severity: {incident.get_severity()} (Level {level}/4)")
            if level >= 3:
                st.error("🚨 High")
            elif level == 2:
                st.warning("⚠️ Medium")
            else:
                st.info("ℹ️ Low")
        
        with col3: #CRUD buttons to delete or edit
            # Use callback functions instead of direct session_state modification
            edit_key = f"edit_btn_{idx}"
            delete_key = f"delete_btn_{idx}"
            
            # Edit button with callback
            if st.button("✏️", key=edit_key):
                st.session_state[f'edit_mode_{idx}'] = True
                st.rerun()
            
            # Delete button with callback
            if st.button("🗑️", key=delete_key):
                if f'confirm_delete_{idx}' not in st.session_state:
                    st.session_state[f'confirm_delete_{idx}'] = True
                    st.warning("Click again to confirm")
                    st.rerun()
                else:
                    db.execute_query(
    "DELETE FROM cyber_incidents WHERE date_reported = ? AND incident_type = ?",
    (incident.get_date_reported(), incident.get_incident_type())
                    )
                    st.success("Deleted!")
                    # Clear session states
                    for key in [f'edit_mode_{idx}', f'confirm_delete_{idx}']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        # Edit form (only shows if edit mode is True)
        if st.session_state.get(f'edit_mode_{idx}', False):
            with st.expander("Edit", expanded=True):
                # Use a form key that includes idx to make it unique
                with st.form(key=f"edit_form_{idx}"):
                    new_type = st.selectbox("Type", ["Malware", "Phishing", "DDoS", "Other"], 
                                          key=f"type_{idx}")
                    new_severity = st.select_slider("Severity", ["Low", "Medium", "High", "Critical"],
                                                  value=incident.get_severity(), key=f"sev_{idx}")
                    new_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"],
                                            key=f"status_{idx}")
                    new_description = st.text_area("Description", value=incident.get_description() or "",
                                key=f"desc_{idx}")                   
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Save"):
                            db.execute_query(
                                "UPDATE cyber_incidents SET incident_type=?, severity=?, status=?, description=? WHERE date_reported=?",
                                (new_type, new_severity, new_status,new_description, incident.get_date_reported())
                            )
                            # Clear edit mode and refresh
                            del st.session_state[f'edit_mode_{idx}']
                            st.rerun()
                    
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            # Just clear edit mode without saving
                            del st.session_state[f'edit_mode_{idx}']
                            st.rerun()
        
        #to display description
        desc = incident.get_description()
        if desc:
            with st.expander("Description"):
                st.write(desc)
        st.divider()
db.close()