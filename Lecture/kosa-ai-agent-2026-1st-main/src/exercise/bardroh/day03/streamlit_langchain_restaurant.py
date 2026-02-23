import os
import streamlit as st
import openai
import json
import requests

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")

@tool
def get_restaurant_info(place, kind):
    """Return restaurant informaton for given place and kind."""
    searching = f"{place} {kind}"
    kakao_api_key = os.getenv("KAKAO_API_KEY")
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(searching)
    headers = {
        "Authorization": f"KakaoAK {kakao_api_key}"
    }
    places = requests.get(url, headers = headers).json()
    return places

@st.cache_resource
def init_agent():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
    
    tools = [get_restaurant_info]
    
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="당신은 식당 추천 전문가입니다. 장소와 종류를 받아서 식당을 추천하세요. 추천할 식당이 없으면 없다고 답하세요."
    )
    return agent

def chat_with_bot(agent, history):
    response = agent.invoke({"messages": history})
    return response["messages"][-1].content

def main():
    st.title("Multi-turn Chatbot with Streamlit and OpenAI(+ Stock)")
    st.chat_input(placeholder="대화를 입력해주세요.", key="chat_input")

    agent = init_agent()

    if "messages" not in st.session_state:
        st.session_state.messages = []        

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.session_state["chat_input"]:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content":user_input})

        with st.spinner('답변을 준비중입니다 ... '):
            response = chat_with_bot(agent, st.session_state.messages)
        with st.chat_message("assistant"):
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content":response})

if __name__ == "__main__":
    main()
