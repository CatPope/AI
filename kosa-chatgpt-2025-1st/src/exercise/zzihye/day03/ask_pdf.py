import gradio as gr
from langchain_community.vectorstores import FAISS
from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain

import os

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("환경 변수 'OPENAI_API_KEY'를 설정하세요.")

# VectorDB 로드
vectorstore = FAISS.load_local(
    "vectordb",
    OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
    allow_dangerous_deserialization=True
)
print("VectorDB 로드 성공!")  # 로드 성공 여부 확인

# LangChain Q&A 체인 생성
llm = OpenAI(temperature=0, max_tokens=150)  # 최대 150 토큰으로 응답 제한

qa_chain = load_qa_chain(llm, chain_type="stuff")

# 질문에 답변하는 함수
def answer_question(question):
    print(f"질문: {question}")
    docs = vectorstore.similarity_search(question, k=1)  # 상위 1개 문서만 검색
    
    # 문서 길이 제한
    MAX_TOKENS = 2000  # 최대 2000 토큰으로 제한
    truncated_docs = []
    total_length = 0
    
    for doc in docs:
        if total_length + len(doc.page_content) > MAX_TOKENS:
            break
        truncated_docs.append(doc)
        total_length += len(doc.page_content)
    
    print(f"사용된 문서 총 길이: {total_length} 토큰")
    return qa_chain.run(input_documents=truncated_docs, question=question)

# Gradio 인터페이스
with gr.Blocks() as demo:
    gr.Markdown("## PDF 기반 ChatGPT")
    question = gr.Textbox(label="질문 입력", placeholder="PDF 내용에 대해 물어보세요.")
    answer = gr.Textbox(label="답변", interactive=False)
    ask_button = gr.Button("질문하기")
    ask_button.click(fn=answer_question, inputs=[question], outputs=[answer])

demo.launch()
