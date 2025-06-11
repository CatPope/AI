import smtplib
from dotenv import load_dotenv
import os


def send_email(title, body):
    # 환경 변수 불러오기
    load_dotenv()
    # prompt 절대 경로 불러오기
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_APP_PW")


    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls() #Transport Layer Security : 메시지 암호화
        connection.login(user=sender_email, password=password)
        connection.sendmail(
            from_addr=sender_email,
            to_addrs="dawoo2140@naver.com",
            msg=f"Subject:{title}\n\n{body}"
        )