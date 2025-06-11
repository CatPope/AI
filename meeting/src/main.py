# main.py

from meeting_stt import SpeechToText
from summarizer import SummaryGenerator
from title_writer import TitleGenerator
from pdf_converter import PDFConverter
from email_sender import EmailSender
from langchain_teddynote import logging
from dotenv import load_dotenv
import os
import re

# langsmith 로그 설정
load_dotenv()
logging.langsmith("meeting", set_enable=True)

# pdf 파일 탬플릿
def pdf_format(title: str, full_text: str, summary: str) -> str:
    return f"# {title}\n\n## 회의 내용\n{full_text}\n\n{summary}"

# <think>...</think> 블록 제거
def remove_think(with_think: str) -> str:
    return re.sub(r"<think>.*?</think>", "", with_think, flags=re.DOTALL)

# 줄바꿈 제거
def remove_ln(with_ln: str) -> str:
    return re.sub(r'[\r\n]+', ' ', with_ln)

# 파일명에 사용할 수 없는 특수 문자 제거
def sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*\n\r]', '', filename)

def main():
    # 1. 음성 인식 수행
    # stt_engine = SpeechToText()
    # full_text = stt_engine.transcribe()
    full_text="""다음 안건 넘어갈게요. 신규 입사자 온보딩 프로세스인데요, 최근 입사한 신입들 피드백을 종합해보니까, 첫 주에 너무 정보가 한꺼번에 쏟아져서 소화가 어렵다는 의견이 있었어요. 특히 시스템 계정, 복지 안내, 팀별 프로세스 등등이 동시에 설명되니까 정리가 안 된다고요.
저도 그 얘기 들었어요. 그래서 생각한 게, ‘신입 주간 체크리스트’ 형태로 각 항목을 시간 순서대로 분배해서 전달하면 어떨까요? 예를 들면 첫날은 사내 시스템 계정 등록, 둘째 날은 복지 가이드 오리엔테이션, 셋째 날은 팀 배정 후 온사이트 투어 이런 식으로요.
그것도 좋고, 제가 보니까 동영상으로 짧게 만들어서 사내 위키에 올리면 반복해서 보기도 좋을 것 같아요. 꼭 똑같은 설명 계속 안 해도 되고요.
좋은 의견이에요. 그럼 “신입 환영 키트”에 안내지랑 영상 링크 QR코드도 포함해서 구성해보죠. 지금은 텀블러랑 마우스패드만 들어있는데, 실용성도 살리고 정보도 전달하면 좋죠.
일단은 온보딩 개선안은 이 흐름으로 잡고, 다음 주까지 프로토타입 만들고 실제 적용은 다음 입사자부터 해보죠. 다음 입사 일정이 언제죠?
이번 달 말로 예정되어 있습니다. 신입 개발자 한 명, 기획팀 한 명 예정이에요."""

    # 2. 요약 생성
    summary_model = SummaryGenerator()
    summary_think_text = summary_model.generate(full_text)
    summary_text = remove_think(summary_think_text)

    # 3. 제목 생성
    title_model = TitleGenerator()
    title_think_text = title_model.generate(summary_text)
    title_ln_text = remove_think(title_think_text)
    title_text = remove_ln(title_ln_text)

    # 4. PDF 변환
    pdf_text = pdf_format(title_text, full_text, summary_text)
    filename = sanitize_filename(title_text)
    pdf_path = f"../data/pdf/{filename}.pdf"

    pdf_converter = PDFConverter()
    pdf_converter.convert(pdf_text, pdf_path)

    # 5. 이메일 발송
    body = f"{summary_text}\n\n자세한 회의 내용은 첨부된 PDF를 확인해주세요."
    email_sender = EmailSender()
    email_sender.send_email(title=title_text, body=body, pdf_path=pdf_path)


if __name__ == "__main__":
    main()
