from openai import OpenAI
import re
import argparse
# from jikko.jikko import *
import math
import numpy as np
import os
import json
import time

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, default="./prompts/robo_basic.txt")
parser.add_argument("--sysprompt", type=str, default="./system_prompts/robo_basic.txt")
args = parser.parse_args()

with open('./config.json', 'r') as f:
    config = json.load(f)

print("Initializing ChatGPT...")
client = OpenAI(
    api_key = config["OPENAI_API_KEY"]
)

with open(args.sysprompt, "r") as f:
    sysprompt = f.read()

chat_history = [
    {
        "role": "system",
        "content": sysprompt
    },
    {
        "role": "user",
        "content": "LED와 부저를 키고싶어"
    },
    {
        "role": "assistant",
        "content": """```python
jk.led_digital(5, HIGH), jk.buzzer(6, 128, 1)
```

이 코드는 지정된 LED 핀을 HIGH로 설정하여 LED를 켜고, 지정된 부저 핀에서 128Hz 주파수의 소리를 1초 동안 발생시킵니다. jk.led_digital(LED_PIN, HIGH) 함수는 지정된 핀 번호에 연결된 LED를 켭니다.  jk.buzzer 함수에서 주파수와 지속 시간을 변경하여 다양한 소리를 낼 수 있습니다."""
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
        temperature=0
    )
    chat_history.append(
        {
            "role": "assistant",
            "content": completion.choices[0].message.content,
        }
    )
    return chat_history[-1]["content"]


print(f"Done.")

code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)


def extract_python_code(content):
    code_blocks = code_block_regex.findall(content)
    if code_blocks:
        full_code = "\n".join(code_blocks)

        if full_code.startswith("python"):
            full_code = full_code[7:]

        return full_code
    else:
        return None


class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"


# print(f"Initializing Jikko...")
# jk = Pyjikko()
# PORT = 'COM3'
# jk.serial_connect(PORT)
# jk.start()
# print(f"Done.")

# with open(args.prompt, "r", encoding='UTF8') as f:
#     prompt = f.read()

# ask(prompt)
# print("Welcome to the Jikko chatbot! I am ready to help you with your Jikko questions and commands.")

# while True:
#     question = input(colors.YELLOW + "Jikko> " + colors.ENDC)

#     if question == "!quit" or question == "!exit":
#         break

#     if question == "!clear":
#         os.system("cls")
#         continue

#     response = ask(question)

#     light, temp, humi, soil = 0, 0, 0, 0

#     print(f"\n{response}\n")

#     code = extract_python_code(response)
#     if code is not None:
#         print("Please wait while I run the code in Jikko...")
#         exec(extract_python_code(response))
#         print("Done!\n")

#         # 이 아래 스마트팜 값에 맞춰 작동하는 기능 작성하세요
#         if light > 600:
#             print('어두운 상태')
