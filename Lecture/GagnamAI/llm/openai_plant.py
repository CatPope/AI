from dotenv import load_dotenv
load_dotenv()

# import os


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

tagging_prompt = ChatPromptTemplate.from_template(
    """
Extract the desired information from the following passage.

Only extract the properties mentioned in the 'Classification' function.

Passage:
{input}
"""
)


class Classification(BaseModel):
    sentiment: str = Field(description="The sentiment of the text")
    aggressiveness: int = Field(
        description="How aggressive the text is on a scale from 1 to 10"
    )
    language: str = Field(description="The language the text is written in")


# LLM
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125").with_structured_output(
    Classification
)

tagging_chain = tagging_prompt | llm

inp = "너를 알게 되어서 나는 믿을 수 없을 정도로 기뻐! 우린 정말 좋은 친구가 될 것 같아!"
res = tagging_chain.invoke({"input": inp})

Classification(sentiment='positive', aggressiveness=1, language='Korean')

print(res.dict())
print(res)