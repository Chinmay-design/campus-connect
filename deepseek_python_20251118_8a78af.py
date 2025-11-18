import streamlit as st
import json
import uuid
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Campus Connect Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modules
from auth import login_page, logout
from database import (
    load_data, save_data, get_user_by_email, create_user,
    get_clubs, get_events, get_marketplace_items,
    get_confessions, get_chats, initialize_sample_data
)
from pages.home import home_page
from pages.clubs import clubs_page
from pages.events import events_page
from pages.marketplace import marketplace_page
from pages.confessions import confessions_page
from pages.chat import chat_page
from pages.admin import admin_page
from pages.profile import profile_page

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "Home Feed"
    if 'privacy_consent' not in st.session_state:
        st.session_state.privacy_consent = False
    
    # Initialize sample data
    initialize_sample_data()
    
    # Check if user is logged in
    if not st.session_state.user:
        login_page()
    else:
        # Check privacy consent for chat features
        if st.session_state.page == "Chat" and not st.session_state.privacy_consent:
            show_privacy_consent()
        else:
            main_app()

def show_privacy_consent():
    """Show privacy consent before accessing chat"""
    st.title("🔒 Privacy Consent Required")
    st.warning("""
    **Before accessing chat features, please read and accept our privacy policy:**
    
    **Your privacy matters:**
    - Private messages are encrypted and secure
    - Admins only access messages for moderation when reported
    - All admin access is logged and audited
    - You can delete your messages anytime
    - Your data is never shared with third parties
    
    **By continuing, you agree to these terms.**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ I Understand & Accept", use_container_width=True):
            st.session_state.privacy_consent = True
            st.rerun()
    
    with col2:
        if st.button("🚫 Go Back", use_container_width=True):
            st.session_state.page = "Home Feed"
            st.rerun()

def main_app():
    """Main application after login"""
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3710/3710275.png", width=80)
        st.write(f"**Welcome, {st.session_state.user['name']}!**")
        st.write(f"🎓 {st.session_state.user.get('year', 'Student')}")
        st.write(f"📧 {st.session_state.user['email']}")
        
        # Privacy consent status
        if st.session_state.privacy_consent:
            st.success("🔒 Privacy Accepted")
        else:
            st.warning("⚠️ Privacy Pending")
        
        st.divider()
        
        # Navigation
        menu_options = [
            "🏠 Home Feed",
            "👥 Clubs & Communities", 
            "📅 Events",
            "🛒 Marketplace",
            "🗣️ Confessions",
            "💬 Chat",
            "👤 My Profile"
        ]
        
        # Add admin option if user is admin
        if st.session_state.user.get('role') == 'admin':
            menu_options.append("⚡ Admin Dashboard")
        
        selected_menu = st.radio("Navigate to:", menu_options)
        
        # Extract page name from emoji
        st.session_state.page = selected_menu.split(" ", 1)[1]
        
        st.divider()
        
        # Quick actions
        st.write("**Quick Actions**")
        if st.button("📢 Create Post", use_container_width=True):
            st.session_state.show_create_post = True
            
        if st.button("🔍 Find Friends", use_container_width=True):
            st.session_state.page = "Clubs & Communities"
            
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
    
    # Route to appropriate page
    if st.session_state.page == "Home Feed":
        home_page()
    elif st.session_state.page == "Clubs & Communities":
        clubs_page()
    elif st.session_state.page == "Events":
        events_page()
    elif st.session_state.page == "Marketplace":
        marketplace_page()
    elif st.session_state.page == "Confessions":
        confessions_page()
    elif st.session_state.page == "Chat":
        chat_page()
    elif st.session_state.page == "Admin Dashboard":
        admin_page()
    elif st.session_state.page == "My Profile":
        profile_page()

if __name__ == "__main__":
    main()