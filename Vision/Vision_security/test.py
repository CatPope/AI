import cv2

# Haar Cascade 얼굴 인식 모델 로드
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 웹캠 실행
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("카메라 프레임을 가져올 수 없습니다.")
        break

    # 원본 프레임의 복사본 생성 (새 창에 표시할 얼굴 영역 추출용)
    frame_copy = frame.copy()

    # 흑백 변환 (Haar Cascade는 흑백 이미지에서 동작)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 얼굴 감지
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # 원본 프레임에 얼굴 사각형 표시
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 복사본에서 얼굴 영역 추출 (사각형이 그려지기 전의 이미지)
        face_roi = frame_copy[y:y+h, x:x+w]

        # 얼굴 영역이 올바르게 추출되었으면 크기를 조정하여 새로운 창에 표시
        if face_roi.size > 0:
            face_resized = cv2.resize(face_roi, (200, 200))  # 예: 200x200 크기로 리사이즈
            cv2.imshow("Detected Face", face_resized)

    # 전체 웹캠 화면 출력 (여기에는 얼굴 사각형이 표시됨)
    cv2.imshow("Face Detection", frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
