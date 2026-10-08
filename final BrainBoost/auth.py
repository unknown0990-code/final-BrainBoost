import streamlit as st
import hashlib
from database import register_user, get_user

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_auth_page():
    st.markdown('<div class="brand-header">BrainBoost Test</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Challenge Your Mind • Improve Your Knowledge • Track Your Progress</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Admin Login"])
    
    # LOGIN TAB
    with tab1:
        st.subheader("Student Login")
        log_user = st.text_input("Username", key="log_user")
        log_pass = st.text_input("Password", type="password", key="log_pass")
        
        if st.button("Login", use_container_width=True):
            if log_user and log_pass:
                user = get_user(log_user)
                if user:
                    hashed_pass = hash_password(log_pass)
                    if user[4] == hashed_pass:
                        st.session_state.logged_in = True
                        st.session_state.username = user[2]
                        st.session_state.name = user[1]
                        st.session_state.is_admin = False
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect Password.")
                else:
                    st.error("Username does not exist.")
            else:
                st.warning("Please fill out all fields.")
                
    # REGISTER TAB
    with tab2:
        st.subheader("New Student Registration")
        reg_name = st.text_input("Full Name")
        reg_user = st.text_input("Choose Username")
        reg_phone = st.text_input("Phone Number")
        reg_pass = st.text_input("Create Password", type="password")
        reg_pass_conf = st.text_input("Confirm Password", type="password")
        
        if st.button("Register", use_container_width=True):
            if reg_name and reg_user and reg_phone and reg_pass and reg_pass_conf:
                if reg_pass == reg_pass_conf:
                    hashed_pass = hash_password(reg_pass)
                    success = register_user(reg_name, reg_user, reg_phone, hashed_pass)
                    if success:
                        st.success("Registration successful! You can now login.")
                    else:
                        st.error("Username already exists. Please choose another one.")
                else:
                    st.error("Passwords do not match.")
            else:
                st.warning("Please fill all required fields.")

    # ADMIN LOGIN TAB
    with tab3:
        st.subheader("Administrator sign in")
        admin_user = st.text_input(" Username")
        admin_pass = st.text_input(" Password", type="password")
        
        if st.button(" Login", use_container_width=True):
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.logged_in = True
                st.session_state.username = "Admin"
                st.session_state.is_admin = True
                st.success("Admin Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Admin Credentials.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.is_admin = False
    # Clear test states
    for key in ['test_started', 'current_q_index', 'test_questions', 'user_answers', 'test_submitted', 'test_score']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()