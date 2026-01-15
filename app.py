import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="🎨 Streamlit Interactive Paint", layout="wide")
st.title("🎨 Streamlit Interactive Paint App")

# --- Sidebar ---
st.sidebar.header("Canvas Settings")
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
stroke_width = st.sidebar.slider("Border Thickness", 1, 20, 5)

# Shape options
shape_type = st.sidebar.selectbox("Shape Type", ["Rectangle", "Circle", "Oval", "Triangle"])
fill_color = st.sidebar.color_picker("Fill Color", "#0000FF")
border_color = st.sidebar.color_picker("Border Color", "#FF0000")

# Canvas size
canvas_size = 500

# --- Initialize Canvas ---
canvas_result = st_canvas(
    fill_color=fill_color + "80",  # 50% transparency for fill
    stroke_width=stroke_width,
    stroke_color=border_color,
    background_color=bg_color,
    width=canvas_size,
    height=canvas_size,
    drawing_mode="rect" if shape_type in ["Rectangle", "Square"] else "circle",
    key="canvas",
    update_streamlit=True
)

# --- Download Button ---
if canvas_result.image_data is not None:
    img_np = cv2.cvtColor(canvas_result.image_data.astype(np.uint8), cv2.COLOR_RGBA2RGB)
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
