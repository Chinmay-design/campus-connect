import streamlit as st
import uuid
from datetime import datetime
from database import load_data, save_data, get_user_by_id

def chat_page():
    """Secure chat page"""
    st.title("💬 Campus Chat")
    st.write("Message other students securely")
    
    # Privacy reminder
    if not st.session_state.get('privacy_consent'):
        st.warning("🔒 Please accept the privacy policy to use chat features")
        return
    
    # Chat interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        display_chat_list()
    
    with col2:
        if st.session_state.get('active_chat'):
            display_chat_messages()
        else:
            display_chat_welcome()

def display_chat_list():
    """Display list of chats"""
    st.subheader("Your Chats")
    
    chats = load_data('chats')
    user_id = st.session_state.user['id']
    
    # Get user's chats
    user_chats = []
    for chat_id, chat in chats.items():
        if user_id in chat.get('participants', []):
            user_chats.append((chat_id, chat))
    
    # Start new chat
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.show_new_chat = True
    
    if st.session_state.get('show_new_chat'):
        start_new_chat()
    
    # Display chat list
    if not user_chats:
        st.info("No chats yet. Start a new conversation!")
        return
    
    for chat_id, chat in user_chats:
        display_chat_list_item(chat_id, chat)

def display_chat_list_item(chat_id, chat):
    """Display a chat in the list"""
    user_id = st.session_state.user['id']
    
    # Get other participant(s)
    participants = chat.get('participants', [])
    other_participants = [p for p in participants if p != user_id]
    
    if len(other_participants) == 1:
        # Direct message
        other_user = get_user_by_id(other_participants[0])
        display_name = other_user['name'] if other_user else "Unknown User"
        emoji = "👤"
    else:
        # Group chat
        display_name = chat.get('name', 'Group Chat')
        emoji = "👥"
    
    # Last message preview
    messages = chat.get('messages', [])
    last_message = messages[-1] if messages else None
    last_preview = last_message['content'][:30] + "..." if last_message and len(last_message['content']) > 30 else last_message['content'] if last_message else "No messages"
    
    # Select chat button
    if st.button(f"{emoji} {display_name}\n{last_preview}", 
                 key=f"chat_{chat_id}",
                 use_container_width=True):
        st.session_state.active_chat = chat_id
    
    st.divider()

def start_new_chat():
    """Start a new chat"""
    st.subheader("Start New Chat")
    
    users = load_data('users')
    current_user_id = st.session_state.user['id']
    
    # Filter out current user and get available users
    available_users = []
    for user_id, user_data in users.items():
        if user_id != current_user_id and user_data.get('email') != 'admin@university.edu':
            available_users.append((user_id, user_data))
    
    if not available_users:
        st.info("No other users available to chat with")
        return
    
    selected_user_id = st.selectbox(
        "Select user to message",
        options=[user[0] for user in available_users],
        format_func=lambda uid: next(user[1]['name'] for user in available_users if user[0] == uid)
    )
    
    message = st.text_input("Initial message")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Chat"):
            if selected_user_id and message.strip():
                create_new_chat(selected_user_id, message.strip())
    
    with col2:
        if st.button("Cancel"):
            st.session_state.show_new_chat = False
            st.rerun()

def create_new_chat(other_user_id, initial_message):
    """Create a new chat with initial message"""
    chats = load_data('chats')
    user_id = st.session_state.user['id']
    
    # Create chat ID (sorted to avoid duplicates)
    participants = sorted([user_id, other_user_id])
    chat_id = f"dm_{'_'.join(participants)}"
    
    # Check if chat already exists
    if chat_id not in chats:
        new_chat = {
            'id': chat_id,
            'participants': participants,
            'type': 'direct',
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'messages': []
        }
        chats[chat_id] = new_chat
    else:
        new_chat = chats[chat_id]
    
    # Add initial message
    message = {
        'id': str(uuid.uuid4()),
        'sender': user_id,
        'content': initial_message,
        'timestamp': datetime.now().isoformat(),
        'read': False
    }
    
    new_chat['messages'].append(message)
    new_chat['last_activity'] = datetime.now().isoformat()
    
    chats[chat_id] = new_chat
    save_data('chats', chats)
    
    st.session_state.active_chat = chat_id
    st.session_state.show_new_chat = False
    st.rerun()

def display_chat_messages():
    """Display messages in active chat"""
    chats = load_data('chats')
    chat_id = st.session_state.active_chat
    
    if chat_id not in chats:
        st.error("Chat not found")
        return
    
    chat = chats[chat_id]
    user_id = st.session_state.user['id']
    
    # Chat header
    participants = chat.get('participants', [])
    other_participants = [p for p in participants if p != user_id]
    
    if len(other_participants) == 1:
        other_user = get_user_by_id(other_participants[0])
        display_name = other_user['name'] if other_user else "Unknown User"
        st.subheader(f"👤 Chat with {display_name}")
    else:
        st.subheader(f"👥 {chat.get('name', 'Group Chat')}")
    
    # Messages area
    messages_container = st.container()
    
    with messages_container:
        display_chat_messages_list(chat, user_id)
    
    # Message input
    st.divider()
    message_input(chat_id)

def display_chat_messages_list(chat, user_id):
    """Display list of messages in chat"""
    messages = chat.get('messages', [])
    
    if not messages:
        st.info("No messages yet. Start the conversation!")
        return
    
    for message in messages:
        is_own_message = message['sender'] == user_id
        display_message_bubble(message, is_own_message)

def display_message_bubble(message, is_own_message):
    """Display a single message bubble"""
    col1, col2 = st.columns([1, 20])
    
    if not is_own_message:
        with col1:
            sender = get_user_by_id(message['sender'])
            st.write("👤")
    
    with col2:
        # Message bubble styling
        bubble_style = """
        <style>
        .message-bubble {
            padding: 10px 15px;
            border-radius: 18px;
            margin: 5px 0;
            max-width: 80%;
            word-wrap: break-word;
            display: inline-block;
        }
        .own-message {
            background-color: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .other-message {
            background-color: #f1f1f1;
            color: black;
        }
        </style>
        """
        st.markdown(bubble_style, unsafe_allow_html=True)
        
        bubble_class = "own-message" if is_own_message else "other-message"
        
        st.markdown(f"""
        <div class="message-bubble {bubble_class}">
            <div>{message['content']}</div>
            <div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">
                {format_timestamp(message['timestamp'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

def message_input(chat_id):
    """Message input component"""
    col1, col2 = st.columns([5, 1])
    
    with col1:
        new_message = st.text_input(
            "Type a message...", 
            key=f"input_{chat_id}",
            placeholder="Press Enter to send",
            label_visibility="collapsed"
        )
    
    with col2:
        send_disabled = not new_message.strip()
        if st.button("Send", disabled=send_disabled, use_container_width=True):
            send_message(chat_id, new_message.strip())

def send_message(chat_id, content):
    """Send a message in chat"""
    chats = load_data('chats')
    
    if chat_id in chats:
        message = {
            'id': str(uuid.uuid4()),
            'sender': st.session_state.user['id'],
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        chats[chat_id]['messages'].append(message)
        chats[chat_id]['last_activity'] = datetime.now().isoformat()
        save_data('chats', chats)
        st.rerun()

def display_chat_welcome():
    """Display welcome message when no chat is selected"""
    st.info("""
    💬 **Welcome to Campus Chat!**
    
    Start a conversation by:
    - Selecting an existing chat from the list
    - Starting a new chat with another student
    - Messaging sellers from marketplace listings
    
    🔒 **Your messages are secure and private**
    """)

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%I:%M %p")
    except:
        return timestamp