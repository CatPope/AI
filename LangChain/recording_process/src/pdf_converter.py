# pdf_converter.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re


class PDFConverter:
    def __init__(self):
        self.font_name = self._register_korean_font()
        self.styles = self._build_styles()

    def _register_korean_font(self):
        font_paths = [
            'C:/Windows/Fonts/malgun.ttf',
            'C:/Windows/Fonts/gulim.ttc',
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont('KoreanFont', path))
                    print(f"한국어 폰트 등록 성공: {path}")
                    return 'KoreanFont'
                except Exception:
                    continue

        print("한국어 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        return 'Helvetica'

    def _build_styles(self):
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Heading1'],
                                  fontName=self.font_name, fontSize=24,
                                  leading=16, spaceBefore=25, spaceAfter=25))

        styles.add(ParagraphStyle(name='CustomHeading2', parent=styles['Heading2'],
                                  fontName=self.font_name, fontSize=20,
                                  leading=16, spaceBefore=20, spaceAfter=20))

        styles.add(ParagraphStyle(name='CustomHeading3', parent=styles['Heading3'],
                                  fontName=self.font_name, fontSize=16,
                                  leading=16, spaceBefore=15, spaceAfter=15))

        styles.add(ParagraphStyle(name='CustomNormal', parent=styles['Normal'],
                                  fontName=self.font_name, fontSize=12,
                                  leading=16, spaceAfter=12))
        return styles

    def convert(self, markdown_text: str, pdf_path: str) -> bool:
        """
        마크다운 형식의 텍스트를 PDF로 저장 (경로 고정)
        """
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=18)

            story = []
            lines = markdown_text.strip().split('\n')

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    story.append(Spacer(1, 6))
                    continue

                if stripped.startswith("# "):
                    story.append(Paragraph(stripped[2:], self.styles['CustomTitle']))
                elif stripped.startswith("## "):
                    story.append(Paragraph(stripped[3:], self.styles['CustomHeading2']))
                elif stripped.startswith("### "):
                    story.append(Paragraph(stripped[4:], self.styles['CustomHeading3']))
                elif stripped.startswith("- ") or stripped.startswith("* "):
                    story.append(Paragraph("• " + self._process_formatting(stripped[2:]), self.styles['CustomNormal']))
                elif re.match(r"^\d+\.\s", stripped):
                    number = re.match(r"^(\d+)\.", stripped).group(1)
                    text = re.sub(r"^\d+\.\s", "", stripped)
                    story.append(Paragraph(f"{number}. {self._process_formatting(text)}", self.styles['CustomNormal']))
                else:
                    story.append(Paragraph(self._process_formatting(stripped), self.styles['CustomNormal']))

            doc.build(story)
            print(f"PDF 저장 완료: {pdf_path}")
            return True

        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {e}")
            return False


    def _process_formatting(self, text: str) -> str:
        """
        마크다운 내 **굵게**, *기울임* 변환 처리
        """
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        return text

    @staticmethod
    def delete_pdf(pdf_path: str) -> bool:
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"삭제 완료: {pdf_path}")
                return True
            print(f"파일 없음: {pdf_path}")
            return False
        except Exception as e:
            print(f"삭제 실패: {e}")
            return False

    @staticmethod
    def clear_pdf_directory(directory: str = "../data/pdf") -> list:
        deleted = []
        try:
            for file in os.listdir(directory):
                if file.endswith(".pdf"):
                    os.remove(os.path.join(directory, file))
                    deleted.append(file)
            print(f"총 {len(deleted)}개 PDF 삭제됨.")
            return deleted
        except Exception as e:
            print(f"디렉토리 접근 오류: {e}")
            return []


# 테스트 실행
if __name__ == "__main__":
    sample_md = """
# 회의 요약

- **담당자**: 홍길동
- 일정: *2025년 6월 12일*
- 내용: 신규 시스템 도입 논의

## 결론
1. 시스템 명세 확정
2. 파일 변환 로직 도입

자세한 내용은 첨부 PDF 참조
    """
    converter = PDFConverter()
    converter.convert(sample_md, "../data/pdf/test_output.pdf")
