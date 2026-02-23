from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")
#load_dotenv()

file_name = 'data/소나기.pdf'

loader = PyPDFLoader(file_name)
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

#embeddings = HuggingFaceEmbeddings()
embeddings = OpenAIEmbeddings()

from langchain_community.vectorstores import FAISS

# LangChain 1.0에서는 VectorstoreIndexCreator 대신 직접 벡터스토어 생성
vectorstore = FAISS.from_documents(docs, embeddings)

# 파일로 저장
vectorstore.save_local("shower")