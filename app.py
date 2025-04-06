import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from main import start_conversation, stop_conversation, toggle_microphone, toggle_speaker, get_mute_states
import time
import numpy as np

# Set page configuration first
st.set_page_config(
    page_title="Vishal Mart Voice Bot",
    page_icon="🎤",
    layout="centered"
)

# Initialize session state
if 'conversation_active' not in st.session_state:
    st.session_state.conversation_active = False
if 'microphone_muted' not in st.session_state:
    st.session_state.microphone_muted = False
if 'speaker_muted' not in st.session_state:
    st.session_state.speaker_muted = False
if 'audio_level' not in st.session_state:
    st.session_state.audio_level = 0

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

# Function to generate voice bars HTML for animation
def generate_voice_bars_html():
    bars_html = '<div class="voice-bars">'
    num_bars = 6
    
    for i in range(num_bars):
        # Calculate height based on position and simulated audio level
        center_factor = 1 - abs(i - num_bars/2) / (num_bars/2)
        t = time.time() * 3  # Time factor for animation speed
        
        # Different animation based on conversation status
        if st.session_state.conversation_active and not st.session_state.microphone_muted:
            # More active animation when conversation is active
            phase = i * 0.3  # Different phase for each bar
            height = 10 + np.sin(t + phase) * 15 * center_factor
            # Add random fluctuations
            height += np.sin(t * 2.5 + i * 0.7) * 10 * np.random.random()
        else:
            # Subtle idle animation when inactive
            height = 5 + np.sin(t * 0.5 + i * 0.2) * 3
            
        height = max(5, height)  # Minimum height
        bars_html += f'<div class="voice-bar" style="height: {height}px;"></div>'
    
    bars_html += '</div>'
    return bars_html

# Add custom CSS for orb and styling
st.markdown("""
<style>
    /* Glassy container effect */
    .stApp {
        background: transparent;
    }
    
    /* Blue glassy orb */
    .blue-orb-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 350px;
        margin: 20px 0;
    }
    
    /* Moving gradient animation */
    @keyframes moveGradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    .blue-orb {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: linear-gradient(45deg, #4facfe, #00f2fe, #0072ff, #00c6ff);
        background-size: 300% 300%;
        animation: moveGradient 8s ease infinite, pulse 4s infinite ease-in-out;
        box-shadow: 
            0 0 60px rgba(79, 172, 254, 0.6),
            0 0 100px rgba(0, 242, 254, 0.4);
        position: relative;
        z-index: 10;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        overflow: hidden;
        margin-bottom: 30px;
    }
    
    /* Glassy highlight on the orb */
    .orb-highlight {
        position: absolute;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.4);
        top: 40px;
        left: 40px;
        filter: blur(8px);
    }
    
    /* Additional inner glow */
    .inner-glow {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: radial-gradient(circle at center, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
        animation: pulse 5s infinite ease-in-out alternate;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.7; }
        50% { transform: scale(1.05); opacity: 0.9; }
    }
    
    /* Listening animation container */
    .listening-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
    }
    
    /* Listening text */
    .listening-text {
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.2rem;
        margin-bottom: 15px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Voice visualization bars */
    .voice-bars {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 50px;
        width: 200px;
        margin: 0 auto 20px auto;
    }
    
    .voice-bar {
        width: 6px;
        height: 5px;
        margin: 0 3px;
        background: #4facfe;
        border-radius: 3px;
        transition: height 0.1s ease;
    }
    
    /* Center the voice visualization container */
    .voice-viz-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 0 auto;
    }
    
    /* Control row styling */
    .control-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin: 20px auto;
        width: 100%;
        text-align: center;
        flex-wrap: nowrap !important;
    }
    
    .control-button {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        padding: 0 15px;
    }
    
    /* Override Streamlit's responsive column behavior */
    .row-widget.stHorizontal {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }
    
    /* Make buttons stay in a row on small screens */
    @media (max-width: 640px) {
        .row-widget.stHorizontal {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
        
        .row-widget.stHorizontal > div {
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: auto !important;
        }
        
        .circular-button button {
            width: 50px !important;
            height: 50px !important;
            font-size: 20px !important;
        }
    }
    
    /* Center all content */
    .stApp > header {
        background-color: transparent;
    }
    
    .main .block-container {
        max-width: 800px;
        padding-top: 1rem;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* Center the buttons */
    .stButton {
        display: flex;
        justify-content: center;
    }
    
    /* Button container */
    .control-buttons {
        margin-top: 30px;
        display: flex;
        justify-content: center;
        gap: 20px;
    }
    
    /* Status indicator */
    .status-indicator {
        margin: 15px 0;
    }
    
    /* Audio controls */
    .audio-controls {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 20px auto;
    }
    
    /* Styling for all buttons */
    button {
        border-radius: 80px !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3) !important;
    }
    
    button:active {
        transform: translateY(0) !important;
    }
    
    /* Circular audio control buttons */
    .circular-button button {
        border-radius: 80px !important;
        width: 60px !important;
        height: 60px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        font-size: 24px !important;
    }
    
    /* Active button styling */
    .active-button button {
        background-color: rgba(79, 172, 254, 0.3) !important;
        border-color: #4facfe !important;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.5) !important;
    }
    
    /* Block container adjustments */
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Hide default Streamlit elements */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Create a container for the main content
main_container = st.container()

with main_container:
    # Animated orb container
    st.markdown("""
    <div class="blue-orb-container">
        <div class="blue-orb">
            <div class="inner-glow"></div>
            <div class="orb-highlight"></div>
        </div>
        <div class="listening-container">
    """, unsafe_allow_html=True)
    
    # Voice visualization
    st.markdown('<div class="voice-viz-container">', unsafe_allow_html=True)
    voice_viz_placeholder = st.empty()
    voice_viz_placeholder.markdown(generate_voice_bars_html(), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Create a single row with fixed-width columns for the buttons
    st.markdown("""
    <style>
    .button-row {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        gap: 5px;
        margin: 20px auto;
        width: 100%;
    }
    .button-container {
        width: 60px;
        height: 60px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    <div class="button-row">
    """, unsafe_allow_html=True)
    
    # Create a 3-column layout with fixed width columns
    button_cols = st.columns([1, 1, 1], gap="small",vertical_alignment="center")
    
    # Mic button
    with button_cols[0]:
        mic_icon = "🎙️" if not st.session_state.microphone_muted else "🔇"
        mic_active_class = "" if st.session_state.microphone_muted else "active-button"
        
        st.markdown(f'<div class="circular-button {mic_active_class}">', unsafe_allow_html=True)
        mic_btn = st.button(
            f"{mic_icon}", 
            key="mic_btn", 
            disabled=not st.session_state.conversation_active
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Start/Stop button
    with button_cols[1]:
        # Button changes based on conversation state
        if st.session_state.conversation_active:
            toggle_btn = st.button(label="⏸️Stop conversation", key="toggle_btn")
        else:
            toggle_btn = st.button(label="▶️Start conversation", key="toggle_btn")
    
    # Speaker button
    with button_cols[2]:
        speaker_icon = "🔊" if not st.session_state.speaker_muted else "🔇"
        speaker_active_class = "" if st.session_state.speaker_muted else "active-button"
        
        st.markdown(f'<div class="circular-button {speaker_active_class}">', unsafe_allow_html=True)
        speaker_btn = st.button(
            f"{speaker_icon}", 
            key="speaker_btn", 
            disabled=not st.session_state.conversation_active
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle button clicks
    if mic_btn:
        on_mic_toggle()
        st.rerun()
        
    if speaker_btn:
        on_speaker_toggle()
        st.rerun()
        
    if toggle_btn:
        if st.session_state.conversation_active:
            on_stop_click()
        else:
            on_start_click()
        st.rerun()

# Rerun the app to animate the visualization (only when active)
if st.session_state.conversation_active:
    time.sleep(0.1)
    st.rerun()