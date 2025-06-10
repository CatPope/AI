from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_teddynote.messages import stream_response

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--examples", type=str, default="../data/prompts/examples.txt")
parser.add_argument("--context", type=str, default="../data/prompts/context.txt")
args = parser.parse_args()

with open(args.examples, "r", encoding='UTF8') as f:
    examples = f.read()
with open(args.context, "r", encoding='UTF8') as f:
    context = f.read()
examples = dict(examples)

# examples = [dict(ex) for examples in ex]



# llm = ChatOllama(model='qwen3:8b')

# example_prompt = PromptTemplate.from_template("Context:\n{context}\nAnswer:\n{answer}")
#
# prompt = FewShotPromptTemplate(
#     examples=examples,
#     example_prompt=example_prompt,
#     suffix="""Context:\n{context}\nAnswer:\n""",
#     input_variables=["context"],
# )
#
# # chain 생성
# chain = prompt | llm | StrOutputParser()
#
# # 결과 출력
# answer = chain.invoke({"context": context})
#
# print(answer)