# email_sender.py

import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os


class EmailSender:
    def __init__(self, receiver_email="dawoo2140@naver.com"):
        load_dotenv()
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.password = os.getenv("EMAIL_APP_PW")
        self.receiver_email = receiver_email
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, title: str, body: str, pdf_path: str = None) -> bool:
        """
        이메일 제목, 본문, PDF 첨부 파일 경로를 받아 전송
        """
        try:
            msg = EmailMessage()
            msg["Subject"] = title
            msg["From"] = self.sender_email
            msg["To"] = self.receiver_email
            msg.set_content(body)

            if pdf_path:
                self._attach_pdf(msg, pdf_path)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.send_message(msg)

            print("이메일 전송 완료.")
            return True

        except Exception as e:
            print(f"이메일 전송 실패: {e}")
            return False

    def _attach_pdf(self, msg: EmailMessage, pdf_path: str):
        """
        PDF 파일을 이메일에 첨부
        """
        if not os.path.exists(pdf_path):
            print(f"첨부 파일 없음: {pdf_path}")
            return

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
            filename = os.path.basename(pdf_path)
            msg.add_attachment(pdf_data,
                               maintype="application",
                               subtype="pdf",
                               filename=filename)


# 테스트 실행
if __name__ == "__main__":
    email_sender = EmailSender()
    sample_title = "PDF 첨부 테스트"
    sample_body = """
# PDF 테스트

자동화된 회의 결과입니다. 첨부파일을 확인해주세요.
    """
    sample_pdf_path = "../data/pdf/test_output.pdf"
    email_sender.send_email(sample_title, sample_body, sample_pdf_path)
