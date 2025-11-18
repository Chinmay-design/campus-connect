import streamlit as st
from datetime import datetime
from database import load_data, save_data, get_user_by_id

def home_page():
    """Home feed with announcements and activity"""
    
    st.title("🏠 Home Feed")
    st.subheader("Latest from your campus community")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        clubs = load_data('clubs')
        st.metric("Active Clubs", len(clubs))
    
    with col2:
        events = load_data('events')
        st.metric("Upcoming Events", len(events))
    
    with col3:
        marketplace = load_data('marketplace')
        st.metric("Marketplace Items", len(marketplace))
    
    with col4:
        users = load_data('users')
        st.metric("Campus Members", len(users))
    
    st.divider()
    
    # Create new post
    with st.expander("📢 Create Announcement", expanded=False):
        if st.session_state.user.get('role') in ['admin', 'club_admin']:
            create_announcement_form()
        else:
            st.info("💡 Only admins and club leaders can create announcements")
    
    # Feed content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_announcements_feed()
    
    with col2:
        display_upcoming_events()
        display_active_clubs()

def create_announcement_form():
    """Form to create new announcement"""
    with st.form("announcement_form"):
        title = st.text_input("Announcement Title")
        content = st.text_area("Content", height=100)
        announcement_type = st.selectbox("Type", ["College", "Club", "Event"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        if st.form_submit_button("📤 Post Announcement"):
            if title and content:
                announcements = load_data('announcements')
                
                new_announcement = {
                    'id': f"announce_{len(announcements) + 1}",
                    'title': title,
                    'content': content,
                    'author': st.session_state.user['name'],
                    'author_id': st.session_state.user['id'],
                    'type': announcement_type.lower(),
                    'priority': priority.lower(),
                    'timestamp': datetime.now().isoformat()
                }
                
                announcements.append(new_announcement)
                save_data('announcements', announcements)
                st.success("🎉 Announcement posted successfully!")
                st.rerun()

def display_announcements_feed():
    """Display announcements feed"""
    st.subheader("📢 Campus Announcements")
    
    announcements = load_data('announcements')
    
    if not announcements:
        st.info("No announcements yet. Be the first to post!")
        return
    
    for announcement in sorted(announcements, 
                             key=lambda x: x['timestamp'], 
                             reverse=True):
        with st.container():
            # Priority indicator
            priority = announcement.get('priority', 'medium')
            priority_color = {
                'high': '🔴',
                'medium': '🟡', 
                'low': '🟢'
            }.get(priority, '🟡')
            
            col1, col2 = st.columns([1, 20])
            
            with col1:
                emoji = "🎓" if announcement['type'] == 'college' else "👥" if announcement['type'] == 'club' else "📅"
                st.write(f"{emoji} {priority_color}")
            
            with col2:
                st.write(f"**{announcement['title']}**")
                st.write(announcement['content'])
                st.caption(f"By {announcement['author']} • {format_timestamp(announcement['timestamp'])}")
            
            st.divider()

def display_upcoming_events():
    """Display upcoming events sidebar"""
    st.subheader("📅 Upcoming Events")
    
    events = load_data('events')
    upcoming_events = []
    
    for event_id, event in events.items():
        if 'date' in event:
            try:
                event_date = datetime.fromisoformat(event['date'])
                if event_date >= datetime.now():
                    upcoming_events.append(event)
            except:
                upcoming_events.append(event)
    
    if not upcoming_events:
        st.info("No upcoming events")
        return
    
    for event in sorted(upcoming_events, key=lambda x: x.get('date', ''))[:3]:
        with st.container():
            st.write(f"**{event['title']}**")
            st.caption(f"📅 {format_date(event.get('date', 'TBA'))}")
            st.caption(f"📍 {event.get('location', 'TBA')}")
            st.caption(f"👥 {len(event.get('rsvps', []))} attending")
            
            if st.button("View Details", key=f"event_{event['id']}"):
                st.session_state.view_event = event['id']
                st.session_state.page = "Events"
            
            st.divider()

def display_active_clubs():
    """Display active clubs sidebar"""
    st.subheader("👥 Active Clubs")
    
    clubs = load_data('clubs')
    
    if not clubs:
        st.info("No clubs yet. Create the first one!")
        return
    
    for club_id, club in list(clubs.items())[:3]:
        with st.container():
            st.write(f"**{club['name']}**")
            st.caption(f"👥 {len(club.get('members', []))} members")
            st.caption(f"📅 {club.get('meeting_schedule', 'Schedule TBA')}")
            
            user_member = st.session_state.user['id'] in club.get('members', [])
            
            if user_member:
                st.success("✅ Joined")
            else:
                if st.button("Join Club", key=f"club_{club_id}"):
                    join_club(club_id)
            
            st.divider()

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return timestamp

def format_date(date_str):
    """Format date for display"""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

def join_club(club_id):
    """Join a club"""
    clubs = load_data('clubs')
    
    if club_id in clubs:
        club = clubs[club_id]
        user_id = st.session_state.user['id']
        
        if user_id not in club.get('members', []):
            club['members'] = club.get('members', []) + [user_id]
            clubs[club_id] = club
            save_data('clubs', clubs)
            st.success(f"🎉 Joined {club['name']}!")
            st.rerun()