import streamlit as st
from services.database_manager import DatabaseManager
from models.it_ticket import ITTicket
from services.ai_assistant import AIAssistant

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    if st.button("Go to Login"):
        st.switch_page("pages/1_🔑Login.py")
    st.stop()
st.set_page_config(page_title="IT Operations", layout="wide")
st.title("IT Operations")

db = DatabaseManager("database/intelligence_platform.db")
ai = AIAssistant()

rows = db.fetch_all("SELECT * FROM it_tickets")
tickets = [ITTicket(*row[:5]) for row in rows] if rows else []
with st.expander("➕ Add New Ticket", expanded=False):
    with st.form("add_ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        with col2:
            new_description = st.text_area("Description")
            new_ticket_type = st.selectbox("Issue Type",["Data Recovery", "Hardware Isse", "Network Isse", "Os Issue", "Persormance Issue", "Software Issue", "Other"])
        submitted = st.form_submit_button("✅ Add Ticket")
        if submitted:
            if new_description:
                # NOTE: Using 'assigned_to' field to store 'ticket_type'
                db.execute_query(
                    "INSERT INTO it_tickets (priority, status, assigned_to, description) VALUES (?, ?, ?, ?)",
                    (new_priority, new_status, new_ticket_type, new_description)
                )
                st.success(f"'{new_ticket_type}' ticket added!")
                st.rerun()
            else:
                st.error("Please enter a description")


st.divider()
rows = db.fetch_all("SELECT * FROM it_tickets")
tickets = [ITTicket(*row[:5]) for row in rows] if rows else []

# AI BULK ANALYSIS ONLY
if tickets:
    if st.button("🚀 Analyze ALL Tickets", type="primary", use_container_width=True):
        tickets_list = "\n".join([f"- #{t.get_id()}: {t.get_priority()} ({t.get_status()})" for t in tickets[:50]])
        ai_prompt = f"Analyze these {len(tickets)} IT tickets:\n{tickets_list}\n\nProvide: 1) Patterns 2) Priority issues 3) Recommendations"
        
        with st.spinner(f"Analyzing {len(tickets)} tickets..."):
            st.subheader("📊 AI Analysis")
            response_box = st.empty()
            full_text = ""
            
            for chunk in ai.send_message(ai_prompt, domain="IT Operations"):
                full_text += chunk
                response_box.markdown(full_text)
        
        st.divider()

if "filter_type" not in st.session_state:
    st.session_state.filter_type = None

issue_types = sorted(set(t.get_priority() for t in tickets if t.get_priority()))
st.write("**Filter by issue type:**")
cols = st.columns(len(issue_types) + 1)

with cols[0]:
    if st.button("All", type="primary" if st.session_state.filter_type is None else "secondary", use_container_width=True):
        st.session_state.filter_type = None
        st.rerun()

for idx, issue in enumerate(issue_types):
    with cols[idx + 1]:
        if st.button(issue, type="primary" if st.session_state.filter_type == issue else "secondary", use_container_width=True):
            st.session_state.filter_type = issue
            st.rerun()

current_filter = st.session_state.filter_type or "All"
st.write(f"**Issue Type:** {current_filter}")

if st.session_state.filter_type:
    filtered = [t for t in tickets if t.get_priority() == st.session_state.filter_type]
else:
    filtered = tickets

col1, col2, col3 = st.columns(3)
with col1: st.metric(f"{current_filter}", len(filtered))
with col2: st.metric("Open", sum(1 for t in filtered if t.get_status() == "Open"))
with col3: st.metric("Total", len(tickets))

st.divider()

for ticket in filtered:
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(f"**#{ticket.get_id()}**")
            st.write(f"Description: {ticket.get_assigned_to()}")
            st.write(f"🕐 {ticket.get_date_created()}")
        with col2:
            st.write(f"**Priority:** {ticket.get_priority()}")
            st.write(f"**Status:** {ticket.get_status()}")
        st.divider()

db.close()