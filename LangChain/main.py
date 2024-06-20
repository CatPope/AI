from openai import OpenAI
import argparse
import dotenv
import os
from playsound import playsound
from gtts import gTTS
import speech_recognition as sr

dotenv.load_dotenv()
config = os.getenv('OPENAI_API_KEY')

parser = argparse.ArgumentParser()
# parser.add_argument("--prompt", type=str, default="./prompts/robo_basic.txt")
parser.add_argument("--sysprompt", type=str, default="./system_prompts/robo_basic.txt")
args = parser.parse_args()
tts_path = os.path.join(os.getcwd(), 'voice.mp3')


print("Initializing ChatGPT...")
client = OpenAI(
    api_key = config
)


with open(args.sysprompt, "r", encoding='UTF8') as f:
    sysprompt = f.read()


chat_history = [
    {
        "role": "system",
        "content": sysprompt
    }
]


#질문 함수
def ask(prompt):
    chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    completion = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=chat_history,
        temperature=1
    )
    chat_history.append(
        {
            "role": "assistant",
            "content": completion.choices[0].message.content,
        }
    )
    return chat_history[-1]["content"]


# 음성 인식 함수
def stt():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("말씀해주세요...")
        audio_data = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio_data, language="ko-KR")
            print("음성 인식 결과:", text)
        except sr.UnknownValueError:
            print("죄송합니다. 음성을 인식할 수 없습니다.")
        except sr.RequestError as e:
            print(f"음성 인식 서비스 요청에 실패했습니다: {e}")
    return text


class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"


while True:
    question = input(colors.YELLOW + "강정이> " + colors.ENDC)

    if question == "!quit" or question == "!exit":
        break

    if question == "!clear":
        os.system("lcs")
        continue

    if question == "audio":
        question = stt()

    response = ask(question)
    print(f"\n{response}\n")

    tts = gTTS(text=response, lang='ko')
    tts.save(tts_path)
    playsound(tts_path)
