import streamlit as st
from services.database_manager import DatabaseManager
from models.dataset import Dataset
from services.ai_assistant import AIAssistant

# Login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    if st.button("Go to Login"): st.switch_page("pages/1_🔑Login.py")
    st.stop()

st.set_page_config(page_title="Data Science Dashboard", layout="wide")
st.title("📊 Data Science Dashboard")

# Initialize
db = DatabaseManager("database/intelligence_platform.db")
ai = AIAssistant()

# CRUD: Add form in sidebar
with st.sidebar:
    st.subheader("➕ Add New Dataset")
    with st.form("add_form"):
        name = st.text_input("Dataset Name")
        source = st.text_input("Source")
        desc = st.text_area("Description")
        if st.form_submit_button("💾 Add"):
            if name:
                db.execute_query(
                    """INSERT INTO datasets_metadata 
                       (dataset_name, source, description, last_updated) 
                       VALUES (?, ?, ?, DATE('now'))""",
                    (name, source, desc)
                )
                st.success(f"✅ Added '{name}'")
                st.rerun()
            else: st.error("❌ Name required")

try:
    # Load data
    total = db.fetch_all("SELECT COUNT(*) FROM datasets_metadata")[0][0]
    rows = db.fetch_all("SELECT dataset_name, last_updated, source, description FROM datasets_metadata LIMIT 50")
    
    datasets = [Dataset(*row) for row in rows]  # Shortened object creation
    
    # AI Analysis
    if datasets and st.button("🚀 Analyze Datasets", type="primary", use_container_width=True):
        datasets_list = "\n".join([f"- {ds.get_name()}" for ds in datasets])
        with st.spinner(f"Analyzing {len(datasets)} datasets..."):
            st.subheader("📊 AI Analysis Results")
            response = st.empty()
            full_text = ""
            for chunk in ai.send_message(f"Analyze: {datasets_list}", domain="Data Science"):
                full_text += chunk
                response.markdown(full_text)
        st.divider()
    
    st.subheader("Dataset Overview")
    st.write(f"**Total Datasets:** {total}")
    st.divider()
    
    # Display datasets with CRUD
    for idx, dataset in enumerate(datasets):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{dataset.get_name()}**")
                st.write(f"Source:{dataset.get_description()}")
                st.write(f"**Updated:** {dataset.get_last_updated()}")
            
            with col2:
                desc = dataset.get_source()
                st.write(f"**Description:**  {desc[:120] + '...' if desc and len(desc) > 120 else desc} ")
            with col3:
                # Edit/Delete buttons
                edit_key, delete_key = f"edit_{idx}", f"delete_{idx}"
                
                if st.button("✏️ Edit", key=edit_key):
                    st.session_state[edit_key] = True
                
                if st.button("🗑️ Delete", key=delete_key):
                    if st.session_state.get(f"confirm_{delete_key}", False):
                        db.execute_query("DELETE FROM datasets_metadata WHERE dataset_name = ?", (dataset.get_name(),))
                        st.success(f"✅ Deleted")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_{delete_key}"] = True
                        st.warning("⚠️ Click again")
            
            # Edit form
            if st.session_state.get(f"edit_{idx}", False):
                with st.expander("✏️ Edit Dataset", expanded=True):
                    with st.form(f"edit_form_{idx}"):
                        new_name = st.text_input("Name", value=dataset.get_name())
                        new_source = st.text_input("Source", value=dataset.get_source())
                        new_desc = st.text_area("Description", value=dataset.get_description() or "")
                        
                        if st.form_submit_button("💾 Save"):
                            db.execute_query(
                                """UPDATE datasets_metadata 
                                   SET dataset_name=?, source=?, description=?, last_updated=DATE('now')
                                   WHERE dataset_name=?""",
                                (new_name, new_source, new_desc, dataset.get_name())
                            )
                            st.session_state[f"edit_{idx}"] = False
                            st.rerun()
                        
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state[f"edit_{idx}"] = False
                            st.rerun()
            
            st.divider()

finally:
    db.close()