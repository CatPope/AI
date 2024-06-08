from openai import OpenAI
import argparse
import dotenv
import os

dotenv.load_dotenv()
config = os.getenv('OPENAI_API_KEY')

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, default="./prompts/robo_basic.txt")
parser.add_argument("--sysprompt", type=str, default="./system_prompts/robo_basic.txt")
args = parser.parse_args()


print("Initializing ChatGPT...")
client = OpenAI(
    api_key = config
)

with open(args.sysprompt, "r", encoding='utf8') as f:
    sysprompt = f.read()



chat_history = [
    {
        "role": "system",
        "content": sysprompt
    },
    {
        "role": "user",
        "content": "나 시험 망쳤어"
    },
    {
        "role": "assistant",
        "content": """
정말..? 시험이 잘 안 풀려서 정말 속상하겠어. 분명히 열심히 준비했을 텐데, 원하는 결과를 얻지 못하면 누구라도 힘들겠지.
하지만 이 시험이 너의 전체 인생을 결정짓는 건 아니야. 이번 경험을 통해 더 성장할 수 있는 계기가 될 거야.
다음에 더 잘할 수 있는 기회가 분명히 올 테니까, 너무 자책하지 말고 스스로를 다독여 주자.
"""
    }
]


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
        os.system("cls")
        continue

    response = ask(question)

    print(f"\n{response}\n")
