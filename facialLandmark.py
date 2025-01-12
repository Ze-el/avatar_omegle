import asyncio
import websockets
import cv2
import mediapipe as mp
import numpy as np
import base64
import json

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# WebSocket server settings
HOST = "0.0.0.0"
PORT = 8765  # You can choose a different port if needed

async def send_frames(websocket, path="/"):  # Accept both websocket and path arguments
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
        
        # Ensure aspect ratio is preserved and avoid using NORM_RECT if aspect ratio is not square

        # Process with MediaPipe FaceMesh
        results = face_mesh.process(image_rgb)

        # Convert the image back to BGR for further processing
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

                # Fill the convex hull (the face region) with a color
                cv2.fillConvexPoly(mask, convex_hull, (200, 160, 120))

                # Blend the mask with the original image
                image = cv2.addWeighted(image, 1.0, mask, 0.5, 1.0)
                # Draw the face landmarks on the original image
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=connection_drawing_spec
                )
                image = cv2.addWeighted(image, 1, mask, 0.6, 0)

        # Encode image to JPEG
        ret, jpeg = cv2.imencode('.jpg', image)
        if ret:
            # Convert to base64
            base64_image = base64.b64encode(jpeg).decode('utf-8')
            frame_message = json.dumps({"frame": base64_image})

            # Send the base64 image as a message to the frontend
            await websocket.send(frame_message)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

async def main():
    # Start WebSocket server
    async with websockets.serve(send_frames, HOST, PORT):
        print(f"WebSocket server started at ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

# Run WebSocket server
asyncio.run(main())
