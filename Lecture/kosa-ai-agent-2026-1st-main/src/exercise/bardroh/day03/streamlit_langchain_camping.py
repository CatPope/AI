import os
import streamlit as st
import openai
import json
import requests
from urllib.parse import quote

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")

ServiceKey=os.getenv("GOCAMPING_SERVICE_KEY")

def get_url_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return None
    
@tool
def get_camping_info_context(keyword):
    """Return camping information context for given keyword. keyword should be an word."""
    keyword = quote(keyword)
    url = f"http://apis.data.go.kr/B551011/GoCamping/searchList?serviceKey={ServiceKey}&keyword={keyword}&numOfRows=10&pageNo=1&MobileOS=ETC&MobileApp=TestApp&_type=json"

    result = get_url_content(url)
    data = json.loads(result)
    
    context = ''
    if data['response']['body']['numOfRows'] > 0 :
        sites = data['response']['body']['items']['item']

        i = 1
        for site in sites:
            context = context + str(i) + ") " + site['facltNm'] + ":" + site['intro'] + "\n"
            i = i + 1
    else:
        context = '데이터 없음'
    return context    

@st.cache_resource
def init_agent():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
    
    tools = [get_camping_info_context]
    
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="당신은 캠핑 전문가입니다. 주어진 정보를 보고 고객이 원하는 캠핑장을 검색해서 답변해야 합니다. 답변할 수 없으면 추천할 캠핑장이 없다고 답변하세요."
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
