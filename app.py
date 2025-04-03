import streamlit as st
from main import start_conversation, stop_conversation, toggle_microphone, toggle_speaker, get_mute_states

# Initialize session state for conversation status and button control
if 'conversation_active' not in st.session_state:
    st.session_state.conversation_active = False
if 'microphone_muted' not in st.session_state:
    st.session_state.microphone_muted = False
if 'speaker_muted' not in st.session_state:
    st.session_state.speaker_muted = False

# Callback functions for buttons
def on_start_click():
    if not st.session_state.conversation_active:
        try:
            success = start_conversation()
            if success:
                st.session_state.conversation_active = True
        except Exception as e:
            st.error(f"Error starting conversation: {e}")

def on_stop_click():
    if st.session_state.conversation_active:
        try:
            success = stop_conversation()
            if success:
                st.session_state.conversation_active = False
        except Exception as e:
            st.error(f"Error stopping conversation: {e}")

def on_mic_toggle():
    try:
        success = toggle_microphone()
        if success:
            # Update mute states from backend
            mute_states = get_mute_states()
            st.session_state.microphone_muted = mute_states["microphone_muted"]
    except Exception as e:
        st.error(f"Error toggling microphone: {e}")

def on_speaker_toggle():
    try:
        success = toggle_speaker()
        if success:
            # Update mute states from backend
            mute_states = get_mute_states()
            st.session_state.speaker_muted = mute_states["speaker_muted"]
    except Exception as e:
        st.error(f"Error toggling speaker: {e}")

# Streamlit UI with centered content
st.set_page_config(layout="centered")

# Container for centered content
container = st.container()

with container:
    # Title and subtitle centered
    st.markdown("<h1 style='text-align: center;'>Vishal Mart Voice Bot</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Technical Support Assistant</h3>", unsafe_allow_html=True)
    
    # Status indicator
    if st.session_state.conversation_active:
        st.markdown("<div style='text-align: center;'><span style='color: green; font-weight: bold;'>Voice Bot is ACTIVE</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center;'><span style='color: gray; font-weight: bold;'>Voice Bot is INACTIVE</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main control buttons
    col1, col2 = st.columns(2)
    
    # Start button
    start_btn = col1.button(
        "Start Conversation", 
        key="start_btn", 
        disabled=st.session_state.conversation_active,
        use_container_width=True
    )
    if start_btn:
        on_start_click()
        # Force a rerun to update the UI without closing the server
        st.rerun()
    
    # Stop button
    stop_btn = col2.button(
        "Stop Conversation", 
        key="stop_btn", 
        disabled=not st.session_state.conversation_active,
        use_container_width=True
    )
    if stop_btn:
        on_stop_click()
        # Force a rerun to update the UI without closing the server
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mute control buttons
    st.markdown("<div style='text-align: center;'><h4>Audio Controls</h4></div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    # Microphone toggle button
    mic_label = "Unmute Microphone" if st.session_state.microphone_muted else "Mute Microphone"
    mic_btn = col3.button(
        mic_label,
        key="mic_btn",
        disabled=not st.session_state.conversation_active,
        use_container_width=True
    )
    if mic_btn:
        on_mic_toggle()
        # Force a rerun to update the UI without closing the server
        st.rerun()
    
    # Speaker toggle button
    speaker_label = "Unmute Speaker" if st.session_state.speaker_muted else "Mute Speaker"
    speaker_btn = col4.button(
        speaker_label,
        key="speaker_btn",
        disabled=not st.session_state.conversation_active,
        use_container_width=True
    )
    if speaker_btn:
        on_speaker_toggle()
        # Force a rerun to update the UI without closing the server
        st.rerun()
    
    # Display current status with icons
    st.markdown("<br>", unsafe_allow_html=True)
    status_col1, status_col2 = st.columns(2)
    
    mic_status = "🔴 Microphone Muted" if st.session_state.microphone_muted else "🟢 Microphone Active"
    speaker_status = "🔴 Speaker Muted" if st.session_state.speaker_muted else "🟢 Speaker Active"
    
    status_col1.markdown(f"<div style='text-align: center;'>{mic_status}</div>", unsafe_allow_html=True)
    status_col2.markdown(f"<div style='text-align: center;'>{speaker_status}</div>", unsafe_allow_html=True)
