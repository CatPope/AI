import os
import asyncio
import streamlit as st
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, FileSearchTool, WebSearchTool, TResponseInputItem, RunResult
 
from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")

import nest_asyncio
nest_asyncio.apply()

rag_agent = Agent(
    name="rag_agent",
    instructions="당신은 RAG 에이전트입니다. 소년과 소녀에 대한 질문을 처리할 수 있습니다.",
    handoff_description="소년과 소녀에 대한 질문은 이 에이전트가 처리합니다.",
    tools=[
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["vs_68eb15438bf48191a5ac66096a90193e"],
        )
    ]
)

websearch_agent = Agent(
    name="websearch_agent",
    instructions="당신은 웹검색 에이전트입니다. 일반적인 질문을 검색하여 처리할 수 있습니다.",
    handoff_description="소년과 소녀에 대한 것이 아닌 질문은 이 에이전트가 처리합니다.",
    tools=[WebSearchTool()]
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions="당신은 친절한 어시스턴트입니다. 사용자의 질문에 친절하게 대답하세요.",
    handoffs=[rag_agent, websearch_agent]
#    tools = [
#        rag_agent.as_tool(
#             tool_name="rag",
#           tool_description="소년과 소녀에 대한 질문을 RAG으로 검색하여 답변할 수 있다.",
#        ),       
#        websearch_agent.as_tool(
#             tool_name="websearch",
#            tool_description="소년과 소녀에 대한 것이 아닌 질문을 웹검색하여 답변할 수 있다.",
#        )
#    ]
)

async def chat_with_bot(messages):
    input_items: list[TResponseInputItem] = []

    for role, content in messages:
        if role == "user":
            input_items.append({"role": "user", "content": content})
        else:
            input_items.append({"role": "assistant", "content": content})
    
    result = Runner.run_sync(orchestrator_agent, input=input_items)
    return result.final_output

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
                full_response = await chat_with_bot(st.session_state["messages"])
                message_placeholder.markdown(full_response)
            
            asyncio.run(stream_response())

        st.session_state["messages"].append(("assistant", full_response))

if __name__ == "__main__":
    main()