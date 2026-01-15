import streamlit as st
import numpy as np
import cv2
from PIL import Image

st.set_page_config(page_title="Interactive Shape Drawer", layout="wide")
st.title("🎨 Interactive Shape Drawer")

# --- Sidebar controls ---
st.sidebar.header("Shape Options")
shape = st.sidebar.selectbox("Select Shape", ["Rectangle", "Square", "Circle", "Oval", "Triangle"])
fill_color = st.sidebar.color_picker("Pick Fill Color", "#0000FF")   # default blue
border_color = st.sidebar.color_picker("Pick Border Color", "#FF0000") # default red
border_thickness = st.sidebar.slider("Border Thickness", 1, 20, 5)
size = st.sidebar.slider("Shape Size", 50, 400, 200)
position_x = st.sidebar.slider("Position X", 0, 500, 250)
position_y = st.sidebar.slider("Position Y", 0, 500, 250)

# --- Convert hex to BGR for OpenCV ---
def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)

fill_bgr = hex_to_bgr(fill_color)
border_bgr = hex_to_bgr(border_color)

# --- Canvas setup ---
canvas_size = 500
canvas = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * 255  # white canvas

# --- Draw selected shape ---
if st.button("Draw Shape"):
    canvas[:] = 255  # clear canvas
    if shape == "Rectangle":
        top_left = (position_x - size//2, position_y - size//2)
        bottom_right = (position_x + size//2, position_y + size//2)
        cv2.rectangle(canvas, top_left, bottom_right, border_bgr, border_thickness)
        cv2.rectangle(canvas, top_left, bottom_right, fill_bgr, -1)
    elif shape == "Square":
        half = size//2
        top_left = (position_x - half, position_y - half)
        bottom_right = (position_x + half, position_y + half)
        cv2.rectangle(canvas, top_left, bottom_right, border_bgr, border_thickness)
        cv2.rectangle(canvas, top_left, bottom_right, fill_bgr, -1)
    elif shape == "Circle":
        cv2.circle(canvas, (position_x, position_y), size//2, border_bgr, border_thickness)
        cv2.circle(canvas, (position_x, position_y), size//2, fill_bgr, -1)
    elif shape == "Oval":
        cv2.ellipse(canvas, (position_x, position_y), (size//2, size//3), 0, 0, 360, border_bgr, border_thickness)
        cv2.ellipse(canvas, (position_x, position_y), (size//2, size//3), 0, 0, 360, fill_bgr, -1)
    elif shape == "Triangle":
        pts = np.array([
            [position_x, position_y - size//2],
            [position_x - size//2, position_y + size//2],
            [position_x + size//2, position_y + size//2]
        ], np.int32).reshape((-1,1,2))
        cv2.polylines(canvas, [pts], True, border_bgr, border_thickness)
        cv2.fillPoly(canvas, [pts], fill_bgr)
    else:
        st.warning("Shape not supported!")

    # Show canvas
    st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
