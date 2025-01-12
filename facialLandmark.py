import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)
mp_drawing_styles = mp.solutions.drawing_styles
landmark_drawing_spec = mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
draw_color = (50, 50, 50)
connection_drawing_spec = mp_drawing.DrawingSpec(color=draw_color, thickness=2)


while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Flip the image horizontally for a later selfie-view display
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)

    # Convert the image back to BGR
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # Create a blank mask to fill the face area
    mask = np.zeros_like(image)

    # Draw the face landmarks and apply mask
    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:

            # Extract the 468 face landmarks
            points = []
            for landmark in landmarks.landmark:
                x = int(landmark.x * image.shape[1])
                y = int(landmark.y * image.shape[0])
                points.append((x, y))

            # Create a convex hull around the face using the landmarks
            points = np.array(points, dtype=np.int32)
            convex_hull = cv2.convexHull(points)

            # Fill the convex hull (the face region) with a color (e.g., red)
            cv2.fillConvexPoly(mask, convex_hull, (200, 160, 120))  # white color

            # opacity = 0.5  # You can adjust this value to make it more or less opaque
            # cv2.addWeighted(image, opacity, mask, 1 - opacity, 0, image)
            image = cv2.addWeighted(image, 1.0, mask, 0.5, 1.0)


            # Draw the face landmarks on the original image
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=connection_drawing_spec
            )

            # Custom connections for nose (for more detailed nose drawing)
            nose_connections = [
                (4, 168),(4, 2), # Nose bridge
            ]

            # Draw custom nose connections
            for connection in nose_connections:
                start_idx, end_idx = connection
                start = landmarks.landmark[start_idx]
                end = landmarks.landmark[end_idx]
                start_point = int(start.x * image.shape[1]), int(start.y * image.shape[0])
                end_point = int(end.x * image.shape[1]), int(end.y * image.shape[0])
                cv2.line(image, start_point, end_point, draw_color, 2)  # Drawing white lines for nose

    # Combine the mask with the original image to show the filled face
    image = cv2.addWeighted(image, 1, mask, 0.6, 0)

    # Show the result
    cv2.imshow('Facial Landmark Detection with Face Mask', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()