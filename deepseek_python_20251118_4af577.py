import streamlit as st
from datetime import datetime
from database import load_data, save_data, log_admin_action, get_user_by_id

def admin_page():
    """Admin dashboard"""
    if st.session_state.user.get('role') != 'admin':
        st.error("🔒 Admin access required")
        st.stop()
    
    st.title("⚡ Admin Dashboard")
    st.warning("**RESTRICTED ACCESS** - All actions are logged and monitored")
    
    # Log admin access
    log_admin_action(st.session_state.user['id'], "accessed_admin_dashboard")
    
    # Admin tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "👥 User Management", 
        "🚩 Moderation", 
        "📢 Announcements",
        "📋 Logs"
    ])
    
    with tab1:
        admin_overview()
    
    with tab2:
        user_management()
    
    with tab3:
        content_moderation()
    
    with tab4:
        announcement_management()
    
    with tab5:
        view_admin_logs()

def admin_overview():
    """Admin overview dashboard"""
    st.subheader("Platform Overview")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users = load_data('users')
        st.metric("Total Users", len(users))
    
    with col2:
        clubs = load_data('clubs')
        st.metric("Active Clubs", len(clubs))
    
    with col3:
        events = load_data('events')
        st.metric("Upcoming Events", len(events))
    
    with col4:
        marketplace = load_data('marketplace')
        st.metric("Marketplace Items", len(marketplace))
    
    st.divider()
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Recent signups (last 7 days)
    recent_users = []
    for user in users.values():
        try:
            join_date = datetime.fromisoformat(user.get('joined_date', ''))
            if (datetime.now() - join_date).days <= 7:
                recent_users.append(user)
        except:
            pass
    
    st.write(f"**New users (last 7 days):** {len(recent_users)}")
    
    # Pending moderation
    confessions = load_data('confessions')
    pending_confessions = [c for c in confessions.values() if c.get('status') == 'pending']
    st.write(f"**Pending confessions:** {len(pending_confessions)}")
    
    reports = load_data('reports')
    pending_reports = [r for r in reports if r.get('status') == 'pending']
    st.write(f"**Pending reports:** {len(pending_reports)}")

def user_management():
    """User management section"""
    st.subheader("👥 User Management")
    
    users = load_data('users')
    
    if not users:
        st.info("No users found")
        return
    
    # User search
    search_query = st.text_input("🔍 Search users...")
    
    # Display users
    for user_id, user in users.items():
        if search_query and search_query.lower() not in user['name'].lower() and search_query.lower() not in user['email'].lower():
            continue
            
        with st.expander(f"👤 {user['name']} ({user['email']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Year:** {user.get('year', 'N/A')}")
                st.write(f"**Branch:** {user.get('branch', 'N/A')}")
                st.write(f"**Interests:** {', '.join(user.get('interests', []))}")
            
            with col2:
                st.write(f"**Role:** {user.get('role', 'student')}")
                st.write(f"**Joined:** {format_date(user.get('joined_date', ''))}")
                st.write(f"**Last Login:** {format_date(user.get('last_login', ''))}")
            
            # Admin actions
            if user_id != st.session_state.user['id']:  # Can't modify own account
                col1, col2 = st.columns(2)
                
                with col1:
                    if user.get('role') != 'admin':
                        if st.button("👑 Make Admin", key=f"admin_{user_id}"):
                            make_user_admin(user_id)
                    else:
                        if st.button("👤 Remove Admin", key=f"remove_admin_{user_id}"):
                            remove_user_admin(user_id)
                
                with col2:
                    if st.button("🚫 Ban User", key=f"ban_{user_id}", type="secondary"):
                        ban_user(user_id)

def content_moderation():
    """Content moderation section"""
    st.subheader("🚩 Content Moderation")
    
    # Pending confessions
    st.write("### Pending Confessions")
    confessions = load_data('confessions')
    pending_confessions = [c for c in confessions.values() if c.get('status') == 'pending']
    
    if not pending_confessions:
        st.success("✅ No pending confessions")
    else:
        for confession in pending_confessions:
            with st.container():
                st.write(f"**Category:** {confession.get('category', 'General')}")
                st.write(confession['content'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("✅ Approve", key=f"approve_{confession['id']}"):
                        approve_confession(confession['id'])
                
                with col2:
                    if st.button("❌ Reject", key=f"reject_{confession['id']}"):
                        reject_confession(confession['id'])
                
                with col3:
                    if st.button("🔍 View Details", key=f"view_{confession['id']}"):
                        st.session_state.view_confession = confession['id']
                
                st.divider()
    
    # Reported content
    st.write("### Reported Content")
    reports = load_data('reports')
    pending_reports = [r for r in reports if r.get('status') == 'pending']
    
    if not pending_reports:
        st.success("✅ No pending reports")
    else:
        for report in pending_reports:
            with st.container():
                confession = confessions.get(report['confession_id'], {})
                st.write(f"**Report ID:** {report['id']}")
                st.write(f"**Confession:** {confession.get('content', 'Content not found')}")
                st.write(f"**Reason:** {report.get('reason', 'N/A')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Dismiss Report", key=f"dismiss_{report['id']}"):
                        dismiss_report(report['id'])
                
                with col2:
                    if st.button("❌ Remove Content", key=f"remove_{report['id']}"):
                        remove_reported_content(report['id'])
                
                st.divider()

def announcement_management():
    """Announcement management"""
    st.subheader("📢 Announcement Management")
    
    # Create announcement
    with st.expander("➕ Create College Announcement", expanded=False):
        with st.form("admin_announcement_form"):
            title = st.text_input("Title")
            content = st.text_area("Content", height=100)
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            
            if st.form_submit_button("Create Announcement"):
                if title and content:
                    announcements = load_data('announcements')
                    
                    new_announcement = {
                        'id': f"announce_{len(announcements) + 1}",
                        'title': title,
                        'content': content,
                        'author': st.session_state.user['name'],
                        'author_id': st.session_state.user['id'],
                        'type': 'college',
                        'priority': priority.lower(),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    announcements.append(new_announcement)
                    save_data('announcements', announcements)
                    log_admin_action(st.session_state.user['id'], "created_announcement", "announcement", new_announcement['id'])
                    st.success("🎉 Announcement created!")
                    st.rerun()

def view_admin_logs():
    """View admin action logs"""
    st.subheader("📋 Admin Action Logs")
    
    logs = load_data('admin_logs')
    
    if not logs:
        st.info("No admin logs yet")
        return
    
    # Show recent logs (last 50)
    recent_logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:50]
    
    for log in recent_logs:
        admin = get_user_by_id(log.get('admin_id', ''))
        admin_name = admin['name'] if admin else "Unknown"
        
        st.write(f"**{admin_name}** - {log.get('action', 'Unknown action')}")
        st.caption(f"Target: {log.get('target_type', 'N/A')} • {format_timestamp(log.get('timestamp', ''))}")
        st.divider()

# Admin action functions
def make_user_admin(user_id):
    """Make a user an admin"""
    users = load_data('users')
    if user_id in users:
        users[user_id]['role'] = 'admin'
        save_data('users', users)
        log_admin_action(st.session_state.user['id'], "made_user_admin", "user", user_id)
        st.success("✅ User promoted to admin")
        st.rerun()

def remove_user_admin(user_id):
    """Remove admin privileges from user"""
    users = load_data('users')
    if user_id in users:
        users[user_id]['role'] = 'student'
        save_data('users', users)
        log_admin_action(st.session_state.user['id'], "removed_user_admin", "user", user_id)
        st.success("✅ Admin privileges removed")
        st.rerun()

def ban_user(user_id):
    """Ban a user"""
    users = load_data('users')
    if user_id in users:
        # In a real app, you'd have a banned status
        st.warning("Ban functionality would be implemented here")
        log_admin_action(st.session_state.user['id'], "banned_user", "user", user_id)

def approve_confession(confession_id):
    """Approve a confession"""
    confessions = load_data('confessions')
    if confession_id in confessions:
        confessions[confession_id]['status'] = 'approved'
        confessions[confession_id]['approved_at'] = datetime.now().isoformat()
        confessions[confession_id]['approved_by'] = st.session_state.user['id']
        save_data('confessions', confessions)
        log_admin_action(st.session_state.user['id'], "approved_confession", "confession", confession_id)
        st.success("✅ Confession approved")
        st.rerun()

def reject_confession(confession_id):
    """Reject a confession"""
    confessions = load_data('confessions')
    if confession_id in confessions:
        confessions[confession_id]['status'] = 'rejected'
        save_data('confessions', confessions)
        log_admin_action(st.session_state.user['id'], "rejected_confession", "confession", confession_id)
        st.success("❌ Confession rejected")
        st.rerun()

def dismiss_report(report_id):
    """Dismiss a report"""
    reports = load_data('reports')
    for report in reports:
        if report['id'] == report_id:
            report['status'] = 'dismissed'
            break
    save_data('reports', reports)
    log_admin_action(st.session_state.user['id'], "dismissed_report", "report", report_id)
    st.success("✅ Report dismissed")
    st.rerun()

def remove_reported_content(report_id):
    """Remove reported content"""
    reports = load_data('reports')
    report = next((r for r in reports if r['id'] == report_id), None)
    
    if report:
        # Remove the reported confession
        confessions = load_data('confessions')
        if report['confession_id'] in confessions:
            del confessions[report['confession_id']]
            save_data('confessions', confessions)
        
        # Mark report as resolved
        report['status'] = 'resolved'
        save_data('reports', reports)
        log_admin_action(st.session_state.user['id'], "removed_reported_content", "confession", report['confession_id'])
        st.success("✅ Content removed and report resolved")
        st.rerun()

def format_date(date_str):
    """Format date for display"""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d, %Y")
    except:
        return "Unknown"

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return timestamp