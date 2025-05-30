import cv2
import time


def show_window(frame, window_name):
    """
    이미지를 창에 띄우는 함수.
    이미지가 None인 경우는 창을 띄우지 않음.
    """
    if frame is not None:
        cv2.imshow(window_name, frame)


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
        self.prev_face_coords = None  # 이전 얼굴 좌표 (흔들림 최소화용)
        self.alpha = 0.8  # smoothing factor
        self.last_face_check_time = 0  # 마지막 얼굴 확인 시간을 기록할 변수
        self.trace_window = False  # 얼굴 추적 창 활성화 여부
        self.frame_clean = None

    def detect_faces(self, frame, moving_average):
        """
        얼굴을 인식하고 안정화된 좌표로 얼굴을 추적하는 메서드입니다.
        - 이동 평균을 적용하여 얼굴 좌표를 안정화합니다.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        self.trace_window = False  # 얼굴 추적 창이 활성화 되었는지 체크하는 플래그

        for (x, y, w, h) in faces:
            if (moving_average is False) or (self.prev_face_coords is None):
                smoothed_x, smoothed_y, smoothed_w, smoothed_h = x, y, w, h
            else:
                smoothed_x = int(self.alpha * self.prev_face_coords[0] + (1 - self.alpha) * x)
                smoothed_y = int(self.alpha * self.prev_face_coords[1] + (1 - self.alpha) * y)
                smoothed_w = int(self.alpha * self.prev_face_coords[2] + (1 - self.alpha) * w)
                smoothed_h = int(self.alpha * self.prev_face_coords[3] + (1 - self.alpha) * h)

            self.prev_face_coords = (smoothed_x, smoothed_y, smoothed_w, smoothed_h)

            return smoothed_x, smoothed_y, smoothed_w, smoothed_h, faces

        return None, None, None, None, faces


    def process_frame(self, frame, moving_average, face_mark=True):
        """
        프레임을 처리하고 얼굴 인식 및 추적 창을 수행하는 메서드입니다.
        """
        smoothed_x, smoothed_y, smoothed_w, smoothed_h, faces = self.detect_faces(frame, moving_average=moving_average)
        if smoothed_x is not None and smoothed_y is not None:
            # 얼굴 중앙 좌표 계산
            center_x = smoothed_x + smoothed_w // 2
            center_y = smoothed_y + smoothed_h // 2

            # 얼굴 추적을 위한 복사본 생성 (새 창에는 사각형이 보이지 않도록)
            self.frame_clean = frame.copy()

            # 얼굴이 경계선 넘었는지 확인
            # self.check_face_tracking(frame_copy, smoothed_x, smoothed_y, smoothed_w, smoothed_h, center_x, center_y)

            # 얼굴 출력
            focused_face = self.tracking_face(self.frame_clean, center_x, center_y)
            print("얼굴 인식중")

            # 원본 프레임에 얼굴 사각형 표시
            if face_mark:
                cv2.rectangle(frame, (smoothed_x, smoothed_y), (smoothed_x + smoothed_w, smoothed_y + smoothed_h), (0, 255, 0), 2)

            return focused_face
        else:
            print("얼굴이 인식되지 않습니다.")
            return None


    def tracking_face(self, frame, center_x, center_y, window_size=300):
        """
        얼굴을 추적하는 창을 설정하는 메서드입니다.
        - 중앙점을 기준으로 300x300 영역을 추적 창으로 설정 합니다.
        """
        x1 = max(center_x - window_size // 2, 0)
        y1 = max(center_y - window_size // 2, 0)
        x2 = min(center_x + window_size // 2, frame.shape[1])
        y2 = min(center_y + window_size // 2, frame.shape[0])

        focused_face = frame[y1:y2, x1:x2]
        self.trace_window = True

        return focused_face


    def handle_no_face_tracking(self, wait_time=0.9):
        """
        얼굴이 추적 창이 활성화 되지 않았을 때 0.5초 대기 후 다시 확인하는 메서드입니다.
        """
        current_time = time.time()
        if current_time - self.last_face_check_time >= wait_time:
            try:
                cv2.destroyWindow("Focused Face")
            except cv2.error:
                pass  # 창이 없으면 그냥 넘어감
            self.last_face_check_time = current_time



class Alarm(FaceDetector):
    def __init__(self):
        super().__init__()


    def zoom_face(self, frame, window_size=300, scale=1.8):

        central_roi = self.process_frame(frame, moving_average=False, face_mark=False)

        # 화면 사이즈
        x_zoomed = int(window_size * scale)
        y_zoomed = int(window_size * scale)

        if central_roi is not None:
            enlarged_roi = cv2.resize(central_roi, (x_zoomed, y_zoomed), interpolation=cv2.INTER_LINEAR)

            # 확대된 이미지의 중앙에서 300x300 영역 다시 추출
            final_crop_x1 = (x_zoomed - window_size) // 2
            final_crop_y1 = (y_zoomed - window_size) // 2
            final_crop_x2 = final_crop_x1 + window_size
            final_crop_y2 = final_crop_y1 + window_size

            frame_copy = frame.copy()

            final_roi = enlarged_roi[final_crop_y1:final_crop_y2, final_crop_x1:final_crop_x2]

            # 결과 화면 출력
            return final_roi
        else:
            return None


    def check_face_tracking(self, frame, smoothed_x, smoothed_y, smoothed_w, smoothed_h, center_x, center_y):
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
            focused_face = self.tracking_face(frame, center_x, center_y)
            show_window(focused_face, 'Focused Face')




class WebcamCapture:
    """
    웹캠 캡처를 담당하는 클래스입니다.
    """
    def __init__(self):
        """
        웹캠을 연결하고, 캡처된 프레임을 처리하는 초기화 작업을 합니다.
        """
        self.cap = cv2.VideoCapture(0)
        self.face_detector = FaceDetector()  # 얼굴 인식 클래스
        self.alarm = Alarm()

        if not self.cap.isOpened():
            print("웹캠을 열 수 없습니다.")
            exit()

    def run(self):
        """
        웹캠에서 비디오를 실시간으로 캡처하고, 얼굴을 인식하여 처리하는 메서드입니다.
        """
        while True:
            ret, frame = self.cap.read()
            flipped_frame = cv2.flip(frame, 1)

            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            # 얼굴 인식 및 확대 처리
            focused_face = self.face_detector.process_frame(flipped_frame, moving_average=True)
            show_window(focused_face, 'Focused Face')

            zoomed_face = self.alarm.zoom_face(flipped_frame)
            show_window(zoomed_face, 'Zoomed Face')

            # 얼굴이 확대되지 않으면 0.8초 대기 후 다시 확인
            # if not self.face_detector.trace_window:
            #     self.face_detector.handle_no_face_tracking(wait_time=1)

            # 결과 프레임 표시
            show_window(flipped_frame, 'Wab Cam')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()



# 실행 부분
if __name__ == "__main__":
    webcam_capture = WebcamCapture()  # 웹캡 캡처 객체 생성
    webcam_capture.run()  # 웹캡 캡처 실행