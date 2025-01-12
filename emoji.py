import cv2
import numpy as np
import dlib

# Load the Haar Cascade Classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load emoji image with transparency (RGBA)
emoji = cv2.imread('emoji.png', cv2.IMREAD_UNCHANGED)

# Ensure the emoji has 4 channels (RGBA)
if emoji.shape[2] == 4:
    # Extract the alpha channel (transparency)
    alpha_channel = emoji[:, :, 3]
    # Create a 3-channel emoji (without alpha)
    emoji_rgb = emoji[:, :, :3]
else:
    emoji_rgb = emoji
    alpha_channel = np.ones_like(emoji_rgb[:, :, 0]) * 255  # If no alpha, use a full opacity mask

# Get the webcam feed
cap = cv2.VideoCapture(0)  # 0 for default camera

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # Loop through all detected faces
    for (x, y, w, h) in faces:
        # Resize the emoji to fit the detected face
        emoji_resized = cv2.resize(emoji_rgb, (w, h))
        alpha_resized = cv2.resize(alpha_channel, (w, h))

        # Create a mask from the resized emoji alpha channel
        _, mask = cv2.threshold(alpha_resized, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Extract the region of interest (ROI) from the frame where the emoji will be placed
        roi = frame[y:y+h, x:x+w]

        # Create the background of the emoji in the ROI (black out the area where the emoji will go)
        frame_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

        # Take only the emoji region from the emoji image
        emoji_fg = cv2.bitwise_and(emoji_resized, emoji_resized, mask=mask)

        # Add the emoji to the frame
        dst = cv2.add(frame_bg, emoji_fg)

        # Place the final result back into the frame
        frame[y:y+h, x:x+w] = dst

    # Display the resulting frame with emoji overlay
    cv2.imshow('Video Feed with Emoji Overlay', frame)

    # Exit the video window by pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture object and close windows
cap.release()
cv2.destroyAllWindows()
