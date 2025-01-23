import streamlit as st
import random
import time

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def create_generator(history):
    chat_logs = []

    for item in history:
        if isinstance(item, dict) and "role" in item and "content" in item:
            chat_logs.append(item)
        elif isinstance(item, list) and len(item) == 2:
             if item[0] is not None:
                message = {
                    "role": "user",
                    "content": item[0]
                }
                chat_logs.append(message)
             if item[1] is not None:
                message = {
                    "role": "assistant",
                    "content": item[1]
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
      temperature=0.5,
      max_tokens=2048,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stream=True
    )
    return gen

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("무엇을 도와드릴까요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        gen = create_generator(st.session_state.messages)
        for response in gen:
            delta = response.choices[0].delta
            if delta.content is not None:
                full_response += delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})