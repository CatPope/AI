import gradio as gr
import random
import time

import os
import openai

from dotenv import load_dotenv
load_dotenv("/home/ubuntu/work/edu-src-all/.env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def create_generator(history):
    messages = [
        {
          "role": "system",
          "content": "당신은 친절한 어시스턴트입니다. 사용자의 질문에 친절하게 대답하세요."
        }
    ]
    
    for item in history:
        if item.get("content"): 
            messages.append(item)
        
    gen = openai.chat.completions.create(
      model="gpt-4o-mini",
      messages=messages,
      temperature=0.5,
      max_tokens=4096,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stream=True
    )
    return gen

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user(user_message, history):
        return "", history + [{"role": "user", "content": user_message}]

    def bot(history):
        history.append({"role": "assistant", "content": ""})
        
        gen = create_generator(history)
        
        while True:
            response = next(gen)
            delta = response.choices[0].delta
            if delta.content is not None:
                history[-1]["content"] += delta.content
            else:
                break
            yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)
    
demo.queue()
demo.launch(server_name='0.0.0.0')