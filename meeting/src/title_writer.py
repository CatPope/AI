# title_writer.py

import os
import sys
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate


class TitleGenerator:
    def __init__(self):
        # 환경 변수 로드 및 경로 설정
        load_dotenv()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prompt_path = os.getenv("PROMPT_PATH")
        self.absolute_prompt_path = os.path.join(self.base_dir, self.prompt_path)
        sys.path.insert(0, self.absolute_prompt_path)

        # 모델 설정
        self.model_name = os.getenv("STRATEGIC_LLM_BASE")
        self.llm = OllamaLLM(model=self.model_name, temperature=0)

        # 프롬프트 예시 불러오기
        self.examples = self._load_examples()

    def _load_examples(self):
        import examples_tpl
        import summarys_pmpt
        import titles_pmpt

        examples = examples_tpl.get_tpl()
        summarys = summarys_pmpt.get_prompt()
        titles = titles_pmpt.get_prompt()

        for i in range(len(titles)):
            if i > 0:
                examples[i]["context"] = summarys[i]
            examples[i]["answer"] = titles[i]
        return examples

    def _build_prompt(self):
        example_prompt = PromptTemplate.from_template("Context:\n{context}\nAnswer:\n{answer}\n")

        return FewShotPromptTemplate(
            examples=self.examples,
            example_prompt=example_prompt,
            suffix="Context:\n{context}\nAnswer:\n",
            input_variables=["context"],
        )

    def generate(self, summary_text: str) -> str:
        """
        summary_text를 기반으로 제목을 생성한다.
        """
        prompt = self._build_prompt()
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"context": summary_text})
        print("제목이 작성되었습니다.")
        return result


# 테스트용 실행
if __name__ == "__main__":
    dummy_summary = """## 회의 요약  
- **신입 온보딩 개선안**:  
  - **문제**: 신입 직원들이 첫 주에 시스템 계정, 복지 안내, 팀 프로세스 등 정보가 한꺼번에 제공되면서 소화에 어려움.  
  - **해결 방안**:  
    1. **주간 체크리스트**로 시간 순서대로 항목 분배 (예: 첫날 시스템 계정 등록, 둘째 날 복지 가이드, 셋째 날 팀 투어 등).  
    2. **동영상 안내** 제작 및 사내 위키에 공유 (반복 학습 용이).  
    3. **신입 환영 키트** 구성: 안내지, 영상 링크 QR코드, 실용성 있는 물품 (텀블러, 마우스패드 등).  

- **실시 계획**:  
  - **프로토타입 개발**: 다음 주까지 완료.  
  - **실제 적용**: 7월 말 입사자부터 시행.  

- **다음 입사 일정**:  
  - **예정일**: 7월 말.  
  - **예상 인원**: 개발자 1명, 기획팀 1명.  

- **추가 고려사항**:  
  - **HRBP 협업**: 온보딩 프로세스 개선을 위해 HRBP와의 협의 필요.  
  - **피드백 수집**: 실제 적용 후 신입 직원의 반응을 모니터링하여 개선.  

**결론**:  
온보딩 프로세스를 체계화하고 정보 전달 방식을 개선해 신입 직원의 적응을 촉진할 수 있는 방안으로, 프로토타입 개발 후 7월 말 입사자부터 적용할 예정입니다.  
"""
    generator = TitleGenerator()
    title = generator.generate(dummy_summary)
    print("\n=== 생성된 제목 ===")
    print(title)
