import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="🎨 Streamlit Paint Pro", layout="wide")
st.title("🎨 Interactive Paint App (Cloud Ready)")

# --- Sidebar Settings ---
st.sidebar.header("Canvas Settings")
canvas_width = st.sidebar.number_input("Canvas Width", min_value=200, max_value=1000, value=500)
canvas_height = st.sidebar.number_input("Canvas Height", min_value=200, max_value=1000, value=500)
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")

st.sidebar.header("Shape Settings")
shape_type = st.sidebar.selectbox("Shape Type", ["Rectangle", "Square", "Circle", "Oval", "Triangle"])
stroke_width = st.sidebar.slider("Border Thickness", 1, 20, 5)
fill_color = st.sidebar.color_picker("Fill Color", "#0000FF")
border_color = st.sidebar.color_picker("Border Color", "#FF0000")

# --- Initialize shape history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Buttons ---
add_shape_btn = st.sidebar.button("Add Shape")
undo_btn = st.sidebar.button("Undo Last")
clear_btn = st.sidebar.button("Clear Canvas")

# --- Initialize canvas for streamlit-drawable-canvas ---
drawing_mode = "rect" if shape_type in ["Rectangle", "Square"] else "circle"

canvas_result = st_canvas(
    fill_color=fill_color + "80",  # semi-transparent fill
    stroke_width=stroke_width,
    stroke_color=border_color,
    background_color=bg_color,
    width=canvas_width,
    height=canvas_height,
    drawing_mode=drawing_mode,
    key="canvas",
    update_streamlit=True
)

# --- Handle Add Shape ---
if add_shape_btn:
    st.session_state.history.append({
        "shape": shape_type,
        "fill": fill_color,
        "border": border_color,
        "thickness": stroke_width
    })

# --- Handle Undo ---
if undo_btn and st.session_state.history:
    st.session_state.history.pop()

# --- Handle Clear Canvas ---
if clear_btn:
    st.session_state.history = []

# --- Convert to PNG for download ---
if canvas_result.image_data is not None:
    img_np = np.array(canvas_result.image_data.astype(np.uint8))
    img_pil = Image.fromarray(img_np)
    buf = io.BytesIO()
    img_pil.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="💾 Download Image",
        data=byte_im,
        file_name="interactive_paint.png",
        mime="image/png"
    )
