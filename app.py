import streamlit as st
import numpy as np
import cv2

st.title("Shape Drawer (Cloud Compatible)")

# Canvas size
width, height = 500, 500

# Create blank canvas
def create_canvas():
    return np.ones((height, width, 3), dtype=np.uint8) * 255

# Draw shapes function
def draw_shape(canvas, shape):
    shape = shape.lower()
    if shape == "rectangle":
        top_left, bottom_right = (100,100), (400,300)
        cv2.rectangle(canvas, top_left, bottom_right, (0,0,255), 5)  # Red border
        cv2.rectangle(canvas, top_left, bottom_right, (255,0,0), -1) # Blue fill
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

# User input
shape_text = st.text_input("Enter a shape (rectangle/circle/triangle):")

if st.button("Draw Shape"):
    canvas = create_canvas()
    canvas = draw_shape(canvas, shape_text)
    st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
