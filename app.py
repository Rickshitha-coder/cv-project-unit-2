import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Virtual Paint (Cloud-Compatible)", layout="wide")
st.title("🎨 Virtual Paint Application (Video Upload Version)")
st.markdown("Upload a video and draw in air using a colored object (blue marker recommended).")

# Sidebar controls
st.sidebar.header("Controls")
color_option = st.sidebar.selectbox(
    "Brush Color",
    ("Blue", "Green", "Red", "Yellow")
)
clear_canvas = st.sidebar.button("Clear Canvas")

# Color mapping
color_map = {
    "Blue": (255, 0, 0),
    "Green": (0, 255, 0),
    "Red": (0, 0, 255),
    "Yellow": (0, 255, 255)
}
draw_color = color_map[color_option]

# File uploader
uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    st.info("Processing video. Please wait...")
    
    # Read video frames
    tfile = uploaded_file
    cap = cv2.VideoCapture(tfile.name if hasattr(tfile, 'name') else uploaded_file)
    
    canvas = None
    prev_x, prev_y = 0, 0

    stframe = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip for natural orientation

        if canvas is None:
            canvas = np.zeros_like(frame)

        if clear_canvas:
            canvas = np.zeros_like(frame)

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # HSV range for BLUE object
        lower_color = np.array([100, 150, 50])
        upper_color = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)

        # Remove noise
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 500:
                x, y, w, h = cv2.boundingRect(c)
                cx = x + w // 2
                cy = y + h // 2

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = cx, cy

                # Draw line
                cv2.line(canvas, (prev_x, prev_y), (cx, cy), draw_color, 5)
                prev_x, prev_y = cx, cy
        else:
            prev_x, prev_y = 0, 0

        # Combine canvas and frame
        output = cv2.add(frame, canvas)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

        stframe.image(output, channels="RGB", use_column_width=True)

    cap.release()
    st.success("Video processing completed!")
else:
    st.info("Upload a video to start drawing.")
