from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_teddynote import logging
from langchain_teddynote.messages import stream_response
from dotenv import load_dotenv
import sys
import os

# 환경 변수 불러오기
load_dotenv()
# prompt 절대 경로 불러오기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_PATH = os.getenv("PROMPT_PATH")
ABSOLUTE_PROMPT_PATH = os.path.join(BASE_DIR, PROMPT_PATH)
sys.path.insert(0, ABSOLUTE_PROMPT_PATH)


# prompt import
import examples_pmpt
import context_pmpt
import titles_pmpt

# 프롬프트 저장
context = context_pmpt.get_prompt()
examples = examples_pmpt.get_prompt()
titles = titles_pmpt.get_prompt()

# langsmith 호출
logging.langsmith("meeting", set_enable=True)

# 회의록과 요약본 병합
for i in range(len(titles)):
    examples[i]["answer"] = titles[i]

# 가벼운 llm
fast_llm = os.getenv("FAST_LLM_BASE")
llm = OllamaLLM(
    model=fast_llm,
    temperature=0
)

# 출력 형식 지정
example_prompt = PromptTemplate.from_template("Context:\n{context}\nAnswer:\n{answer}\n")

# 프롬프트 구성
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Context:\n{context}\nAnswer:\n",
    input_variables=["context"],
)

# chain 생성
chain = prompt | llm | StrOutputParser()

# 결과 출력
result = chain.stream({"context": context})

stream_response(result)