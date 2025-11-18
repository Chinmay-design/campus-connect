import streamlit as st
import uuid
from datetime import datetime
from database import load_data, save_data

def confessions_page():
    """Confessions page"""
    st.title("🗣️ Anonymous Confessions")
    st.write("Share your thoughts anonymously! All posts are moderated.")
    
    # Privacy notice
    st.info("""
    🔒 **Your privacy is protected:**
    - Posts are completely anonymous
    - No user information is stored with confessions
    - Moderators review content before publishing
    - Be respectful and follow community guidelines
    """)
    
    # Create confession
    with st.expander("✍️ Write a Confession", expanded=False):
        create_confession_form()
    
    # Display confessions
    display_confessions_feed()

def create_confession_form():
    """Form to create anonymous confession"""
    with st.form("confession_form"):
        content = st.text_area("Your Confession", height=120,
                             placeholder="Share your thoughts, experiences, or feelings...",
                             help="Be respectful and mindful of others. No hate speech or harassment.")
        
        category = st.selectbox("Category", 
                              ["General", "Love & Relationships", "Academic", "Social", "Funny", "Advice"])
        
        # Community guidelines
        st.checkbox("I agree to follow community guidelines", key="guidelines_agreed")
        
        if st.form_submit_button("Submit Confession"):
            if content and st.session_state.guidelines_agreed:
                if len(content.strip()) < 10:
                    st.error("Please write at least 10 characters")
                elif len(content) > 1000:
                    st.error("Confession too long (max 1000 characters)")
                else:
                    submit_confession(content, category)
            else:
                st.error("Please agree to community guidelines and write a confession")

def submit_confession(content, category):
    """Submit a new confession for moderation"""
    confessions = load_data('confessions')
    confession_id = f"confess_{str(uuid.uuid4())[:8]}"
    
    new_confession = {
        'id': confession_id,
        'content': content.strip(),
        'category': category,
        'status': 'pending',  # Needs moderation
        'upvotes': 0,
        'downvotes': 0,
        'reports': 0,
        'comments': [],
        'created_at': datetime.now().isoformat(),
        'approved_at': None,
        'approved_by': None
    }
    
    confessions[confession_id] = new_confession
    save_data('confessions', confessions)
    st.success("""
    📝 Confession submitted for moderation!
    It will be reviewed by moderators before appearing publicly.
    """)
    st.rerun()

def display_confessions_feed():
    """Display approved confessions"""
    confessions = load_data('confessions')
    
    # Filter approved confessions
    approved_confessions = [
        conf for conf in confessions.values() 
        if conf.get('status') == 'approved'
    ]
    
    if not approved_confessions:
        st.info("""
        No confessions yet. Be the first to share!
        
        💡 **Confession ideas:**
        - Something funny that happened in class
        - Advice you wish you had earlier
        - Appreciation for someone on campus
        - Thoughts about college life
        """)
        return
    
    # Sort by engagement (upvotes - downvotes)
    approved_confessions.sort(key=lambda x: (x.get('upvotes', 0) - x.get('downvotes', 0)), reverse=True)
    
    # Category filter
    categories = list(set(conf.get('category', 'General') for conf in approved_confessions))
    selected_category = st.selectbox("Filter by category", ["All"] + sorted(categories))
    
    if selected_category != "All":
        approved_confessions = [conf for conf in approved_confessions if conf.get('category') == selected_category]
    
    # Display confessions
    for confession in approved_confessions:
        display_confession_card(confession)

def display_confession_card(confession):
    """Display a single confession card"""
    with st.container():
        # Header with category and engagement
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.caption(f"#{confession.get('category', 'General')}")
        
        with col2:
            score = confession.get('upvotes', 0) - confession.get('downvotes', 0)
            st.caption(f"❤️ {score}")
        
        # Confession content
        st.write(confession['content'])
        
        # Engagement buttons
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        
        with col1:
            if st.button("👍", key=f"up_{confession['id']}"):
                vote_confession(confession['id'], 'upvote')
        
        with col2:
            if st.button("👎", key=f"down_{confession['id']}"):
                vote_confession(confession['id'], 'downvote')
        
        with col3:
            if st.button("💬 Comment", key=f"comment_{confession['id']}"):
                st.session_state.show_comments = confession['id']
        
        with col4:
            if st.button("🚩 Report", key=f"report_{confession['id']}"):
                report_confession(confession['id'])
        
        # Comments section
        if st.session_state.get('show_comments') == confession['id']:
            display_comments(confession)
        
        st.divider()

def vote_confession(confession_id, vote_type):
    """Vote on a confession"""
    confessions = load_data('confessions')
    
    if confession_id in confessions:
        if vote_type == 'upvote':
            confessions[confession_id]['upvotes'] = confessions[confession_id].get('upvotes', 0) + 1
        else:
            confessions[confession_id]['downvotes'] = confessions[confession_id].get('downvotes', 0) + 1
        
        save_data('confessions', confessions)
        st.rerun()

def report_confession(confession_id):
    """Report a confession"""
    reports = load_data('reports')
    
    new_report = {
        'id': str(uuid.uuid4()),
        'confession_id': confession_id,
        'reporter_id': st.session_state.user['id'],
        'reason': 'Inappropriate content',
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    reports.append(new_report)
    save_data('reports', reports)
    
    # Also increment report count on confession
    confessions = load_data('confessions')
    if confession_id in confessions:
        confessions[confession_id]['reports'] = confessions[confession_id].get('reports', 0) + 1
        save_data('confessions', confessions)
    
    st.success("🚩 Thank you for reporting. Moderators will review this content.")
    st.rerun()

def display_comments(confession):
    """Display comments for a confession"""
    st.write("---")
    st.write("**Comments:**")
    
    comments = confession.get('comments', [])
    
    if not comments:
        st.info("No comments yet. Be the first to comment!")
    
    for comment in comments:
        st.write(f"**Anonymous:** {comment['content']}")
        st.caption(f"Posted {format_timestamp(comment.get('timestamp', ''))}")
        st.divider()
    
    # Add comment form
    with st.form(f"comment_form_{confession['id']}"):
        new_comment = st.text_input("Add a comment...", placeholder="Keep it respectful!")
        if st.form_submit_button("Post Comment"):
            if new_comment.strip():
                add_comment(confession['id'], new_comment.strip())
            else:
                st.error("Please write a comment")

def add_comment(confession_id, content):
    """Add a comment to a confession"""
    confessions = load_data('confessions')
    
    if confession_id in confessions:
        new_comment = {
            'id': str(uuid.uuid4()),
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        confessions[confession_id]['comments'] = confessions[confession_id].get('comments', []) + [new_comment]
        save_data('confessions', confessions)
        st.rerun()

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%b %d, %Y")
    except:
        return "Unknown"