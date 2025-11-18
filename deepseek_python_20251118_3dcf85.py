import streamlit as st
import re
import uuid
import bcrypt
from datetime import datetime
from database import get_user_by_email, create_user, load_data, save_data

def login_page():
    """Display login/signup page"""
    
    st.title("🎓 Campus Connect Hub")
    st.subheader("Your College Community Platform")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        login_form()
    
    with tab2:
        signup_form()

def login_form():
    """Login form"""
    with st.form("login_form"):
        email = st.text_input("📧 College Email")
        password = st.text_input("🔑 Password", type="password")
        
        if st.form_submit_button("Login", use_container_width=True):
            if authenticate_user(email, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password")

def signup_form():
    """Signup form for new students"""
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("📧 College Email", placeholder="john@university.edu")
            year = st.selectbox("Academic Year", 
                              ["", "Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
        
        with col2:
            branch = st.text_input("Major/Branch", placeholder="Computer Science")
            password = st.text_input("🔑 Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        interests = st.multiselect("Interests (max 5)", [
            "Programming", "AI/ML", "Web Development", "Data Science",
            "Engineering", "Business", "Arts", "Sports", "Music",
            "Dance", "Photography", "Writing", "Research", "Gaming"
        ], max_selections=5)
        
        # Privacy agreement
        privacy_agreed = st.checkbox("I agree to the privacy policy and terms of service")
        
        if st.form_submit_button("Create Account", use_container_width=True):
            # Validation
            errors = []
            
            if not name:
                errors.append("Please enter your name")
            if not is_college_email(email):
                errors.append("Please use your college email address")
            if password != confirm_password:
                errors.append("Passwords do not match")
            if len(password) < 6:
                errors.append("Password must be at least 6 characters")
            if not year:
                errors.append("Please select your academic year")
            if not branch:
                errors.append("Please enter your major/branch")
            if not privacy_agreed:
                errors.append("You must agree to the privacy policy")
            if get_user_by_email(email):
                errors.append("An account with this email already exists")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create user
                user_data = {
                    "id": str(uuid.uuid4()),
                    "email": email.lower().strip(),
                    "name": name.strip(),
                    "year": year,
                    "branch": branch.strip(),
                    "interests": interests,
                    "password": hash_password(password),  # ✅ SECURE - hashed password
                    "is_verified": True,
                    "joined_date": datetime.now().isoformat(),
                    "role": "student",
                    "last_login": datetime.now().isoformat()
                }
                
                if create_user(user_data):
                    st.session_state.user = user_data
                    st.session_state.privacy_consent = True
                    st.success("Account created successfully! 🎉")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create account")

def hash_password(password):
    """Hash a password for secure storage"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a stored password against one provided by user"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

def is_college_email(email):
    """Basic college email validation"""
    if not email or "@" not in email:
        return False
    college_domains = [".edu", ".ac.", "college", "university"]
    email_domain = email.lower().split("@")[1]
    return any(domain in email_domain for domain in college_domains)

def authenticate_user(email, password):
    """Authenticate user credentials"""
    user = get_user_by_email(email)
    if user and verify_password(password, user.get('password', '')):
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        users = load_data('users')
        users[user['id']] = user
        save_data('users', users)
        
        st.session_state.user = user
        return True
    return False

def logout():
    """Logout user"""
    st.session_state.user = None
    st.session_state.page = "Home Feed"
    st.session_state.privacy_consent = False
    st.rerun()