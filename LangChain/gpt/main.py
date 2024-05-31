from openai import OpenAI
import argparse
import dotenv
import os

dotenv.load_dotenv()
config = os.getenv('OPENAI_API_KEY')

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, default="../prompts/robo_basic.txt")
parser.add_argument("--sysprompt", type=str, default="C:\Users\USER\Documents\GitHub\AI\LangChain\system_prompts\robo_basic.txt")
args = parser.parse_args()


print("Initializing ChatGPT...")
client = OpenAI(
    api_key = config
)

with open(args.sysprompt, "r") as f:
    sysprompt = f.read()

print(sysprompt)


# chat_history = [
#     {
#         "role": "system",
#         "content": sysprompt
#     },
#     {
#         "role": "user",
#         "content": "나 시험 망쳤어"
#     },
#     {
#         "role": "assistant",
#         "content": """
# 아이고... 괜찮아?
# """
#     }
# ]


# def ask(prompt):
#     chat_history.append(
#         {
#             "role": "user",
#             "content": prompt,
#         }
#     )
#     completion = client.chat.completions.create(
#         # model="gpt-3.5-turbo",
#         model="gpt-4",
#         messages=chat_history,
#         temperature=1
#     )
#     chat_history.append(
#         {
#             "role": "assistant",
#             "content": completion.choices[0].message.content,
#         }
#     )
#     print("take history")
#     print(chat_history)
#     return chat_history[-1]["content"]





# class colors:  # You may need to change color settings
#     RED = "\033[31m"
#     ENDC = "\033[m"
#     GREEN = "\033[32m"
#     YELLOW = "\033[33m"
#     BLUE = "\033[34m"


# while True:
#     question = input(colors.YELLOW + "Jikko> " + colors.ENDC)

#     if question == "!quit" or question == "!exit":
#         break

#     if question == "!clear":
#         os.system("cls")
#         continue

#     response = ask(question)

#     print(f"\n{response}\n")
