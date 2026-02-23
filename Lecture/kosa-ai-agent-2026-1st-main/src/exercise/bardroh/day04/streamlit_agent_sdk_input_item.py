import os
import asyncio
import streamlit as st
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, TResponseInputItem
 
from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")

agent = Agent(
    name="ChatBot",
    instructions="당신은 친절한 어시스턴트입니다. 사용자의 질문에 친절하게 대답하세요.",
    model="gpt-4o-mini"
)

async def chat_with_bot(messages):
    input_items: list[TResponseInputItem] = []

    for role, content in messages:
        if role == "user":
            input_items.append({"role": "user", "content": content})
        else:
            input_items.append({"role": "assistant", "content": content})
    
    result = Runner.run_streamed(agent, input=input_items)
    return result

def main():
    st.title("Multi-turn Chatbot with Agent SDK")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 이전 메시지 표시
    for role, content in st.session_state["messages"]:
        with st.chat_message(role):
            st.markdown(content)

    if user_input := st.chat_input("대화를 입력해주세요."):
        st.session_state["messages"].append(("user", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            async def stream_response():
                nonlocal full_response
                result = await chat_with_bot(st.session_state["messages"])
                
                async for event in result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        full_response += event.data.delta
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            
            asyncio.run(stream_response())

        st.session_state["messages"].append(("assistant", full_response))

if __name__ == "__main__":
    main()