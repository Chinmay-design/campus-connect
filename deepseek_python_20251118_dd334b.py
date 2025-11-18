import streamlit as st
from datetime import datetime
from database import load_data, save_data

def profile_page():
    """User profile page"""
    st.title("👤 My Profile")
    
    user = st.session_state.user
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
        st.write(f"**Member since:** {format_date(user.get('joined_date', ''))}")
        st.write(f"**Last login:** {format_date(user.get('last_login', ''))}")
        
    with col2:
        st.subheader(user['name'])
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Year:** {user.get('year', 'Not specified')}")
        st.write(f"**Branch:** {user.get('branch', 'Not specified')}")
        st.write(f"**Interests:** {', '.join(user.get('interests', []))}")
        st.write(f"**Role:** {user.get('role', 'student').title()}")
    
    st.divider()
    
    # User activity stats
    display_user_activity()
    
    st.divider()
    
    # Edit profile
    with st.expander("✏️ Edit Profile", expanded=False):
        edit_profile_form()

def display_user_activity():
    """Display user activity statistics"""
    st.subheader("📊 My Activity")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        clubs = load_data('clubs')
        user_clubs = sum(1 for club in clubs.values() if st.session_state.user['id'] in club.get('members', []))
        st.metric("Clubs Joined", user_clubs)
    
    with col2:
        events = load_data('events')
        user_rsvps = sum(1 for event in events.values() if st.session_state.user['id'] in event.get('rsvps', []))
        st.metric("Events RSVP'd", user_rsvps)
    
    with col3:
        marketplace = load_data('marketplace')
        user_listings = sum(1 for listing in marketplace.values() if listing.get('seller_id') == st.session_state.user['id'])
        st.metric("Listings", user_listings)
    
    with col4:
        confessions = load_data('confessions')
        user_confessions = sum(1 for conf in confessions.values() if conf.get('status') == 'approved')
        st.metric("Confessions", user_confessions)

def edit_profile_form():
    """Form to edit user profile"""
    user = st.session_state.user
    
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Name", value=user['name'])
            new_year = st.selectbox("Year", 
                                  ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"],
                                  index=["Freshman", "Sophomore", "Junior", "Senior", "Graduate"].index(user.get('year', 'Freshman')))
        
        with col2:
            new_branch = st.text_input("Branch", value=user.get('branch', ''))
            new_interests = st.multiselect("Interests", [
                "Programming", "AI/ML", "Web Development", "Data Science",
                "Engineering", "Business", "Arts", "Sports", "Music",
                "Dance", "Photography", "Writing", "Research", "Gaming"
            ], default=user.get('interests', []))
        
        if st.form_submit_button("💾 Update Profile"):
            # Update user data
            user['name'] = new_name.strip()
            user['year'] = new_year
            user['branch'] = new_branch.strip()
            user['interests'] = new_interests
            
            # Save to database
            users = load_data('users')
            users[user['id']] = user
            save_data('users', users)
            
            # Update session state
            st.session_state.user = user
            
            st.success("✅ Profile updated successfully!")
            st.rerun()

def format_date(date_str):
    """Format date for display"""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%B %d, %Y")
    except:
        return "Unknown"