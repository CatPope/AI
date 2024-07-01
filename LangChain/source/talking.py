from openai import OpenAI
import argparse
import os
import dotenv
import gtts
import playsound as ps
import speech_recognition as sr


class Talking:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--sysprompt", type=str, default=r"C:\Users\USER\Documents\GitHub\AI\LangChain\data\system_prompts")
        args = parser.parse_args()

        print("Initializing ChatGPT...")

        dotenv.load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key = api_key)


        with open(args.sysprompt, "r", encoding='utf-8') as f:
            sysprompt = f.read()


        self.chat_history = [
            {
                "role": "system",
                "content": sysprompt
            },
            {
                "role": "user",
                "content": "오늘 계단에서 굴렀어"
            },
            {
                "role": "assistant",
                "content": "아이고... 괜찮아? 다친곳은 없어?"
            }
        ]


    def ask(self, prompt):
        self.chat_history.append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages = self.chat_history,
            temperature=0
        )
        self.chat_history.append(
            {
                "role": "assistant",
                "content": completion.choices[0].message.content,
            }
        )
        return self.chat_history[-1]["content"]


    def TTS(self, source):
        tts = gtts.gTTS(text=source, lang='ko')
        tts.save('./data/voice.mp3')
        ps.playsound('./data/voice.mp3')


    def STT(self):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("환경 소음 조정 중...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("듣기 시작...")

            try:
                while True:
                    # 음성을 듣고 최대 5초 동안 대기, 최대 10초 동안 듣기
                    print("음성 대기 중...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # 음성을 인식하여 텍스트로 변환
                    print("음성 인식 중...")
                    text = recognizer.recognize_google(audio, language="ko-KR")
                    print(f"인식된 텍스트: {text}")
                    
                    # 인식된 텍스트가 "a"이면 프로그램 종료
                    if text.lower() == "a":
                        print("사용자가 종료를 요청했습니다.")
                        break
                    


            except sr.WaitTimeoutError:
                print("음성이 시작되기를 기다리는 중 타임아웃 발생")
                self.TTS("다시한번 말해줄래?")
            except sr.UnknownValueError:
                print("음성을 이해할 수 없음")
                self.TTS("미안해. 뭐라고 이야기 하는지 모르겠어.")
            except sr.RequestError as e:
                print(f"요청 오류 발생: {e}")
                self.TTS("요청 오류 발생 삐빅")
            except KeyboardInterrupt:
                print("사용자에 의해 프로그램 종료")


    class colors:  # You may need to change color settings
        RED = "\033[31m"
        ENDC = "\033[m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"


    def run(self):
        while True:
            question = input(self.colors.YELLOW + "강정이> " + self.colors.ENDC)

            if question == "!quit" or question == "!exit":
                break

            if question == "!clear":
                os.system("cls")
                continue

            response = self.ask(question)

            print(f"\n{response}\n")


if __name__ == "__main__":
    Tk = Talking()
    Tk.run()