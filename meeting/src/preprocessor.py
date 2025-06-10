from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_teddynote import logging
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_teddynote.messages import stream_response
from dotenv import load_dotenv
import argparse
import json



load_dotenv()
logging.langsmith("meeting", set_enable=True)

llm = OllamaLLM(
    model="qwen3:8b",
    temperature=0
)


print(llm.invoke("안녕?"))