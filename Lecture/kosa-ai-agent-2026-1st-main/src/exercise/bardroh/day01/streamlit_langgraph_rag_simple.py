import os
import streamlit as st
from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Generator, Any

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.vectorstores import FAISS
from langgraph.graph import END, START, StateGraph

load_dotenv("/home/ubuntu/work/edu-src-all/.env")


@st.cache_resource
def get_retriever():
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(
        "shower",
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )
    retriever = vectorstore.as_retriever()
    return retriever

class RAGState(TypedDict):
    query: str
    context: list[str]
    response: Generator[Any, None, None]

def retrieve(state: RAGState) -> RAGState:
    query = state["query"]
    retriever = get_retriever()

    docs = retriever.invoke(query)
    context = [doc.page_content for doc in docs]

    return {**state, "context": context}


def generate_response(state: RAGState) -> RAGState:
    query = state["query"]
    context = state["context"]

    prompt = ChatPromptTemplate.from_template(
        """
다음 정보를 바탕으로 질문에 답변해주세요. 제공된 정보에 답변이 없다면, 
정보가 충분하지 않다고 솔직히 답변해주세요.

정보:
{context}

질문: {query}

답변:
"""
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm | StrOutputParser()

    response = chain.stream(
        {
            "context": "\n\n".join(context),
            "query": query,
        }
    )

    return {**state, "response": response}

@st.cache_resource
def get_graph():
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate_response)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()

def chat_with_bot(messages):
    graph = get_graph()
    inputs = {"query": messages[-1]["content"]}
    print(inputs)

    latest_output = None
    for output in graph.stream(inputs):
        latest_output = output

    for _, value in latest_output.items():
        if isinstance(value, dict) and "response" in value:
            return value["response"]

    return None

def main():
    st.title("Simple RAG Chatbot with Streamlit and OpenAI")
    st.chat_input(placeholder="대화를 입력해주세요.", key="chat_input")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.session_state["chat_input"]:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        response = chat_with_bot(
            [{"role": "user", "content": user_input}]
        )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for chunk in response:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )


if __name__ == "__main__":
    main()
