# db.simlarity_search 버그 수정 필요
import streamlit as st
import os
import openai
import time
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI  # import 경로 수정
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores.faiss import FAISS  # import 경로 수정

openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_resource
def get_db():
    return FAISS.load_local("pdf", embeddings=OpenAIEmbeddings, allow_dangerous_deserialization=True)

def chat_with_bot(history, db):
    content = "당신은 친절한 어시스턴트입니다. 주어진 데이터를 보고 사용자에 친절하게 대답하세요.\n" 
    content += "*" * 50
    docs = db.similarity_search(history[-1]["content"])
    for doc in docs:
        content += doc.page_content + "\n"
        content += "*" * 50
        
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
      max_tokens=512,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stream=True
    )
    return gen

# 세션 상태
if "index" not in st.session_state:
    st.session_state.index = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("PDF 문서 질의응답")

uploaded_file = st.file_uploader("PDF 파일 업로드", type="pdf")

if uploaded_file:
    if st.session_state.index is None:
        try:
            with st.spinner("PDF 파일 처리 중..."):
                bytes_data = uploaded_file.read()
                with open("temp.pdf", "wb") as f:  # 임시 파일 저장
                    f.write(bytes_data)
                    loader = PyPDFLoader("temp.pdf")
                    documents = loader.load()
                    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                    docs = text_splitter.split_documents(documents)
                    
                    embeddings = OpenAIEmbeddings()
                    index = VectorstoreIndexCreator(
                                vectorstore_cls=FAISS,
                                embedding=embeddings,
                            ).from_loaders([loader])
                    st.session_state.index = index
                    
                    index.vectorstore.save_local("pdf")
                    os.remove("temp.pdf")
        except Exception as e:
            st.error(f"오류: {e}")
            st.stop()
    
    user_input = ""
    
    db = get_db()
    
    # 채팅 입력창
    if user_input := st.chat_input("질문을 입력하세요:"):
        if st.session_state.index is None:
            st.error("PDF 파일이 없습니다.")
            st.stop()
            
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        gen = chat_with_bot(st.session_state.messages, db)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in gen:
                delta = response.choices[0].delta
                if delta.content is not None:
                    full_response += delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
                
elif st.session_state.index is None:
    st.write("PDF 파일이 없습니다.")
    
