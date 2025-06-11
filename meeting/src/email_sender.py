import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

def send_email(receiver_email, title, body, pdf_path=None):
    # .env 파일에서 환경 변수 로드
    load_dotenv()

    # sender_email = os.getenv("SENDER_EMAIL")
    # password = os.getenv("EMAIL_APP_PW")
    sender_email = "dajung2140@gmail.com"
    password = "zsuq zqdw laqp zbow"

    # 이메일 메시지 구성
    msg = EmailMessage()
    msg["Subject"] = title
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(body)

    # PDF 첨부 파일이 있는 경우 추가
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
            pdf_filename = os.path.basename(pdf_path)
            msg.add_attachment(pdf_data,
                               maintype="application",
                               subtype="pdf",
                               filename=pdf_filename)

    # 이메일 전송
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)

    print("이메일 전송 완료.")


send_email("dawoo2140@naver.com", "PDF 첨부 테스트", "PDF 확인 부탁드립니다.", "../data/pdf/example_output.pdf")