import streamlit as st
import numpy as np
import cv2
from PIL import Image
import speech_recognition as sr

st.title("Shape Drawer with Voice & Text")

# Canvas size
width, height = 500, 500

# Initialize white canvas
def create_canvas():
    return np.ones((height, width, 3), dtype=np.uint8) * 255

canvas = create_canvas()

# Draw shapes function
def draw_shape(canvas, shape):
    shape = shape.lower()
    if shape == "rectangle":
        top_left = (100, 100)
        bottom_right = (400, 300)
        cv2.rectangle(canvas, top_left, bottom_right, (0, 0, 255), 5)  # red border
        cv2.rectangle(canvas, top_left, bottom_right, (255, 0, 0), -1) # blue fill
    elif shape == "circle":
        center = (250, 250)
        radius = 100
        cv2.circle(canvas, center, radius, (0,0,255), 5)
        cv2.circle(canvas, center, radius, (255,0,0), -1)
    elif shape == "triangle":
        pts = np.array([[250,100],[150,350],[350,350]], np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(canvas, [pts], isClosed=True, color=(0,0,255), thickness=5)
        cv2.fillPoly(canvas, [pts], color=(255,0,0))
    else:
        st.warning("Shape not recognized!")
    return canvas

# --- Option 1: Text input ---
shape_text = st.text_input("Enter a shape (rectangle/circle/triangle)")
if st.button("Draw Shape"):
    canvas = create_canvas()
    canvas = draw_shape(canvas, shape_text)
    st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))

# --- Option 2: Voice input ---
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
