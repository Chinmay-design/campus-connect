import streamlit as st
import uuid
from datetime import datetime
from database import load_data, save_data, get_user_by_id

def clubs_page():
    """Clubs and communities page"""
    st.title("👥 Clubs & Communities")
    st.write("Join clubs and connect with students who share your interests!")
    
    # Create new club
    with st.expander("➕ Create New Club", expanded=False):
        create_club_form()
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search clubs...", placeholder="Search by name or tags")
    
    with col2:
        filter_tag = st.selectbox("Filter by tag", ["All"] + get_all_club_tags())
    
    # Display clubs
    display_clubs_grid(search_query, filter_tag)

def create_club_form():
    """Form to create new club"""
    with st.form("create_club_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Club Name")
            meeting_schedule = st.text_input("Meeting Schedule", placeholder="e.g., Wednesdays 6-8 PM")
            location = st.text_input("Meeting Location")
        
        with col2:
            tags = st.multiselect("Tags", [
                "Programming", "Technology", "Arts", "Sports", "Music", 
                "Debate", "Academic", "Social", "Cultural", "Gaming"
            ])
            max_members = st.number_input("Max Members", min_value=5, max_value=500, value=50)
        
        description = st.text_area("Club Description", height=100, 
                                 placeholder="Describe your club's purpose, activities, and who should join...")
        
        if st.form_submit_button("Create Club"):
            if name and description:
                clubs = load_data('clubs')
                club_id = f"club_{str(uuid.uuid4())[:8]}"
                
                new_club = {
                    'id': club_id,
                    'name': name,
                    'description': description,
                    'members': [st.session_state.user['id']],
                    'admins': [st.session_state.user['id']],
                    'tags': tags,
                    'meeting_schedule': meeting_schedule,
                    'location': location,
                    'max_members': max_members,
                    'created_at': datetime.now().isoformat(),
                    'created_by': st.session_state.user['id']
                }
                
                clubs[club_id] = new_club
                save_data('clubs', clubs)
                st.success(f"🎉 Club '{name}' created successfully!")
                st.rerun()
            else:
                st.error("Please fill in club name and description")

def get_all_club_tags():
    """Get all unique tags from clubs"""
    clubs = load_data('clubs')
    all_tags = set()
    for club in clubs.values():
        all_tags.update(club.get('tags', []))
    return sorted(list(all_tags))

def display_clubs_grid(search_query, filter_tag):
    """Display clubs in a grid layout"""
    clubs = load_data('clubs')
    
    if not clubs:
        st.info("No clubs found. Be the first to create a club!")
        return
    
    # Filter clubs
    filtered_clubs = {}
    for club_id, club in clubs.items():
        # Search filter
        if search_query:
            search_lower = search_query.lower()
            name_match = search_lower in club['name'].lower()
            desc_match = search_lower in club.get('description', '').lower()
            tag_match = any(search_lower in tag.lower() for tag in club.get('tags', []))
            if not (name_match or desc_match or tag_match):
                continue
        
        # Tag filter
        if filter_tag != "All" and filter_tag not in club.get('tags', []):
            continue
            
        filtered_clubs[club_id] = club
    
    if not filtered_clubs:
        st.warning("No clubs match your search criteria.")
        return
    
    # Display clubs in columns
    clubs_list = list(filtered_clubs.values())
    
    for i in range(0, len(clubs_list), 2):
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(clubs_list):
                club = clubs_list[i + j]
                with cols[j]:
                    display_club_card(club)

def display_club_card(club):
    """Display a single club card"""
    with st.container():
        st.subheader(club['name'])
        
        # Tags
        tags = club.get('tags', [])
        if tags:
            st.write(" ".join([f"`{tag}`" for tag in tags[:3]]))
        
        # Description
        st.write(club['description'][:150] + "..." if len(club.get('description', '')) > 150 else club.get('description', ''))
        
        # Club info
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"👥 {len(club.get('members', []))} members")
        with col2:
            st.caption(f"📅 {club.get('meeting_schedule', 'TBA')}")
        
        # Join/Leave button
        user_member = st.session_state.user['id'] in club.get('members', [])
        
        if user_member:
            if st.button("✅ Joined", key=f"joined_{club['id']}", disabled=True):
                pass
            if st.button("🚪 Leave", key=f"leave_{club['id']}"):
                leave_club(club['id'])
        else:
            if st.button("➕ Join Club", key=f"join_{club['id']}"):
                join_club(club['id'])
        
        st.divider()

def join_club(club_id):
    """Join a club"""
    clubs = load_data('clubs')
    
    if club_id in clubs:
        club = clubs[club_id]
        user_id = st.session_state.user['id']
        
        if user_id not in club.get('members', []):
            current_members = len(club.get('members', []))
            max_members = club.get('max_members', 50)
            
            if current_members >= max_members:
                st.error("❌ Club is full!")
                return
                
            club['members'] = club.get('members', []) + [user_id]
            clubs[club_id] = club
            save_data('clubs', clubs)
            st.success(f"🎉 Joined {club['name']}!")
            st.rerun()

def leave_club(club_id):
    """Leave a club"""
    clubs = load_data('clubs')
    
    if club_id in clubs:
        club = clubs[club_id]
        user_id = st.session_state.user['id']
        
        if user_id in club.get('members', []):
            club['members'] = [m for m in club.get('members', []) if m != user_id]
            
            # Remove from admins if they were one
            if user_id in club.get('admins', []):
                club['admins'] = [a for a in club.get('admins', []) if a != user_id]
            
            clubs[club_id] = club
            save_data('clubs', clubs)
            st.success(f"👋 Left {club['name']}")
            st.rerun()