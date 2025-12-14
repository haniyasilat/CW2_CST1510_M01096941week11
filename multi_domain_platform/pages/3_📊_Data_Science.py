import streamlit as st
from services.database_manager import DatabaseManager
from models.dataset import Dataset
from services.ai_assistant import AIAssistant
import re
import pandas as pd
import plotly.express as px

#add config and titale
st.set_page_config(page_title="Data Science Dashboard", layout="wide")

#requires login before accessing this page
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    if st.button("Go to Login"):
        st.switch_page("pages/1_🔑Login.py")
    st.stop()


def make_safe_key(name, idx):
    """Convert dataset name to a safe session_state key"""
    safe_name = re.sub(r'\W+', '_', name)
    return f"{safe_name}_{idx}"
#initialize database and AI assistant
def main():
    st.title("📊 Data Science Dashboard")
    db = DatabaseManager("database/intelligence_platform.db")
    ai = AIAssistant()

    # add new dataset throught side bar
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

    try:# Get the total count from the database
        total_count = db.fetch_all("SELECT COUNT(*) FROM datasets_metadata")[0][0]
        # Load only 50 datasets for display
        rows = db.fetch_all(
         "SELECT dataset_name, last_updated, source, description FROM datasets_metadata LIMIT 50"
        )
        datasets = [Dataset(*row) for row in rows]

        st.subheader("Dataset Overview")
        st.write(f"**Total Datasets:** {total_count}")  # This is the true total
        st.caption(f"DATASET DISPLAYED: {len(rows)}")
        # display pie chart for visualization using plotly.express
        if datasets:
            df_sources = pd.DataFrame([{
                "Source": d.get_description() or "Unknown"
            } for d in datasets])
            if not df_sources.empty:
                source_counts = df_sources['Source'].value_counts().reset_index()
                source_counts.columns = ['Source', 'Count']
                fig = px.pie(
                    source_counts,
                    values='Count',
                    names='Source',
                    title="Dataset Sources Distribution",
                    color='Source',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        st.divider()

        #display each dataset line by line
        for idx, dataset in enumerate(datasets):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                # Dataset info
                with col1:
                    st.write(f"**{dataset.get_name()}**")
                    st.write(f"**Source:** {dataset.get_description()}" )
                    
                    st.write(f"**Updated:** {dataset.get_last_updated()}")
                
                # Description
                with col2:
                    desc = dataset.get_source() #error in database 'source' is switchid with 'description'
                    st.write(f"**Description:** {desc[:120]}{'...' if desc and len(desc)>120 else ''}"if desc else "**Description:** (None)")
                
                # Edit/Delete buttons
                edit_key = f"edit_{make_safe_key(dataset.get_name(), idx)}"
                delete_key = f"delete_{make_safe_key(dataset.get_name(), idx)}"

                with col3:
                    if st.button("✏️ Edit", key=f"edit_btn_{idx}"):
                        st.session_state[edit_key] = True
                        st.rerun()
                          #delete button with confirmation
                    if st.button("🗑️ Delete", key=f"delete_btn_{idx}"):
                        if st.session_state.get(delete_key, False):
                            db.execute_query(
                                "DELETE FROM datasets_metadata WHERE dataset_name = ?",
                                (dataset.get_name(),)
                            )
                            st.success(f"✅ Deleted '{dataset.get_name()}'")
                            st.rerun()
                        else:
                            st.session_state[delete_key] = True
                            st.warning("⚠️ Click DELETE again to confirm")
                            st.rerun()

                #edit form
                if st.session_state.get(edit_key, False):
                    with st.expander("✏️ Edit Dataset", expanded=True):
                        with st.form(f"edit_form_{idx}"):
                            updated_name = st.text_input("Name", value=dataset.get_name())
                            updated_source = st.text_input("Source", value=dataset.get_source() or "")
                            updated_desc = st.text_area("Description", value=dataset.get_description() or "")
                            col_save, col_cancel = st.columns(2) #save and cancel button
                            with col_save:
                                if st.form_submit_button("💾 Save"):
                                    db.execute_query(#last_updated date gets updated automatically when datset is edited
                                    #update the dataset in the database
                                        """UPDATE datasets_metadata 
                                           SET dataset_name = ?, source = ?, description = ?, last_updated = DATE('now')
                                           WHERE dataset_name = ?""",
                                        (updated_name, updated_source, updated_desc, dataset.get_name())
                                    )
                                    st.success("✅ Changes saved!")
                                    st.session_state[edit_key] = False
                                    st.rerun()
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[edit_key] = False
                                    st.rerun()

                st.divider()

    finally:
        db.close() #close database connection
#run dashboard
if __name__ == "__main__":
    main()
