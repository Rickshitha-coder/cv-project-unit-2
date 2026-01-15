import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io

st.set_page_config(page_title="🎨 Streamlit Paint Pro", layout="wide")
st.title("🎨 Streamlit Mini Paint App Pro")

# --- Sidebar ---
st.sidebar.header("Shape Controls")

# Shape and customization
shape = st.sidebar.selectbox("Select Shape", ["Rectangle", "Square", "Circle", "Oval", "Triangle"])
fill_color = st.sidebar.color_picker("Fill Color", "#0000FF")
border_color = st.sidebar.color_picker("Border Color", "#FF0000")
border_thickness = st.sidebar.slider("Border Thickness", 1, 20, 5)
size = st.sidebar.slider("Shape Size", 50, 400, 200)
position_x = st.sidebar.slider("Position X", 0, 500, 250)
position_y = st.sidebar.slider("Position Y", 0, 500, 250)

bg_color = st.sidebar.color_picker("Canvas Background Color", "#FFFFFF")

# --- Canvas size ---
canvas_size = 500

# --- Initialize canvas and history ---
if "canvas" not in st.session_state or st.sidebar.button("Clear Canvas"):
    st.session_state.canvas = np.ones((canvas_size, canvas_size, 3), np.uint8) * 255
    st.session_state.history = []  # store all shapes
    # Set background color
    bg_bgr = tuple(int(bg_color[i:i+2],16) for i in (1,3,5))[::-1]
    st.session_state.canvas[:] = bg_bgr

canvas = st.session_state.canvas

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

# --- Buttons ---
col1, col2, col3 = st.sidebar.columns(3)
add_shape_btn = col1.button("Add Shape")
undo_btn = col2.button("Undo Last")
clear_btn = col3.button("Clear Canvas")

# --- Handle add shape ---
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

# --- Handle undo ---
if undo_btn and st.session_state.history:
    st.session_state.history.pop()

# --- Handle clear canvas ---
if clear_btn:
    st.session_state.history = []

# --- Redraw canvas from history ---
canvas[:] = bg_bgr
for s in st.session_state.history:
    canvas = draw_shape_on_canvas(canvas, s)

# --- Display canvas ---
st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB), use_column_width=True)

# --- Download button ---
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
