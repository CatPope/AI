import os
import requests
from dotenv import load_dotenv

from langchain_teddynote.logging import langsmith
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from typing import Optional

# ====== 환경 변수 설정 ======
load_dotenv()
langsmith("llm_test", set_enable=True)
API_URL = os.getenv("API_URL", "http://192.168.10.239:8081/completion")
MODEL_PATH = os.getenv("MODEL_PATH", "C:/Users/qwer/Documents/GitHub/AI/LangChain/asking_company/model/gemma-3-r1984-27b-q8_0.gguf")
PDF_PATH = os.getenv("PDF_PATH", "/doc/files/타임소프트 회사소개서.pdf")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./faiss_index")
SYSTEM_PROMPT = """<SystemPrompt>
Take a deep breath and think through your response step by step.  
If anything is unclear or you have questions, keep asking the user for clarification.  
Ensure every sentence ends with a period ('.').

You are a chatbot providing RAG (Retrieval-Augmented Generation) functionality. You handle user queries by searching relevant information in internal documents or external knowledge stores, then generate accurate, reliable answers based solely on that information.

1. Role Definition (Role)  
   - Understand the user’s question, then execute the RAG workflow: search documents → extract information → generate the answer.

2. Communication Style (Style)  
   - Use a polite, professional tone and clearly indicate how you searched and what sources you used.  
   - Explain complex concepts in simple language and include examples or quoted passages when helpful.  
   - Ensure every sentence ends with a period ('.').

3. Functions (Functions)  
   - **Query Analysis**: If needed, ask follow-up questions to clarify the user’s intent.  
   - **Document Search**: Use your VectorDB (e.g., Chroma, Elasticsearch) to retrieve relevant documents via embedding similarity or keyword search.  
   - **Information Extraction**: Identify key sentences or data in the retrieved documents to serve as evidence.  
   - **Answer Generation**: Compose a clear, coherent answer based on the extracted information, citing document titles or locations.  
   - **Further Verification**: After answering, if any points remain unclear, continue to ask questions to ensure understanding.

4. Constraints (Constraints)  
   - Base your answers strictly on information found within the searched documents; if something cannot be found, respond with “Unknown.”  
   - Do not provide the final answer until the user explicitly requests “Show me the result.” Ask any additional questions first.  
   - Ensure all search and answer steps rely on official documents or verified sources; avoid speculation or false information.  
   - Ensure every sentence ends with a period ('.').  
</SystemPrompt>"""

# ====== LangChain Custom LLM(REST API Wrapper, pydantic 호환) ======
class RESTAPILLM(LLM):
    api_url: str
    n_predict: int = 50
    temperature: float = 0.2
    system_prompt: Optional[str] = ""

    def _call(self, prompt, stop=None):
        headers = {"Content-Type": "application/json"}
        payload = {
            "prompt": f"{self.system_prompt}\n질문: {prompt}",
            "n_predict": self.n_predict,
            "temperature": self.temperature,
            "stream": False
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        if response.ok:
            data = response.json()
            return data.get("content", "")
        else:
            return f"[REST API 오류] {response.status_code}: {response.text}"

    @property
    def _llm_type(self):
        return "rest_api_llm"

# ====== 벡터 DB 불러오기/생성 함수 ======
def get_or_create_faiss_index(pdf_path, vector_db_path):
    if os.path.exists(vector_db_path):
        return FAISS.load_local(vector_db_path, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
    # 새로 생성
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = VectorstoreIndexCreator(
        vectorstore_cls=FAISS,
        embedding=embeddings,
    ).from_documents(docs)
    # 벡터 DB 저장 (필요시 주석 해제)
    # index.vectorstore.save_local(vector_db_path)
    return index.vectorstore

# ====== 프롬프트 설정 ======
prompt_template = PromptTemplate(
    input_variables=["question"],
    template=SYSTEM_PROMPT + "\n질문: {question}\n답변:"
)

# ====== LangChain 체인 정의 ======
def get_chain(llm, prompt_template):
    return prompt_template | llm | StrOutputParser()

# ====== 메인 CLI 함수 ======
def run_llm_chat():
    print("REST API LLM 모드입니다. (exit 입력 시 종료)\n")
    llm = RESTAPILLM(api_url=API_URL, n_predict=50, temperature=0, system_prompt=SYSTEM_PROMPT)
    chain = get_chain(llm, prompt_template)
    while True:
        user_input = input("질문: ")
        if user_input.strip().lower() == "exit":
            print("종료합니다.")
            break
        if not user_input.strip():
            print("질문이 없습니다. 정확한 질문을 입력해주세요.")
            continue
        answer = chain.invoke({"question": user_input})
        print(f"\n답변: {answer.strip()}\n")

def run_rag_chat():
    print("REST API RAG(PDF) 모드입니다. (exit 입력 시 종료)\n")
    vector_db = get_or_create_faiss_index(PDF_PATH, VECTOR_DB_PATH)
    llm = RESTAPILLM(api_url=API_URL, n_predict=50, temperature=0, system_prompt=SYSTEM_PROMPT)
    chain = get_chain(llm, prompt_template)

    while True:
        user_input = input("질문: ")
        if user_input.strip().lower() == "exit":
            print("종료합니다.")
            break
        if not user_input.strip():
            print("질문이 없습니다. 정확한 질문을 입력해주세요.")
            continue
        # RAG: 유사 문서 추출
        docs = vector_db.similarity_search(user_input, k=5)
        context = "\n\n".join(doc.page_content for doc in docs)
        formatted_question = f"{user_input}\n\n<documents>\n{context}\n<documents>"
        answer = chain.invoke({"question": formatted_question})
        print(f"\n답변: {answer.strip()}\n")

if __name__ == "__main__":
    print("모드를 선택하세요:")
    print("1. REST API LLM 모드 (기본)")
    print("2. REST API RAG(PDF) 모드")
    mode = input("선택 (1/2): ").strip()
    if mode == "2":
        run_rag_chat()
    else:
        run_llm_chat()
