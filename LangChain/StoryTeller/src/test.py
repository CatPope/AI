from langgraph.checkpoint.memory import MemorySaver
from langchain_teddynote import logging
from dotenv import load_dotenv

# langsmith 로그 설정
load_dotenv()
logging.langsmith("meeting", set_enable=True)


memory = MemorySaver()