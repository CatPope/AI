import cv2
import time  # 시간을 다루기 위한 모듈 추가

class FaceDetector:
    """
    얼굴 인식과 관련된 기능을 담당하는 클래스입니다.
    """
    def __init__(self):
        """
        클래스 초기화
        - Haar Cascade 얼굴 인식 모델 로드
        - 웹캠 연결 설정
        """
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.prev_face_coords = None  # 이전 얼굴 좌표 (흔들림 최소화용)
        self.alpha = 0.8  # smoothing factor
        self.last_face_check_time = 0  # 마지막 얼굴 확인 시간을 기록할 변수
        self.face_zoomed = False  # 얼굴 확대 여부

        if not self.cap.isOpened():
            print("웹캠을 열 수 없습니다.")
            exit()

    def detect_faces(self, frame):
        """
        얼굴을 인식하고 안정화된 좌표로 얼굴을 추적하는 메서드입니다.
        - 이동 평균을 적용하여 얼굴 좌표를 안정화합니다.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        self.face_zoomed = False  # 얼굴 확대가 수행되었는지 체크하는 플래그

        for (x, y, w, h) in faces:
            if self.prev_face_coords is None:
                smoothed_x, smoothed_y, smoothed_w, smoothed_h = x, y, w, h
            else:
                smoothed_x = int(self.alpha * self.prev_face_coords[0] + (1 - self.alpha) * x)
                smoothed_y = int(self.alpha * self.prev_face_coords[1] + (1 - self.alpha) * y)
                smoothed_w = int(self.alpha * self.prev_face_coords[2] + (1 - self.alpha) * w)
                smoothed_h = int(self.alpha * self.prev_face_coords[3] + (1 - self.alpha) * h)

            self.prev_face_coords = (smoothed_x, smoothed_y, smoothed_w, smoothed_h)

            return smoothed_x, smoothed_y, smoothed_w, smoothed_h, faces

        return None, None, None, None, None

    def zoom_face(self, frame, center_x, center_y, zoom_size=300):
        """
        얼굴을 확대하여 보여주는 메서드입니다.
        - 중앙점을 기준으로 300x300 영역을 확대하여 보여줍니다.
        """
        x1 = max(center_x - zoom_size // 2, 0)
        y1 = max(center_y - zoom_size // 2, 0)
        x2 = min(center_x + zoom_size // 2, frame.shape[1])
        y2 = min(center_y + zoom_size // 2, frame.shape[0])

        enlarged_face = frame[y1:y2, x1:x2]
        cv2.namedWindow("Zoomed Face", cv2.WINDOW_NORMAL)
        cv2.imshow("Zoomed Face", enlarged_face)
        self.face_zoomed = True

    def process_frame(self, frame):
        """
        프레임을 처리하고 얼굴 인식 및 확대를 수행하는 메서드입니다.
        """
        smoothed_x, smoothed_y, smoothed_w, smoothed_h, faces = self.detect_faces(frame)
        if smoothed_x is not None and smoothed_y is not None:
            # 얼굴 중앙 좌표 계산
            center_x = smoothed_x + smoothed_w // 2
            center_y = smoothed_y + smoothed_h // 2

            # 대각선 및 얼굴 확대 확인
            self.draw_diagonals(frame, smoothed_x, smoothed_y, smoothed_w, smoothed_h)
            self.check_face_zoom(frame, smoothed_x, smoothed_y, smoothed_w, smoothed_h, center_x, center_y)

    def draw_diagonals(self, frame, smoothed_x, smoothed_y, smoothed_w, smoothed_h):
        """
        얼굴 주변에 두 개의 대각선을 그리는 메서드입니다.
        """
        cv2.line(frame, (500, 400), (400, 50), (0, 0, 255), 2)  # 빨간색
        cv2.line(frame, (100, 400), (200, 50), (0, 0, 255), 2)  # 빨간색

    def check_face_zoom(self, frame, smoothed_x, smoothed_y, smoothed_w, smoothed_h, center_x, center_y):
        """
        얼굴이 대각선 아래에 위치하면 확대하여 보여주는 메서드입니다.
        """
        m1 = (50 - 400) / (400 - 500)  # 기울기
        b1 = 400 - m1 * 500           # y 절편
        m2 = (50 - 400) / (200 - 100)  # 기울기
        b2 = 400 - m2 * 100           # y 절편
        bottom_y = smoothed_y + smoothed_h
        left_x = smoothed_x
        right_x = smoothed_x + smoothed_w

        # 얼굴의 하단이 대각선 아래에 있는지 확인
        if (bottom_y <= m1 * right_x + b1) or (bottom_y <= m2 * left_x + b2):
            self.zoom_face(frame, center_x, center_y)

    def handle_no_face_zoom(self):
        """
        얼굴이 확대되지 않았을 때 0.5초 대기 후 다시 확인하는 메서드입니다.
        """
        current_time = time.time()
        if current_time - self.last_face_check_time >= 0.5:
            try:
                cv2.destroyWindow("Zoomed Face")
            except cv2.error:
                pass  # 창이 없으면 그냥 넘어감
            self.last_face_check_time = current_time

class WebcamCapture:
    """
    웹캠 캡처를 담당하는 클래스입니다.
    """
    def __init__(self):
        """
        웹캠을 연결하고, 캡처된 프레임을 처리하는 초기화 작업을 합니다.
        """
        self.face_detector = FaceDetector()  # 얼굴 인식 클래스
        self.cap = cv2.VideoCapture(0)

    def run(self):
        """
        웹캠에서 비디오를 실시간으로 캡처하고, 얼굴을 인식하여 처리하는 메서드입니다.
        """
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # 얼굴 인식 및 확대 처리
            self.face_detector.process_frame(frame)

            # 얼굴이 확대되지 않으면 0.5초 대기 후 다시 확인
            if not self.face_detector.face_zoomed:
                self.face_detector.handle_no_face_zoom()

            # 결과 프레임 표시
            cv2.imshow('Face Detection with Diagonal Lines', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


# 실행 부분
if __name__ == "__main__":
    webcam_capture = WebcamCapture()  # 웹캡 캡처 객체 생성
    webcam_capture.run()  # 웹캡 캡처 실행
