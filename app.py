import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io

st.set_page_config(page_title="🎨 Streamlit Paint Pro", layout="wide")
st.title("🎨 Streamlit Mini Paint App Pro – Live Preview & Move Shapes")

# --- Sidebar Controls ---
st.sidebar.header("Shape Controls")

shape = st.sidebar.selectbox("Select Shape", ["Rectangle", "Square", "Circle", "Oval", "Triangle"])
fill_color = st.sidebar.color_picker("Fill Color", "#0000FF")
border_color = st.sidebar.color_picker("Border Color", "#FF0000")
border_thickness = st.sidebar.slider("Border Thickness", 1, 20, 5)
rotation_angle = st.sidebar.slider("Rotation Angle (Degrees)", 0, 360, 0)

# Separate width & height for rectangles
rect_width = st.sidebar.slider("Rectangle Width", 50, 400, 200)
rect_height = st.sidebar.slider("Rectangle Height", 50, 400, 100)

# Size for other shapes
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

# --- Draw Rotated Rectangle ---
def draw_rotated_rectangle(canvas, center, width, height, angle, fill_color, border_color, thickness):
    rect = ((center[0], center[1]), (width, height), angle)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(canvas, [box], 0, border_color, thickness)
    cv2.fillPoly(canvas, [box], fill_color)
    return canvas

# --- Draw Shape Function ---
def draw_shape_on_canvas(canvas, shape_info):
    s = shape_info
    shape_type = s["shape"]
    pos_x, pos_y = s["position"]
    size = s.get("size", 200)
    fill_bgr = s["fill"]
    border_bgr = s["border"]
    thickness = s["thickness"]
    rotation = s.get("rotation", 0)
    rect_w = s.get("rect_w", size)
    rect_h = s.get("rect_h", size)

    if shape_type == "Rectangle":
        canvas = draw_rotated_rectangle(canvas, (pos_x,pos_y), rect_w, rect_h, rotation, fill_bgr, border_bgr, thickness)
    elif shape_type == "Square":
        canvas = draw_rotated_rectangle(canvas, (pos_x,pos_y), size, size, rotation, fill_bgr, border_bgr, thickness)
    elif shape_type == "Circle":
        cv2.circle(canvas, (pos_x, pos_y), size//2, border_bgr, thickness)
        cv2.circle(canvas, (pos_x, pos_y), size//2, fill_bgr, -1)
    elif shape_type == "Oval":
        M = cv2.getRotationMatrix2D((pos_x,pos_y), rotation, 1)
        overlay = np.zeros_like(canvas)
        cv2.ellipse(overlay, (pos_x,pos_y), (size//2, size//3), 0, 0, 360, fill_bgr, -1)
        cv2.ellipse(overlay, (pos_x,pos_y), (size//2, size//3), 0, 0, 360, border_bgr, thickness)
        canvas = cv2.warpAffine(overlay, M, (canvas.shape[1], canvas.shape[0]), dst=canvas, borderMode=cv2.BORDER_TRANSPARENT)
    elif shape_type == "Triangle":
        pts = np.array([
            [pos_x, pos_y - size//2],
            [pos_x - size//2, pos_y + size//2],
            [pos_x + size//2, pos_y + size//2]
        ], np.float32)
        rot_matrix = cv2.getRotationMatrix2D((pos_x,pos_y), rotation, 1)
        pts = cv2.transform(np.array([pts]), rot_matrix)[0]
        pts = pts.astype(np.int32).reshape((-1,1,2))
        cv2.polylines(canvas, [pts], True, border_bgr, thickness)
        cv2.fillPoly(canvas, [pts], fill_bgr)
    return canvas

# --- Sidebar Buttons with unique keys ---
add_shape_btn = st.sidebar.button("Add Shape", key="add_shape")
undo_btn = st.sidebar.button("Undo Last", key="undo_last")
clear_btn = st.sidebar.button("Clear Canvas", key="clear_canvas")

# --- Redraw Canvas from History ---
for s in st.session_state.history:
    canvas = draw_shape_on_canvas(canvas, s)

# --- Live Preview of Current Shape ---
preview_shape = {
    "shape": shape,
    "position": (position_x, position_y),
    "size": size,
    "rect_w": rect_width,
    "rect_h": rect_height,
    "fill": fill_bgr,
    "border": border_bgr,
    "thickness": border_thickness,
    "rotation": rotation_angle
}
canvas = draw_shape_on_canvas(canvas, preview_shape)

# --- Handle Add Shape ---
if add_shape_btn:
    st.session_state.history.append(preview_shape)

# --- Handle Undo ---
if undo_btn and st.session_state.history:
    st.session_state.history.pop()

# --- Handle Clear Canvas ---
if clear_btn:
    st.session_state.history = []

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
