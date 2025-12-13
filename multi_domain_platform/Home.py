import streamlit as st

st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Intelligence Platform Dashboard")
st.markdown("### Unified Dashboard for Cybersecurity, Data Science & IT Operations")

# Introduction
st.markdown("""
Welcome to the **Intelligence Platform** – a unified dashboard that provides AI-powered insights 
across multiple domains. Navigate to different sections using the sidebar.
""")

# Domain cards
st.markdown("## 📊 Available Dashboards")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🛡️ Cybersecurity")
    st.markdown("""
    - View security incidents
    - AI-powered threat analysis
    - Risk assessment & prioritization
    - Actionable recommendations
    """)
    if st.button("Go to Cybersecurity", key="cyber"):
        st.switch_page("pages/2_🛡️_Cybersecurity.py")

with col2:
    st.markdown("### 📈 Data Science")
    st.markdown("""
    - Dataset catalog & metadata
    - AI-driven data analysis
    - Pattern recognition
    - Integration insights
    """)
    if st.button("Go to Data Science", key="data"):
        st.switch_page("pages/3_📊_Data_Science.py")

with col3:
    st.markdown("### ⚙️ IT Operations")
    st.markdown("""
    - Ticket management
    - Issue tracking & filtering
    - AI operations analysis
    - Resource optimization
    """)
    if st.button("Go to IT Operations", key="it"):
        st.switch_page("pages/4_💻_IT_Operations.py")

# System status (optional)
st.divider()
st.markdown("## 📈 System Status")

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    st.metric("AI Assistant", "Online", "Ready")

with status_col2:
    st.metric("Database", "Connected", "Active")

with status_col3:
    st.metric("Last Updated", "Today", "-")

with status_col4:
    st.metric("Total Records", "1,250+", "+15 today")

# Quick links in sidebar
with st.sidebar:
    st.markdown("## 🔗 Quick Links")
    st.page_link("home.py", label="🏠 Home")
    st.page_link("pages/2_🛡️_Cybersecurity.py", label="🛡️ Cybersecurity")
    st.page_link("pages/3_📊_Data_Science.py", label="📊 Data Science")
    st.page_link("pages/4_💻_IT_Operations.py", label="💻 IT Operations")
    