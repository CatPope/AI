import os
import streamlit as st
import openai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import CrossEncoder
from typing import List
from langchain_core.documents import Document

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")
#load_dotenv()

@st.cache_resource
def get_cross_encoder():
    return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

@st.cache_resource
def get_db():
    return FAISS.load_local("shower", embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)

def rewrite_query(query: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "당신은 검색 쿼리를 개선하는 전문가입니다. 사용자의 질문을 분석하고, 더 정확한 검색 결과를 얻을 수 있도록 쿼리를 재작성해주세요. 원래 의도는 유지하되 더 많은 관련 정보를 검색할 수 있도록 해주세요. 재작성된 쿼리만 출력해주세요"
        },
        {
            "role": "user",
            "content": f"다음 쿼리를 벡터 검색에 더 적합하게 재작성해주세요: '{query}'. 키워드를 추가하거나 더 구체적인 표현으로 바꿔주세요."
        }
    ]
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=256
    )
    
    rewritten_query = response.choices[0].message.content
    return rewritten_query

def rerank_documents(query: str, docs: List[Document], top_k: int = 4) -> List[Document]:
    cross_encoder = get_cross_encoder()
    
    doc_query_pairs = [(query, doc.page_content) for doc in docs]
    scores = cross_encoder.predict(doc_query_pairs)
    
    doc_score_pairs = list(zip(docs, scores))
    ranked_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
    
    return [doc for doc, score in ranked_pairs[:top_k]]

def chat_with_bot(history, db):
    user_query = history[-1]["content"]
    
    rewritten_query = rewrite_query(user_query)
    st.session_state.last_rewritten_query = rewritten_query  
    raw_docs = db.similarity_search(rewritten_query, k=8)
    
    docs = rerank_documents(user_query, raw_docs)
    
    content = "당신은 친절한 어시스턴트입니다. 주어진 데이터를 보고 사용자에 친절하게 대답하세요.\n" 
    content += "*" * 50
    for doc in docs:
        content += doc.page_content + "\n"
        content += "*" * 50
    
    st.sidebar.write("원본 쿼리:", user_query)
    st.sidebar.write("재작성된 쿼리:", rewritten_query)
    
    messages = [
        {
          "role": "system",
          "content": content
        }
    ]
    messages.extend(history)
    
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

def main():
    st.title("Advanced RAG Chatbot with Query Rewrite & Reranking")
    
    if "rewritten_query" not in st.session_state:
        st.session_state.rewritten_query = ""
    
    st.chat_input(placeholder="대화를 입력해주세요.", key="chat_input")
    db = get_db()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if user_input := st.session_state["chat_input"]:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        gen = chat_with_bot(st.session_state.messages, db)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""        
            for chunk in gen:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()