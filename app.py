import streamlit as st
import numpy as np
import cv2
from PIL import Image
import sys

# Try to import speech recognition, but ignore errors in cloud
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    st.warning("Voice recognition is disabled in this environment.")

# --- Canvas setup ---
width, height = 500, 500

def create_canvas():
    return np.ones((height, width, 3), dtype=np.uint8) * 255

def draw_shape(canvas, shape):
    shape = shape.lower()
    if shape == "rectangle":
        top_left, bottom_right = (100,100), (400,300)
        cv2.rectangle(canvas, top_left, bottom_right, (0,0,255), 5)
        cv2.rectangle(canvas, top_left, bottom_right, (255,0,0), -1)
    elif shape == "circle":
        cv2.circle(canvas, (250,250), 100, (0,0,255), 5)
        cv2.circle(canvas, (250,250), 100, (255,0,0), -1)
    elif shape == "triangle":
        pts = np.array([[250,100],[150,350],[350,350]], np.int32).reshape((-1,1,2))
        cv2.polylines(canvas, [pts], True, (0,0,255), 5)
        cv2.fillPoly(canvas, [pts], (255,0,0))
    else:
        st.warning("Shape not recognized!")
    return canvas

canvas = create_canvas()

# --- Text input ---
shape_text = st.text_input("Enter a shape (rectangle/circle/triangle)")
if st.button("Draw Shape"):
    canvas = create_canvas()
    canvas = draw_shape(canvas, shape_text)
    st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))

# --- Voice input (local only) ---
if SPEECH_AVAILABLE:
    if st.button("Draw Shape via Voice"):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Please speak now")
            audio = r.listen(source, phrase_time_limit=3)
            try:
                voice_shape = r.recognize_google(audio)
                st.success(f"You said: {voice_shape}")
                canvas = create_canvas()
                canvas = draw_shape(canvas, voice_shape)
                st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
            except:
                st.error("Could not recognize audio. Try again.")
else:
    st.info("Voice input not available in this environment. Use text input.")
