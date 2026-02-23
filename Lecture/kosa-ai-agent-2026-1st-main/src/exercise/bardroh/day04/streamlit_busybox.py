import asyncio
import atexit
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import streamlit as st

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")
#load_dotenv()

class SyncReActAgent:
    def __init__(self, model_name="gpt-4o-mini", server_config=None):
        self.model = ChatOpenAI(model=model_name)
        self.server_config = server_config or {
            "busybox": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
        self._agent = None
        self._client = None

        # 별도 event loop 생성 (streamlit async loop와 충돌 방지)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._setup())

    async def _setup(self):
        self._client = MultiServerMCPClient(self.server_config)
        #await self._client.__aenter__()
        tools = await self._client.get_tools()
        if not tools:
            raise RuntimeError("No tools found. Check MCP server configuration.")
        self._agent = create_agent(self.model, tools)

    def invoke(self, messages: str):
        return self.loop.run_until_complete(
            self._agent.ainvoke({"messages": messages})
        )

    def close(self):
        try:
            if self._client:
                self.loop.run_until_complete(
                    self._client.__aexit__(None, None, None)
                )
        except Exception as e:
            print(f"[WARN] Agent close failed: {e}")


@st.cache_resource
def init_agent():
    agent = SyncReActAgent()
    atexit.register(agent.close)
    return agent


def chat_with_bot(messages, agent):
    response = agent.invoke(messages)
    return response["messages"][-1].content


def main():
    st.title("Multi-turn Chatbot with Streamlit and MCP")

    agent = init_agent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("대화를 입력해주세요.")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner('답변을 준비중입니다 ...'):
            response = chat_with_bot(st.session_state.messages, agent)

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
