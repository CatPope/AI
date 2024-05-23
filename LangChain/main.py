import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

chat = ChatOpenAI(model="gpt-4", temperature=0.2)

