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
        self.imotion = '감정'
        self.response = '대답'

        parser = argparse.ArgumentParser()
        parser.add_argument("--sysprompt", type=str, default="./data/system_prompts/robo_basic.txt")
        parser.add_argument("--voice", type=str, default="./data/sound/voice.mp3")
        self.args = parser.parse_args()

        # print("Initializing ChatGPT...")

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
        content = self.chat_history[-1]["content"]
        # print(content)
        response, question = content.split("\\n")
        return response, question


    def TTS(self, source):
        tts = gtts.gTTS(text=source, lang='ko')
        tts.save(self.args.voice)
        try:
            ps.playsound(self.args.voice)
        except Exception as e:
            # print(f"installing voice...")


    def STT(self):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            # print("환경소음 측정중...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            self.TTS("응?")
            try:
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio_data, language="ko-KR")
                # print("음성 인식 결과:", text)
            except sr.UnknownValueError:
                # print("죄송합니다. 음성을 인식할 수 없습니다.")
                self.TTS("미안해. 뭐라고 하는지 모르겠어..")
                text = ""
            except sr.WaitTimeoutError:
                # print("인식 시간 초과")
                self.TTS("다시한번 말해줄래?")
                text = ""
            except sr.RequestError as e:
                # print(f"음성 인식 서비스 요청에 실패했습니다: {e}")
                text = ""
        return text


    def handle_exit(self, question):
        if question in ["잘가", "bye", "빠이", "exit"]:
            self.TTS("좀 있다 이야기 하자~")
            question = ''
        return question


    def get_response_imotion(self):
        # 질문 수동 입력 코드
        question = input("나> ")
        if question == "audio":
            question = self.STT()
        # 질문 음성인식 코드
        # question = self.STT()

        # 질문을 보고 종료할지 결정할 코드
        question = self.handle_exit(question)

        # 질문이 있으면 음성 대답 하는 코드, 없으면 return none
        if question:
            response, imotion = self.ask(question)
            # print(f"강정이>{response}")
            return response, imotion
        else:
            return None, None


if __name__ == "__main__":
    Tk = Talking()
    Tk.run()