import dotenv



dotenv.load_dotenv()

from langchain_openai import ChatOpenAI

chat = ChatOpenAI(model="gpt-3.5-turbo -1106", temperature=0.2)

from langchain_core.messages import HumanMessage

chat.invoke(
    [
        HumanMessage(
            content="Translate this sentence from English to French: I love programming."
        )
    ]
)

