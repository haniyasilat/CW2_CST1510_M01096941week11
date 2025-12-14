import streamlit as st
from services.auth_manager import AuthManager
from services.database_manager import DatabaseManager
import re
#create streamlit page metadata and alyout
st.set_page_config(
    page_title="Login/Register",
    page_icon="🔑",
    layout="wide"
)

# create database connection
#databasemanager manages SQLite operations
#AuthManager ahndles login, registration and role 
db = DatabaseManager("database/intelligence_platform.db")
auth = AuthManager(db)

#initialise session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
# Password strength checker, using regex
def check_password_strength(password):
    if len(password) < 8:
        return "❌ Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return "❌ Must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "❌ Must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "❌ Must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "⚠️ Consider adding a special character for extra security"
    return "✅ Strong password"

#when user is logged in
if st.session_state.logged_in:
    st.balloons()
    st.success(f"### ✅ Welcome back, {st.session_state.username}!")
    st.info(f"**Role:** {st.session_state.user_role.title()}")
    st.markdown("---")
    
    # Quick dashboard access, buttons that redirected to the selected dashboard
    st.markdown("#### 🚀 Quick Access")

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    
    st.markdown("---")
    
    # button for logout
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        del st.session_state.logged_in
        del st.session_state.username
        st.rerun()
    
    st.stop()

#create login page
st.title("Login or create an account")
#separte tabs for login and register
tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

with tab1:
    st.subheader("Existing User")
    
    login_username = st.text_input("Username", key="login_user")
    login_password = st.text_input("Password", type="password", key="login_pass")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        remember = st.checkbox("Remember me")
    
    if st.button("Login", type="primary", use_container_width=True):
        if not login_username or not login_password:
            #Basic input validation to avoid empty submissions
            st.error("Please enter both username and password")
        else: #authenticate user credentials via AuthManager
            user_data = auth.login_user_with_role(login_username, login_password)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                #store user role, deflauts to "user", if not defines
                st.session_state.user_role = user_data.get('role', 'user')
                st.success(f"✅ Login successful! Role: {st.session_state.user_role}")
                st.rerun()
            else: #error message if authentication fails
                st.error("Invalid credentials. Please try again.")

with tab2:
    st.subheader("New User")
    
    new_username = st.text_input("Choose username", key="reg_user")
    new_password = st.text_input("Password", type="password", key="reg_pass")
    confirm_password = st.text_input("Confirm password", type="password", key="reg_confirm")
    #options for roles
    user_role = st.selectbox(
        "Select your role",
        ["analyst", "researcher", "technician", "admin"],
        format_func=lambda x: x.title()
    )
    
    # Password strength indicator
    if new_password:
        strength = check_password_strength(new_password)
        if "✅" in strength:
            st.success(strength)
        elif "⚠️" in strength:
            st.warning(strength)
        else:
            st.error(strength)
    
    if st.button("Register", type="primary", use_container_width=True):
        if not new_username or not new_password:
            st.error("All fields are required")
        elif new_password != confirm_password:
            st.error("Passwords do not match")
        elif len(new_username) < 3:
            st.error("Username must be at least 3 characters")
        elif "❌" in check_password_strength(new_password):
            st.error("Password does not meet strength requirements")
        else:
            try:
                auth.register_user(new_username, new_password, user_role)
                st.balloons()
                st.success("🎉 Registration successful!")
                st.info("Switch to the Login tab to access your account")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")