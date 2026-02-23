import gradio as gr
import random
import time

import os
import openai

from dotenv import load_dotenv
load_dotenv("/home/ubuntu/work/edu-src-all/.env")

openai.api_key = os.getenv("OPENAI_API_KEY")
chat_logs = []

import tiktoken
from typing import List, Dict, Any

def count_chatml_tokens(messages: List[Dict[str, str]], model = "gpt-4o-mini"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    num_tokens = 0
    
    for message in messages:
        # <|im_start|>{role}\n{content}<|im_end|> 
        num_tokens += 4
        
        for key, value in message.items():
            if value is not None:
                num_tokens += len(encoding.encode(str(value)))
    
    num_tokens += 2
    
    return num_tokens

def create_generator(text):
    message =  {
        "role": "user",
        "content": text
    }
    chat_logs.append(message)            
    
    messages=[
        {
          "role": "system",
          "content": "당신은 친절한 어시스턴트입니다. 사용자의 질문에 친절하게 대답하세요."
        }
    ]
    messages.extend(chat_logs)
        
    gen = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_completion_tokens=4096,
        stream=True
    )
    return gen

def compress_chatlogs():
    global chat_logs

    mid = len(chat_logs) // 2
    first_half = chat_logs[:mid]
    second_half = chat_logs[mid:]

    messages=[
        {
          "role": "system",
          "content": "다음 대화를 최대 3문장으로 간략하게 요약하세요."
        }
    ]
    messages.extend(first_half)
    print(messages)
    
    response = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        max_completion_tokens=1024
    )

    print("압축된 대화: " + response.choices[0].message.content)
    compressed = [{
        "role": "assistant",
        "content": "압축된 대화:" + response.choices[0].message.content
    }]

    chat_logs = compressed + second_half 

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user(user_message, history):
        return "", history + [{"role": "user", "content": user_message}]

    def bot(history):
        # 마지막 사용자 메시지 가져오기
        user_message = history[-1]["content"]
        gen = create_generator(user_message)
        
        # assistant 메시지 추가
        history.append({"role": "assistant", "content": ""})
        
        while True:
            response = next(gen)
            delta = response.choices[0].delta
            if delta.content is not None:
                history[-1]["content"] += delta.content
            else:
                break
            yield history
    
    MAX_TOKENS = 1024

    def add_to_chatlogs(history):
        message =  {
            "role": "assistant",
            "content": history[-1]["content"]
        }
        chat_logs.append(message)          
        if count_chatml_tokens(chat_logs) > MAX_TOKENS:  
            compress_chatlogs()

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    ).then(
        add_to_chatlogs, chatbot, None
    )

    clear.click(lambda: None, None, chatbot, queue=False)
    
demo.queue()
demo.launch(server_name='0.0.0.0')