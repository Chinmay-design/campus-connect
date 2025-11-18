import streamlit as st
import uuid
from datetime import datetime, timedelta
from database import load_data, save_data, get_user_by_id

def events_page():
    """Events page"""
    st.title("📅 Campus Events")
    st.write("Discover and RSVP to upcoming events!")
    
    # Create new event
    with st.expander("➕ Create New Event", expanded=False):
        create_event_form()
    
    # View options
    view_option = st.radio("View:", ["Upcoming Events", "Past Events", "My RSVPs"], horizontal=True)
    
    # Display events based on selection
    if view_option == "Upcoming Events":
        display_upcoming_events()
    elif view_option == "Past Events":
        display_past_events()
    elif view_option == "My RSVPs":
        display_my_rsvps()

def create_event_form():
    """Form to create new event"""
    with st.form("create_event_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Event Title")
            date = st.date_input("Date", min_value=datetime.now().date())
            time = st.time_input("Time")
            location = st.text_input("Location")
        
        with col2:
            max_attendees = st.number_input("Max Attendees", min_value=1, max_value=1000, value=50)
            club_id = st.selectbox("Hosting Club", get_user_clubs_options())
            tags = st.multiselect("Tags", ["Social", "Academic", "Workshop", "Sports", "Cultural", "Networking"])
        
        description = st.text_area("Event Description", height=100,
                                 placeholder="Describe your event, what attendees can expect, and any requirements...")
        
        if st.form_submit_button("Create Event"):
            if title and description:
                events = load_data('events')
                event_id = f"event_{str(uuid.uuid4())[:8]}"
                
                # Combine date and time
                event_datetime = datetime.combine(date, time)
                
                new_event = {
                    'id': event_id,
                    'title': title,
                    'description': description,
                    'date': event_datetime.isoformat(),
                    'time': time.strftime("%H:%M"),
                    'location': location,
                    'max_attendees': max_attendees,
                    'club_id': club_id,
                    'created_by': st.session_state.user['id'],
                    'rsvps': [st.session_state.user['id']],  # Creator auto-RSVPs
                    'tags': tags,
                    'created_at': datetime.now().isoformat()
                }
                
                events[event_id] = new_event
                save_data('events', events)
                st.success(f"🎉 Event '{title}' created successfully!")
                st.rerun()
            else:
                st.error("Please fill in event title and description")

def get_user_clubs_options():
    """Get clubs the user can create events for"""
    clubs = load_data('clubs')
    user_clubs = []
    
    for club_id, club in clubs.items():
        user_id = st.session_state.user['id']
        if user_id in club.get('admins', []) or user_id in club.get('members', []):
            user_clubs.append(club_id)
    
    return user_clubs if user_clubs else ['personal']

def display_upcoming_events():
    """Display upcoming events"""
    events = load_data('events')
    upcoming_events = []
    
    for event in events.values():
        try:
            event_date = datetime.fromisoformat(event['date'])
            if event_date >= datetime.now():
                upcoming_events.append(event)
        except:
            pass
    
    if not upcoming_events:
        st.info("No upcoming events. Create the first one!")
        return
    
    # Sort by date
    upcoming_events.sort(key=lambda x: x.get('date', ''))
    
    for event in upcoming_events:
        display_event_card(event)

def display_past_events():
    """Display past events"""
    events = load_data('events')
    past_events = []
    
    for event in events.values():
        try:
            event_date = datetime.fromisoformat(event['date'])
            if event_date < datetime.now():
                past_events.append(event)
        except:
            pass
    
    if not past_events:
        st.info("No past events yet.")
        return
    
    # Sort by date (most recent first)
    past_events.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    for event in past_events:
        display_event_card(event, is_past=True)

def display_my_rsvps():
    """Display events user has RSVP'd to"""
    events = load_data('events')
    my_rsvps = []
    user_id = st.session_state.user['id']
    
    for event in events.values():
        if user_id in event.get('rsvps', []):
            my_rsvps.append(event)
    
    if not my_rsvps:
        st.info("You haven't RSVP'd to any events yet.")
        return
    
    # Sort by date
    my_rsvps.sort(key=lambda x: x.get('date', ''))
    
    for event in my_rsvps:
        display_event_card(event, show_rsvp_status=True)

def display_event_card(event, is_past=False, show_rsvp_status=False):
    """Display a single event card"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(event['title'])
            
            # Event details
            try:
                event_date = datetime.fromisoformat(event['date'])
                date_str = event_date.strftime("%b %d, %Y at %I:%M %p")
            except:
                date_str = "Date TBA"
            
            st.write(f"**📅 When:** {date_str}")
            st.write(f"**📍 Where:** {event.get('location', 'TBA')}")
            
            # Tags
            tags = event.get('tags', [])
            if tags:
                st.write(" ".join([f"`{tag}`" for tag in tags]))
            
            # Description preview
            desc = event.get('description', '')
            if len(desc) > 150:
                st.write(desc[:150] + "...")
            else:
                st.write(desc)
        
        with col2:
            # RSVP info
            rsvp_count = len(event.get('rsvps', []))
            max_attendees = event.get('max_attendees', 50)
            st.write(f"👥 {rsvp_count}/{max_attendees}")
            
            # RSVP button
            user_rsvped = st.session_state.user['id'] in event.get('rsvps', [])
            
            if is_past:
                st.info("🎉 Event ended")
            elif user_rsvped:
                if st.button("✅ Going", key=f"going_{event['id']}", disabled=True):
                    pass
                if st.button("❌ Cancel", key=f"cancel_{event['id']}"):
                    cancel_rsvp(event['id'])
            else:
                if rsvp_count >= max_attendees:
                    st.error("❌ Full")
                else:
                    if st.button("✋ RSVP", key=f"rsvp_{event['id']}"):
                        rsvp_to_event(event['id'])
            
            if show_rsvp_status and user_rsvped:
                st.success("✅ You're going!")
        
        st.divider()

def rsvp_to_event(event_id):
    """RSVP to an event"""
    events = load_data('events')
    
    if event_id in events:
        event = events[event_id]
        user_id = st.session_state.user['id']
        
        if user_id not in event.get('rsvps', []):
            if len(event.get('rsvps', [])) >= event.get('max_attendees', 50):
                st.error("❌ Event is full!")
                return
                
            event['rsvps'] = event.get('rsvps', []) + [user_id]
            events[event_id] = event
            save_data('events', events)
            st.success("🎉 You're going!")
            st.rerun()

def cancel_rsvp(event_id):
    """Cancel RSVP to an event"""
    events = load_data('events')
    
    if event_id in events:
        event = events[event_id]
        user_id = st.session_state.user['id']
        
        if user_id in event.get('rsvps', []):
            event['rsvps'] = [r for r in event.get('rsvps', []) if r != user_id]
            events[event_id] = event
            save_data('events', events)
            st.info("👋 RSVP cancelled")
            st.rerun()