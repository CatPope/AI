# meeting_stt.py
import speech_recognition as sr


class SpeechToText:
    def __init__(self, timeout=300, noise_duration=0.5):
        self.recognizer = sr.Recognizer()
        self.timeout = timeout
        self.noise_duration = noise_duration
        self.accumulated_text = ""

    def transcribe(self):
        print("연속 음성 인식을 시작합니다. 침묵 시 종료됩니다.")

        with sr.Microphone() as source:
            print("환경소음 측정중...")
            self.recognizer.adjust_for_ambient_noise(source, duration=self.noise_duration)

            while True:
                try:
                    print("말씀해주세요...")
                    audio_data = self.recognizer.listen(source, timeout=self.timeout)
                    text = self.recognizer.recognize_google(audio_data, language="ko-KR")
                    print(f"인식된 내용: {text}")
                    self.accumulated_text += text + ".\n"
                    print(f"누적 내용:\n{self.accumulated_text.strip()}")
                    print("-" * 50)

                except sr.UnknownValueError:
                    print("음성을 인식할 수 없습니다.")
                    continue
                except sr.WaitTimeoutError:
                    print("시간 초과로 음성 인식을 종료합니다.")
                    break
                except sr.RequestError as e:
                    print(f"음성 인식 서비스 오류: {e}")
                    break

        return self.accumulated_text.strip()


def run_stt():
    stt = SpeechToText()
    return stt.transcribe()


if __name__ == "__main__":
    result = run_stt()
    print("\n=== 최종 결과 ===")
    print(result)
