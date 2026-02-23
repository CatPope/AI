# pip install langgraph==0.2.74 (ToolNode)

import os
import streamlit as st
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import CrossEncoder
from typing import List, Dict, Any, Annotated, TypedDict, Optional, Union
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")

#load_dotenv()
class GraphState(TypedDict):
    query: str
    rewritten_query: Optional[str]
    retrieved_docs: Optional[List[Document]]
    web_results: Optional[List[Dict[str, str]]]
    relevant_docs_found: bool
    answer: Optional[str]
    answer_quality: Optional[str]
    history: List[Dict[str, str]]
    
@st.cache_resource
def get_cross_encoder():
    return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

@st.cache_resource
def get_db():
    return FAISS.load_local("shower", embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)

def rewrite_query(state: GraphState) -> GraphState:
    """
    Rewrite the query to improve retrieval performance using OpenAI.
    """
    query = state["query"]
    
    messages = [
        {
            "role": "system",
            "content": "당신은 검색 쿼리를 개선하는 전문가입니다. 사용자의 질문을 분석하고, 더 정확한 검색 결과를 얻을 수 있도록 쿼리를 재작성해주세요. 원래 의도는 유지하되 더 많은 관련 정보를 검색할 수 있도록 해주세요."
        },
        {
            "role": "user",
            "content": f"다음 쿼리를 벡터 검색에 더 적합하게 재작성해주세요: '{query}'. 키워드를 추가하거나 더 구체적인 표현으로 바꿔주세요. 재작성된 쿼리만 출력해주세요."
        }
    ]
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=256
    )
    
    rewritten_query = response.choices[0].message.content
    
    new_state = state.copy()
    new_state["rewritten_query"] = rewritten_query
    return new_state

def retrieve_documents(state: GraphState) -> GraphState:
    """
    Retrieve documents from vector store using the rewritten query.
    """
    db = get_db()
    rewritten_query = state["rewritten_query"] or state["query"]
    raw_docs = db.similarity_search(rewritten_query, k=8)
    
    new_state = state.copy()
    new_state["retrieved_docs"] = raw_docs
    return new_state

def rerank_documents(state: GraphState) -> GraphState:
    """
    Rerank documents using a cross-encoder model and check if they're relevant.
    """
    query = state["query"]
    docs = state["retrieved_docs"]
    
    cross_encoder = get_cross_encoder()
    
    doc_query_pairs = [(query, doc.page_content) for doc in docs]
    scores = cross_encoder.predict(doc_query_pairs)
    
    doc_score_pairs = list(zip(docs, scores))
    ranked_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
    
    reranked_docs = [doc for doc, score in ranked_pairs[:4]]
    
    relevant_docs_found = any(score > 8 for _, score in ranked_pairs[:4])
    
    new_state = state.copy()
    new_state["retrieved_docs"] = reranked_docs
    new_state["relevant_docs_found"] = relevant_docs_found
    return new_state

def web_search(state: GraphState) -> GraphState:
    """
    Perform web search using Tavily when no relevant documents are found.
    """
    query = state["query"]
    
    search_tool = TavilySearchResults(k=3)
    web_results = search_tool.invoke(query)
    
    formatted_results = []
    for result in web_results:
        formatted_results.append({
            "title": result.get("title", ""),
            "content": result.get("content", ""),
            "url": result.get("url", "")
        })
    
    new_state = state.copy()
    new_state["web_results"] = formatted_results
    return new_state

def generate_answer(state: GraphState) -> GraphState:
    """
    Generate answer based on retrieved documents or web search results.
    """
    query = state["query"]
    history = state["history"]
    
    if state["relevant_docs_found"]:
        content = "당신은 친절한 어시스턴트입니다. 주어진 데이터를 보고 사용자에 친절하게 대답하세요.\n" 
        content += "*" * 50
        for doc in state["retrieved_docs"]:
            content += doc.page_content + "\n"
            content += "*" * 50
    else:
        content = "당신은 친절한 어시스턴트입니다. 웹 검색 결과를 보고 사용자에 친절하게 대답하세요.\n"
        content += "*" * 50
        for result in state["web_results"]:
            content += f"제목: {result['title']}\n내용: {result['content']}\n출처: {result['url']}\n"
            content += "*" * 50
    
    messages = [
        {
          "role": "system",
          "content": content
        }
    ]
    messages.extend(history)
    
    response = openai.chat.completions.create(
      model="gpt-4o-mini",
      messages=messages,
      temperature=0.5,
      max_tokens=512,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    
    answer = response.choices[0].message.content
    
    new_state = state.copy()
    new_state["answer"] = answer
    return new_state

def evaluate_answer_quality(state: GraphState) -> GraphState:
    """
    Evaluate the quality of the generated answer.
    """
    query = state["query"]
    answer = state["answer"]
    
    messages = [
        {
            "role": "system",
            "content": "당신은 AI 답변의 품질을 평가하는 전문가입니다. 사용자의 질문과 AI의 답변을 분석하고, 답변이 질문에 도움이 되는지 평가해주세요."
        },
        {
            "role": "user",
            "content": f"다음 질문과 답변을 평가하세요:\n\n질문: {query}\n\n답변: {answer}\n\n이 답변이 질문에 도움이 되나요? '도움됨' 또는 '도움안됨' 중 하나로만 응답해주세요."
        }
    ]
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=10
    )
    
    quality_assessment = response.choices[0].message.content
    
    new_state = state.copy()
    new_state["answer_quality"] = quality_assessment
    return new_state

def format_final_answer(state: GraphState) -> GraphState:
    """
    Format the final answer based on quality assessment.
    """
    quality = state["answer_quality"]
    answer = state["answer"]
    
    if "도움됨" in quality:
        final_answer = answer
    else:
        final_answer = "죄송합니다. 이 질문에 대한 적절한 답변을 제공할 수 없습니다. 질문을 더 구체적으로 해주시거나 다른 방식으로 질문해 주세요."
    
    new_state = state.copy()
    new_state["history"].append({"role": "assistant", "content": final_answer})
    return new_state

def should_perform_web_search(state: GraphState) -> str:
    """
    Determine whether to perform web search based on document relevance.
    """
    if state["relevant_docs_found"]:
        return "generate_answer"
    else:
        return "web_search"

def is_answer_helpful(state: GraphState) -> str:
    """
    Determine whether to provide the generated answer based on quality assessment.
    """
    if "도움됨" in state["answer_quality"]:
        return "final_answer"
    else:
        return "final_answer"  

def build_graph() -> StateGraph:
    """
    Build the LangGraph workflow.
    """
    workflow = StateGraph(GraphState)
    
    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("retrieve_documents", retrieve_documents)
    workflow.add_node("rerank_documents", rerank_documents)
    workflow.add_node("web_search", web_search)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("evaluate_answer", evaluate_answer_quality)
    workflow.add_node("final_answer", format_final_answer)
    
    # Add edges to the graph
    workflow.add_edge("rewrite_query", "retrieve_documents")
    workflow.add_edge("retrieve_documents", "rerank_documents")
    workflow.add_conditional_edges(
        "rerank_documents",
        should_perform_web_search,
        {
            "generate_answer": "generate_answer",
            "web_search": "web_search"
        }
    )
    workflow.add_edge("web_search", "generate_answer")
    workflow.add_edge("generate_answer", "evaluate_answer")
    workflow.add_conditional_edges(
        "evaluate_answer",
        is_answer_helpful,
        {
            "final_answer": "final_answer"
        }
    )
    workflow.add_edge("final_answer", END)
    
    workflow.set_entry_point("rewrite_query")
    
    return workflow

def chat_with_graph(state: GraphState) -> GraphState:
    """
    Run the graph with the given state.
    """
    graph = build_graph().compile()
    return graph.invoke(state)

def main():
    st.title("LangGraph RAG Chatbot with Reranking & Web Search")
    
    st.chat_input(placeholder="대화를 입력해주세요.", key="chat_input")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if user_input := st.session_state["chat_input"]:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        messages_for_history = [msg for msg in st.session_state.messages]
        initial_state = GraphState(
            query=user_input,
            rewritten_query=None,
            retrieved_docs=None,
            web_results=None,
            relevant_docs_found=False,
            answer=None,
            answer_quality=None,
            history=messages_for_history
        )
        
        with st.spinner("처리 중..."):
            final_state = chat_with_graph(initial_state)
            st.session_state.last_state = final_state
        
        final_answer = final_state["history"][-1]["content"]
        with st.chat_message("assistant"):
            st.markdown(final_answer)

        st.session_state.messages.append({"role": "assistant", "content": final_answer})
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False
    
    with st.sidebar:
        st.session_state.show_debug = st.toggle("디버그 모드", st.session_state.show_debug)
        
        if st.session_state.show_debug:
            st.subheader("디버그 정보")
            if "last_state" in st.session_state:
                debug_state = st.session_state.last_state
                st.write("원본 쿼리:", debug_state.get("query", ""))
                st.write("재작성된 쿼리:", debug_state.get("rewritten_query", ""))
                st.write("관련 문서 찾음:", debug_state.get("relevant_docs_found", False))
                st.write("웹 검색 수행:", not debug_state.get("relevant_docs_found", True))
                st.write("답변 품질:", debug_state.get("answer_quality", ""))
    

if __name__ == "__main__":
    main()