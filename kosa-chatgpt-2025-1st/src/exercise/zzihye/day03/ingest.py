from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from PyPDF2 import PdfReader
import os

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("환경 변수 'OPENAI_API_KEY'를 설정하세요.")

def pdf_to_vectors(pdf_path, db_path):
    # PDF 텍스트 읽기
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # 텍스트를 청크로 나누기
    from langchain.text_splitter import CharacterTextSplitter

    text_splitter = CharacterTextSplitter(
        chunk_size=300,      # 청크 크기를 300으로 줄임
        chunk_overlap=50     # 청크 간 중복을 50으로 줄임
    )
    chunks = text_splitter.split_text(text)


    # VectorDB 생성
    documents = [Document(page_content=chunk) for chunk in chunks]
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(db_path)
    print(f"VectorDB 저장 완료: {db_path}")

if __name__ == "__main__":
    # 테스트용 PDF 파일과 VectorDB 경로 설정
    pdf_path = "소나기.pdf"  # 테스트 PDF 경로
    db_path = "vectordb"
    pdf_to_vectors(pdf_path, db_path)
