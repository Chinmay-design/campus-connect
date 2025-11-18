import streamlit as st
import uuid
from datetime import datetime
from database import load_data, save_data, get_user_by_id

def marketplace_page():
    """Marketplace page"""
    st.title("🛒 Campus Marketplace")
    st.write("Buy and sell items with fellow students!")
    
    # Create new listing
    with st.expander("➕ Create New Listing", expanded=False):
        create_listing_form()
    
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search items...", placeholder="Search by title or description")
    
    with col2:
        category_filter = st.selectbox("Category", ["All", "Books", "Electronics", "Furniture", "Clothing", "Other"])
    
    with col3:
        status_filter = st.selectbox("Status", ["All", "Available", "Sold"])
    
    # Display listings
    display_marketplace_listings(search_query, category_filter, status_filter)

def create_listing_form():
    """Form to create new marketplace listing"""
    with st.form("create_listing_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Item Title")
            price = st.number_input("Price ($)", min_value=0.0, step=1.0, format="%.2f")
            category = st.selectbox("Category", ["Books", "Electronics", "Furniture", "Clothing", "Other"])
            condition = st.selectbox("Condition", ["New", "Like New", "Good", "Fair", "Poor"])
        
        with col2:
            contact_method = st.selectbox("Contact Method", ["In-app Chat", "Email", "Phone"])
            contact_info = st.text_input("Contact Info", placeholder="Email or phone number")
            location = st.text_input("Pickup Location", placeholder="e.g., Student Center, Dorm A, etc.")
        
        description = st.text_area("Item Description", height=100,
                                 placeholder="Describe your item, any features, why you're selling...")
        
        if st.form_submit_button("Create Listing"):
            if title and price > 0 and description:
                marketplace = load_data('marketplace')
                listing_id = f"item_{str(uuid.uuid4())[:8]}"
                
                new_listing = {
                    'id': listing_id,
                    'title': title,
                    'description': description,
                    'price': price,
                    'category': category,
                    'condition': condition,
                    'contact_method': contact_method,
                    'contact_info': contact_info if contact_method != "In-app Chat" else "",
                    'location': location,
                    'seller_id': st.session_state.user['id'],
                    'seller_name': st.session_state.user['name'],
                    'status': 'available',
                    'created_at': datetime.now().isoformat(),
                    'views': 0,
                    'interested': []
                }
                
                marketplace[listing_id] = new_listing
                save_data('marketplace', marketplace)
                st.success(f"🎉 Listing '{title}' created successfully!")
                st.rerun()
            else:
                st.error("Please fill in title, price, and description")

def display_marketplace_listings(search_query, category_filter, status_filter):
    """Display marketplace listings"""
    marketplace = load_data('marketplace')
    
    if not marketplace:
        st.info("No listings found. Be the first to create a listing!")
        return
    
    # Filter listings
    filtered_listings = []
    for listing in marketplace.values():
        # Search filter
        if search_query:
            search_lower = search_query.lower()
            title_match = search_lower in listing['title'].lower()
            desc_match = search_lower in listing.get('description', '').lower()
            if not (title_match or desc_match):
                continue
        
        # Category filter
        if category_filter != "All" and listing['category'] != category_filter:
            continue
            
        # Status filter
        if status_filter != "All" and listing['status'] != status_filter.lower():
            continue
            
        filtered_listings.append(listing)
    
    if not filtered_listings:
        st.warning("No listings match your search criteria.")
        return
    
    # Sort by newest first
    filtered_listings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Display in grid
    for i in range(0, len(filtered_listings), 2):
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(filtered_listings):
                listing = filtered_listings[i + j]
                with cols[j]:
                    display_listing_card(listing)

def display_listing_card(listing):
    """Display a single marketplace listing card"""
    with st.container():
        # Status badge
        status = listing.get('status', 'available')
        status_color = {
            'available': '🟢',
            'sold': '🔴',
            'pending': '🟡'
        }.get(status, '⚪')
        
        st.write(f"{status_color} **{status.upper()}**")
        
        st.subheader(listing['title'])
        st.write(f"**${listing['price']:.2f}** • {listing['category']} • {listing['condition']}")
        
        # Description preview
        desc = listing.get('description', '')
        if len(desc) > 100:
            st.write(desc[:100] + "...")
        else:
            st.write(desc)
        
        # Listing details
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"📍 {listing.get('location', 'TBA')}")
        with col2:
            st.caption(f"👤 {listing.get('seller_name', 'Unknown')}")
        
        # Action buttons
        if listing['seller_id'] == st.session_state.user['id']:
            # Seller actions
            col1, col2 = st.columns(2)
            with col1:
                if listing['status'] == 'available':
                    if st.button("✅ Mark Sold", key=f"sold_{listing['id']}"):
                        mark_listing_sold(listing['id'])
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{listing['id']}"):
                    delete_listing(listing['id'])
        else:
            # Buyer actions
            if listing['status'] == 'available':
                if listing['contact_method'] == 'In-app Chat':
                    if st.button("💬 Contact Seller", key=f"contact_{listing['id']}"):
                        start_chat_with_seller(listing)
                else:
                    st.info(f"📞 Contact: {listing.get('contact_info', 'N/A')}")
        
        st.divider()

def mark_listing_sold(listing_id):
    """Mark a listing as sold"""
    marketplace = load_data('marketplace')
    
    if listing_id in marketplace:
        marketplace[listing_id]['status'] = 'sold'
        save_data('marketplace', marketplace)
        st.success("✅ Listing marked as sold!")
        st.rerun()

def delete_listing(listing_id):
    """Delete a marketplace listing"""
    marketplace = load_data('marketplace')
    
    if listing_id in marketplace:
        del marketplace[listing_id]
        save_data('marketplace', marketplace)
        st.success("🗑️ Listing deleted!")
        st.rerun()

def start_chat_with_seller(listing):
    """Start a chat with seller"""
    st.session_state.start_chat_with = listing['seller_id']
    st.session_state.chat_context = f"Interested in: {listing['title']}"
    st.session_state.page = "Chat"
    st.rerun()