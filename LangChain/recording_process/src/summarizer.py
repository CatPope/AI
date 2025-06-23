# summarizer.py

import os
import sys
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate


class SummaryGenerator:
    def __init__(self):
        # 환경 변수 로드 및 경로 설정
        load_dotenv()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prompt_path = os.getenv("PROMPT_PATH")
        self.absolute_prompt_path = os.path.join(self.base_dir, self.prompt_path)
        sys.path.insert(0, self.absolute_prompt_path)

        # 모델 설정
        self.model_name = os.getenv("STRATEGIC_LLM_BASE")

        # 프롬프트 모듈 import 및 구성
        self.examples = self._load_examples()
        self.prompt = self._build_prompt()
        self.llm = OllamaLLM(model=self.model_name, temperature=0)

    def _load_examples(self):
        import examples_tpl
        import summarys_pmpt
        examples = examples_tpl.get_tpl()
        summarys = summarys_pmpt.get_prompt()

        for i in range(len(summarys)):
            examples[i]["answer"] = summarys[i]

        return examples

    def _build_prompt(self):
        example_prompt = PromptTemplate.from_template("Context:\n{context}\nAnswer:\n{answer}\n")
        return FewShotPromptTemplate(
            examples=self.examples,
            example_prompt=example_prompt,
            suffix="Context:\n{context}\nAnswer:\n",
            input_variables=["context"],
        )

    def generate(self, full_text: str):
        chain = self.prompt | self.llm | StrOutputParser()
        result = chain.invoke({"context": full_text})
        print("요약본이 작성되었습니다.")
        return result


# 테스트 실행
if __name__ == "__main__":
    generator = SummaryGenerator()
    summary = generator.generate("밥먹고 청소하고 자자.")
    print("\n=== 요약 결과 ===")
    print(summary)