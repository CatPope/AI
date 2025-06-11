import speech_recognition as sr


def STT():
    recognizer = sr.Recognizer()
    accumulated_text = ""  # 누적된 텍스트 저장

    print("연속 음성 인식을 시작합니다. 5분 동안 침묵하면 종료됩니다.")

    with sr.Microphone() as source:
        print("환경소음 측정중...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        while True:
            try:
                print("말씀해주세요... (5분 타임아웃)")
                # 5분(300초) 타임아웃, 자동 침묵 감지로 발화 완료 판단
                audio_data = recognizer.listen(source, timeout=300)

                # 음성 인식 수행
                text = recognizer.recognize_google(audio_data, language="ko-KR")
                print(f"인식된 내용: {text}")

                # 누적 텍스트에 추가 (마침표와 줄바꿈 포함)
                accumulated_text += text + ".\n"
                print(f"현재까지 누적: {accumulated_text.strip()}")
                print("-" * 50)

            except sr.UnknownValueError:
                print("음성을 인식할 수 없습니다. 다시 말씀해주세요.")
                continue

            except sr.WaitTimeoutError:
                print("5분 동안 침묵하여 음성 인식을 종료합니다.")
                break

            except sr.RequestError as e:
                print(f"음성 인식 서비스 요청에 실패했습니다: {e}")
                break

    return accumulated_text.strip()  # 마지막 줄바꿈 제거하여 반환


# 실행
if __name__ == "__main__":
    result = STT()
    print("\n=== 최종 결과 ===")
    print(result)