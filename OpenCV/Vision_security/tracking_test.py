import cv2


class WindowManager:
    def __init__(self):
        self.frame_copy = None

    @staticmethod
    def create_windows():
        cv2.namedWindow("WebCam")
        cv2.namedWindow("Tracking")

    @staticmethod
    def update_window(window_name, frame):
        cv2.imshow(window_name, frame)

    @staticmethod
    def close_windows():
        cv2.destroyAllWindows()

    def set_window_size(self, frame, center_x, center_y, window_size):
        """
        self.frame_copy = frame.copy()

        x1 = max(center_x - window_size // 2, 0)
        y1 = max(center_y - window_size // 2, 0)
        x2 = min(center_x + window_size // 2, self.frame_copy.shape[1])
        y2 = min(center_y + window_size // 2, self.frame_copy.shape[0])

        focused_face = self.frame_copy[y1:y2, x1:x2]
        # self.trace_window = True
        return focused_face
        """
        x1 = max(center_x - window_size // 2, 0)
        y1 = max(center_y - window_size // 2, 0)
        x2 = min(center_x + window_size // 2, frame.shape[1])
        y2 = min(center_y + window_size // 2, frame.shape[0])

        self.frame_copy = frame.copy()

        focused_face = self.frame_copy[y1:y2, x1:x2]
        # self.trace_window = True
        return focused_face


class FaceTracker:
    def __init__(self, window_manager):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.window_manager = window_manager
        self.smoothed_x = None
        self.smoothed_y = None
        self.smoothed_w = None
        self.smoothed_h = None
        self.alpha = 0.8

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def track(self, frame, window_size=300):
        faces = self.detect(frame)
        for (x, y, w, h) in faces:
            if self.smoothed_x is None:
                self.smoothed_x, self.smoothed_y, self.smoothed_w, self.smoothed_h = x, y, w, h
            else:
                self.smoothed_x = int(self.alpha * self.smoothed_x + (1 - self.alpha) * x)
                self.smoothed_y = int(self.alpha * self.smoothed_y + (1 - self.alpha) * y)
                self.smoothed_w = int(self.alpha * self.smoothed_w + (1 - self.alpha) * w)
                self.smoothed_h = int(self.alpha * self.smoothed_h + (1 - self.alpha) * h)

            center_x = self.smoothed_x + self.smoothed_w // 2
            center_y = self.smoothed_y + self.smoothed_h // 2

            smooth_frame = self.window_manager.set_window_size(frame, center_x, center_y, window_size)

            face_coord = (x, y, w, h)

            return smooth_frame, face_coord
        return None, None

    def zoomed_face(self, frame, window_size=300, scale=1.8):
        try:
            frame = frame.copy()
            zoomed_face = None
            faces = self.detect(frame)
            for (x, y, w, h) in faces:
                center_x = x + w // 2
                center_y = y + h // 2

                zoomed_face = self.window_manager.set_window_size(frame, center_x, center_y, window_size)

            # 화면 사이즈
            x_zoomed = int(window_size * scale)
            y_zoomed = int(window_size * scale)

            if zoomed_face is not None:
                enlarged_roi = cv2.resize(zoomed_face, (x_zoomed, y_zoomed), interpolation=cv2.INTER_LINEAR)

                # 확대된 이미지의 중앙에서 300x300 영역 다시 추출
                final_crop_x1 = (x_zoomed - window_size) // 2
                final_crop_y1 = (y_zoomed - window_size) // 2
                final_crop_x2 = final_crop_x1 + window_size
                final_crop_y2 = final_crop_y1 + window_size

                final_roi = enlarged_roi[final_crop_y1:final_crop_y2, final_crop_x1:final_crop_x2]

                # 결과 화면 출력
                return final_roi
            else:
                return None
        except Exception as e:
            print(e)

    def draw_face(self, frame, original_coords=None):
        if frame is None:
            print("No frame")
        elif self.smoothed_x is None:
            pass
        elif original_coords:
            x, y, w, h = original_coords
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        elif original_coords is None:
            cv2.rectangle(frame, (self.smoothed_x, self.smoothed_y), (self.smoothed_x + self.smoothed_w, self.smoothed_y + self.smoothed_h), (255, 0, 0), 2)