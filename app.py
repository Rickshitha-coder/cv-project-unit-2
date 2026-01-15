import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io

st.set_page_config(page_title="🎨 Streamlit Paint Pro", layout="wide")
st.title("🎨 Streamlit Mini Paint App Pro")

# --- Sidebar Controls ---
st.sidebar.header("Shape Controls")

shape = st.sidebar.selectbox("Select Shape", ["Rectangle", "Square", "Circle", "Oval", "Triangle"])
fill_color = st.sidebar.color_picker("Fill Color", "#0000FF")
border_color = st.sidebar.color_picker("Border Color", "#FF0000")
border_thickness = st.sidebar.slider("Border Thickness", 1, 20, 5)
size = st.sidebar.slider("Shape Size", 50, 400, 200)
position_x = st.sidebar.slider("Position X", 0, 500, 250)
position_y = st.sidebar.slider("Position Y", 0, 500, 250)
bg_color = st.sidebar.color_picker("Canvas Background Color", "#FFFFFF")

# --- Canvas Setup ---
canvas_size = 500

# Initialize history if not already
if "history" not in st.session_state:
    st.session_state.history = []

# Convert hex to BGR
def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2],16)
    g = int(hex_color[2:4],16)
    b = int(hex_color[4:6],16)
    return (b,g,r)

fill_bgr = hex_to_bgr(fill_color)
border_bgr = hex_to_bgr(border_color)
bg_bgr = hex_to_bgr(bg_color)

# Initialize canvas for this run
canvas = np.ones((canvas_size, canvas_size, 3), np.uint8) * 255
canvas[:] = bg_bgr  # fill background

# --- Draw shape function ---
def draw_shape_on_canvas(canvas, shape_info):
    s = shape_info
    shape_type = s["shape"]
    pos_x, pos_y = s["position"]
    size = s["size"]
    fill_bgr = s["fill"]
    border_bgr = s["border"]
    thickness = s["thickness"]

    if shape_type == "Rectangle":
        top_left = (pos_x - size//2, pos_y - size//2)
        bottom_right = (pos_x + size//2, pos_y + size//2)
        cv2.rectangle(canvas, top_left, bottom_right, border_bgr, thickness)
        cv2.rectangle(canvas, top_left, bottom_right, fill_bgr, -1)
    elif shape_type == "Square":
        half = size//2
        top_left = (pos_x - half, pos_y - half)
        bottom_right = (pos_x + half, pos_y + half)
        cv2.rectangle(canvas, top_left, bottom_right, border_bgr, thickness)
        cv2.rectangle(canvas, top_left, bottom_right, fill_bgr, -1)
    elif shape_type == "Circle":
        cv2.circle(canvas, (pos_x, pos_y), size//2, border_bgr, thickness)
        cv2.circle(canvas, (pos_x, pos_y), size//2, fill_bgr, -1)
    elif shape_type == "Oval":
        cv2.ellipse(canvas, (pos_x, pos_y), (size//2, size//3), 0, 0, 360, border_bgr, thickness)
        cv2.ellipse(canvas, (pos_x, pos_y), (size//2, size//3), 0, 0, 360, fill_bgr, -1)
    elif shape_type == "Triangle":
        pts = np.array([
            [pos_x, pos_y - size//2],
            [pos_x - size//2, pos_y + size//2],
            [pos_x + size//2, pos_y + size//2]
        ], np.int32).reshape((-1,1,2))
        cv2.polylines(canvas, [pts], True, border_bgr, thickness)
        cv2.fillPoly(canvas, [pts], fill_bgr)
    return canvas

# --- Sidebar Buttons with unique keys ---
add_shape_btn = st.sidebar.button("Add Shape", key="add_shape")
undo_btn = st.sidebar.button("Undo Last", key="undo_last")
clear_btn = st.sidebar.button("Clear Canvas", key="clear_canvas")

# --- Handle Add Shape ---
if add_shape_btn:
    shape_info = {
        "shape": shape,
        "position": (position_x, position_y),
        "size": size,
        "fill": fill_bgr,
        "border": border_bgr,
        "thickness": border_thickness
    }
    st.session_state.history.append(shape_info)

# --- Handle Undo ---
if undo_btn and st.session_state.history:
    st.session_state.history.pop()

# --- Handle Clear Canvas ---
if clear_btn:
    st.session_state.history = []

# --- Redraw Canvas from History ---
for s in st.session_state.history:
    canvas = draw_shape_on_canvas(canvas, s)

# --- Display Canvas ---
st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB), use_column_width=True)

# --- Download Button ---
def convert_np_to_bytes(img_np):
    img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    img_pil.save(buf, format="PNG")
    return buf.getvalue()

st.download_button(
    "💾 Download Image",
    data=convert_np_to_bytes(canvas),
    file_name="my_paint.png",
    mime="image/png"
)
