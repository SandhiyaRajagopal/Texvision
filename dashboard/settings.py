import streamlit as st
import os
from config.settings import PIXEL_TO_CM_RATIO, MODEL_PATH

def render():
    st.title("System Settings")
    
    st.markdown("### Camera Calibration")
    st.info("Adjust the pixel to centimeter ratio based on your camera setup.")
    new_ratio = st.number_input("Pixel to CM Ratio", value=PIXEL_TO_CM_RATIO, step=0.01)
    
    st.markdown("### Model Configuration")
    st.text_input("YOLO Model Path", value=MODEL_PATH, disabled=True)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully. (Note: Runtime persistence requires saving to config file which will be implemented in future)")
