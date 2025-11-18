import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta

# In-memory storage for MVP
DATA_STORE = {
    'users': {},
    'clubs': {},
    'events': {},
    'marketplace': {},
    'confessions': {},
    'chats': {},
    'announcements': [],
    'reports': [],
    'admin_logs': []
}

def load_data(data_type):
    """Load data from storage"""
    return DATA_STORE.get(data_type, {})

def save_data(data_type, data):
    """Save data to storage"""
    DATA_STORE[data_type] = data
    return True

def get_user_by_email(email):
    """Get user by email"""
    users = load_data('users')
    for user_id, user_data in users.items():
        if user_data.get('email', '').lower() == email.lower():
            return user_data
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    users = load_data('users')
    return users.get(user_id)

def create_user(user_data):
    """Create new user"""
    users = load_data('users')
    users[user_data['id']] = user_data
    return save_data('users', users)

def get_clubs():
    """Get all clubs"""
    return load_data('clubs')

def get_events():
    """Get all events"""
    return load_data('events')

def get_marketplace_items():
    """Get all marketplace items"""
    return load_data('marketplace')

def get_confessions():
    """Get all confessions"""
    return load_data('confessions')

def get_chats():
    """Get all chats"""
    return load_data('chats')

def log_admin_action(user_id, action, target_type=None, target_id=None):
    """Log admin actions for audit trail"""
    logs = load_data('admin_logs')
    logs.append({
        'admin_id': user_id,
        'action': action,
        'target_type': target_type,
        'target_id': target_id,
        'timestamp': datetime.now().isoformat(),
        'ip_address': '127.0.0.1'  # In production, get real IP
    })
    save_data('admin_logs', logs)

# Initialize sample data
def initialize_sample_data():
    """Initialize with sample data for demo"""
    if not DATA_STORE['clubs']:
        sample_clubs = {
            'cs_club': {
                'id': 'cs_club',
                'name': 'Computer Science Club',
                'description': 'For students interested in programming, AI, web development, and technology. Join us for hackathons, workshops, and coding sessions!',
                'members': [],
                'admins': [],
                'created_at': datetime.now().isoformat(),
                'tags': ['programming', 'technology', 'coding', 'AI', 'webdev'],
                'meeting_schedule': 'Every Wednesday 6-8 PM',
                'location': 'Tech Building Room 301'
            },
            'debate_club': {
                'id': 'debate_club', 
                'name': 'Debate Society',
                'description': 'Sharpen your public speaking, critical thinking, and argumentation skills. Participate in tournaments and weekly debates.',
                'members': [],
                'admins': [],
                'created_at': datetime.now().isoformat(),
                'tags': ['public speaking', 'debate', 'politics', 'critical thinking'],
                'meeting_schedule': 'Fridays 4-6 PM',
                'location': 'Humanities Building Room 204'
            },
            'music_club': {
                'id': 'music_club',
                'name': 'Music & Arts Club',
                'description': 'For musicians, singers, and music lovers. Jam sessions, performances, and collaborative projects.',
                'members': [],
                'admins': [],
                'created_at': datetime.now().isoformat(),
                'tags': ['music', 'arts', 'performance', 'singing'],
                'meeting_schedule': 'Tuesdays 7-9 PM',
                'location': 'Arts Center Room 101'
            }
        }
        DATA_STORE['clubs'] = sample_clubs
    
    if not DATA_STORE['announcements']:
        sample_announcements = [
            {
                'id': 'announce_1',
                'title': 'Welcome to Campus Connect! 🎉',
                'content': 'Welcome to our new campus community platform! This is your space to connect with fellow students, join clubs, participate in events, and build your campus network. Get started by exploring clubs or creating your first post!',
                'author': 'Campus Admin',
                'author_id': 'system',
                'type': 'college',
                'timestamp': datetime.now().isoformat(),
                'priority': 'high'
            },
            {
                'id': 'announce_2', 
                'title': 'Annual Hackathon 2024 - Registrations Open!',
                'content': 'Get ready for the biggest coding event of the year! Form teams of 2-4 and showcase your skills. Prizes include $5000 cash, internships, and tech gadgets. Register by November 30th.',
                'author': 'CS Club',
                'author_id': 'cs_club',
                'type': 'club',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'priority': 'medium'
            },
            {
                'id': 'announce_3',
                'title': 'Campus Winter Festival - Volunteers Needed',
                'content': 'Help us make this years winter festival unforgettable! We need volunteers for setup, coordination, and activities. Sign up for shifts and get community service hours.',
                'author': 'Student Affairs',
                'author_id': 'system',
                'type': 'event',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'priority': 'medium'
            }
        ]
        DATA_STORE['announcements'] = sample_announcements
    
    if not DATA_STORE['events']:
        sample_events = {
            'event_1': {
                'id': 'event_1',
                'title': 'Welcome Party for New Students 🎊',
                'description': 'Kick off the semester with food, games, and music! Meet your fellow students, learn about campus clubs, and win awesome prizes. All students welcome!',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'time': '18:00',
                'location': 'Student Center Main Hall',
                'club_id': 'system',
                'created_by': 'system',
                'rsvps': [],
                'max_attendees': 200,
                'created_at': datetime.now().isoformat(),
                'tags': ['social', 'welcome', 'party'],
                'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400'
            },
            'event_2': {
                'id': 'event_2',
                'title': 'CS Club: Intro to Python Workshop 🐍',
                'description': 'Perfect for beginners! Learn Python basics with hands-on exercises. Bring your laptop and we\'ll help you set up your development environment. No prior experience needed.',
                'date': (datetime.now() + timedelta(days=14)).isoformat(),
                'time': '16:00',
                'location': 'Computer Lab B, Tech Building',
                'club_id': 'cs_club',
                'created_by': 'cs_club',
                'rsvps': [],
                'max_attendees': 30,
                'created_at': datetime.now().isoformat(),
                'tags': ['workshop', 'programming', 'python', 'beginner'],
                'image_url': 'https://images.unsplash.com/photo-1526379879527-8559ecfcaec0?w=400'
            },
            'event_3': {
                'id': 'event_3',
                'title': 'Debate Tournament: Climate Change Solutions',
                'description': 'Compete in our monthly debate tournament! Topic: "Resolved: Individual actions are more important than policy changes in addressing climate change." Open to all skill levels.',
                'date': (datetime.now() + timedelta(days=10)).isoformat(),
                'time': '14:00',
                'location': 'Auditorium A',
                'club_id': 'debate_club',
                'created_by': 'debate_club',
                'rsvps': [],
                'max_attendees': 50,
                'created_at': datetime.now().isoformat(),
                'tags': ['debate', 'competition', 'climate', 'politics'],
                'image_url': 'https://images.unsplash.com/photo-1551818255-e6e109cbcb0e?w=400'
            }
        }
        DATA_STORE['events'] = sample_events
    
    if not DATA_STORE['users']:
        # Add a sample admin user
        import bcrypt
        admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin_user = {
            'id': 'admin_1',
            'email': 'admin@university.edu',
            'name': 'Campus Administrator',
            'year': 'Graduate',
            'branch': 'Administration',
            'interests': ['Management', 'Student Affairs', 'Technology'],
            'password': admin_password,
            'is_verified': True,
            'joined_date': datetime.now().isoformat(),
            'role': 'admin',
            'last_login': datetime.now().isoformat()
        }
        DATA_STORE['users'] = {'admin_1': admin_user}