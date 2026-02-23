from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")
#load_dotenv()

#embeddings = HuggingFaceEmbeddings()
embeddings = OpenAIEmbeddings()

from langchain_community.vectorstores import FAISS
db = FAISS.load_local("shower", embeddings=embeddings, allow_dangerous_deserialization=True)

# 스트림

import gradio as gr
import random
import time

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def create_generator(text):
    content = "당신은 친절한 어시스턴트입니다. 주어진 데이터를 보고 사용자에 친절하게 대답하세요.\n" 
    content += "*" * 50
    docs = db.similarity_search(text)
    for doc in docs:
        content += doc.page_content + "\n"
        content += "*" * 50
        
    messages = [
        {
          "role": "system",
          "content": content
        },
        {
          "role": "user",
          "content": text
        },
    ]

    gen = openai.chat.completions.create(
      model="gpt-4o-mini",
      messages=messages,
      temperature=0.5,
      max_tokens=512,
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
        # 마지막 사용자 메시지 가져오기
        user_message = history[-1]["content"]
        
        # content가 리스트인 경우 문자열로 변환
        if isinstance(user_message, list):
            user_message = " ".join([item if isinstance(item, str) else str(item) for item in user_message])
        
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

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)
    
demo.queue()
demo.launch(server_name='0.0.0.0')