import streamlit as st
from services.database_manager import DatabaseManager
from models.it_ticket import ITTicket
from services.ai_assistant import AIAssistant
import pandas as pd
import plotly.express as px

#required login before accessing this page
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    if st.button("Go to Login"):
        st.switch_page("pages/1_🔑Login.py")
    st.stop()
#config and tital
st.set_page_config(page_title="IT Operations", layout="wide")
st.title("IT Operations")
#initialize database
db = DatabaseManager("database/intelligence_platform.db")
ai = AIAssistant()
#add new ticket, form style to prevent empty submisson
with st.expander("➕ Add New Ticket", expanded=False):
    with st.form("add_ticket_form"):
        col1, col2 = st.columns(2) #slpit into two columns for neat layout
        with col1:
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            new_ticket_type = st.selectbox("Priority",["Data Recovery", "Hardware Isse", "Network Isse", "Os Issue", "Persormance Issue", "Software Issue", "Other"])

        with col2:
            new_description = st.text_area("Description")
        submitted = st.form_submit_button("✅ Add Ticket")
        if submitted:
            if new_description: #ensure description is provided
                db.execute_query(
                    "INSERT INTO it_tickets (status, assigned_to, description) VALUES ( ?, ?, ?)",
                    ( new_status, new_ticket_type, new_description)
                )
                st.success(f"'{new_ticket_type}' ticket added!")
                st.rerun() #refresh the page to show the new ticket
            else:
                st.error("Please enter a description")
st.divider()
#load all tickets
rows = db.fetch_all("SELECT * FROM it_tickets")
tickets = [ITTicket(*row[:5]) for row in rows] if rows else []

#ai analysis, analyzes all tickets together
if tickets:
    if st.button("🚀 Analyze ALL Tickets", type="primary", use_container_width=True):
        #prepares a summary list of tickets for AI
        tickets_list = "\n".join([f"- #{t.get_id()}: {t.get_priority()} ({t.get_status()})" for t in tickets[:50]])
        ai_prompt = f"Analyze these {len(tickets)} IT tickets:\n{tickets_list}\n\nProvide: 1) Patterns 2) Priority issues 3) Recommendations"
        
        with st.spinner(f"Analyzing {len(tickets)} tickets..."):
            st.subheader("📊 AI Analysis")
            response_box = st.empty()
            full_text = ""
            #AI response is typed out word by word
            for chunk in ai.send_message(ai_prompt, domain="IT Operations"):
                full_text += chunk
                response_box.markdown(full_text)
        
        st.divider()
#create a filter setup
if "filter_type" not in st.session_state:
    st.session_state.filter_type = None
#get unique issue types for filter button
issue_types = sorted(set(t.get_priority() for t in tickets if t.get_priority()))
st.write("**Filter by issue type:**")
cols = st.columns(len(issue_types) + 1)
#garphs-visualization 
#using pandas and plotly.express
if tickets:
    df = pd.DataFrame([
        {
            "Priority": t.get_priority(),
            "Status": t.get_status()
        }
        for t in tickets
    ])

    # Count tickets by priority
    priority_counts = df["Priority"].value_counts().reset_index()
    priority_counts.columns = ["Priority", "Count"]

    fig = px.bar(
        priority_counts,
        x="Priority",
        y="Count",
        color="Priority",
        title="Tickets by Priority"
    )

    st.plotly_chart(fig, use_container_width=True)
#filter buttons
with cols[0]:
    if st.button("All", type="primary" if st.session_state.filter_type is None else "secondary", use_container_width=True):
        st.session_state.filter_type = None
        st.rerun()
#buttons for each issue type to filter tickets
for idx, issue in enumerate(issue_types):
    with cols[idx + 1]: #place each issue type button in its own column
        if st.button(issue, type="primary" if st.session_state.filter_type == issue else "secondary", use_container_width=True):
            st.session_state.filter_type = issue #Set active filter to clicked issue type
            st.rerun() #refresh page

current_filter = st.session_state.filter_type or "All"
st.write(f"**Issue Type:** {current_filter}")

if st.session_state.filter_type:
    filtered = [t for t in tickets if t.get_priority() == st.session_state.filter_type]
else:
    filtered = tickets
#metrics-displayes total tickets of a specific filer, open tickets, and total tickets
col1, col2, col3 = st.columns(3)
with col1: st.metric(f"{current_filter}", len(filtered))
with col2: st.metric("Open", sum(1 for t in filtered if t.get_status() == "Open"))
with col3: st.metric("Total", len(tickets))

st.divider()
#display tickets line by line
for ticket in filtered:
    with st.container():
        col1, col2 = st.columns([1, 0.5])
        with col1:
            st.write(f"**#{ticket.get_id()}**")
            st.write(f"Description: {ticket.get_assigned_to()}")
            st.write(f"🕐 {ticket.get_date_created()}")
        with col2:
            st.write(f"**Priority:** {ticket.get_priority()}")
            st.write(f"**Status:** {ticket.get_status()}")
        st.divider()
#close database connection
db.close()