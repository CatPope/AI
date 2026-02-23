import os
import streamlit as st
from openai import OpenAI
from openai.types.responses import ResponseTextDeltaEvent

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_bot(messages):
    gen = client.responses.create(
        model="gpt-4o-mini",
        input=messages,
        stream=True
    )
    return gen

def main():
    st.title("Multi-turn Chatbot with Responses API")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("대화를 입력해주세요."):
        st.session_state["messages"].append(
            {
                "role":"user",
                "content": user_input
            }
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        gen = chat_with_bot(st.session_state["messages"])
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for event in gen:
                if isinstance(event, ResponseTextDeltaEvent):
                    full_response += event.delta
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        st.session_state["messages"].append(
            {
                "role":"assistant",
                "content": full_response
            }
        )

if __name__ == "__main__":
    main()