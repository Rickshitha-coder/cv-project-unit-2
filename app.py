import cv2
import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Shape Detection App", layout="wide")
st.title("🖌 Interactive Shape Detection & Drawing")

# Sidebar for input options
st.sidebar.header("Input Options")
input_mode = st.sidebar.radio("Select Input Type", ["Upload Image", "Use Webcam"])

def detect_shapes(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    
    # Edge detection
    edges = cv2.Canny(blur, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        # Approximate contour
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        # Get bounding box for text
        x, y, w, h = cv2.boundingRect(approx)
        
        # Identify shape
        if len(approx) == 3:
            shape_name = "Triangle"
        elif len(approx) == 4:
            aspect_ratio = w / float(h)
            shape_name = "Square" if 0.95 <= aspect_ratio <= 1.05 else "Rectangle"
        elif len(approx) == 5:
            shape_name = "Pentagon"
        else:
            shape_name = "Circle"
        
        # Draw contour and label
        cv2.drawContours(img, [approx], -1, (0, 255, 0), 3)
        cv2.putText(img, shape_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
    
    return img

if input_mode == "Upload Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["png","jpg","jpeg"])
    if uploaded_file is not None:
        # Convert to OpenCV format
        image = Image.open(uploaded_file)
        img = np.array(image)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        result_img = detect_shapes(img)
        # Convert back to RGB for Streamlit display
        result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
        st.image(result_img, caption="Detected Shapes", use_column_width=True)

elif input_mode == "Use Webcam":
    stframe = st.empty()
    run = st.button("Start Webcam")
    cap = cv2.VideoCapture(0)
    
    if run:
        while True:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to grab frame.")
                break
            frame = detect_shapes(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            stframe.image(frame, channels="RGB")
    cap.release()
