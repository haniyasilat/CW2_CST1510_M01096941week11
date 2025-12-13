import streamlit as st
from services.database_manager import DatabaseManager
from models.dataset import Dataset
from services.ai_assistant import AIAssistant

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    if st.button("Go to Login"):
        st.switch_page("pages/1_🔑Login.py")
    st.stop()

st.set_page_config(page_title="Data Science Dashboard", layout="wide")

def main():
    st.title("📊 Data Science Dashboard")
    
    # Initialize
    db = DatabaseManager("database/intelligence_platform.db")
    ai = AIAssistant()
    
    # CRUD: Add New Dataset Form in sidebar
    with st.sidebar:
        st.subheader("➕ Add New Dataset")
        with st.form("add_dataset_form"):
            new_name = st.text_input("Dataset Name")
            new_source = st.text_input("Source")
            new_description = st.text_area("Description")
            
            if st.form_submit_button("💾 Add Dataset"):
                if new_name:
                    db.execute_query(
                        """INSERT INTO datasets_metadata 
                           (dataset_name, source, description, last_updated) 
                           VALUES (?, ?, ?, DATE('now'))""",
                        (new_name, new_source, new_description)
                    )
                    st.success(f"✅ Added '{new_name}'")
                    st.rerun()
                else:
                    st.error("❌ Dataset name is required")
    
    try:
        total_count = db.fetch_all("SELECT COUNT(*) FROM datasets_metadata")[0][0]
        rows = db.fetch_all("SELECT dataset_name, last_updated, source, description FROM datasets_metadata LIMIT 50")
        
        datasets = [
            Dataset(
                name=row[0],
                last_updated=row[1],
                source=row[2],
                description=row[3]
            )
            for row in rows
        ]
        
        # AI ANALYSIS
        if datasets:
            if st.button("🚀 Analyze These Datasets", type="primary", use_container_width=True):
                datasets_list = "\n".join([f"- {ds.get_name()} ({ds.get_source()})" for ds in datasets])
                ai_prompt = f"Analyze these {len(datasets)} datasets:\n{datasets_list}\n\nProvide: 1) Common patterns 2) Analysis opportunities 3) Integration potential"
                
                with st.spinner(f"Analyzing {len(datasets)} datasets..."):
                    st.subheader("📊 AI Analysis Results")
                    response_box = st.empty()
                    full_text = ""
                    
                    for chunk in ai.send_message(ai_prompt, domain="Data Science"):
                        full_text += chunk
                        response_box.markdown(full_text)
                
                st.divider()
        
        st.subheader("Dataset Overview")
        st.write(f"**Total Datasets:** {total_count}")
        st.divider()
              
        for idx, dataset in enumerate(datasets):  # Add index
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{dataset.get_name()}**")
                    st.write(f"**Source:** {dataset.get_source()}")
                    st.write(f"**Updated:** {dataset.get_last_updated()}")
                
                with col2:
                    desc = dataset.get_description()
                    if desc:
                        if len(desc) > 50:
                            st.write(f"**Description:** {desc[:120]}...")
                        else:
                            st.write(f"**Description:** {desc}")
                    else:
                        st.write("**Description:** (No description)")
                
                with col3:
                    # Use unique keys with index
                    edit_key = f"edit_{dataset.get_name()}_{idx}"
                    delete_key = f"delete_{dataset.get_name()}_{idx}"
                    
                    # EDIT button
                    if st.button("✏️ Edit", key=edit_key):
                        st.session_state[f'edit_{dataset.get_name()}_{idx}'] = True
                    
                    # DELETE button
                    if st.button("🗑️ Delete", key=delete_key):
                        if st.session_state.get(f'confirm_delete_{dataset.get_name()}_{idx}', False):
                            db.execute_query(
                                "DELETE FROM datasets_metadata WHERE dataset_name = ?",
                                (dataset.get_name(),)
                            )
                            st.success(f"✅ Deleted '{dataset.get_name()}'")
                            st.rerun()
                        else:
                            st.session_state[f'confirm_delete_{dataset.get_name()}_{idx}'] = True
                            st.warning(f"⚠️ Click DELETE again to confirm")
                
                # EDIT FORM (appears when edit button clicked)
                if st.session_state.get(f'edit_{dataset.get_name()}_{idx}', False):
                    with st.expander("✏️ Edit Dataset", expanded=True):
                        with st.form(f"edit_form_{dataset.get_name()}_{idx}"):
                            updated_name = st.text_input("Name", value=dataset.get_name(), key=f"name_{idx}")
                            updated_source = st.text_input("Source", value=dataset.get_source(), key=f"source_{idx}")
                            updated_desc = st.text_area("Description", value=dataset.get_description() or "", key=f"desc_{idx}")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save", key=f"save_{idx}"):
                                    db.execute_query(
                                        """UPDATE datasets_metadata 
                                           SET dataset_name = ?, source = ?, description = ?, last_updated = DATE('now')
                                           WHERE dataset_name = ?""",
                                        (updated_name, updated_source, updated_desc, dataset.get_name())
                                    )
                                    st.success("✅ Changes saved!")
                                    st.session_state[f'edit_{dataset.get_name()}_{idx}'] = False
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel", key=f"cancel_{idx}"):
                                    st.session_state[f'edit_{dataset.get_name()}_{idx}'] = False
                                    st.rerun()
                
                st.divider()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()