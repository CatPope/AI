from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import os


def markdown_to_pdf(markdown_text, output_filename):
    """
    Markdown 문자열을 PDF 파일로 변환 (reportlab 사용)

    Args:
        markdown_text (str): 변환할 markdown 문자열
        output_filename (str): 저장할 PDF 파일명 (예: "output.pdf")

    Returns:
        bool: 변환 성공 여부
    """
    try:
        # 한국어 폰트 등록 (시스템 폰트 사용)
        font_paths = [
            'C:/Windows/Fonts/malgun.ttf',  # Windows - 맑은 고딕
            'C:/Windows/Fonts/gulim.ttc',  # Windows - 굴림
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',  # macOS
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'  # Linux
        ]

        korean_font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                    korean_font_registered = True
                    print(f"한국어 폰트 등록 성공: {font_path}")
                    break
                except:
                    continue

        if not korean_font_registered:
            print("한국어 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")

        # PDF 문서 생성
        doc = SimpleDocTemplate(output_filename, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        # 스타일 설정
        styles = getSampleStyleSheet()

        # 한국어 폰트 사용 여부에 따른 폰트명 설정
        font_name = 'KoreanFont' if korean_font_registered else 'Helvetica'

        # 커스텀 스타일 정의
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=24,
            spaceAfter=20,
            spaceBefore=20
        ))

        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=20,
            spaceAfter=15,
            spaceBefore=15
        ))

        styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontName=font_name,
            fontSize=16,
            spaceAfter=12,
            spaceBefore=12
        ))

        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            spaceAfter=10
        ))

        # 문서 요소들을 저장할 리스트
        story = []

        # Markdown 텍스트를 줄 단위로 처리
        lines = markdown_text.strip().split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:  # 빈 줄
                story.append(Spacer(1, 6))
                i += 1
                continue

            # 제목 처리
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, styles['CustomTitle']))
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, styles['CustomHeading2']))
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, styles['CustomHeading3']))

            # 순서 없는 리스트 처리
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                # 굵은글씨, 기울임 처리
                text = process_formatting(text)
                story.append(Paragraph(f"• {text}", styles['CustomNormal']))

            # 순서 있는 리스트 처리
            elif re.match(r'^\d+\.\s', line):
                text = re.sub(r'^\d+\.\s', '', line).strip()
                # 굵은글씨, 기울임 처리
                text = process_formatting(text)
                number = re.match(r'^(\d+)\.', line).group(1)
                story.append(Paragraph(f"{number}. {text}", styles['CustomNormal']))

            # 일반 텍스트 처리
            else:
                # 굵은글씨, 기울임 처리
                text = process_formatting(line)
                story.append(Paragraph(text, styles['CustomNormal']))

            i += 1

        # PDF 생성
        doc.build(story)
        print(f"PDF 파일이 성공적으로 생성되었습니다: {output_filename}")
        return True

    except Exception as e:
        print(f"PDF 변환 중 오류가 발생했습니다: {e}")
        return False


def process_formatting(text):
    """
    굵은글씨, 기울임 등의 마크다운 서식을 HTML 태그로 변환
    """
    # **굵은글씨** -> <b>굵은글씨</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    # *기울임* -> <i>기울임</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)

    return text


def delete_pdf(filename):
    """
    PDF 파일을 삭제하는 함수

    Args:
        filename (str): 삭제할 PDF 파일명 (예: "output.pdf")

    Returns:
        bool: 삭제 성공 여부
    """
    try:
        file_path = f"../data/pdf/{filename}.pdf"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"PDF 파일이 성공적으로 삭제되었습니다: {file_path}")
            return True
        else:
            print(f"파일을 찾을 수 없습니다: {file_path}")
            return False

    except PermissionError:
        print(f"파일 삭제 권한이 없습니다: {file_path}")
        return False
    except Exception as e:
        print(f"파일 삭제 중 오류가 발생했습니다: {e}")
        return False


def delete_all_pdfs_in_directory(directory="../data/pdf"):
    """
    특정 디렉토리의 모든 PDF 파일을 삭제하는 함수

    Args:
        directory (str): 대상 디렉토리 경로 (기본값: 현재 디렉토리)

    Returns:
        list: 삭제된 파일 목록
    """
    try:
        deleted_files = []

        # 디렉토리의 모든 파일 확인
        for filename in os.listdir(directory):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                    print(f"삭제됨: {filename}")
                except Exception as e:
                    print(f"삭제 실패 {filename}: {e}")

        if deleted_files:
            print(f"\n총 {len(deleted_files)}개의 PDF 파일이 삭제되었습니다.")
        else:
            print("삭제할 PDF 파일이 없습니다.")

        return deleted_files

    except Exception as e:
        print(f"디렉토리 접근 오류: {e}")
        return []

def md_to_pdf(markdown_text, filename):
    # PDF 변환 실행
    markdown_to_pdf(markdown_text, f"../data/pdf/{filename}.pdf")