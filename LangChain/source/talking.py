from openai import OpenAI
import argparse
import os
import dotenv
import gtts
import playsound as ps
import speech_recognition as sr
import time


class Talking:
    def __init__(self):
        self.stop = False

        parser = argparse.ArgumentParser()
        parser.add_argument("--sysprompt", type=str, default="./data/system_prompts/robo_basic.txt")
        parser.add_argument("--voice", type=str, default="./data/sound/voice.mp3")
        self.args = parser.parse_args()

        print("Initializing ChatGPT...")

        dotenv.load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key = api_key)

        with open(self.args.sysprompt, "r", encoding='UTF-8') as f:
            sysprompt = f.read()

        self.chat_history = [
            {
                "role": "system",
                "content": sysprompt
            }
        ]

        self.TTS("준비 됐어!")


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
        tts.save(self.args.voice)
        try:
            ps.playsound(self.args.voice)
        except Exception as e:
            print(f"installing voice...")


    def STT(self):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("환경소음 측정중...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("이제 말해줘...")
            self.TTS("응?")
            try:
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio_data, language="ko-KR")
                print("음성 인식 결과:", text)
            except sr.UnknownValueError:
                print("죄송합니다. 음성을 인식할 수 없습니다.")
                self.TTS("미안해. 뭐라고 하는지 모르겠어..")
                text = ""
            except sr.WaitTimeoutError:
                print("인식 시간 초과")
                self.TTS("다시한번 말해줄래?")
                text = ""
            except sr.RequestError as e:
                print(f"음성 인식 서비스 요청에 실패했습니다: {e}")
                text = ""
        return text


    def stop_handle(self):
        if self.stop:
            self.stop = False
            self.TTS("필요하면 불러줘")
        else:
            self.stop = True


    def handle_exit(self, question):
        if question in ["잘가", "bye", "빠이", "exit"]:
            self.stop = True
            question = ''
        return question


    def run(self):
        # 택스트 수동 입력 코드
        question = input("나> ")
        if question == "audio":
            question = self.STT()

        # question = self.STT()

        self.handle_exit(question)
        if self.stop:
            print("대화를 종료합니다.")
            self.TTS("안녕~")
            question = ""

        if question:
            response = self.ask(question)
            print(f"강정이>{response}")
            self.TTS(response)


if __name__ == "__main__":
    Tk = Talking()
    Tk.run()