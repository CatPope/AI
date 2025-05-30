import cv2
from tracking_test import WindowManager, FaceTracker
from boundary import Boundary, WarningManager
import asyncio


class LineBoundary(Boundary):
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point

    def draw_boundary(self, frame):
        cv2.line(frame, self.start_point, self.end_point, (0, 0, 255), 2)

    def is_crossed(self, face_coords):
        top_y, bottom_y, left_x, right_x = face_coords
        if top_y > self.end_point[1]:
            return False
        else:
            return True


def line_over():
    cap = cv2.VideoCapture(0)
    window_manager = WindowManager()
    face_tracker = FaceTracker(window_manager)

    line_boundary = LineBoundary(start_point=(100, 100), end_point=(500, 100))
    warning_manager = WarningManager(line_boundary)
    window_manager.create_windows()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        tracked_face, face_coords = face_tracker.track(frame)
        zoomed_face = face_tracker.zoomed_face(frame)

        face_tracker.draw_face(frame)
        face_tracker.draw_face(frame, face_coords)

        if face_coords is not None:
            warning = warning_manager.check_boundary(face_coords)
            if warning:
                warning_manager.trigger_warning()

        if tracked_face is not None:
            window_manager.update_window("Tracking", tracked_face)
            window_manager.update_window("Zoom Face", tracked_face)

        line_boundary.draw_boundary(frame)  # Example coordinates

        window_manager.update_window("WebCam", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    window_manager.close_windows()

if __name__ == "__main__":
    line_over()
