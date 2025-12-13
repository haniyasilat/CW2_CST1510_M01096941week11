from openai import OpenAI
import streamlit as st
from typing import List, Dict 
class AIAssistant:
    """Handles AI chat for diffienrt expert domains."""
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self._history: List[Dict[str, str]] = []  # ✅ INITIALIZE HISTORY
        self._system_prompt = "You are a helpful assistant."
        self.assistants={
            "Cybersecurity": {
                "prompt": "You are a cybersecurity expert. Analyze incidents, threats, and"
                " vulnerabilities. Provide technical guidance using MITRE ATT&CK, CVE "
                "references. Prioritize actionable recommendations.",
            },
            "Data Science":{
                "prompt":
                "You are a data science expert. Help with data"
                " analysis, visualization, statistical methods, and machine learning."
                " Explain concepts clearly and suggest appropriate techniques.",},
            "IT Operations": {
                "prompt": "You are an IT operations expert. Help troubleshoot issues,"
                " optimize systems, manage tasks, and provide infrastructure guidance."
                " Focus on practical solutions.",}
        }
    def get_assistant_prompt(self, domain: str) -> str:
        """get system prompt for specific domain"""
        return self.assistants.get(domain, {}).get("prompt", self._system_prompt)
    def send_message(self, user_message: str, domain: str = "Cybersecurity"): 
        """Send a message and yield AI response chunks for streaming"""
    # Add user message to history
        self._history.append({"role": "user", "content": user_message})
    
    # Get response for specific domain
        system_prompt = self.get_assistant_prompt(domain)
        full_messages = [{"role": "system", "content": system_prompt}] + self._history
    
    # Create streaming request
        stream = self.client.chat.completions.create(
        model="gpt-4.1-nano",  # Make sure this is a valid model name
        messages=full_messages,
        stream=True
)
    
    # Stream response word by word
        full_response = ""
        for chunk in stream:
         if chunk.choices[0].delta.content:
                word = chunk.choices[0].delta.content
                full_response += word
                yield word  # ← YIELD each chunk instead of just collecting
    
    # Store complete response in history
        self._history.append({"role": "assistant", "content": full_response})
    def clear_history(self):
        self._history.clear()