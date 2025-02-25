from dotenv import load_dotenv
import os
# import openai
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.vectorstores import FAISS


# 테스트용 api 불러오는 코드
# def env_loader():
#     load_dotenv()
#     openai.api_key = os.getenv("OPENAI_API_KEY")


def pdf_loader(file_path):
    loader = PyPDFLoader(file_path)
    return loader

# pdf 내용 출력
def show_pdf(loader):
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    context = [doc.page_content for doc in docs]
    print(context)


def create_vectorstore(loader, model):
    embeddings = OllamaEmbeddings(model=model)
    #embeddings = HuggingFaceEmbeddings()
    index = VectorstoreIndexCreator(
        vectorstore_cls=FAISS,
        embedding=embeddings,
        ).from_loaders([loader])
    # 파일로 저장
    index.vectorstore.save_local("vectorstore")
    return index


def set_model(model):
    chat = ChatOllama(
        model=model,
        temperature=0.1,
        num_predict=512,
        top_p=1,
    )
    return chat


def chat_setup():
    file_path = "C:/Users/user/Documents/GitLab/Test_Dawoo/mammoth_Langchain/doc/타임소프트 회사소개서.pdf"
    model = 'llama3.2-bllossom-kor-3B:latest'

    # env_loader()
    loader = pdf_loader(file_path)
    # show_pdf(loader)
    index = create_vectorstore(loader=loader, model=model)
    chat = set_model(model=model)

    return chat, index


def chat_input(index, user_input, chat):
    return index.query( user_input, llm=chat, )


if __name__ == "__main__":
    while True:
        chat, index = chat_setup()

        user_input = input("you: ")
        print(f"you: {user_input}")

        if user_input == "exit":
            break
        elif user_input.replace(" ", "") == "":
            print("chat: 질문이 없습니다. 정확한 질문을 해주시면 답변해 드리겠습니다.")
        else:
            chat_text = chat_input(
                chat=chat,
                index=index,
                user_input=user_input,
            )
            print(f"chat: {chat_text}")