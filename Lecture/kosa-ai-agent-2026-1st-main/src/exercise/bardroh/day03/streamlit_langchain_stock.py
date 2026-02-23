import os
import streamlit as st
import openai
import json
from pykrx import stock

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")
#load_dotenv()

@tool
def get_market_ohlcv(start_date, end_date, ticker):
    """Return prices within given dates for ticker stock. start_date and end_date shoule be 'YYYYMMDD' format."""
    start_date = start_date.strip()
    end_date = end_date.strip()
    ticker = ticker.strip()
    stock_name = stock.get_market_ticker_name(ticker)
    df = stock.get_market_ohlcv(start_date, end_date, ticker)
    df['종목명'] = [stock_name] * len(df)

    return json.dumps(df.to_dict(orient='records'), ensure_ascii=False)

@st.cache_resource
def init_agent():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
    
    tools = [get_market_ohlcv]
    
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="당신은 주식 분석가입니다. 주어진 정보를 보고 주식에 대한 의견을 전달하세요."
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
