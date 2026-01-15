import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io

st.set_page_config(page_title="🎨 Streamlit Paint", layout="wide")
st.title("🎨 Streamlit Mini Paint App")

# --- Sidebar controls ---
st.sidebar.header("Shape Options")

# Shape selection
shape = st.sidebar.selectbox("Select Shape", ["Rectangle", "Square", "Circle", "Oval", "Triangle"])

# Color pickers
fill_color = st.sidebar.color_picker("Fill Color", "#0000FF")   # default blue
border_color = st.sidebar.color_picker("Border Color", "#FF0000") # default red
border_thickness = st.sidebar.slider("Border Thickness", 1, 20, 5)

# Size and position
size = st.sidebar.slider("Shape Size", 50, 400, 200)
position_x = st.sidebar.slider("Position X", 0, 500, 250)
position_y = st.sidebar.slider("Position Y", 0, 500, 250)

# Canvas background
bg_color = st.sidebar.color_picker("Canvas Background Color", "#FFFFFF")

# Clear canvas button
clear_canvas = st.sidebar.button("Clear Canvas")

# --- Convert hex to BGR ---
def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2],16)
    g = int(hex_color[2:4],16)
    b = int(hex_color[4:6],16)
    return (b,g,r)

fill_bgr = hex_to_bgr(fill_color)
border_bgr = hex_to_bgr(border_color)
bg_bgr = hex_to_bgr(bg_color)

# --- Canvas setup ---
canvas_size = 500
if "canvas" not in st.session_state or clear_canvas:
    st.session_state.canvas = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * 255
    st.session_state.canvas[:] = bg_bgr

canvas = st.session_state.canvas

# --- Draw shapes ---
if st.button("Add Shape"):
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

    st.session_state.canvas = canvas

# --- Display canvas ---
st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB), use_column_width=True)

# --- Download button ---
def convert_np_to_bytes(img_np):
    img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    img_pil.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

st.download_button(
    label="💾 Download Image",
    data=convert_np_to_bytes(canvas),
    file_name="my_drawing.png",
    mime="image/png"
)
