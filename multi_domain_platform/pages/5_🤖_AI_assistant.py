import streamlit as st
from services.ai_assistant import AIAssistant

# Initialize
ai_assistant = AIAssistant()

# Session state
if "selected" not in st.session_state:
    st.session_state.selected = "Cybersecurity"

if "messages" not in st.session_state:
    st.session_state.messages = {}

# Initialize chat for each assistant
for name in ["Cybersecurity", "Data Science", "IT Operations"]:
    if name not in st.session_state.messages:
        st.session_state.messages[name] = []

# Sidebar
with st.sidebar:
    st.title("Assistant")
    selected = st.radio(
        "Choose:",
        ["Cybersecurity", "Data Science", "IT Operations"],
        index=["Cybersecurity", "Data Science", "IT Operations"].index(st.session_state.selected)
    )
    
    if selected != st.session_state.selected:
        st.session_state.selected = selected
        st.rerun()
    
    if st.button("Clear Chat"):
        st.session_state.messages[st.session_state.selected] = []
        st.rerun()

# Main
st.title(f"{st.session_state.selected}")

# Get current messages
current_messages = st.session_state.messages[st.session_state.selected]

# Show chat
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Ask..."):
    # Add user message
    current_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        # Simple response (no streaming animation)
        response = ai_assistant.send_message(prompt, st.session_state.selected)
        st.write(response)
        current_messages.append({"role": "assistant", "content": response})