from langchain_community.llms import LlamaCpp
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.indexes import VectorstoreIndexCreator
from langchain.prompts import PromptTemplate

system_prompt = """<SystemPrompt>
숨을 깊게 쉬고, 순차적으로 고민한 뒤에 대답하세요.
...
"""

llm = LlamaCpp(
    model_path="C:/Users/qwer/Documents/GitHub/AI/LangChain/asking_company/model/gemma-3-r1984-27b-q8_0.gguf",
    n_ctx=4096,
    n_gpu_layers=-1,
    temperature=0.2,
    verbose=True,
)

loader = PyPDFLoader("/doc/files/타임소프트 회사소개서.pdf")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # 명시적 설정
index = VectorstoreIndexCreator(
    vectorstore_cls=FAISS,
    embedding=embeddings,
).from_documents(docs)

prompt_template = PromptTemplate(
    input_variables=["question"],
    template=system_prompt + "\n질문: {question}\n답변:"
)

while True:
    user_input = input("you: ")

    if user_input.strip() == "":
        print("질문이 없습니다. 정확한 질문을 입력해주세요.")
        continue
    if user_input.lower() == "exit":
        break

    formatted_question = prompt_template.format(question=user_input)

    try:
        response = index.query(formatted_question, llm=llm)
        print(f"chat: {response}")
    except Exception as e:
        print(f"[Error] {e}")
