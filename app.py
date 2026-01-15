import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Virtual Paint", layout="wide")

st.title("🎨 Virtual Paint Application")
st.markdown("Draw in air using a **colored object** (blue marker recommended).")

# Sidebar controls
st.sidebar.header("Controls")
run = st.sidebar.checkbox("Start Camera")

color_option = st.sidebar.selectbox(
    "Brush Color",
    ("Blue", "Green", "Red", "Yellow")
)

clear = st.sidebar.button("Clear Canvas")

# Color mapping
color_map = {
    "Blue": (255, 0, 0),
    "Green": (0, 255, 0),
    "Red": (0, 0, 255),
    "Yellow": (0, 255, 255)
}
draw_color = color_map[color_option]

# HSV range for BLUE object (best for tracking)
lower_color = np.array([100, 150, 50])
upper_color = np.array([140, 255, 255])

frame_placeholder = st.empty()

if run:
    cap = cv2.VideoCapture(0)

    canvas = None
    prev_x, prev_y = 0, 0

    while run:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera not accessible")
            break

        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = np.zeros_like(frame)

        if clear:
            canvas = np.zeros_like(frame)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_color, upper_color)

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 500:
                x, y, w, h = cv2.boundingRect(c)
                cx = x + w // 2
                cy = y + h // 2

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = cx, cy

                cv2.line(canvas, (prev_x, prev_y), (cx, cy), draw_color, 5)
                prev_x, prev_y = cx, cy
        else:
            prev_x, prev_y = 0, 0

        output = cv2.add(frame, canvas)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

        frame_placeholder.image(output, channels="RGB")

    cap.release()
else:
    st.info("Enable **Start Camera** to begin drawing 🎨")
